from typing import override
from sqlmodel import select, and_
from ..model.repositories import Repository
from ..model.repository_bindings import RepositoryBinding
from ..model.repository_analyses import RepositoryAnalysis, AnalysisStatus
from ..interface.repositories import (
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
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
    def add(self, user_id: int, repo_id: int, name: str) -> None:
        self.session.add(RepositoryBinding(
            repo_id=repo_id,
            user_id=user_id
        ))
        self.session.commit()
        repo = self.session.get(Repository, repo_id)
        if repo is not None:
            return
        analysis = RepositoryAnalysis(
            repo_id=repo_id,
            status=AnalysisStatus.PENDING
        )
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        self.session.add(Repository(
            id=repo_id,
            analysis_id=analysis.id,
        ))
        self.session.commit()
        '''
        analizer = RepoAnalizer(analisis.id)
        @analizer.callback
        def callback(result: str):
            self.session.add(RepositoryAnalysis(    # FIXME: 可能存在session被关闭的风险
                repo_id=repo_id,
                status=AnalysisStatus.COMPLETED,
                analysis_json=result
            ))
            self.session.commit()
        threading.Thread(target=analizer.analyze).start()
        '''


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
