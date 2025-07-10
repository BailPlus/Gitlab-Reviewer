from typing import override
from threading import Thread
from gitlab import Gitlab
from ..model.repositories import Repository
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoBinder,
    ISqlRepoAnalysisSetter,
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
    sql_repo_getter: ISqlRepoGetter
    sql_userrepo_getter: ISqlUserRepoGetter
    sql_repo_adder: ISqlRepoAdder
    sql_repo_binder: ISqlRepoBinder
    sql_repo_analysis_setter: ISqlRepoAnalysisSetter

    def __init__(
            self, 
            gl: Gitlab,
            sql_repo_getter: ISqlRepoGetter,
            sql_userrepo_getter: ISqlUserRepoGetter,
            sql_repo_adder: ISqlRepoAdder,
            sql_repo_binder: ISqlRepoBinder,
            sql_repo_analysis_setter: ISqlRepoAnalysisSetter
    ):
        self.gl = gl
        self.sql_repo_getter = sql_repo_getter
        self.sql_userrepo_getter = sql_userrepo_getter
        self.sql_repo_adder = sql_repo_adder
        self.sql_repo_binder = sql_repo_binder
        self.sql_repo_analysis_setter = sql_repo_analysis_setter

    @override
    def add(self, user_id: int, repo_name: str):
        # 获取仓库id
        try:
            repo_id = self.gl.projects.get(repo_name).id
        except gitlab.exceptions.GitlabGetError as e:
            raise RepoNotExist from e

        # 检查仓库是否绑定过
        for repo in self.sql_userrepo_getter.get(user_id):
            if repo.id == repo_id:
                raise RepoAlreadyBinded

        # 添加仓库
        try:
            self.sql_repo_getter.get(repo_id)
        except RepoNotExist:
            self.sql_repo_adder.add(repo_id)
            self.sql_repo_analysis_setter.add(repo_id)
        self.sql_repo_binder.bind(user_id, repo_id)

        # 创建分析线程并定义回调。等待AI组提供RepoAnalizer
        '''        
        analizer = get_repo_analyzer(repo_id)   # 在core.analysis中定义这个工厂函数，用于创建RepoAnalizer对象
        @analizer.ondone
        def callback(result: str):
            self.sql_repo_analysis_setter.set(repo_id, result)
        @analizer.onfail
        def callback_fail(result: str):
            self.sql_repo_analysis_setter.set_failed(repo_id)
        Thread(target=analizer.analyze).start()
        '''


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
