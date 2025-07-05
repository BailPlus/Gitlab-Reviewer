from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, ForeignKey
from . import TimestampMixin


class Repositories(TimestampMixin, SQLModel, table=True):
    id: int = Field(sa_column=Column(
        Integer,
        primary_key=True,
        autoincrement=False,
        nullable=False
    ), description='gitlab中的仓库id')
    user_id: int = Field(sa_column=Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    ), description='用户id')
    name: str = Field(nullable=False, description='仓库名称')
