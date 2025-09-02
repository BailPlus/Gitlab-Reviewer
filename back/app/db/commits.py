from typing import Optional
from sqlmodel import select
from ..model import ReviewStatus
from ..model.commit_reviews import CommitReview
from ..model.webhook_logs import WebhookLog
from ..errors.review import *
from . import get_session

__all__ = [
    'create_review',
    'get_review',
    'update_review'
]


def create_review(repo_id: int, before: str, after: str) -> CommitReview:
    review = CommitReview(
        repo_id=repo_id,
        before_commit=before,
        after_commit=after,
    )
    with get_session() as session:
        session.add(review)
        session.commit()
        session.refresh(review)
    return review


def get_review(review_id: int) -> CommitReview:
    with get_session() as session:
        review = session.get(CommitReview, review_id)
    if review is None:
        raise ReviewNotExist
    return review


# def get_review_by_commit_id(commit_id: str) -> CommitReview:
#     with get_session() as session:
#         review = (session.exec(
#             select(CommitReviewBinding)
#             .filter_by(commit_id=commit_id)
#         )
#         .one()
#         .review)
#     if review is None:
#         raise ReviewNotExist
#     return review


def get_review_by_commit_id(commit_id: str) -> CommitReview:
    with get_session() as session:
        review = (session.exec(
            select(CommitReview)
            .filter_by(after_commit=commit_id)
        )
        .one_or_none())
    if review is None:
        raise ReviewNotExist
    return review


def update_review(review: CommitReview, status: ReviewStatus, review_json: Optional[str] = None):
    review.status = status
    review.review_json = review_json
    with get_session() as session:
        session.add(review)
        session.commit()


def record_webhook_received(data: str):
    with get_session() as session:
        session.add(WebhookLog(data=data))
        session.commit()
