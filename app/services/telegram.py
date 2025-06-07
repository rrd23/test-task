from aiogram import Bot
from ..config import settings
import logging

logger = logging.getLogger(__name__)

async def send_telegram_message(telegram_id: str, text: str):
    """
    Отправка сообщения в Telegram
    
    Args:
        telegram_id: ID пользователя в Telegram
        text: Текст сообщения
        
    Returns:
        bool: True если сообщение отправлено успешно
        
    Raises:
        ValueError: Если токен бота не настроен
        Exception: При ошибке отправки сообщения
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning(f"Токен Telegram бота не настроен. Сообщение для {telegram_id}: {text}")
        raise ValueError("Telegram bot token not configured")

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
        logger.info(f"Сообщение успешно отправлено в Telegram пользователю {telegram_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram пользователю {telegram_id}: {str(e)}")
        raise e
    finally:
        await bot.session.close()