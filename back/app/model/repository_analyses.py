from typing import Optional
from sqlmodel import SQLModel, Field
from . import TimestampMixin, ReviewStatus


class RepositoryAnalysis(TimestampMixin, SQLModel, table=True):
    __tablename__ = "repository_analyses" # type: ignore
    id: int = Field(default=None, primary_key=True, description='仓库分析id')
    repo_id: int = Field(foreign_key="repositories.id", description='仓库id')
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description='仓库分析状态')
    analysis_json: Optional[str] = Field(default=None, description='仓库分析结果', nullable=True)
