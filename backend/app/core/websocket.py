"""
WebSocket Manager for real-time communication
"""

import json
import asyncio
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import structlog
from datetime import datetime

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connections by user ID for targeted messaging
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Heartbeat tracking
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("WebSocket ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Store connection
            self.active_connections[connection_id] = websocket
            
            # Store connection metadata
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "last_heartbeat": datetime.utcnow().isoformat()
            }
            
            # Map user to connection if user_id provided
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
            
            # Start heartbeat for this connection
            self.heartbeat_tasks[connection_id] = asyncio.create_task(
                self._heartbeat_loop(connection_id)
            )
            
            logger.info(
                "WebSocket connection established",
                connection_id=connection_id,
                user_id=user_id,
                total_connections=len(self.active_connections)
            )
            
            # Send welcome message
            await self.send_personal_message(connection_id, {
                "type": "connected",
                "data": {
                    "connection_id": connection_id,
                    "message": "Connected to Levitiis monitoring system",
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
        except Exception as e:
            logger.error("Failed to establish WebSocket connection", error=str(e))
            raise

    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        try:
            # Cancel heartbeat task
            if connection_id in self.heartbeat_tasks:
                self.heartbeat_tasks[connection_id].cancel()
                del self.heartbeat_tasks[connection_id]
            
            # Get user_id before removing metadata
            user_id = None
            if connection_id in self.connection_metadata:
                user_id = self.connection_metadata[connection_id].get("user_id")
                del self.connection_metadata[connection_id]
            
            # Remove from user connections mapping
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove connection
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            
            logger.info(
                "WebSocket connection closed",
                connection_id=connection_id,
                user_id=user_id,
                total_connections=len(self.active_connections)
            )
            
        except Exception as e:
            logger.error("Error during WebSocket disconnect", error=str(e))

    async def send_personal_message(self, connection_id: str, message: dict):
        """Send a message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
                
                logger.debug(
                    "Message sent to connection",
                    connection_id=connection_id,
                    message_type=message.get("type")
                )
                
            except WebSocketDisconnect:
                logger.warning("Connection disconnected during message send", connection_id=connection_id)
                await self.disconnect(connection_id)
            except Exception as e:
                logger.error("Failed to send message to connection", connection_id=connection_id, error=str(e))

    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all connections of a specific user"""
        if user_id in self.user_connections:
            connection_ids = list(self.user_connections[user_id])
            for connection_id in connection_ids:
                await self.send_personal_message(connection_id, message)

    async def broadcast(self, message: dict, exclude_connections: Set[str] = None):
        """Broadcast a message to all active connections"""
        exclude_connections = exclude_connections or set()
        
        connection_ids = [
            conn_id for conn_id in self.active_connections.keys()
            if conn_id not in exclude_connections
        ]
        
        logger.debug(
            "Broadcasting message",
            message_type=message.get("type"),
            recipient_count=len(connection_ids)
        )
        
        # Send to all connections concurrently
        tasks = [
            self.send_personal_message(connection_id, message)
            for connection_id in connection_ids
        ]
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_machine_update(self, machine_data: dict):
        """Broadcast machine status update to all connections"""
        message = {
            "type": "machine_update",
            "data": machine_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_machine_metrics(self, metrics_data: dict):
        """Broadcast machine metrics to all connections"""
        message = {
            "type": "machine_metrics",
            "data": metrics_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_machine_alert(self, alert_data: dict):
        """Broadcast machine alert to all connections"""
        message = {
            "type": "machine_alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def send_machines_list(self, connection_id: str, machines_data: List[dict]):
        """Send complete machines list to a specific connection"""
        message = {
            "type": "machines_list",
            "data": machines_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(connection_id, message)

    async def handle_heartbeat(self, connection_id: str):
        """Handle heartbeat from client"""
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["last_heartbeat"] = datetime.utcnow().isoformat()
            
            # Send pong response
            await self.send_personal_message(connection_id, {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })

    async def _heartbeat_loop(self, connection_id: str):
        """Internal heartbeat loop for connection monitoring"""
        try:
            while connection_id in self.active_connections:
                await asyncio.sleep(30)  # Send ping every 30 seconds
                
                if connection_id in self.active_connections:
                    await self.send_personal_message(connection_id, {
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
        except asyncio.CancelledError:
            logger.debug("Heartbeat loop cancelled", connection_id=connection_id)
        except Exception as e:
            logger.error("Error in heartbeat loop", connection_id=connection_id, error=str(e))

    def get_connection_stats(self) -> dict:
        """Get current connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "connections_by_user": {
                user_id: len(connections) 
                for user_id, connections in self.user_connections.items()
            }
        }


# Global connection manager instance
connection_manager = ConnectionManager()