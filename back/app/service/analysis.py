from threading import Thread
from gitlab import Gitlab
from ..model.tokens import Token
from ..model.repository_analyses import RepositoryAnalysis
from ..db import analysis as db
from ..errors.auth import PermissionDenied
from ..errors.analysis import *
from ..openai.openai import generate_repo_analysis
from . import repositories, auth

__all__ = [
    "analyze",
    "get_analysis",
    "get_analysis_history",
    "score_repo",
    "get_score",
]


def analyze(token: Token, repo_id: int, branch: str):
    """进行分析"""
    _check_permission(token.user_id, repo_id)
    gl = auth.verify_gitlab_token(token.token)
    Thread(target=_analyze_thread, args=(gl, repo_id, branch)).start()  # XXX: 线程不安全


def score_repo(token: Token, repo_id: int, branch: str):
    """获取仓库分数"""
    _check_permission(token.user.id, repo_id)
    gl = auth.verify_gitlab_token(token.token)
    Thread(target=_score_thread, args=(gl, repo_id, branch)).start()  # XXX: 线程不安全


def get_analysis(token: Token, analysis_id: int) -> RepositoryAnalysis:
    """根据分析id获取分析结果"""
    analysis = db.get_analysis(analysis_id)
    _check_permission(token.user.id, analysis.repo_id)
    match analysis.status:
        case db.AnalysisStatus.COMPLETED:
            return analysis
        case db.AnalysisStatus.PENDING:
            raise PendingAnalysis
        case db.AnalysisStatus.FAILED:
            raise FailedAnalysis


def get_analysis_history(token: Token, repo_id: int) -> list[int]:
    """获取仓库历史分析id"""
    _check_permission(token.user.id, repo_id)
    return db.get_analysis_history(repo_id)


def get_score(token: Token, repo_id: int):
    """获取仓库分数"""
    _check_permission(token.user.id, repo_id)
    return db.get_score(repo_id)


def _check_permission(user_id: int, repo_id: int):
    """验证用户是否绑定analysis对应的仓库"""
    # XXX: 建议进行压测，在用户绑定的仓库数量很多时
    for repo in repositories.get_user_binded_repos(user_id):
        if repo.id == repo_id:
            break
    else:
        raise PermissionDenied


def _analyze_thread(gl: Gitlab, repo_id: int, branch: str):
    """进行分析的线程"""
    try:
        analysis_json = generate_repo_analysis(gl, repo_id, branch)
    except Exception:
        db.fail_analysis(repo_id)   # XXX: 需要给出错误信息
    else:
        db.update_analysis(repo_id, analysis_json)


def _score_thread(gl: Gitlab, repo_id: int, branch: str):
    raise NotImplementedError   # TODO
    try:
        score = NotImplemented
    except Exception:
        db.fail_analysis(repo_id)
        db.save_score(-1)
    else:
        db.save_score(repo_id, score)
