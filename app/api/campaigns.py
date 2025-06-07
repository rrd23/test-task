from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..database import get_session
from ..models.models import Campaign, CampaignUser, User, NotificationStatus
from ..schemas.campaign import CampaignCreate, Campaign as CampaignSchema, CampaignStatus
from ..tasks.notification_tasks import send_notifications

router = APIRouter()

@router.post("/", response_model=CampaignSchema)
async def create_campaign(
    campaign: CampaignCreate,
    session: AsyncSession = Depends(get_session)
):
    # Проверяем существование всех пользователей
    for user_id in campaign.user_ids:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Пользователь с id {user_id} не найден"
            )
    
    # Создаем кампанию
    db_campaign = Campaign(text=campaign.text)
    session.add(db_campaign)
    await session.commit()
    await session.refresh(db_campaign)

    # Добавляем пользователей в кампанию
    for user_id in campaign.user_ids:
        campaign_user = CampaignUser(
            campaign_id=db_campaign.id,
            user_id=user_id
        )
        session.add(campaign_user)
    
    await session.commit()
    
    # Загружаем кампанию с пользователями для ответа
    stmt = select(Campaign).where(Campaign.id == db_campaign.id).options(
        selectinload(Campaign.users).selectinload(CampaignUser.user)
    )
    result = await session.execute(stmt)
    campaign_with_users = result.scalar_one()
    
    # Запускаем асинхронную отправку уведомлений
    send_notifications.delay(db_campaign.id)
    
    return campaign_with_users

@router.get("/{campaign_id}/status", response_model=CampaignStatus)
async def get_campaign_status(
    campaign_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Загружаем кампанию с пользователями
    stmt = select(Campaign).where(Campaign.id == campaign_id).options(
        selectinload(Campaign.users).selectinload(CampaignUser.user)
    )
    result = await session.execute(stmt)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Кампания не найдена"
        )
    
    # Подсчитываем статистику - ✅ Исправлено: правильное обращение к enum
    total_notifications = len(campaign.users)
    sent_notifications = sum(1 for cu in campaign.users if cu.status == NotificationStatus.SENT)
    failed_notifications = sum(1 for cu in campaign.users if cu.status == NotificationStatus.FAILED)
    pending_notifications = sum(1 for cu in campaign.users if cu.status == NotificationStatus.PENDING)
    
    # Определяем общий статус кампании
    if failed_notifications == total_notifications:
        status = "failed"
    elif sent_notifications == total_notifications:
        status = "completed"
    elif sent_notifications > 0 or failed_notifications > 0:
        status = "in_progress"
    else:
        status = "pending"
    
    return CampaignStatus(
        id=campaign.id,
        status=status,
        total_notifications=total_notifications,
        sent_notifications=sent_notifications,
        failed_notifications=failed_notifications,
        pending_notifications=pending_notifications,
        created_at=campaign.created_at
    )

@router.get("/", response_model=list[CampaignSchema])
async def get_campaigns(
    session: AsyncSession = Depends(get_session)
):
    """Получение списка всех кампаний"""
    stmt = select(Campaign).options(
        selectinload(Campaign.users).selectinload(CampaignUser.user)
    )
    result = await session.execute(stmt)
    campaigns = result.scalars().all()
    return campaigns