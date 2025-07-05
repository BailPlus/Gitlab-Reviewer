from typing import override
from sqlmodel import select, and_
from ..model.repositories import Repository
from ..model.repository_bindings import RepositoryBinding
from ..model.repository_analyses import RepositoryAnalysis, AnalysisStatus
from ..interface.repositories import (
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoBinder,
    ISqlRepoAnalysisSetter,
    ISqlRepoDeleter
)
from . import SqlContextManager
from ..errors.repositories import *


class SqlRepoGetter(SqlContextManager, ISqlRepoGetter):
    @override
    def get(self, id: int) -> Repository:
        if not (repo := self.session.get(Repository, id)):
            raise RepoNotExist
        return repo


class SqlUserRepoGetter(SqlContextManager, ISqlUserRepoGetter):
    @override
    def get(self, user_id: int) -> list[Repository]:
        return list(self.session.exec(
            select(Repository)
                .join(RepositoryBinding, and_(RepositoryBinding.repo_id == Repository.id))
                .where(RepositoryBinding.user_id == user_id)
        ).all())


class SqlRepoAdder(SqlContextManager, ISqlRepoAdder):
    @override
    def add(self, repo_id: int) -> None:
        self.session.add(Repository(
            id=repo_id
        ))
        self.session.commit()


class SqlRepoBinder(SqlContextManager, ISqlRepoBinder):
    @override
    def bind(self, user_id: int, repo_id: int):
        self.session.add(RepositoryBinding(
            repo_id=repo_id,
            user_id=user_id
        ))
        self.session.commit()


class SqlRepoAnalysisSetter(SqlContextManager, ISqlRepoAnalysisSetter):
    @override
    def add(self, repo_id: int):
        # 创建并插入分析对象
        analysis = RepositoryAnalysis(
            repo_id=repo_id,
            status=AnalysisStatus.PENDING
        )
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)

        # 在仓库对象中引用分析对象
        assert (repo := self.session.get(Repository, repo_id)) is not None
        repo.analysis_id = analysis.id
        self.session.add(repo)
        self.session.commit()

    @override
    def set(self, repo_id: int, analysis_json: str):
        assert (repo := self.session.get(Repository, repo_id)) is not None
        assert (analysis := self.session.get(RepositoryAnalysis,repo.analysis_id)) is not None
        analysis.status = AnalysisStatus.COMPLETED
        analysis.analysis_json = analysis_json
        self.session.add(analysis)
        self.session.commit()


    @override
    def set_failed(self, repo_id: int):
        assert (repo := self.session.get(Repository, repo_id)) is not None
        assert (analysis := self.session.get(RepositoryAnalysis,repo.analysis_id)) is not None
        analysis.status = AnalysisStatus.FAILED
        self.session.add(analysis)
        self.session.commit()


class SqlRepoDeleter(SqlContextManager, ISqlRepoDeleter):
    @override
    def delete(self, user_id: int, repo_id: int) -> None:
        # 根据repo_id和user_id获取仓库绑定对象
        bind = self.session.exec(
            select(RepositoryBinding)
                .where(and_(
                    RepositoryBinding.repo_id == repo_id,
                    RepositoryBinding.user_id == user_id
                ))
        ).first()

        # 删除仓库绑定对象
        self.session.delete(bind)
        self.session.commit()

        # 检查仓库绑定计数，如果为0，则删除仓库
        remain_binds = self.session.exec(
            select(RepositoryBinding)
                .where(RepositoryBinding.repo_id == repo_id)
        ).all()
        if not remain_binds:
            repo = self.session.get(Repository, repo_id)
            if repo is not None:
                self.session.delete(repo)
                self.session.commit()
