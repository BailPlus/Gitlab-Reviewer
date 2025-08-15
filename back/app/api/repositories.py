from fastapi import APIRouter, Request
from ..service.auth import get_token_from_cookie
from ..service.repositories import *
from ..schema import BaseOutput, EmptyOutput
from ..schema import repositories as repo_models

router = APIRouter(prefix='/api/repositories')


@router.get('/',
            response_model=BaseOutput[list[
                repo_models.GetRepositoriesOutput
            ]])
async def get_repositories(request: Request):
    """获取用户绑定的仓库列表"""
    token = get_token_from_cookie(request)
    repos = get_user_binded_repos(token.user.id)
    return BaseOutput(data=[repo_models.GetRepositoriesOutput(
        id=repo.id
    ) for repo in repos])


@router.post('/', response_model=EmptyOutput)
async def add_repository(
    request: Request,
    input_schema: repo_models.AddRepositoryInput,
):
    """绑定新仓库"""
    token = get_token_from_cookie(request)
    bind_repo(token, input_schema.repo_name)
    return EmptyOutput()


@router.delete('/{repo_id}', response_model=EmptyOutput)
async def delete_repository(
    request: Request,
    repo_id: int,
):
    """解绑仓库"""
    token = get_token_from_cookie(request)
    unbind_repo(
        user_id=token.user.id,
        repo_id=repo_id
    )
    return EmptyOutput()
