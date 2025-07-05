from typing import override
from httpx import AsyncClient
from ..model.repositories import Repositories
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoDeleter
)
from ..errors.auth import PermissionDenied

class RepoGetter(IRepoGetter):
    """获取用户绑定的仓库列表"""
    sql_repo_getter: ISqlUserRepoGetter

    def __init__(self, sql_repo_getter: ISqlUserRepoGetter):
        self.sql_repo_getter = sql_repo_getter

    @override
    def get(self, user_id: int) -> list[Repositories]:
        return self.sql_repo_getter.get(user_id)


class RepoAdder(IRepoAdder):
    """绑定新仓库"""
    sql_repo_adder: ISqlRepoAdder

    def __init__(self, sql_repo_adder: ISqlRepoAdder):
        self.sql_repo_adder = sql_repo_adder

    @override
    def add(self, user_id: int, repo_name: str):
        #TODO: 通过gitlab sdk获取仓库信息
        repo_id = int()
        url = str()
        self.sql_repo_adder.add(user_id, repo_id, repo_name, url)


class RepoDeleter(IRepoDeleter):
    """删除仓库"""
    sql_repo_getter: ISqlRepoGetter
    sql_repo_deleter: ISqlRepoDeleter

    def __init__(self,
                 sql_repo_getter: ISqlRepoGetter,
                 sql_repo_deleter: ISqlRepoDeleter):
        self.sql_repo_getter = sql_repo_getter
        self.sql_repo_deleter = sql_repo_deleter

    @override
    def delete(self, user_id: int, repo_id: int):
        if self.sql_repo_getter.get(repo_id).user_id != user_id:
            raise PermissionDenied(info='这不是你的仓库')
        self.sql_repo_deleter.delete(repo_id)
