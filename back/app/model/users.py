from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer
from . import TimestampMixin


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users" # type: ignore
    id: int = Field(sa_column=Column(
        Integer,
        primary_key=True,
        autoincrement=False,
        nullable=False
    ))
    username: str
    email: str
