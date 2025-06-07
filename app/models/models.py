from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class NotificationStatus(enum.Enum):
    PENDING = "pending"  # Ожидает отправки
    SENT = "sent"       # Отправлено
    FAILED = "failed"   # Ошибка отправки

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    telegram_id = Column(String, nullable=True)  # Опциональный Telegram ID
    created_at = Column(DateTime, default=datetime.utcnow)  # Время создания

    campaigns = relationship("CampaignUser", back_populates="user")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)  # Текст уведомления
    created_at = Column(DateTime, default=datetime.utcnow)  # Время создания

    users = relationship("CampaignUser", back_populates="campaign")

class CampaignUser(Base):
    __tablename__ = "campaign_users"

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)  # Статус отправки
    created_at = Column(DateTime, default=datetime.utcnow)  # Время создания
    sent_at = Column(DateTime, nullable=True)  # Время отправки

    campaign = relationship("Campaign", back_populates="users")
    user = relationship("User", back_populates="campaigns")