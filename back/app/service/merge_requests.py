from threading import Thread
from ..db import merge_requests as db
from ..model import ReviewStatus
from ..model.tokens import Token
from ..model.mr_reviews import MrReview
from ..service import auth, notifications
from ..openai import openai
from ..errors.review import *
import json, logging

__all__ = [
    "review_merge_request",
    "get_mr_review",
]


def review_merge_request(repo_id: int, mr_iid: int):
    Thread(target=_review_thread, args=(repo_id, mr_iid)).start()


def get_mr_review(token: Token, repo_id: int, merge_request_id: int) -> MrReview:
    auth.check_repo_permission(token.user.id, repo_id)
    review = db.get_mr_review(repo_id, merge_request_id)
    match review.status:
        case ReviewStatus.PENDING:
            raise PendingReview
        case ReviewStatus.FAILED:
            raise FailedReview
        case ReviewStatus.COMPLETED:
            return review


def _create_pending_review(repo_id: int, mr_iid: int) -> MrReview:
    return db.create_review(repo_id, mr_iid)


def _finish_review(review: MrReview, review_json: str):
    db.update_review(review, ReviewStatus.COMPLETED, review_json)


def _fail_review(review: MrReview):
    db.update_review(review, ReviewStatus.FAILED)


def _verify_review_json_validity(review_json: str):
    review_dict = json.loads(review_json)
    assert 'info' in review_dict and 'suggestion' in review_dict and 'level' in review_dict


def _review_thread(repo_id: int, mr_iid: int):
    review = _create_pending_review(repo_id, mr_iid)
    gl = auth.get_root_gitlab_obj()
    try:
        review_json = openai.generate_mr_review(gl, repo_id, mr_iid)
        _verify_review_json_validity(review_json)
    except Exception as e:
        logging.error(f"Failed to generate commit review: {e}")
        _fail_review(review)
    else:
        _finish_review(review, review_json)
        notifications.NotifyMethod.send_all(repo_id, review_json)
