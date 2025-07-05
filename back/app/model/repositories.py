from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, ForeignKey
from . import TimestampMixin


class Repository(TimestampMixin, SQLModel, table=True):
    __tablename__ = "repositories" # type: ignore
    id: int = Field(sa_column=Column(
        Integer,
        primary_key=True,
        autoincrement=False,
        nullable=False
    ), description='gitlab中的仓库id')
    analysis_id: Optional[int] = Field(default=None, sa_column=Column(
        Integer,
        ForeignKey("repository_analyses.id", ondelete="CASCADE"),
        nullable=True,  # 双向外键不能同时为非空
    ), description='用户id')
