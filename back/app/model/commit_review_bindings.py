from sqlmodel import SQLModel, Field, Relationship
from . import TimestampMixin
from .commit_reviews import CommitReview


class CommitReviewBinding(TimestampMixin, SQLModel, table=True):
    __tablename__ = "commit_review_bindings" # pyright: ignore[reportAssignmentType]
    id: int = Field(default=None, primary_key=True, description='commit_review绑定记录id')
    commit_id: str = Field(unique=True, description='commit_id')
    review_id: int = Field(foreign_key='commit_reviews.id', description='commit评审id')
    review: CommitReview = Relationship(
        cascade_delete=True,
    )

'''
        sa_relationship=relationship(
            'CommitReview',
            foreign_keys='CommitReviewBinding.review_id',
            uselist=False
        )
    )
'''
