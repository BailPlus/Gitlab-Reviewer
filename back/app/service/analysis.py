from .auth import verify_gitlab_token
from ..model.tokens import Token


def analyze(repo_id: int, branch: str) -> str:
    """进行分析"""
    raise NotImplementedError   # TODO


def get_analysis(token: Token, analysis_id: int) -> str:
    """获取分析结果"""
    gl = verify_gitlab_token(token.token)
    


def get_analysis_history(repo_id: int) -> list[int]:
    """获取仓库历史分析结果"""
