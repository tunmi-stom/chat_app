from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from models.room import Room
from models.room_membership import RoomMembership
from models.user import User
from utils.helpers import hash_password, verify_password, generate_room_id
from schemas.rooms import RoomCreateData, RoomLogin, RoomResponse
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
            db.flush()

            owner_membership = RoomMembership(
                user_id=user.id,
                room_id=new_room.room_id,
                role=Roles.SUPERUSER.value
            )

            db.add(owner_membership)
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
        room = db.query(Room).filter(Room.name == data.name).with_for_update().first()
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room doesn't exists."
            )
            
        # Determine the user's role
        role = Roles.SUPERUSER.value if user.id == room.owner_id else Roles.USER.value
        
        # Check the passwords
        if not verify_password(data.key, room.hashed_pass_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid room password."
            )
        
        # Get the room
        room_data = rooms_manager.get_room(room.room_id)
        
        # Raise error of room is inactive or is `None`
        if room_data is None or not room_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Room inactive or unavailable."
            )
        
        # Check room membership. If member exists, raise an error
        member = db.query(RoomMembership).filter(
            RoomMembership.user_id == user.id,
            RoomMembership.room_id == room.room_id
        ).first()
        if member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Already a member."
            )
            
        new_member = RoomMembership(
            user_id=user.id,
            room_id=room.room_id,
            role=role
        )
        
        # Return the number of members
        membership_count = db.query(RoomMembership).filter(RoomMembership.room_id == room.room_id).count()
        
        # Raise error if number of participants exceeded the maximum.
        if membership_count >= room.max_participants:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Max Participants reached!"
            )

        try:
            db.add(new_member)
            db.flush()
            
            db.commit()
            db.refresh(new_member)
        except:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occured adding the membership"
            )
        
        # # Get the manager of the room
        # manager: ConnectionManager = room_data["manager"]
        
        db_members = db.query(RoomMembership).filter(RoomMembership.room_id == room.room_id).all()
        
        return {
            "room_id": room.room_id,
            "room_name": room.room_id,
            "role": role,
            "members": {
                "total": len(db_members),
                "data": [{
                    "user": participant.user_id,
                    "role": participant.role
                } for participant in db_members]
            }
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

        # Get the data on the room (user_id, room_id and role) if it exists.
        membership = db.query(RoomMembership).filter(
            RoomMembership.room_id == room_id,
            RoomMembership.user_id == user.id
        ).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this room."
            )
            
        # Accepting the connection
        await manager.connect(websocket, user, membership.role)
        
        # Broadcast joining the room to all participants
        await manager.broadcast_message(f"{user.username} is online", websocket)

        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast_message(data, websocket)
        except WebSocketDisconnect:
            pass
        finally:
            manager.disconnect(websocket)
            await manager.broadcast_message(f"{user.username} has gone offline", websocket)
    
    @staticmethod
    def get_room_list(db: Session, page: int, limit: int):
        offset = (page - 1) * limit
        rooms = db.query(Room).offset(offset).limit(limit).all()
        return [RoomResponse.model_validate(room) for room in rooms]
    
    @staticmethod
    def delete_room(db: Session, room_id: str, email: str):
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
            
        # Check if room exists
        room = db.query(Room).filter(Room.room_id == room_id).first()
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room doesn't exists."
            )
            
        if room.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient Permissions"
            )
        
        try:
            db.delete(room)
            db.commit()
        except:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A Database Error occured while deleting room."
            )
            
        return None