import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.models import User, Campaign, CampaignUser, NotificationStatus
from ..database import async_session
from .celery_app import celery_app
from ..services.telegram import send_telegram_message

@celery_app.task(name='send_notifications')
def send_notifications(campaign_id: int):
    """Отправка уведомлений для кампании"""
    return asyncio.run(_send_notifications(campaign_id))

async def _send_notifications(campaign_id: int):
    async with async_session() as session:
        # Получаем кампанию и её пользователей с полной загрузкой relationships
        stmt = select(Campaign).where(Campaign.id == campaign_id).options(
            selectinload(Campaign.users).selectinload(CampaignUser.user)
        )
        result = await session.execute(stmt)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            print(f"Кампания с ID {campaign_id} не найдена")
            return

        print(f"Начинаем отправку уведомлений для кампании {campaign_id}")

        for campaign_user in campaign.users:
            try:
                # Имитация отправки email
                await simulate_email_send(campaign_user.user.email, campaign.text)
                
                # Если у пользователя есть telegram_id, отправляем сообщение в Telegram
                if campaign_user.user.telegram_id:
                    await send_telegram_message(
                        campaign_user.user.telegram_id,
                        campaign.text
                    )
                
                campaign_user.status = NotificationStatus.SENT
                campaign_user.sent_at = datetime.utcnow()
                print(f"Уведомление отправлено пользователю {campaign_user.user.email}")
                
            except Exception as e:
                campaign_user.status = NotificationStatus.FAILED
                print(f"Ошибка отправки уведомления пользователю {campaign_user.user.email}: {str(e)}")
            
            # Сохраняем изменения для каждого пользователя
            await session.commit()

        print(f"Завершена отправка уведомлений для кампании {campaign_id}")

async def simulate_email_send(email: str, text: str):
    """Имитация отправки email"""
    await asyncio.sleep(1)
    print(f"Email отправлен на {email}: {text}")