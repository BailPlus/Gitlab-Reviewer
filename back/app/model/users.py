from typing import Optional
from sqlmodel import SQLModel, Field, ForeignKey
from sqlalchemy import Column, Integer
from . import TimestampMixin


class Users(TimestampMixin, SQLModel, table=True):
    id: int = Field(sa_column=Column(
        Integer,
        primary_key=True,
        autoincrement=False,
        nullable=False
    ))
    username: str
    email: str


class Tokens(TimestampMixin, SQLModel, table=True):
    token: str = Field(primary_key=True)
    user_id: int = Field(sa_column=Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE")
    ))
    exp: int
