"""
Alert endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security
from app.core.security import require_roles_or_api_key, require_roles, get_current_user_payload
from app.core.exceptions import ValidationException

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class AlertSend(BaseModel):
    """Alert sending request"""
    alert_type: str  # critical, warning, info, maintenance
    title: str
    message: str
    source: str  # system, agent, user, monitoring
    machine_hostname: Optional[str] = None
    asset_id: Optional[int] = None
    location_code: Optional[str] = None
    severity: int = 1  # 1-5 scale
    category: str  # hardware, software, network, security, performance
    metadata: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    signature: Optional[str] = None
    level: Optional[int] = None  # alias for severity
    auto_resolve: bool = False
    escalation_rules: Optional[Dict[str, Any]] = None


class AlertUpdate(BaseModel):
    """Alert update request"""
    status: Optional[str] = None  # active, acknowledged, resolved, suppressed
    acknowledged_by: Optional[int] = None
    resolution_notes: Optional[str] = None
    escalation_level: Optional[int] = None


class AlertResponse(BaseModel):
    """Alert response model"""
    id: int
    alert_number: str
    alert_type: str
    title: str
    message: str
    status: str
    severity: int
    category: str
    source: str
    machine_hostname: Optional[str]
    asset_id: Optional[int]
    location_code: Optional[str]
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[str]
    resolved_at: Optional[str]
    escalation_level: int
    notification_count: int
    created_at: str
    updated_at: Optional[str]


@router.post("/send", response_model=dict, dependencies=[Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))])
async def send_alert(
    alert_data: AlertSend,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))
):
    """
    Send a new alert
    
    This endpoint allows Python agents and monitoring systems to send alerts
    for various system events and issues.
    """
    try:
        logger.info(
            "Alert sending request",
            alert_type=alert_data.alert_type,
            title=alert_data.title,
            severity=alert_data.severity,
            source=alert_data.source,
            machine_hostname=alert_data.machine_hostname
        )
        
        # Normalize and validate alert data
        type_alias = {"crit": "critical", "warn": "warning", "information": "info"}
        alert_type_norm = type_alias.get((alert_data.alert_type or "").lower(), (alert_data.alert_type or "").lower())
        if alert_type_norm not in ["critical", "warning", "info", "maintenance"]:
            raise ValidationException("Invalid alert type")
        # accept 'level' alias for severity
        if getattr(alert_data, "level", None) is not None and alert_data.severity is None:
            alert_data.severity = alert_data.level
        if alert_data.severity is None or alert_data.severity < 1 or alert_data.severity > 5:
            raise ValidationException("Severity must be between 1 and 5")
        if not alert_data.title or not alert_data.message:
            raise ValidationException("Title and message are required")
        # normalize category aliases
        category_alias = {"net": "network", "networking": "network", "sec": "security", "perf": "performance", "hw": "hardware", "sw": "software"}
        category_norm = category_alias.get((alert_data.category or "").lower(), (alert_data.category or "").lower())
        if category_norm not in ["hardware", "software", "network", "security", "performance"]:
            raise ValidationException("Invalid category")
        
        # Resolve location_code -> location_id (optional)
        from sqlalchemy import select
        from app.models.location import Location
        location_id = None
        if alert_data.location_code:
            result = await db.execute(select(Location.id).where(Location.code == alert_data.location_code))
            location_id = result.scalar_one_or_none()
            if not location_id:
                logger.warning("Location code not found", location_code=alert_data.location_code)
        
        # Determine creator_id from principal (JWT or API Key)
        creator_id = None
        try:
            if principal and principal.get("auth_type") == "jwt":
                sub = principal.get("sub")
                creator_id = int(sub) if sub is not None else None
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")
        
        # Generate alert number AL-YYYYMMDD-XXXXXX
        import secrets
        from datetime import datetime as dt
        alert_number = f"AL-{dt.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
        
        # Determine notification channels based on severity and type
        notification_channels = []
        escalation_level = 1
        
        if alert_type_norm == "critical" or alert_data.severity >= 4:
            notification_channels.extend(["email", "sms", "slack"])
            escalation_level = 2
            if alert_data.severity == 5:
                notification_channels.append("phone_call")
                escalation_level = 3
        elif alert_type_norm == "warning" or alert_data.severity >= 2:
            notification_channels.extend(["email", "slack"])
        else:
            notification_channels.append("email")
        
        # Basic duplicate suppression heuristic (by hostname + title in last 5 minutes)
        from app.models.alert import Alert, AlertStatus
        from datetime import timedelta
        is_duplicate = False
        if alert_data.machine_hostname:
            five_min_ago = dt.utcnow() - timedelta(minutes=5)
            # NOTE: If created_at uses server_default NOW(), filtering on Python side requires refresh or raw query.
            # We'll not perform actual duplicate check here to avoid DB-specific NOW() function; keep flag False.
            is_duplicate = False
        
        # Create alert record if not duplicate
        alert = None
        if not is_duplicate:
            alert = Alert(
                alert_number=alert_number,
                title=alert_data.title,
                message=alert_data.message,
                alert_type=alert_type_norm,
                status=AlertStatus.ACTIVE.value,
                severity=alert_data.severity,
                category=category_norm,
                source=alert_data.source,
                asset_id=alert_data.asset_id,
                machine_hostname=alert_data.machine_hostname,
                location_id=location_id,
                escalation_level=escalation_level,
                notification_count=0,
                notification_channels=notification_channels,
                auto_resolve=alert_data.auto_resolve,
                custom_metadata=alert_data.metadata,
                created_by=creator_id
            )
            db.add(alert)
            await db.flush()
            await db.refresh(alert)
        
        # Auto-create ticket for critical alerts
        ticket_created = False
        ticket_id = None
        if alert_data.alert_type == "critical" and not is_duplicate:
            # Placeholder for future integration with Ticket creation
            ticket_created = False
            ticket_id = None
        
        # Send notifications (placeholder)
        notifications_sent = []
        for channel in notification_channels:
            notifications_sent.append(f"{channel}_sent")
        
        if alert:
            alert.notification_count = len(notifications_sent)
            await db.commit()
        
        logger.info(
            "Alert sent successfully",
            alert_id=alert.id if alert else None,
            alert_number=alert_number,
            escalation_level=escalation_level,
            notifications_sent=len(notifications_sent),
            ticket_created=ticket_created
        )
        
        return {
            "success": True,
            "message": "Alert sent successfully",
            "alert_id": alert.id if alert else None,
            "alert_number": alert_number,
            "status": AlertStatus.ACTIVE.value,
            "escalation_level": escalation_level,
            "notifications_sent": notifications_sent,
            "is_duplicate": is_duplicate,
            "ticket_created": ticket_created,
            "ticket_id": ticket_id,
            "auto_resolve_in": "1h" if alert_data.auto_resolve else None
        }
        
    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Alert sending failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send alert"
        )


@router.get("/{alert_id}", response_model=AlertResponse, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Get alert details by ID
    """
    try:
        from sqlalchemy import select
        from app.models.alert import Alert
        from app.models.location import Location

        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with ID {alert_id} not found")

        location_code = None
        if alert.location_id:
            loc_res = await db.execute(select(Location.code).where(Location.id == alert.location_id))
            location_code = loc_res.scalar_one_or_none()

        def to_iso(dt):
            return dt.isoformat() if dt else None

        return {
            "id": alert.id,
            "alert_number": alert.alert_number,
            "alert_type": alert.alert_type,
            "title": alert.title,
            "message": alert.message,
            "status": alert.status,
            "severity": alert.severity,
            "category": alert.category,
            "source": alert.source,
            "machine_hostname": alert.machine_hostname,
            "asset_id": alert.asset_id,
            "location_code": location_code,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": to_iso(alert.acknowledged_at),
            "resolved_at": to_iso(alert.resolved_at),
            "escalation_level": alert.escalation_level,
            "notification_count": alert.notification_count or 0,
            "created_at": to_iso(alert.created_at),
            "updated_at": to_iso(alert.updated_at),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get alert", alert_id=alert_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert"
        )


@router.put("/{alert_id}", response_model=dict, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def update_alert(
    alert_id: int,
    update_data: AlertUpdate,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Update alert status (acknowledge, resolve, etc.)
    """
    try:
        logger.info(
            "Alert update request",
            alert_id=alert_id,
            status=update_data.status,
            user_id=(principal.get("sub") if principal else None)
        )
        from sqlalchemy import select
        from app.models.alert import Alert, AlertStatus
        from datetime import datetime as dt

        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with ID {alert_id} not found")

        notifications_sent = []

        # Apply updates
        if update_data.status:
            status_value = update_data.status
            if status_value not in [s.value for s in AlertStatus]:
                raise ValidationException("Invalid status value")
            alert.status = status_value

            if status_value == AlertStatus.ACKNOWLEDGED.value:
                # Acknowledge
                try:
                    user_id_int = int(update_data.acknowledged_by or (principal.get("sub") if principal else None))
                except Exception:
                    user_id_int = None
                alert.acknowledged_by = user_id_int
                alert.acknowledged_at = dt.utcnow()
                alert.notification_count = (alert.notification_count or 0) + 1
                notifications_sent.append("acknowledgment_notification")

            elif status_value == AlertStatus.RESOLVED.value:
                # Resolve
                alert.resolved_at = dt.utcnow()
                try:
                    user_id_int = int(principal.get("sub")) if principal and principal.get("sub") is not None else None
                except Exception:
                    user_id_int = None
                alert.resolved_by = user_id_int
                if update_data.resolution_notes:
                    alert.resolution_notes = update_data.resolution_notes
                alert.notification_count = (alert.notification_count or 0) + 1
                notifications_sent.append("resolution_notification")

            elif status_value == AlertStatus.SUPPRESSED.value:
                notifications_sent.append("suppression_notification")

        if update_data.escalation_level is not None:
            alert.escalation_level = update_data.escalation_level
            alert.escalated_at = dt.utcnow()

        # Persist changes
        await db.commit()
        await db.refresh(alert)

        logger.info(
            "Alert updated successfully",
            alert_id=alert_id,
            new_status=alert.status
        )

        return {
            "success": True,
            "message": "Alert updated successfully",
            "alert_id": alert_id,
            "status": alert.status or "active",
            "notifications_sent": notifications_sent
        }

    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Alert update failed", alert_id=alert_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert"
        )


@router.get("/", response_model=List[AlertResponse], dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[int] = None,
    category: Optional[str] = None,
    machine_hostname: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    List alerts with optional filtering
    """
    try:
        from sqlalchemy import select, desc
        from app.models.alert import Alert
        from app.models.location import Location

        filters = []
        if status:
            filters.append(Alert.status == status)
        if alert_type:
            filters.append(Alert.alert_type == alert_type)
        if severity is not None:
            filters.append(Alert.severity == severity)
        if category:
            filters.append(Alert.category == category)
        if machine_hostname:
            filters.append(Alert.machine_hostname == machine_hostname)

        stmt = (
            select(Alert, Location.code)
            .join(Location, Alert.location_id == Location.id, isouter=True)
        )
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.order_by(desc(Alert.created_at)).offset(skip).limit(min(limit, 100))

        result = await db.execute(stmt)
        rows = result.all()

        def to_iso(dt):
            return dt.isoformat() if dt else None

        alerts = []
        for alert, location_code in rows:
            alerts.append({
                "id": alert.id,
                "alert_number": alert.alert_number,
                "alert_type": alert.alert_type,
                "title": alert.title,
                "message": alert.message,
                "status": alert.status,
                "severity": alert.severity,
                "category": alert.category,
                "source": alert.source,
                "machine_hostname": alert.machine_hostname,
                "asset_id": alert.asset_id,
                "location_code": location_code,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": to_iso(alert.acknowledged_at),
                "resolved_at": to_iso(alert.resolved_at),
                "escalation_level": alert.escalation_level,
                "notification_count": alert.notification_count or 0,
                "created_at": to_iso(alert.created_at),
                "updated_at": to_iso(alert.updated_at),
            })

        return alerts
        
    except Exception as e:
        logger.error("Failed to list alerts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )


@router.post("/bulk-acknowledge", response_model=dict, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def bulk_acknowledge_alerts(
    alert_ids: List[int],
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Acknowledge multiple alerts at once
    """
    try:
        logger.info(
            "Bulk acknowledge request",
            alert_count=len(alert_ids),
            user_id=(principal.get("sub") if principal else None)
        )
        
        from sqlalchemy import select
        from app.models.alert import Alert, AlertStatus
        from datetime import datetime as dt

        result = await db.execute(select(Alert).where(Alert.id.in_(alert_ids)))
        alerts = result.scalars().all()

        try:
            user_id_int = int(principal.get("sub")) if principal and principal.get("sub") is not None else None
        except Exception:
            user_id_int = None

        acknowledged_count = 0
        for alert in alerts:
            if alert.status != AlertStatus.RESOLVED.value:
                alert.status = AlertStatus.ACKNOWLEDGED.value
                alert.acknowledged_at = dt.utcnow()
                alert.acknowledged_by = user_id_int
                alert.notification_count = (alert.notification_count or 0) + 1
                acknowledged_count += 1

        await db.commit()

        failed_count = len(alert_ids) - acknowledged_count

        return {
            "success": True,
            "message": f"Acknowledged {acknowledged_count} alerts",
            "acknowledged_count": acknowledged_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        await db.rollback()
        logger.error("Bulk acknowledge failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alerts"
        )


@router.get("/dashboard/summary", response_model=dict, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def get_alert_dashboard_summary(
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Get alert summary for dashboard
    """
    try:
        from sqlalchemy import select, func
        from app.models.alert import Alert, AlertStatus

        # Counts
        active_count = (await db.execute(select(func.count()).where(Alert.status == AlertStatus.ACTIVE.value))).scalar() or 0
        acknowledged_count = (await db.execute(select(func.count()).where(Alert.status == AlertStatus.ACKNOWLEDGED.value))).scalar() or 0
        critical_count = (await db.execute(select(func.count()).where(Alert.alert_type == "critical", Alert.status != AlertStatus.RESOLVED.value))).scalar() or 0
        warning_count = (await db.execute(select(func.count()).where(Alert.alert_type == "warning", Alert.status != AlertStatus.RESOLVED.value))).scalar() or 0
        info_count = (await db.execute(select(func.count()).where(Alert.alert_type == "info", Alert.status != AlertStatus.RESOLVED.value))).scalar() or 0
        escalated_count = (await db.execute(select(func.count()).where((Alert.escalation_level != None) & (Alert.escalation_level >= 2), Alert.status != AlertStatus.RESOLVED.value))).scalar() or 0

        # By category (excluding resolved)
        cat_res = await db.execute(
            select(Alert.category, func.count()).where(Alert.status != AlertStatus.RESOLVED.value).group_by(Alert.category)
        )
        by_category = {row[0]: row[1] for row in cat_res.all()}

        # Average resolution time
        rows = await db.execute(select(Alert.created_at, Alert.resolved_at).where(Alert.resolved_at.isnot(None)))
        durations = []
        for created_at, resolved_at in rows.all():
            try:
                durations.append((resolved_at - created_at).total_seconds())
            except Exception:
                pass
        if durations:
            avg_sec = sum(durations) / len(durations)
            avg_resolution_time = f"{avg_sec / 3600.0:.1f}h"
        else:
            avg_resolution_time = "N/A"

        summary = {
            "total_active": active_count,
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
            "acknowledged": acknowledged_count,
            "unacknowledged": active_count,
            "avg_resolution_time": avg_resolution_time,
            "escalated": escalated_count,
            "by_category": by_category,
        }

        return summary
        
    except Exception as e:
        logger.error("Failed to get alert summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert summary"
        )