"""
Machine endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
import structlog

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security
from app.core.exceptions import NotFoundException, ValidationException

from sqlalchemy import select
from datetime import datetime, timezone
import uuid
from app.models.machine import Machine
from app.models.location import Location
from app.core.security import require_roles_or_api_key, require_roles
from app.models.asset import Asset
from app.models.movement import AssetAudit
from app.core.security import compute_audit_record_hash, compute_audit_signature

logger = structlog.get_logger()

router = APIRouter()

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from JWT token"""
    logger.info("get_current_user called", credentials_type=type(credentials).__name__)
    if credentials:
        logger.info("credentials received", token_prefix=credentials.credentials[:20] if credentials.credentials else "None")
    else:
        logger.warning("No credentials received")
    return get_current_user_id(credentials)


# Pydantic models
class MachineRegister(BaseModel):
    """Machine registration request"""
    hostname: str
    ip_address: str
    mac_address: str
    machine_type: str
    os_info: Optional[str] = None
    cpu_info: Optional[str] = None
    memory_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    location_code: Optional[str] = None
    department: Optional[str] = None
    agent_version: Optional[str] = None
    # Campos conforme schema detalhado
    machine_id: Optional[str] = None
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None
    signature: Optional[str] = None
    # Integração com ativos
    asset_tag: Optional[str] = None
    asset_id: Optional[int] = None


class MachineStatus(BaseModel):
    """Machine status update"""
    hostname: str
    status: str  # online, offline, maintenance, error
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    uptime_seconds: Optional[int] = None
    last_seen: Optional[str] = None
    agent_version: Optional[str] = None
    errors: Optional[List[str]] = None
    # Campos conforme schema detalhado
    heartbeat_ts: Optional[str] = None
    metrics: Optional[dict] = None  # { cpu: {usage_percent}, mem: {usage_percent}, disk: {usage_percent|used_percent}, net: {...} }


class MachineResponse(BaseModel):
    """Machine response model"""
    id: int
    hostname: str
    ip_address: str
    mac_address: str
    machine_type: str
    status: str
    location_code: Optional[str]
    department: Optional[str]
    last_seen: Optional[str]
    created_at: str
    updated_at: Optional[str]
    asset_tag: Optional[str]


@router.post("/register", response_model=dict, dependencies=[Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))])
async def register_machine(
    machine_data: MachineRegister,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))
):
    """
    Register a new machine in the system
    
    This endpoint allows Python agents to register themselves
    with the asset management system.
    """
    try:
        logger.info(
            "Machine registration request",
            hostname=machine_data.hostname,
            ip=machine_data.ip_address,
            auth_type=principal.get("auth_type"),
            user_id=principal.get("sub") if principal.get("auth_type") == "jwt" else None
        )
        
        # Validate required fields
        if not machine_data.hostname or not machine_data.ip_address:
            raise ValidationException("Hostname and IP address are required")
        
        # Check if machine already exists by hostname
        existing = await db.execute(
            select(Machine).where(Machine.hostname == machine_data.hostname)
        )
        existing_machine = existing.scalar_one_or_none()
        if existing_machine:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Machine with hostname {machine_data.hostname} already exists")
        
        # Resolve location_id from location_code if provided
        location_id = None
        if machine_data.location_code:
            loc_res = await db.execute(
                select(Location).where(Location.code == machine_data.location_code)
            )
            location = loc_res.scalar_one_or_none()
            location_id = location.id if location else None        # Resolver ativo por asset_tag ou asset_id (opcional)
        linked_asset = None
        if machine_data.asset_tag or machine_data.asset_id:
            asset_query = None
            if machine_data.asset_tag:
                asset_query = select(Asset).where(Asset.asset_tag == machine_data.asset_tag)
            elif machine_data.asset_id:
                asset_query = select(Asset).where(Asset.id == machine_data.asset_id)
            if asset_query is not None:
                ares = await db.execute(asset_query)
                linked_asset = ares.scalar_one_or_none()
        
        # Create new machine record
        machine = Machine(
            hostname=machine_data.hostname,
            machine_id=machine_data.machine_id or str(uuid.uuid4()),
            ip_address=machine_data.ip_address,
            mac_address=machine_data.mac_address,
            machine_type=machine_data.machine_type,
            status="unknown",
            operating_system=machine_data.os_info,
            cpu_model=machine_data.cpu_info,
            ram_total_gb=machine_data.memory_gb,
            disk_total_gb=machine_data.disk_gb,
            location_id=location_id,
            agent_version=machine_data.agent_version,
            agent_last_seen=datetime.now(timezone.utc),
            custom_metadata={
                **(machine_data.metadata or {}),
                **({"asset_id": linked_asset.id, "asset_tag": linked_asset.asset_tag} if linked_asset else {})
            } if (machine_data.metadata or linked_asset) else None,
        )
        
        db.add(machine)
        await db.commit()
        await db.refresh(machine)

        # Registrar trilha de auditoria ao vincular ativo
        if linked_asset:
            audit_payload = {
                "action": "link_machine_asset",
                "table_name": "machines",
                "record_id": machine.id,
                "asset_id": linked_asset.id,
                "asset_tag": linked_asset.asset_tag,
                "machine_hostname": machine.hostname,
                "machine_uuid": machine.machine_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            record_hash = compute_audit_record_hash(audit_payload)
            signature = compute_audit_signature(record_hash)
            audit = AssetAudit(
                asset_id=linked_asset.id,
                action="link_machine_asset",
                table_name="machines",
                record_id=str(machine.id),
                prev_hash=None,
                record_hash=record_hash,
                signature=signature,
            )
            db.add(audit)
            await db.commit()
        
        logger.info(
            "Machine registered successfully",
            machine_id=machine.id,
            hostname=machine.hostname
        )
        
        return {
            "success": True,
            "message": "Machine registered successfully",
            "machine_id": machine.id,
            "hostname": machine.hostname,
            "asset_tag": linked_asset.asset_tag if linked_asset else None,
            "registration_token": "mock-token-123"
        }
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error("Machine registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register machine"
        )


@router.post("/status", response_model=dict, dependencies=[Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))])
async def update_machine_status(
    status_data: MachineStatus,
    db: AsyncSession = Depends(get_async_session),
    principal: dict = Depends(require_roles_or_api_key(["admin", "gestor", "agent", "system"]))
):
    """
    Update machine status and metrics
    
    This endpoint receives status updates from Python agents
    running on monitored machines.
    """
    try:
        logger.info(
            "Machine status update",
            hostname=status_data.hostname,
            status=status_data.status,
            auth_type=principal.get("auth_type"),
            user_id=principal.get("sub") if principal.get("auth_type") == "jwt" else None
        )
        
        # Validate machine exists
        res = await db.execute(select(Machine).where(Machine.hostname == status_data.hostname))
        machine = res.scalar_one_or_none()
        if not machine:
            raise NotFoundException(f"Machine with hostname {status_data.hostname} not found")
        
        # Update machine status and metrics
        machine.status = status_data.status
        # Métricas aninhadas têm precedência, se fornecidas
        cpu_nested = None
        mem_nested = None
        disk_nested = None
        if status_data.metrics:
            cpu_nested = (status_data.metrics.get("cpu") or {}).get("usage_percent")
            mem_nested = (status_data.metrics.get("mem") or {}).get("usage_percent")
            disk_nested = (status_data.metrics.get("disk") or {}).get("usage_percent")
            if disk_nested is None:
                disk_nested = (status_data.metrics.get("disk") or {}).get("used_percent")
        machine.cpu_usage_percent = cpu_nested if cpu_nested is not None else status_data.cpu_usage
        machine.ram_usage_percent = mem_nested if mem_nested is not None else status_data.memory_usage
        machine.disk_usage_percent = disk_nested if disk_nested is not None else status_data.disk_usage
        machine.uptime_seconds = status_data.uptime_seconds
        machine.agent_version = status_data.agent_version or machine.agent_version
        machine.agent_last_seen = datetime.now(timezone.utc)
        
        await db.commit()
        
        # Check for alerts based on metrics
        alerts_triggered = []
        if status_data.cpu_usage and status_data.cpu_usage > 90:
            alerts_triggered.append("High CPU usage detected")
        if status_data.memory_usage and status_data.memory_usage > 85:
            alerts_triggered.append("High memory usage detected")
        if status_data.disk_usage and status_data.disk_usage > 90:
            alerts_triggered.append("Low disk space detected")
        
        logger.info(
            "Machine status updated",
            hostname=status_data.hostname,
            alerts_count=len(alerts_triggered)
        )
        
        return {
            "success": True,
            "message": "Status updated successfully",
            "hostname": status_data.hostname,
            "alerts_triggered": alerts_triggered,
            "next_update_interval": 300
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Machine status update failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update machine status"
        )


@router.get("/{machine_id}/status", response_model=dict, dependencies=[Depends(require_roles(["admin", "gestor", "auditor", "agent", "system"]))])
async def get_machine_status(
    machine_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user)
):
    """
    Get current status of a specific machine
    """
    try:
        # Buscar máquina por id numérico ou por UUID (machine_id)
        if machine_id.isdigit():
            result = await db.execute(select(Machine).where(Machine.id == int(machine_id)))
        else:
            result = await db.execute(select(Machine).where(Machine.machine_id == machine_id))
        machine = result.scalar_one_or_none()
        if not machine:
            raise NotFoundException(f"Machine with ID {machine_id} not found")

        # Construir resposta com dados reais
        return {
            "machine_id": machine.machine_id,
            "hostname": machine.hostname,
            "status": machine.status,
            "cpu_usage": machine.cpu_usage_percent,
            "memory_usage": machine.ram_usage_percent,
            "disk_usage": machine.disk_usage_percent,
            "uptime_seconds": machine.uptime_seconds,
            "last_seen": machine.agent_last_seen.isoformat() if machine.agent_last_seen else None,
            "agent_version": machine.agent_version,
            "asset_tag": (machine.custom_metadata or {}).get("asset_tag") if isinstance(machine.custom_metadata, dict) else None,
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to get machine status", machine_id=machine_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve machine status"
        )


@router.get("/", response_model=List[MachineResponse], dependencies=[Depends(require_roles(["admin", "gestor", "auditor", "agent", "system"]))])
async def list_machines(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    hostname: Optional[str] = None,
    machine_type: Optional[str] = None,
    location_code: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(get_current_user)
):
    """
    List all registered machines with optional filtering
    """
    try:
        query = select(Machine)
        if status_filter:
            query = query.where(Machine.status == status_filter)
        if hostname:
            query = query.where(Machine.hostname.ilike(f"%{hostname}%"))
        if machine_type:
            query = query.where(Machine.machine_type == machine_type)
        if location_code:
            loc_res = await db.execute(select(Location.id).where(Location.code == location_code))
            location_id = loc_res.scalar_one_or_none()
            if location_id is None:
                return []
            query = query.where(Machine.location_id == location_id)
        query = query.order_by(Machine.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        machines = result.scalars().all()

        responses: List[MachineResponse] = []
        for m in machines:
            # Resolver location_code
            location_code = None
            if m.location_id:
                loc_res = await db.execute(select(Location.code).where(Location.id == m.location_id))
                location_code = loc_res.scalar_one_or_none()
            # Resolver asset_tag de custom_metadata
            asset_tag = None
            try:
                if m.custom_metadata and isinstance(m.custom_metadata, dict):
                    asset_tag = m.custom_metadata.get("asset_tag")
            except Exception:
                asset_tag = None

            responses.append(MachineResponse(
                id=m.id,
                hostname=m.hostname,
                ip_address=m.ip_address,
                mac_address=m.mac_address,
                machine_type=m.machine_type,
                status=m.status,
                location_code=location_code,
                department=None,  # Campo não presente no modelo atual
                last_seen=m.agent_last_seen.isoformat() if m.agent_last_seen else None,
                created_at=m.created_at.isoformat() if m.created_at else datetime.now(timezone.utc).isoformat(),
                updated_at=m.updated_at.isoformat() if m.updated_at else None,
                asset_tag=asset_tag,
            ))

        return responses
        
    except Exception as e:
        logger.error("Failed to list machines", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve machines"
        )