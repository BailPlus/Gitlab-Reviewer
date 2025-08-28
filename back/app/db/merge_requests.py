from typing import Optional
from sqlmodel import select
from ..model import ReviewStatus
from ..model.mr_reviews import MrReview
from ..errors.review import *
from . import get_session

__all__ = [
    "get_mr_review",
]


def create_review(repo_id: int, mr_iid: int) -> MrReview:
    review = MrReview(
        repo_id=repo_id,
        mr_iid=mr_iid,
    )
    with get_session() as session:
        session.add(review)
        session.commit()
        session.refresh(review)
    return review


def get_mr_review(repo_id: int, mr_iid: int) -> MrReview:
    """
    获取merge request的评论
    """
    with get_session() as session:
        review = session.exec(
            select(MrReview)
            .where(MrReview.repo_id == repo_id)
            .where(MrReview.mr_iid == mr_iid)
        ).one_or_none()
    if review is None:
        raise ReviewNotExist
    return review


def update_review(review: MrReview, status: ReviewStatus, review_json: Optional[str] = None):
    review.status = status
    review.review_json = review_json
    with get_session() as session:
        session.add(review)
        session.commit()
