from fastapi import APIRouter, Request
from ..service.commits import *
from ..service.auth import get_token_from_cookie
from ..service.merge_requests import handle_pipeline_event
from ..schema import commits as commits_models
from ..schema import BaseOutput, EmptyOutput
import json, logging

webhook_router = APIRouter(prefix='/api/webhooks')
router = APIRouter(prefix='/api/commits')


@webhook_router.post('/gitlab', response_model=EmptyOutput)
async def gitlab_webhook_receiver(request: Request):
    # 验证webhook密钥
    verify_gitlab_webhook_token(request.headers.get('X-Gitlab-Token'))

    # 记录webhook数据
    data: dict = await request.json()
    record_webhook_received(json.dumps(data, ensure_ascii=False))

    # 解析webhook数据
    match data.get('event_name') or data.get('object_kind'):
        case 'push':
            logging.info(f'Received push event from repo {data["project_id"]}')
            repo_id = data['project_id']
            before = data['before']
            after = data['after']
            review_commit(repo_id, before, after)
        # case 'merge_request':
        #     logging.info(f'Received merge request event from repo {data["project"]["id"]}')
        #     repo_id = data['project']['id']
        #     mr_iid = data['object_attributes']['iid']
        #     review_merge_request(repo_id, mr_iid)
        case 'pipeline':
            logging.info(f'Received pipeline event from repo {data["project"]["id"]}')
            handle_pipeline_event(data)
    return EmptyOutput()


@router.get('/{commit_id}/review', response_model=BaseOutput[commits_models.GetReviewOutput])
async def get_commits_review_route(
    request: Request,
    commit_id: str,
):
    token = get_token_from_cookie(request)
    review = get_review_by_commit(token, commit_id)
    assert review.review_json
    return BaseOutput(data=commits_models.GetReviewOutput(
        review=review.review_json,
        created_at=int(review.created_at.timestamp()),
    ))


@router.post('/{commit_id}/apply-suggestions', response_model=EmptyOutput)
async def apply_commit_suggestions_route(
    request: Request,
    commit_id: str,
):
    token = get_token_from_cookie(request)
    apply_commit_suggestions(token, commit_id)
    return EmptyOutput()
