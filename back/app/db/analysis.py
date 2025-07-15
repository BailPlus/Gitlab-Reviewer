from typing import override
from sqlmodel import select, desc
from . import SqlContextManager
from ..interface.analysis import (
    ISqlAnalisisGetter,
    ISqlAnalysisSetter
)
from ..model.repositories import Repository
from ..model.repository_analyses import RepositoryAnalysis, AnalysisStatus
from ..errors.analysis import *


class SqlRepoAnalysisGetter(SqlContextManager, ISqlAnalisisGetter):
    @override
    def get_analysis(self, analysis_id: int) -> RepositoryAnalysis:
        if not (analysis := self.session.get(RepositoryAnalysis, analysis_id)):
            raise AnalysisNotExist
        return analysis

    @override
    def get_analysis_history(self, repo_id: int) -> list[int]:
        analyses = self.session.exec(
            select(RepositoryAnalysis.id)
                .where(RepositoryAnalysis.repo_id == repo_id)
                .order_by(desc(RepositoryAnalysis.id))
        ).all()
        return list(analyses)


class SqlRepoAnalysisSetter(SqlContextManager, ISqlAnalysisSetter):
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
