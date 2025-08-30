from typing import Optional
from sqlmodel import SQLModel, Field
from . import TimestampMixin, ReviewStatus


class MrReview(TimestampMixin, SQLModel, table=True):
    __tablename__ = "mr_reviews" # pyright: ignore[reportAssignmentType]
    id: int = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repositories.id")
    mr_iid: int = Field(description='项目内的merge request id')
    review_json: Optional[str] = Field(default=None, description='评析结果')
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description='评析状态')
