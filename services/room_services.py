from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from models.room import Room
from models.user import User
from utils.helpers import hash_password, verify_password, generate_room_id
from schemas.rooms import RoomCreateData, RoomLogin, RoomResponse
from schemas.users import UserResponse
from .ws_manager import rooms_manager, ConnectionManager
from utils.enums import Roles

class RoomService:
    @staticmethod
    def create_room(db: Session, email: str, data: RoomCreateData):
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
            
        # Check if room exists
        room = db.query(Room).filter(Room.name == data.name).first()
        if room is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Room already exists."
            )
            
        new_room = Room(
            name=data.name,
            desc=data.desc,
            room_id=generate_room_id(len(data.name)),
            max_participants=data.max_participants,
            hashed_pass_key=hash_password(data.key),
            owner_id=user.id
        )
            
        try:
            db.add(new_room)
            db.commit()
            db.refresh(new_room)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating room."
            )
            
        return new_room.room_id
    
    @staticmethod
    def enter_room(
        db: Session, 
        email: str, 
        data: RoomLogin
    ):
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
            
        # Check if room exists
        room = db.query(Room).filter(Room.name == data.name).first()
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room doesn't exists."
            )
            
        # Determine the user's role
        if user.id == room.owner_id:
            role = Roles.SUPERUSER.value
        else:
            role = Roles.USER.value
        
        # Check the passwords
        if not verify_password(data.key, room.hashed_pass_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid room password."
            )

        # Get the room
        room_data = rooms_manager.get_room(room.room_id)
        
        # Raise error of room is inactive
        if not room_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Room inactive."
            )
        
        # Get the manager of the room
        manager: ConnectionManager = room_data["manager"]
        
        already_connected = any(
            participant["user_email"] == user.email
            for participant in manager.active_participants
        )
        
        # Raise error if number of participants exceeded the maximum.
        if (not already_connected and len(manager.active_participants) >= room.max_participants):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Max Participants reached!"
            )

        return {
            "room_id": room.room_id,
            "room_name": room.name,
            "role": role
        }
    
    @staticmethod
    async def chat_room(
        db: Session, 
        email: str, 
        websocket: WebSocket, 
        room_id: str,
        pass_key: str
    ):
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        # Check if the room exists
        room = db.query(Room).filter(Room.room_id == room_id).first()
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room doesn't exists."
            )
            
        # Get room data.
        room_data = rooms_manager.get_room(room.room_id)
        if room_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room data not found."
            )
            
        # Get the room manager
        manager: ConnectionManager = room_data.get("manager")
        
        # Get the data on the room (room_name, room_id and role). Also 
        # some necessary validations
        room_access_data = RoomService.enter_room(db, email, RoomLogin(name=room.name, key=pass_key))
        
        # Accepting the connection
        await manager.connect(websocket, user, room_access_data["role"])
        
        # Broadcast joining the room to all participants
        await manager.broadcast_message(f"User {user.email} has joined the chat", websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast_message(data, websocket)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast_message(f"User {user.email} has left the chat", websocket)
    
    @staticmethod
    def get_room_list(db: Session, page: int, limit: int):
        # Calculate the offset
        offset = (limit - 1) * page
        
        rooms = db.query(Room).offset(offset).limit(limit).all()
        return [RoomResponse.model_validate(room) for room in rooms]