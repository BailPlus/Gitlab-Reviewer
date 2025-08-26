from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from . import TimestampMixin


class CommitReviewStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


class CommitReview(TimestampMixin, SQLModel, table=True):
    __tablename__ = "commit_reviews" # pyright: ignore[reportAssignmentType]
    id: int = Field(default=None, primary_key=True, description='commit评审id')
    repo_id: int = Field(foreign_key="repositories.id", description='仓库id')
    before_commit: str = Field(description='推送前的最后一个commit')
    after_commit: str = Field(unique=True, description='推送后的最后一个commit')
    status: CommitReviewStatus = Field(default=CommitReviewStatus.PENDING, description='commit评审状态')
    review_json: Optional[str] = Field(default=None, description='commit评审结果')
