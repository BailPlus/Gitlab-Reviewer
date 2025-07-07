from typing import override
from sqlmodel import select
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
            select(Repository)\
                .where(Repository.user_id == user_id)
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
    def delete(self, repo_id: int) -> None:
        self.session.delete(
            self.session.get(Repository, repo_id)
        )
        self.session.commit()
