from abc import ABC, abstractmethod
from ..model.repository_analyses import RepositoryAnalysis
from . import IContextManager


class IRepoAnalizer(ABC):
    """仓库分析器接口"""
    @abstractmethod
    def analyze(self, repo_id: int, branch: str) -> str:
        """进行分析"""


class IAnalisisGetter(ABC):
    """仓库分析结果获取接口"""
    @abstractmethod
    def get_analysis(self, analysis_id: int) -> str:
        """获取分析结果"""


class IAnalysisHistoryGetter(ABC):
    """仓库分析历史获取接口"""
    @abstractmethod
    def get_analysis_history(self, repo_id: int) -> list[int]:
        """获取仓库历史分析结果"""


class ISqlAnalisisGetter(ABC):
    """从数据库中获取仓库分析结果接口"""
    @abstractmethod
    def get_analysis(self, analysis_id: int) -> RepositoryAnalysis:
        """获取仓库分析结果"""
    
    @abstractmethod
    def get_analysis_history(self, repo_id: int) -> list[int]:
        """获取仓库历史分析结果"""


class ISqlAnalysisSetter(IContextManager):
    """数据库设置仓库分析结果的接口"""
    @abstractmethod
    def add(self, repo_id: int):
        """增加仓库分析条目并设置状态为pending"""

    @abstractmethod
    def set(self, repo_id: int, analysis_json: str):
        """设置仓库分析结果（状态为completed）"""

    @abstractmethod
    def set_failed(self, repo_id: int):
        """设置仓库分析状态为failed"""
