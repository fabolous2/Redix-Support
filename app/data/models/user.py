from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.models import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    topic_id: Mapped[int] = mapped_column(Integer, unique=True)
    status: Mapped[str] = mapped_column(String, server_default='not banned')
    unban_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    info_message: Mapped[int] = mapped_column(Integer)
