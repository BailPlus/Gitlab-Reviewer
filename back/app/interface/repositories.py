from abc import ABC, abstractmethod
from ..model.repositories import Repository
from . import IContextManager


class IRepoGetter(ABC):
    """获取当前用户所有仓库的接口"""
    @abstractmethod
    def get(self, user_id: int) -> list[Repository]:
        """获取"""


class IRepoAdder(ABC):
    """绑定新仓库的接口"""
    @abstractmethod
    def add(self, user_id: int, repo_name: str) -> None:
        """绑定"""


class IRepoDeleter(ABC):
    """解绑仓库的接口"""
    @abstractmethod
    def delete(self, user_id: int, repo_id: int) -> None:
        """解绑"""


class ISqlRepoGetter(IContextManager):
    """数据库根据id获取仓库的接口"""
    @abstractmethod
    def get(self, id: int) -> Repository:
        """获取"""


class ISqlUserRepoGetter(IContextManager):
    """数据库获取当前用户所有仓库的接口"""
    @abstractmethod
    def get(self, user_id: int) -> list[Repository]:
        """获取"""


class ISqlRepoAdder(IContextManager):
    """数据库绑定新仓库的接口"""
    @abstractmethod
    def add(self, repo_id: int):
        """注册仓库"""


class ISqlRepoBinder(IContextManager):
    """数据库绑定新仓库的接口"""
    @abstractmethod
    def bind(self, user_id: int, repo_id: int):
        """用户绑定仓库"""


class ISqlRepoAnalysisSetter(IContextManager):
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


class ISqlRepoDeleter(IContextManager):
    """数据库解绑仓库的接口"""
    @abstractmethod
    def delete(self, user_id: int, repo_id: int):
        """解绑"""
