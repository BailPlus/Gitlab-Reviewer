from fastapi import APIRouter, Request
from ..schema import BaseOutput, EmptyOutput, analysis as analysis_models
from ..service.auth import get_token_from_cookie, check_repo_permission
from ..service.analysis import *

router = APIRouter(prefix='/api/analysis')


@router.post('/', response_model=EmptyOutput)
async def post_analysis(
    request: Request,
    input_schema: analysis_models.PostAnalysisInput,
):
    token = get_token_from_cookie(request)
    repo_id = input_schema.repo_id
    branch = input_schema.branch
    analyze(token, repo_id, branch)
    return EmptyOutput()


@router.get('/history', response_model=BaseOutput[analysis_models.GetAnalysisHistoryOutput])
async def get_analysis_history_route(
    request: Request,
    repo_id: int,
):
    token = get_token_from_cookie(request)
    analysis_history = get_analysis_history(token, repo_id)
    return BaseOutput(data=analysis_models.GetAnalysisHistoryOutput(
        analysis_history=analysis_history
    ))


@router.get('/{analysis_id}', response_model=BaseOutput[analysis_models.GetAnalysisOutput])
async def get_analysis_route(
    request: Request,
    analysis_id: int,
):
    token = get_token_from_cookie(request)
    analysis_obj = get_analysis(token, analysis_id)
    score = get_score(token, analysis_obj.repo_id)
    assert analysis_obj.analysis_json is not None
    return analysis_models.GetAnalysisOutput(
        analyze_time=int(analysis_obj.created_at.timestamp()),
        result=analysis_obj.analysis_json,
        score=score
    )
