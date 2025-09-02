from sqlmodel import SQLModel, Field
from . import TimestampMixin


class RepositoryMetric(TimestampMixin, SQLModel, table=True):
    __tablename__ = "repository_metrics" # type: ignore
    id: int = Field(default=None, primary_key=True, description='仓库指标记录id')
    repo_id: int = Field(foreign_key="repositories.id", description='仓库id')
    quality_score: float = Field(description='质量得分')
