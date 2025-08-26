from threading import Thread
from ..core.config import settings
from ..errors.auth import InvalidGitlabWebhookToken
from ..errors.commits import *
from ..model.tokens import Token
from ..model.commit_reviews import CommitReview, CommitReviewStatus
from . import auth, notifications
from ..db import commits as db
from ..openai import openai
import logging, json

__all__ = [
    'RiskLevel',
    'verify_gitlab_webhook_token',
    'review_commit',
    'get_review_by_commit',
    'apply_commit_suggestions',
]


class RiskLevel:
    level: int
    name: str

    EVENT: 'RiskLevel' = None # pyright: ignore[reportAssignmentType]
    BUG: 'RiskLevel' = None # pyright: ignore[reportAssignmentType]
    INSECURE: 'RiskLevel' = None # pyright: ignore[reportAssignmentType]
    LEAK: 'RiskLevel' = None # pyright: ignore[reportAssignmentType]

    def __init__(self, level: int, name: str):
        self.level = level
        self.name = name

    @classmethod
    def from_int(cls, level: int) -> 'RiskLevel':
        return {
            0: cls.EVENT,
            1: cls.BUG,
            2: cls.INSECURE,
            3: cls.LEAK,
        }[level]

RiskLevel.EVENT = RiskLevel(0, 'low')
RiskLevel.BUG = RiskLevel(1, 'medium')
RiskLevel.INSECURE = RiskLevel(2, 'high')
RiskLevel.LEAK = RiskLevel(3, 'critical')


def verify_gitlab_webhook_token(token: str|None):
    if token != settings.gitlab_webhook_token:
        raise InvalidGitlabWebhookToken


def review_commit(repo_id: int, before: str, after: str):
    Thread(target=_review_thread, args=(repo_id, before, after)).start()


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


def _verify_review_json_validity(review_json: str):
    review_dict = json.loads(review_json)
    assert 'info' in review_dict and 'suggestion' in review_dict and 'level' in review_dict


def _review_thread(repo_id: int, before: str, after: str):
    review = _create_pending_review(repo_id, before, after)
    gl = auth.get_root_gitlab_obj()
    try:
        review_json = openai.generate_commit_review(gl, repo_id, before, after)
        _verify_review_json_validity(review_json)
    except Exception as e:
        logging.error(f"Failed to generate commit review: {e}")
        _fail_review(review)
    else:
        _finish_review(review, review_json)
        notifications.NotifyMethod.send_all(repo_id, review_json)
