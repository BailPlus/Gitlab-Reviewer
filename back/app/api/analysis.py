from typing import Annotated
from fastapi import APIRouter, Depends, Cookie
from ..interface.auth import ITokenGetter
from ..schema.cookies import CookiesSchema
from ..schema import BaseOutput, EmptyOutput, analysis as analysis_models
from ..core.auth import get_token_getter

router = APIRouter(prefix='/api/analysis')


@router.post('/', response_model=EmptyOutput)
def post_analysis(
    input_schema: analysis_models.PostAnalysisInput,
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter),
):
    uid = token_getter.get(cookies.token)
    repo_id = input_schema.repo_id
    return EmptyOutput()


@router.get('/history', response_model=BaseOutput[analysis_models.GetAnalysisHistoryOutput])
def get_analysis_history(
    repo_id: int,
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter),
):
    uid = token_getter.get(cookies.token)
    return BaseOutput(data=analysis_models.GetAnalysisHistoryOutput(
        analysis_history=[]
    ))


@router.get('/{analysis_id}', response_model=analysis_models.GetAnalysisOutput)
def get_analysis(
    analysis_id: int,
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter),
):
    uid = token_getter.get(cookies.token)
    return analysis_models.GetAnalysisOutput(
        analyze_time=0,
        result="",
        score=0
    )
