from fastapi import APIRouter, Request
from ..schema import BaseOutput, EmptyOutput, analysis as analysis_models
from ..service.auth import get_token_from_cookie

router = APIRouter(prefix='/api/analysis')


@router.post('/', response_model=EmptyOutput)
async def post_analysis(
    request: Request,
    input_schema: analysis_models.PostAnalysisInput,
):
    token = get_token_from_cookie(request)
    repo_id = input_schema.repo_id
    return EmptyOutput()


@router.get('/history', response_model=BaseOutput[analysis_models.GetAnalysisHistoryOutput])
async def get_analysis_history(
    request: Request,
    repo_id: int,
):
    token = get_token_from_cookie(request)
    return BaseOutput(data=analysis_models.GetAnalysisHistoryOutput(
        analysis_history=[]
    ))


@router.get('/{analysis_id}', response_model=analysis_models.GetAnalysisOutput)
async def get_analysis(
    request: Request,
    analysis_id: int,
):
    token = get_token_from_cookie(request)
    return analysis_models.GetAnalysisOutput(
        analyze_time=0,
        result="",
        score=0
    )
