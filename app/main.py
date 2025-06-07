from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import users, campaigns
from .config import settings
from .database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.APP_NAME,
    description="Service for sending email and Telegram notifications",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])

@app.get("/")
async def root():
    return {"message": "Notification Service API"}