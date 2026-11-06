from fastapi import APIRouter, Depends, WebSocket, Query
from core.dependency import get_current_user, get_websocket_user
from core.db_config import db_dependency
from services.room_services import RoomService
from schemas.rooms import RoomCreateData, RoomLogin

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)

@router.post("/create")
def create_room(
    db: db_dependency, 
    data: RoomCreateData, 
    email: str = Depends(get_current_user)
):
    room = RoomService.create_room(db, email, data)
    return {"detail": "Room Created", "data": room}

@router.post("/enter-room")
def register_for_room(
    db: db_dependency, 
    roomlogin: RoomLogin, 
    email: str = Depends(get_current_user)
):
    data = RoomService.enter_room(db, email, roomlogin)
    return {"detail": "Room Entered.", "data": data}

@router.get("/")
def get_rooms(db: db_dependency, page: int = Query(1, ge=1), limit: int = Query(20)):
    data = RoomService.get_room_list(db, page, limit)
    return {"detail": data}

@router.websocket("/{room_id}")
async def chat_room(
    db: db_dependency, 
    websocket: WebSocket, 
    room_id: str, 
    key: str,
    email: str = Depends(get_websocket_user)
):
    email: str = get_websocket_user(websocket, db)
    await RoomService.chat_room(db, email, websocket, room_id, key)
