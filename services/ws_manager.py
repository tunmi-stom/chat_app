from fastapi import WebSocket
from typing import List, Dict, Any
from models.user import User

class ConnectionManager:
    def __init__(self):
        self.active_participants: List[Dict[str, Any]] = []
        
    async def connect(self, websocket: WebSocket, user: User, role: str):
        await websocket.accept()
        self.active_participants.append(
            {
                "user_email": user.email,
                "websocket": websocket,
                "role": role
            }
        )
        
    def disconnect(self, websocket: WebSocket):
        self.active_participants = [
            participant
            for participant in self.active_participants 
            if participant["websocket"] != websocket
        ]
    
    # async def send_message(
    #     self,
    #     websocket: WebSocket,
    #     message: str
    # ): 
    #     await websocket.send_text(message)
        
    async def broadcast_message(
        self, 
        message: str, 
        user: User
    ):
        for participant in self.active_participants:
            if participant["user_email"] == user.email:
                continue
            await participant["websocket"].send_text(message)
                
                
class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, Any]] = {}
        
    def get_room(self, room_id: str, is_active: bool = True) -> Dict[str, Any]:
        if room_id not in self.rooms:
            self.rooms[room_id] = {"manager": ConnectionManager(), "is_active": is_active}
        
        return self.rooms[room_id]

    def remove_room(self, room_id: str):
        room = self.rooms.get(room_id)
        if room is None:
            return
        
        manager: ConnectionManager = room.get("manager")
        if not manager.active_participants:
            self.rooms.pop(room_id)
            
rooms_manager = RoomManager()