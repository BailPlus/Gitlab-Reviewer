from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from . import TimestampMixin
from .repository_analyses import RepositoryAnalysis


class Repository(TimestampMixin, SQLModel, table=True):
    __tablename__ = "repositories" # type: ignore
    id: int = Field(sa_column=Column(
        Integer,
        primary_key=True,
        autoincrement=False,
        nullable=False
    ), description='gitlab中的仓库id')
    analysis_id: Optional[int] = Field(
        default=None,
        foreign_key='repository_analyses.id',
        nullable=True,
        description='最新分析id'
    )
    analysis: RepositoryAnalysis = Relationship(
        cascade_delete=True,
        sa_relationship=relationship(
            'RepositoryAnalysis',
            foreign_keys='Repository.analysis_id',
            uselist=False,
            cascade='all, delete',
            single_parent=True
        )
    )
    webhook_id: int = Field(description='webhook id')
