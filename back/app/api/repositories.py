from typing import Annotated
from fastapi import APIRouter, Depends, Cookie
from ..interface.auth import ITokenGetter
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
)
from ..core.auth import get_token_getter
from ..core.repositories import (
    get_repo_getter,
    get_repo_adder,
    get_repo_deleter,
)
from ..schema import BaseOutput, EmptyOutput
from ..schema.cookies import CookiesSchema
from ..schema import repositories as repo_models

router = APIRouter(prefix='/api/repositories')


@router.get('/',
            response_model=BaseOutput[list[
                repo_models.GetRepositoriesOutput
            ]])
async def get_repositories(
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter),
    repo_getter: IRepoGetter = Depends(get_repo_getter)
):
    """获取用户绑定的仓库列表"""
    uid = token_getter.get(cookies.token)
    repos = repo_getter.get(uid)
    output_models = [repo_models.GetRepositoriesOutput(
        id=repo.id
    ) for repo in repos]
    return BaseOutput(data=output_models)


@router.post('/', response_model=EmptyOutput)
async def add_repository(
    input_schema: repo_models.AddRepositoryInput,
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter),
    repo_adder: IRepoAdder = Depends(get_repo_adder)
):
    """绑定新仓库"""
    uid = token_getter.get(cookies.token)
    repo_name = input_schema.repo_name
    repo_adder.add(uid, repo_name)
    return EmptyOutput()


@router.delete('/{id}', response_model=EmptyOutput)
async def delete_repository(
    id: int,
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter),
    repo_deleter: IRepoDeleter = Depends(get_repo_deleter)
):
    """解绑仓库"""
    uid = token_getter.get(cookies.token)
    repo_deleter.delete(
        user_id=uid,
        repo_id=id
    )
    return EmptyOutput()
