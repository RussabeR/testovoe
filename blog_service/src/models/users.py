from datetime import datetime, timezone
from typing import List
from sqlalchemy import (
    String,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.connectors.database import Base
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.models.posts import PostsOrm


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    email: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    posts: Mapped[List["PostsOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
