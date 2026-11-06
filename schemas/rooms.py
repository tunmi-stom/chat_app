from pydantic import BaseModel

class RoomSchema(BaseModel):
    id: int
    name: str
    desc: str
    is_active: bool
    room_id: str
    key: str
    max_participants: int
    
class RoomCreateData(BaseModel):
    name: str
    desc: str | None = None
    key: str
    max_participants: int
    
class RoomLogin(BaseModel):
    name: str
    key: str