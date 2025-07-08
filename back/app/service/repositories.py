from typing import override
from gitlab import Gitlab
from ..model.repositories import Repository
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoDeleter
)
from ..errors.auth import PermissionDenied
from ..errors.repositories import *
import gitlab.exceptions

class RepoGetter(IRepoGetter):
    """获取用户绑定的仓库列表"""
    sql_repo_getter: ISqlUserRepoGetter

    def __init__(self, sql_repo_getter: ISqlUserRepoGetter):
        self.sql_repo_getter = sql_repo_getter

    @override
    def get(self, user_id: int) -> list[Repository]:
        return self.sql_repo_getter.get(user_id)


class RepoAdder(IRepoAdder):
    """绑定新仓库"""
    gl: Gitlab
    sql_repo_adder: ISqlRepoAdder

    def __init__(
            self, 
            gl: Gitlab,
            sql_repo_adder: ISqlRepoAdder
    ):
        self.gl = gl
        self.sql_repo_adder = sql_repo_adder

    @override
    def add(self, user_id: int, repo_name: str):
        try:
            repo_id = self.gl.projects.get(repo_name).id
        except gitlab.exceptions.GitlabGetError as e:
            raise RepoNotExist from e
        self.sql_repo_adder.add(user_id, repo_id, repo_name)


class RepoDeleter(IRepoDeleter):
    """删除仓库"""
    sql_user_repo_getter: ISqlUserRepoGetter
    sql_repo_deleter: ISqlRepoDeleter

    def __init__(self,
                 sql_user_repo_getter: ISqlUserRepoGetter,
                 sql_repo_deleter: ISqlRepoDeleter):
        self.sql_user_repo_getter = sql_user_repo_getter
        self.sql_repo_deleter = sql_repo_deleter

    @override
    def delete(self, user_id: int, repo_id: int):
        for repo in self.sql_user_repo_getter.get(user_id):
            if repo.id == repo_id:
                break
        else:
            raise PermissionDenied(info='这不是你的仓库')
        self.sql_repo_deleter.delete(user_id, repo_id)
