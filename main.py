from fastapi import WebSocket, FastAPI
from core.config import settings
from routers import auth_routes, room_routes, user_routes
from core.db_config import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(room_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def ping():
    return {"message": "pong!"}

@app.websocket("/ws")
async def websockets_tut(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("This is your Echo server!")
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"You said: {data}")