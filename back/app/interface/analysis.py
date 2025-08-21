from abc import ABC, abstractmethod


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
