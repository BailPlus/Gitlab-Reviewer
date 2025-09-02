from threading import Thread
from typing import Optional
from gitlab import Gitlab
from ..model import ReviewStatus
from ..model.tokens import Token
from ..model.repository_analyses import RepositoryAnalysis
from ..db import analysis as db
from ..errors.review import *
from ..openai import openai
from . import auth
import traceback

__all__ = [
    "analyze",
    "get_analysis",
    "get_analysis_history",
    "get_score",
]


def analyze(token: Token, repo_id: int, branch: Optional[str] = None):
    """进行分析"""
    auth.check_repo_permission(token.user_id, repo_id)
    gl = auth.get_root_gitlab_obj()
    if branch is None:
        branch = _get_default_branch(gl, repo_id)
    _create_analysis(repo_id)
    Thread(target=_analyze_thread, args=(gl, repo_id, branch)).start()  # XXX: 线程不安全
    Thread(target=_score_thread, args=(gl, repo_id, branch)).start()    # XXX: 线程不安全


def get_analysis(token: Token, analysis_id: int) -> RepositoryAnalysis:
    """根据分析id获取分析结果"""
    analysis = db.get_analysis(analysis_id)
    auth.check_repo_permission(token.user.id, analysis.repo_id)
    match analysis.status:
        case ReviewStatus.COMPLETED:
            return analysis
        case ReviewStatus.PENDING:
            raise PendingReview
        case ReviewStatus.FAILED:
            raise FailedReview


def get_analysis_history(token: Token, repo_id: int) -> list[int]:
    """获取仓库历史分析id"""
    auth.check_repo_permission(token.user.id, repo_id)
    return db.get_analysis_history(repo_id)


def get_score(token: Token, repo_id: int):
    """获取仓库分数"""
    auth.check_repo_permission(token.user.id, repo_id)
    return db.get_score(repo_id)


def _create_analysis(repo_id: int) -> RepositoryAnalysis:
    return db.create_analysis(repo_id)


def _analyze_thread(gl: Gitlab, repo_id: int, branch: str):
    """进行分析的线程"""
    try:
        analysis_json = openai.generate_repo_analysis(gl, repo_id, branch)
    except Exception:
        db.fail_analysis(repo_id)   # XXX: 需要给出错误信息
        traceback.print_exc()   # XXX: 建议改为log
    else:
        db.update_analysis(repo_id, analysis_json)


def _score_thread(gl: Gitlab, repo_id: int, branch: str):
    try:
        ##raise NotImplementedError   # TODO
        score = -1
    except Exception:
        db.fail_analysis(repo_id)
        db.save_score(repo_id, -1)
    else:
        db.save_score(repo_id, score)


def _get_default_branch(gl: Gitlab, repo_id: int) -> str:
    return gl.projects.get(repo_id).default_branch
