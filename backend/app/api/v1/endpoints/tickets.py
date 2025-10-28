"""
Ticket endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security
from app.core.exceptions import NotFoundException, ValidationException
from sqlalchemy import select
from app.core.security import require_roles_or_api_key
from app.core.security import require_roles, get_current_user_payload

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class TicketCreate(BaseModel):
    """Ticket creation request"""
    title: str
    description: str
    priority: str  # low, medium, high, critical
    category: str  # hardware, software, network, security, other
    asset_id: Optional[int] = None
    machine_hostname: Optional[str] = None
    location_code: Optional[str] = None
    requester_email: Optional[str] = None
    requester_name: Optional[str] = None
    department: Optional[str] = None
    attachments: Optional[List[str]] = None


class TicketUpdate(BaseModel):
    """Ticket update request"""
    status: Optional[str] = None  # open, in_progress, resolved, closed
    assigned_to: Optional[int] = None
    priority: Optional[str] = None
    resolution: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None


class TicketComment(BaseModel):
    """Ticket comment"""
    comment: str
    is_internal: bool = False
    attachments: Optional[List[str]] = None


class TicketResponse(BaseModel):
    """Ticket response model"""
    id: int
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    asset_id: Optional[int]
    machine_hostname: Optional[str]
    location_code: Optional[str]
    requester_name: Optional[str]
    requester_email: Optional[str]
    assigned_to: Optional[int]
    assigned_to_name: Optional[str]
    resolution: Optional[str]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    created_at: str
    updated_at: Optional[str]
    resolved_at: Optional[str]


@router.post("/create", response_model=TicketResponse, dependencies=[Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))])
async def create_ticket(
    ticket: TicketCreate,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))
):
    """
    Create a new support ticket
    
    This endpoint allows creation of support tickets for asset-related issues.
    Can be called by Python agents or web interface.
    """
    try:
        logger.info(
            "Ticket creation request",
            title=ticket.title,
            priority=ticket.priority,
            category=ticket.category,
            auth_type=principal.get("auth_type")
        )
        
        if not ticket.title or not ticket.description:
            raise ValidationException("Title and description are required")
        
        from app.models.ticket import Ticket, TicketPriority, TicketCategory, TicketStatus
        priority_norm = (ticket.priority or "").lower()
        alias_map = {"low": "low", "medium": "medium", "med": "medium", "high": "high", "critical": "critical", "crit": "critical"}
        priority_norm = alias_map.get(priority_norm, priority_norm)
        if priority_norm not in [p.value for p in TicketPriority]:
            raise ValidationException("Invalid priority level")
        
        category_norm = (ticket.category or "").lower()
        category_alias = {"net": "network"}
        category_norm = category_alias.get(category_norm, category_norm)
        if category_norm not in [c.value for c in TicketCategory]:
            raise ValidationException("Invalid category")
        
        from sqlalchemy import select
        from app.models.location import Location
        location_id = None
        if ticket.location_code:
            result = await db.execute(select(Location.id).where(Location.code == ticket.location_code))
            location_id = result.scalar_one_or_none()
            if not location_id:
                logger.warning("Location code not found", location_code=ticket.location_code)
        
        creator_id = None
        try:
            if principal and principal.get("auth_type") == "jwt":
                sub = principal.get("sub")
                creator_id = int(sub) if sub is not None else None
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")
        if creator_id is None and principal.get("auth_type") == "jwt":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user token")
        
        import secrets
        from datetime import datetime as dt
        ticket_number = f"TK-{dt.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
        
        metadata = {"attachments": ticket.attachments or []}
        
        ticket = Ticket(
            ticket_number=ticket_number,
            title=ticket.title,
            description=ticket.description,
            status=TicketStatus.OPEN.value,
            priority=priority_norm,
            category=category_norm,
            asset_id=ticket.asset_id,
            machine_hostname=ticket.machine_hostname,
            location_id=location_id,
            requester_name=ticket.requester_name,
            requester_email=ticket.requester_email,
            department=ticket.department,
            assigned_to=None,
            resolution=None,
            estimated_hours=None,
            actual_hours=None,
            custom_metadata=metadata,
            created_by=creator_id
        )
        db.add(ticket)
        await db.flush()
        await db.refresh(ticket)
        
        if ticket.asset_id is not None:
            from app.models.movement import AssetAudit
            from app.core.security import compute_audit_record_hash, compute_audit_signature
            
            prev_hash = None
            try:
                from sqlalchemy import select
                result = await db.execute(
                    select(AssetAudit.record_hash)
                    .where(AssetAudit.asset_id == ticket.asset_id)
                    .order_by(AssetAudit.id.desc())
                    .limit(1)
                )
                prev_hash = result.scalar_one_or_none()
            except Exception:
                prev_hash = None
            
            audit_payload = {
                "action": "CREATE",
                "table_name": "tickets",
                "record_id": ticket.id,
                "asset_id": ticket.asset_id,
                "ticket_number": ticket.ticket_number,
                "priority": ticket.priority,
                "category": ticket.category,
                "created_by": creator_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            record_hash = compute_audit_record_hash(audit_payload)
            signature = compute_audit_signature(record_hash, prev_hash)
            
            audit = AssetAudit(
                asset_id=ticket.asset_id,
                action="CREATE",
                table_name="tickets",
                record_id=ticket.id,
                field_name=None,
                old_value=None,
                new_value=None,
                reason=None,
                ip_address=None,
                user_agent=None,
                custom_metadata={"ticket_number": ticket.ticket_number, "priority": ticket.priority, "category": ticket.category},
                prev_hash=prev_hash,
                record_hash=record_hash,
                signature=signature,
                signature_algorithm="HMAC-SHA256",
                created_by=creator_id
            )
            db.add(audit)
        
        # Auto-assign placeholder logic
        assigned_to = ticket.assigned_to
        if category_norm == "network" and priority_norm in ["high", "critical"]:
            assigned_to = ticket.assigned_to
        
        # Notifications
        notifications_sent = []
        if priority_norm == "critical":
            notifications_sent.extend(["email_to_managers", "sms_to_oncall"])
        elif priority_norm == "high":
            notifications_sent.append("email_to_support")
        
        await db.commit()
        
        logger.info(
            "Ticket created successfully",
            ticket_id=ticket.id,
            ticket_number=ticket.ticket_number,
            assigned_to=assigned_to
        )
        
        # Prepare response fields according to TicketResponse
        assigned_to_name = None
        if ticket.assigned_to:
            from app.models.user import User
            user_result = await db.execute(select(User.full_name).where(User.id == ticket.assigned_to))
            assigned_to_name = user_result.scalar_one_or_none()
        
        location_code = None
        if ticket.location_id:
            from app.models.location import Location
            loc_result = await db.execute(select(Location.code).where(Location.id == ticket.location_id))
            location_code = loc_result.scalar_one_or_none()
        
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "priority": ticket.priority,
            "category": ticket.category,
            "asset_id": ticket.asset_id,
            "machine_hostname": ticket.machine_hostname,
            "location_code": location_code,
            "requester_name": ticket.requester_name,
            "requester_email": ticket.requester_email,
            "assigned_to": ticket.assigned_to,
            "assigned_to_name": assigned_to_name,
            "resolution": ticket.resolution,
            "estimated_hours": ticket.estimated_hours,
            "actual_hours": ticket.actual_hours,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None
        }
        
    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Ticket creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ticket"
        )


@router.get("/{ticket_id}", response_model=TicketResponse, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Get ticket details by ID
    """
    try:
        from app.models.ticket import Ticket
        from app.models.location import Location
        from app.models.user import User

        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} not found")

        assigned_to_name = None
        if ticket.assigned_to:
            user_result = await db.execute(select(User.full_name).where(User.id == ticket.assigned_to))
            assigned_to_name = user_result.scalar_one_or_none()

        location_code = None
        if ticket.location_id:
            loc_result = await db.execute(select(Location.code).where(Location.id == ticket.location_id))
            location_code = loc_result.scalar_one_or_none()

        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "priority": ticket.priority,
            "category": ticket.category,
            "asset_id": ticket.asset_id,
            "machine_hostname": ticket.machine_hostname,
            "location_code": location_code,
            "requester_name": ticket.requester_name,
            "requester_email": ticket.requester_email,
            "assigned_to": ticket.assigned_to,
            "assigned_to_name": assigned_to_name,
            "resolution": ticket.resolution,
            "estimated_hours": ticket.estimated_hours,
            "actual_hours": ticket.actual_hours,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to get ticket", ticket_id=ticket_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ticket"
        )


@router.put("/{ticket_id}", response_model=dict, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Update ticket status and details
    """
    try:
        logger.info(
            "Ticket update request",
            ticket_id=ticket_id,
            status=update_data.status,
            user_id=(principal.get("sub") if principal else None)
        )
        
        # TODO: Implement actual database logic
        # ticket = await get_ticket_by_id(db, ticket_id)
        # if not ticket:
        #     raise NotFoundException(f"Ticket with ID {ticket_id} not found")
        
        # Update ticket
        # updated_ticket = await update_ticket_record(db, ticket_id, update_data, current_user)
        
        # Handle status changes
        notifications_sent = []
        if update_data.status == "resolved":
            notifications_sent.append("email_to_requester")
        elif update_data.status == "closed":
            notifications_sent.append("satisfaction_survey")
        
        logger.info(
            "Ticket updated successfully",
            ticket_id=ticket_id,
            new_status=update_data.status
        )
        
        return {
            "success": True,
            "message": "Ticket updated successfully",
            "ticket_id": ticket_id,
            "status": update_data.status or "open",
            "notifications_sent": notifications_sent
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Ticket update failed", ticket_id=ticket_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ticket"
        )


@router.post("/{ticket_id}/comments", response_model=dict, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def add_ticket_comment(
    ticket_id: int,
    comment_data: TicketComment,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    Add comment to ticket
    """
    try:
        logger.info(
            "Adding ticket comment",
            ticket_id=ticket_id,
            is_internal=comment_data.is_internal,
            user_id=(principal.get("sub") if principal else None)
        )
        
        # TODO: Implement actual database logic
        # comment = await add_comment_to_ticket(db, ticket_id, comment_data, current_user)
        
        comment_id = 1  # Mock ID
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment_id": comment_id,
            "ticket_id": ticket_id
        }
        
    except Exception as e:
        logger.error("Failed to add comment", ticket_id=ticket_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )


@router.get("", response_model=List[TicketResponse], dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
@router.get("/", response_model=List[TicketResponse], dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
async def list_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(get_current_user_payload)
):
    """
    List tickets with optional filtering
    """
    try:
        from app.models.ticket import Ticket
        from sqlalchemy import and_
        from app.models.location import Location
        from app.models.user import User

        filters = []
        if status:
            filters.append(Ticket.status == status)
        if priority:
            filters.append(Ticket.priority == priority)
        if category:
            filters.append(Ticket.category == category)
        if assigned_to is not None:
            filters.append(Ticket.assigned_to == assigned_to)

        query = select(Ticket)
        if filters:
            query = query.where(and_(*filters))
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        tickets = result.scalars().all()

        responses = []
        for t in tickets:
            assigned_to_name = None
            if t.assigned_to:
                user_result = await db.execute(select(User.full_name).where(User.id == t.assigned_to))
                assigned_to_name = user_result.scalar_one_or_none()

            location_code = None
            if t.location_id:
                loc_result = await db.execute(select(Location.code).where(Location.id == t.location_id))
                location_code = loc_result.scalar_one_or_none()

            responses.append({
                "id": t.id,
                "ticket_number": t.ticket_number,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "category": t.category,
                "asset_id": t.asset_id,
                "machine_hostname": t.machine_hostname,
                "location_code": location_code,
                "requester_name": t.requester_name,
                "requester_email": t.requester_email,
                "assigned_to": t.assigned_to,
                "assigned_to_name": assigned_to_name,
                "resolution": t.resolution,
                "estimated_hours": t.estimated_hours,
                "actual_hours": t.actual_hours,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None
            })

        return responses
        
    except Exception as e:
        logger.error("Failed to list tickets", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tickets"
        )