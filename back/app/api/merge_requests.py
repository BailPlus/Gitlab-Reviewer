from fastapi import APIRouter, Request
from ..schema import BaseOutput
from ..schema.merge_requests import *
from ..service.auth import get_token_from_cookie
from ..service.merge_requests import *

router = APIRouter(prefix="/api/merge_requests")


@router.get("/{repo_id}/{merge_request_id}/review", response_model=BaseOutput[MrReviewOutput])
def get_mr_review_route(
    request: Request,
    repo_id: int,
    merge_request_id: int,
):
    token = get_token_from_cookie(request)
    review = get_mr_review(token, repo_id, merge_request_id)
    assert review.review_json
    return BaseOutput(data=MrReviewOutput(
        review=review.review_json,
        created_at=int(review.created_at.timestamp()),
    ))
