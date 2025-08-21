from sqlmodel import select, desc
from ..model.repositories import Repository
from ..model.repository_analyses import RepositoryAnalysis, AnalysisStatus
from ..model.repository_metrics import RepositoryMetric
from . import get_session
from ..errors.analysis import *

__all__ = [
    "get_analysis",
    "get_analysis_history",
    'create_analysis',
    'update_analysis',
    'fail_analysis',
]


def get_analysis(analysis_id: int) -> RepositoryAnalysis:
    with get_session() as session:
        if not (analysis := session.get(RepositoryAnalysis, analysis_id)):
            raise AnalysisNotExist
    return analysis


def get_analysis_history(repo_id: int) -> list[int]:
    with get_session() as session:
        analyses = session.exec(
            select(RepositoryAnalysis.id)
                .where(RepositoryAnalysis.repo_id == repo_id)
                .order_by(desc(RepositoryAnalysis.id))
        ).all()
    return list(analyses)


def create_analysis(repo_id: int) -> RepositoryAnalysis:
    with get_session() as session:
        # 创建并插入分析对象
        analysis = RepositoryAnalysis(
            repo_id=repo_id,
            status=AnalysisStatus.PENDING
        )
        session.add(analysis)
        session.commit()
        session.refresh(analysis)

        # 在仓库对象中引用分析对象
        assert (repo := session.get(Repository, repo_id)) is not None
        repo.analysis = analysis
        session.add(repo)
        session.commit()
    return analysis


def update_analysis(repo_id: int, analysis_json: str):
    with get_session() as session:
        assert (repo := session.get(Repository, repo_id)) is not None
        assert (analysis := session.get(RepositoryAnalysis,repo.analysis_id)) is not None
        analysis.status = AnalysisStatus.COMPLETED
        analysis.analysis_json = analysis_json
        session.add(analysis)
        session.commit()


def fail_analysis(repo_id: int):
    with get_session() as session:
        assert (repo := session.get(Repository, repo_id)) is not None
        assert (analysis := session.get(RepositoryAnalysis,repo.analysis_id)) is not None
        analysis.status = AnalysisStatus.FAILED
        session.add(analysis)
        session.commit()


def get_score(repo_id: int) -> float:
    with get_session() as session:
        assert (repo := session.get(Repository, repo_id)) is not None
        return (session.exec(
            select(RepositoryMetric)
            .filter_by(repo_id=repo_id)
        )
        .one()
        .quality_score)


def save_score(repo_id: int, score: float):
    with get_session() as session:
        assert (repo := session.get(Repository, repo_id)) is not None
        session.add(
            RepositoryMetric(repo_id=repo_id, quality_score=score)
        )
        session.commit()
