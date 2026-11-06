from pydantic import BaseModel, ConfigDict

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

class RoomResponse(BaseModel):
    name: str | None = None
    desc: str | None = None
    max_participants: int | None = None
    room_id: str | None = None
    
    model_config = ConfigDict(from_attributes=True)