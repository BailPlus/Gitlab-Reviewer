from sqlmodel import SQLModel, Field
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
