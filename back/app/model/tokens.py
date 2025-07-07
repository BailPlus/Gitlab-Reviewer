from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, ForeignKey
from . import TimestampMixin


class Token(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tokens" # type: ignore
    token: str = Field(primary_key=True)
    user_id: int = Field(sa_column=Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    ))
    exp: int = Field(nullable=False)
