from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.connectors.database import Base

if TYPE_CHECKING:
    from src.models.users import UsersOrm





class PostsOrm(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(String(250), nullable=False)



    user: Mapped["UsersOrm"] = relationship(
        back_populates="posts"
    )


