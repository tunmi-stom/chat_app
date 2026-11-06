from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Include Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def ping():
    return {"message": "pong!"}