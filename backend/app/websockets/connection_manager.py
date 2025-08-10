"""
WebSocket Connection Manager

Handles multiple WebSocket connections and provides broadcasting capabilities
for real-time updates to connected clients.
"""

from fastapi import WebSocket
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

class ConnectionManager:
    """Manages WebSocket connections for different channels"""
    
    def __init__(self):
        # Dictionary mapping channel names to sets of active connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Accept a new WebSocket connection and add to channel"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        logger.info(f"Client connected to channel '{channel}'. Active connections: {len(self.active_connections[channel])}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket connection from channel"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"Client disconnected from channel '{channel}'. Active connections: {len(self.active_connections[channel])}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_channel(self, message: str, channel: str):
        """Broadcast a message to all connections in a channel"""
        if channel not in self.active_connections:
            logger.warning(f"Attempted to broadcast to non-existent channel: {channel}")
            return
        
        disconnected_connections = set()
        
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected_connections.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.active_connections[channel].discard(connection)
    
    async def broadcast_json_to_channel(self, data: dict, channel: str):
        """Broadcast JSON data to all connections in a channel"""
        message = json.dumps(data, cls=DateTimeEncoder)
        await self.broadcast_to_channel(message, channel)
    
    def get_channel_count(self, channel: str) -> int:
        """Get the number of active connections in a channel"""
        return len(self.active_connections.get(channel, set()))
    
    def get_all_channels(self) -> List[str]:
        """Get list of all active channels"""
        return list(self.active_connections.keys()) 