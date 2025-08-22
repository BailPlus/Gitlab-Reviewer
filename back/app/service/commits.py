from ..core.config import settings
from ..errors.auth import InvalidGitlabWebhookToken
from ..errors.commits import *
from ..model.tokens import Token
from ..model.commit_reviews import CommitReview, CommitReviewStatus
from . import auth
from ..db import commits as db
from ..openai.openai import generate_commit_review
import logging

__all__ = [
    'verify_gitlab_webhook_token',
    'review_commit',
    'get_review_by_commit',
    'apply_commit_suggestions',
]


def verify_gitlab_webhook_token(token: str|None):
    if token != settings.gitlab_webhook_token:
        raise InvalidGitlabWebhookToken


def review_commit(repo_id: int, before: str, after: str):
    _review_thread(repo_id, before, after)


def get_review_by_commit(token: Token, commit_id: str) -> CommitReview:
    review = db.get_review_by_commit_id(commit_id)
    repo_id = review.repo_id
    auth.check_repo_permission(token.user_id, repo_id)
    match review.status:
        case CommitReviewStatus.PENDING:
            raise PendingReview
        case CommitReviewStatus.FAILED:
            raise FailedReview
        case CommitReviewStatus.COMPLETED:
            return review


def apply_commit_suggestions(token: Token, commit_id: str):
    raise NotImplementedError   # TODO


def _create_pending_review(repo_id: int, before: str, after: str) -> CommitReview:
    return db.create_review(repo_id, before, after)


def _finish_review(review: CommitReview, review_json: str):
    db.update_review(review, CommitReviewStatus.COMPLETED, review_json)


def _fail_review(review: CommitReview):
    db.update_review(review, CommitReviewStatus.FAILED)


def _review_thread(repo_id: int, before: str, after: str):
    review = _create_pending_review(repo_id, before, after)
    gl = auth.verify_gitlab_token(token)    # FIXME: token如何解决
    try:
        review_json = generate_commit_review(gl, repo_id, before, after)
    except Exception as e:
        logging.error(f"Failed to generate commit review: {e}")
        _fail_review(review)
    else:
        _finish_review(review, review_json)
