"""
Asset management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security
from app.core.exceptions import NotFoundException, ValidationException

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class AssetCreate(BaseModel):
    """Asset creation request"""
    name: str
    asset_tag: str
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    asset_type: str  # desktop, laptop, server, printer, network, mobile, other
    category: Optional[str] = None
    location_id: Optional[int] = None
    assigned_to: Optional[int] = None
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = None
    warranty_expiry: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    network_info: Optional[Dict[str, Any]] = None


class AssetUpdate(BaseModel):
    """Asset update request"""
    name: Optional[str] = None
    status: Optional[str] = None  # active, inactive, maintenance, disposed, lost, stolen
    location_id: Optional[int] = None
    assigned_to: Optional[int] = None
    specifications: Optional[Dict[str, Any]] = None
    network_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class AssetResponse(BaseModel):
    """Asset response model"""
    id: int
    name: str
    asset_tag: str
    serial_number: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]
    asset_type: str
    category: Optional[str]
    status: str
    location_id: Optional[int]
    location_name: Optional[str]
    assigned_to: Optional[int]
    assigned_to_name: Optional[str]
    purchase_date: Optional[str]
    purchase_cost: Optional[float]
    warranty_expiry: Optional[str]
    specifications: Optional[Dict[str, Any]]
    network_info: Optional[Dict[str, Any]]
    created_at: str
    updated_at: Optional[str]


class AssetMovement(BaseModel):
    """Asset movement request"""
    from_location_id: Optional[int] = None
    to_location_id: int
    assigned_to: Optional[int] = None
    movement_type: str  # transfer, assignment, return, maintenance
    notes: Optional[str] = None


@router.post("/", response_model=dict)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Create a new asset
    """
    try:
        logger.info(
            "Asset creation request",
            name=asset_data.name,
            asset_tag=asset_data.asset_tag,
            asset_type=asset_data.asset_type,
            user_id=current_user
        )
        
        # Validate required fields
        if not asset_data.name or not asset_data.asset_tag:
            raise ValidationException("Name and asset tag are required")
        
        if asset_data.asset_type not in ["desktop", "laptop", "server", "printer", "network", "mobile", "other"]:
            raise ValidationException("Invalid asset type")
        
        # TODO: Check if asset tag already exists
        # existing_asset = await get_asset_by_tag(db, asset_data.asset_tag)
        # if existing_asset:
        #     raise ValidationException("Asset tag already exists")
        
        # TODO: Implement actual database logic
        # asset = await create_asset_record(db, asset_data, current_user)
        
        asset_id = 1  # Mock ID
        
        logger.info(
            "Asset created successfully",
            asset_id=asset_id,
            asset_tag=asset_data.asset_tag
        )
        
        return {
            "success": True,
            "message": "Asset created successfully",
            "asset_id": asset_id,
            "asset_tag": asset_data.asset_tag
        }
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error("Asset creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create asset"
        )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Get asset details by ID
    """
    try:
        # TODO: Implement actual database logic
        # asset = await get_asset_by_id(db, asset_id)
        # if not asset:
        #     raise NotFoundException(f"Asset with ID {asset_id} not found")
        
        # Mock response
        return {
            "id": asset_id,
            "name": "Dell OptiPlex 7090",
            "asset_tag": "DT-001",
            "serial_number": "ABC123456",
            "model": "OptiPlex 7090",
            "manufacturer": "Dell",
            "asset_type": "desktop",
            "category": "Workstation",
            "status": "active",
            "location_id": 1,
            "location_name": "Floor 1 - Room 101",
            "assigned_to": 1,
            "assigned_to_name": "John Doe",
            "purchase_date": "2023-01-15",
            "purchase_cost": 1200.00,
            "warranty_expiry": "2026-01-15",
            "specifications": {
                "cpu": "Intel i7-11700",
                "ram": "16GB DDR4",
                "storage": "512GB SSD",
                "os": "Windows 11 Pro"
            },
            "network_info": {
                "hostname": "workstation-001",
                "ip_address": "192.168.1.100",
                "mac_address": "00:11:22:33:44:55"
            },
            "created_at": "2023-01-15T10:00:00Z",
            "updated_at": "2024-01-15T09:00:00Z"
        }
        
    except Exception as e:
        logger.error("Failed to get asset", asset_id=asset_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset"
        )


@router.put("/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: int,
    update_data: AssetUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Update asset information
    """
    try:
        logger.info(
            "Asset update request",
            asset_id=asset_id,
            status=update_data.status,
            user_id=current_user
        )
        
        # TODO: Implement actual database logic
        # asset = await get_asset_by_id(db, asset_id)
        # if not asset:
        #     raise NotFoundException(f"Asset with ID {asset_id} not found")
        
        # Update asset
        # updated_asset = await update_asset_record(db, asset_id, update_data, current_user)
        
        logger.info(
            "Asset updated successfully",
            asset_id=asset_id
        )
        
        return {
            "success": True,
            "message": "Asset updated successfully",
            "asset_id": asset_id
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Asset update failed", asset_id=asset_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update asset"
        )


@router.get("/", response_model=List[AssetResponse])
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    location_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    List assets with optional filtering and search
    """
    try:
        # TODO: Implement actual database logic
        # assets = await get_assets(db, skip=skip, limit=limit, filters={...})
        
        # Mock response
        assets = [
            {
                "id": 1,
                "name": "Dell OptiPlex 7090",
                "asset_tag": "DT-001",
                "serial_number": "ABC123456",
                "model": "OptiPlex 7090",
                "manufacturer": "Dell",
                "asset_type": "desktop",
                "category": "Workstation",
                "status": "active",
                "location_id": 1,
                "location_name": "Floor 1 - Room 101",
                "assigned_to": 1,
                "assigned_to_name": "John Doe",
                "purchase_date": "2023-01-15",
                "purchase_cost": 1200.00,
                "warranty_expiry": "2026-01-15",
                "specifications": {
                    "cpu": "Intel i7-11700",
                    "ram": "16GB DDR4",
                    "storage": "512GB SSD",
                    "os": "Windows 11 Pro"
                },
                "network_info": {
                    "hostname": "workstation-001",
                    "ip_address": "192.168.1.100",
                    "mac_address": "00:11:22:33:44:55"
                },
                "created_at": "2023-01-15T10:00:00Z",
                "updated_at": "2024-01-15T09:00:00Z"
            }
        ]
        
        return assets
        
    except Exception as e:
        logger.error("Failed to list assets", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assets"
        )


@router.post("/{asset_id}/move", response_model=dict)
async def move_asset(
    asset_id: int,
    movement_data: AssetMovement,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Move asset to different location or assign to user
    """
    try:
        logger.info(
            "Asset movement request",
            asset_id=asset_id,
            to_location_id=movement_data.to_location_id,
            movement_type=movement_data.movement_type,
            user_id=current_user
        )
        
        # TODO: Implement actual database logic
        # asset = await get_asset_by_id(db, asset_id)
        # if not asset:
        #     raise NotFoundException(f"Asset with ID {asset_id} not found")
        
        # Create movement record
        # movement = await create_asset_movement(db, asset_id, movement_data, current_user)
        
        movement_id = 1  # Mock ID
        
        logger.info(
            "Asset moved successfully",
            asset_id=asset_id,
            movement_id=movement_id
        )
        
        return {
            "success": True,
            "message": "Asset moved successfully",
            "movement_id": movement_id,
            "asset_id": asset_id
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Asset movement failed", asset_id=asset_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to move asset"
        )


@router.get("/{asset_id}/history", response_model=List[dict])
async def get_asset_history(
    asset_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Get asset movement and audit history
    """
    try:
        # TODO: Implement actual database logic
        # history = await get_asset_history(db, asset_id)
        
        # Mock response
        history = [
            {
                "id": 1,
                "action": "created",
                "description": "Asset created",
                "user_name": "Admin User",
                "timestamp": "2023-01-15T10:00:00Z",
                "details": {
                    "location": "Warehouse",
                    "status": "inactive"
                }
            },
            {
                "id": 2,
                "action": "moved",
                "description": "Moved to Floor 1 - Room 101",
                "user_name": "IT Manager",
                "timestamp": "2023-01-16T09:00:00Z",
                "details": {
                    "from_location": "Warehouse",
                    "to_location": "Floor 1 - Room 101"
                }
            },
            {
                "id": 3,
                "action": "assigned",
                "description": "Assigned to John Doe",
                "user_name": "IT Manager",
                "timestamp": "2023-01-16T09:30:00Z",
                "details": {
                    "assigned_to": "John Doe",
                    "status": "active"
                }
            }
        ]
        
        return history
        
    except Exception as e:
        logger.error("Failed to get asset history", asset_id=asset_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset history"
        )


@router.get("/dashboard/summary", response_model=dict)
async def get_asset_dashboard_summary(
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Get asset summary for dashboard
    """
    try:
        # TODO: Implement actual database logic
        # summary = await get_asset_summary(db)
        
        # Mock response
        summary = {
            "total_assets": 1250,
            "active": 1100,
            "inactive": 80,
            "maintenance": 45,
            "disposed": 25,
            "by_type": {
                "desktop": 450,
                "laptop": 380,
                "server": 120,
                "printer": 85,
                "network": 95,
                "mobile": 120
            },
            "by_location": {
                "Floor 1": 320,
                "Floor 2": 280,
                "Floor 3": 250,
                "Data Center": 120,
                "Warehouse": 180,
                "Remote": 100
            },
            "warranty_expiring": {
                "next_30_days": 15,
                "next_90_days": 45,
                "expired": 23
            },
            "value": {
                "total_value": 2500000.00,
                "avg_age_months": 18,
                "depreciation_rate": 0.15
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error("Failed to get asset summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset summary"
        )