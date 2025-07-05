from fastapi import APIRouter
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoDeleter
)

router = APIRouter(prefix='/api/repositories')


@router.get('/')
def get_repositories():
    """获取用户绑定的仓库列表"""


@router.post('/')
def add_repository():
    """绑定新仓库"""


@router.delete('/{id}')
def delete_repository(id: int):
    """解绑仓库"""
