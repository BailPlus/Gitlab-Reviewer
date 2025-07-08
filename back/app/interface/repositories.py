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
    def add(self, user_id: int, repo_id: int, name: str):
        """绑定"""


class ISqlRepoDeleter(IContextManager):
    """数据库解绑仓库的接口"""
    @abstractmethod
    def delete(self, user_id: int, repo_id: int):
        """解绑"""
