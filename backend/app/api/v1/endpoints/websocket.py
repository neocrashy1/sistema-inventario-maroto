"""
WebSocket endpoints for real-time communication
"""

import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security
from app.core.websocket import connection_manager
from app.core.exceptions import ValidationException

logger = structlog.get_logger()

router = APIRouter()


async def get_current_user_websocket(token: str = Query(None)) -> str:
    """Get current user ID from WebSocket token parameter"""
    if not token:
        raise ValidationException("Authentication token required")
    
    try:
        # Create a mock credentials object for the security function
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        credentials = MockCredentials(token)
        return get_current_user_id(credentials)
    except Exception as e:
        logger.error("WebSocket authentication failed", error=str(e))
        raise ValidationException("Invalid authentication token")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Main WebSocket endpoint for real-time communication
    
    Query Parameters:
    - token: JWT authentication token
    """
    connection_id = str(uuid.uuid4())
    user_id = None
    
    try:
        # Authenticate user if token provided
        if token:
            try:
                user_id = await get_current_user_websocket(token)
                logger.info("WebSocket user authenticated", user_id=user_id, connection_id=connection_id)
            except Exception as e:
                logger.warning("WebSocket authentication failed", error=str(e))
                await websocket.close(code=4001, reason="Authentication failed")
                return
        
        # Accept connection
        await connection_manager.connect(websocket, connection_id, user_id)
        
        # Send initial machines list if authenticated
        if user_id:
            # TODO: Get actual machines from database
            machines_data = [
                {
                    "id": 1,
                    "hostname": "workstation-001",
                    "ip_address": "192.168.1.100",
                    "status": "online",
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.1,
                    "last_seen": "2024-01-15T10:30:00Z"
                },
                {
                    "id": 2,
                    "hostname": "server-001",
                    "ip_address": "192.168.1.200",
                    "status": "online",
                    "cpu_usage": 78.5,
                    "memory_usage": 82.1,
                    "disk_usage": 45.7,
                    "last_seen": "2024-01-15T10:29:45Z"
                }
            ]
            await connection_manager.send_machines_list(connection_id, machines_data)
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                logger.debug(
                    "WebSocket message received",
                    connection_id=connection_id,
                    message_type=message.get("type")
                )
                
                # Handle different message types
                await handle_websocket_message(connection_id, message, user_id, db)
                
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected", connection_id=connection_id)
                break
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received", connection_id=connection_id)
                await connection_manager.send_personal_message(connection_id, {
                    "type": "error",
                    "data": {"message": "Invalid JSON format"},
                    "timestamp": "2024-01-15T10:30:00Z"
                })
            except Exception as e:
                logger.error("Error processing WebSocket message", connection_id=connection_id, error=str(e))
                await connection_manager.send_personal_message(connection_id, {
                    "type": "error",
                    "data": {"message": "Internal server error"},
                    "timestamp": "2024-01-15T10:30:00Z"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed", connection_id=connection_id)
    except Exception as e:
        logger.error("WebSocket connection error", connection_id=connection_id, error=str(e))
    finally:
        await connection_manager.disconnect(connection_id)


async def handle_websocket_message(
    connection_id: str, 
    message: dict, 
    user_id: str, 
    db: AsyncSession
):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    data = message.get("data", {})
    
    try:
        if message_type == "ping":
            # Handle heartbeat
            await connection_manager.handle_heartbeat(connection_id)
            
        elif message_type == "subscribe_machines":
            # Subscribe to machine updates
            logger.info("Client subscribed to machine updates", connection_id=connection_id)
            await connection_manager.send_personal_message(connection_id, {
                "type": "subscribed",
                "data": {"subscription": "machines"},
                "timestamp": "2024-01-15T10:30:00Z"
            })
            
        elif message_type == "get_machine_status":
            # Get specific machine status
            machine_id = data.get("machine_id")
            if machine_id:
                # TODO: Get actual machine status from database
                machine_status = {
                    "machine_id": machine_id,
                    "hostname": f"machine-{machine_id}",
                    "status": "online",
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.1,
                    "uptime_seconds": 86400,
                    "last_seen": "2024-01-15T10:30:00Z"
                }
                
                await connection_manager.send_personal_message(connection_id, {
                    "type": "machine_status",
                    "data": machine_status,
                    "timestamp": "2024-01-15T10:30:00Z"
                })
            
        elif message_type == "refresh_machines":
            # Refresh machines list
            # TODO: Get updated machines from database
            machines_data = [
                {
                    "id": 1,
                    "hostname": "workstation-001",
                    "ip_address": "192.168.1.100",
                    "status": "online",
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.1,
                    "last_seen": "2024-01-15T10:30:00Z"
                }
            ]
            await connection_manager.send_machines_list(connection_id, machines_data)
            
        else:
            logger.warning("Unknown message type", message_type=message_type, connection_id=connection_id)
            await connection_manager.send_personal_message(connection_id, {
                "type": "error",
                "data": {"message": f"Unknown message type: {message_type}"},
                "timestamp": "2024-01-15T10:30:00Z"
            })
            
    except Exception as e:
        logger.error("Error handling WebSocket message", message_type=message_type, error=str(e))
        await connection_manager.send_personal_message(connection_id, {
            "type": "error",
            "data": {"message": "Failed to process message"},
            "timestamp": "2024-01-15T10:30:00Z"
        })


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return connection_manager.get_connection_stats()


# Function to broadcast machine updates (to be called from other parts of the application)
async def broadcast_machine_update(machine_data: dict):
    """Broadcast machine update to all connected clients"""
    await connection_manager.broadcast_machine_update(machine_data)


async def broadcast_machine_metrics(metrics_data: dict):
    """Broadcast machine metrics to all connected clients"""
    await connection_manager.broadcast_machine_metrics(metrics_data)


async def broadcast_machine_alert(alert_data: dict):
    """Broadcast machine alert to all connected clients"""
    await connection_manager.broadcast_machine_alert(alert_data)