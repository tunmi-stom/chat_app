from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from core.dependency import get_current_user
from core.db_config import db_dependency
from services.room_services import RoomService
from schemas.rooms import RoomCreateData, RoomLogin

router = APIRouter(
    prefix="/room",
    tags=["room"]
)

@router.post("/create")
def create_room(
    db: db_dependency, 
    data: RoomCreateData, 
    email: str = Depends(get_current_user)
):
    room = RoomService.create_room(db, email, data)
    return {"detail": "Room Created", "data": room}

@router.post("/enter-room/{room_id}")
def register_for_room(
    db: db_dependency, 
    roomlogin: RoomLogin, 
    email: str = Depends(get_current_user)
):
    data = RoomService.enter_room(db, email, roomlogin)
    return {"detail": "Room Entered.", "data": data}

@router.websocket("/{room_id}")
async def chat_room(
    db: db_dependency, 
    websocket: WebSocket, 
    login_data: RoomLogin,
    email: str = Depends(get_current_user)
):
    RoomService.chat_room(db, email, websocket, login_data)