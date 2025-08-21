from sqlmodel import SQLModel, Field, Relationship
from . import TimestampMixin
from .users import User
import time


class Token(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tokens" # type: ignore
    token: str = Field(primary_key=True, description="token")
    user_id: int = Field(foreign_key="users.id", description="用户id")
    user: User = Relationship(passive_deletes='all')
    exp: int = Field(nullable=False, description="过期时间")

    @property
    def is_expired(self) -> bool:
        return time.time() > self.exp
