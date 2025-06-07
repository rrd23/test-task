from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_session
from ..models.models import User
from ..schemas.user import UserCreate, User as UserSchema

router = APIRouter()

@router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, существует ли пользователь с таким email
    stmt = select(User).where(User.email == user.email)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )

    db_user = User(**user.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_session)
):
    """Получение списка всех пользователей"""
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получение пользователя по ID"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
    return user