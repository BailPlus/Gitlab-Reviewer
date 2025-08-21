from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from . import TimestampMixin


class AnalysisStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


class RepositoryAnalysis(TimestampMixin, SQLModel, table=True):
    __tablename__ = "repository_analyses" # type: ignore
    id: int = Field(default=None, primary_key=True, description='仓库分析id')
    repo_id: int = Field(foreign_key="repositories.id", description='仓库id')
    status: AnalysisStatus = Field(description='仓库分析状态')
    analysis_json: Optional[str] = Field(default=None, description='仓库分析结果', nullable=True)
