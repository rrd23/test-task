from aiogram import Bot
from ..config import settings
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)

async def send_telegram_message(telegram_id: str, text: str):
    """
    Отправка сообщения в Telegram через прямой API вызов
    
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

    # Используем прямой API вызов для лучшей поддержки UTF-8
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Убеждаемся, что текст правильно закодирован
    logger.info(f"Отправляем текст в Telegram: {repr(text)}")
    logger.info(f"Тип текста: {type(text)}")
    logger.info(f"Длина текста: {len(text)}")
    
    data = {
        'chat_id': telegram_id,
        'text': text
    }
    
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        logger.info(f"Сообщение успешно отправлено в Telegram пользователю {telegram_id}")
                        return True
                    else:
                        error_msg = result.get('description', 'Unknown error')
                        logger.error(f"Ошибка API Telegram: {error_msg}")
                        raise Exception(f"Telegram API error: {error_msg}")
                else:
                    error_text = await response.text()
                    logger.error(f"HTTP error {response.status}: {error_text}")
                    raise Exception(f"HTTP error {response.status}: {error_text}")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram пользователю {telegram_id}: {str(e)}")
        raise e