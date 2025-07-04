from abc import ABC, abstractmethod
from . import IContextManager

class IGitlabTokenGetter(ABC):
    """gitlab token获取器接口"""
    @abstractmethod
    async def get_token(self, code: str):
        """获取token"""

    @property
    @abstractmethod
    def token(self) -> str:
        """返回token"""

    @property
    @abstractmethod
    def token_age(self) -> int:
        """返回token有效期"""


class IGitlabUserinfoGetter(ABC):
    """gitlab用户信息获取器接口"""
    @abstractmethod
    async def get(self, token: str):
        """获取用户信息"""

    @property
    @abstractmethod
    def uid(self) -> int:
        """返回用户id"""

    @property
    @abstractmethod
    def username(self) -> str:
        """返回用户名"""
    
    @property
    @abstractmethod
    def email(self) -> str:
        """返回用户邮箱"""


class IUserinfoGetter(ABC):
    """用户信息获取器接口"""
    @abstractmethod
    def get(self, uid: int):
        """获取用户信息"""

    @property
    @abstractmethod
    def username(self) -> str:
        """返回用户名"""

    @property
    @abstractmethod
    def email(self) -> str:
        """返回用户邮箱"""


class IUserinfoSetter(ABC):
    """用户信息更新器接口"""    
    @abstractmethod
    def init(self, uid: int):
        """初始化对象，设置uid"""

    @abstractmethod
    def set(self, username: str, email: str):
        """设置用户名及邮箱"""


class ITokenGetter(ABC):
    """Token获取接口"""
    @abstractmethod
    def get(self, token: str) -> int:
        """获取token对应的uid"""


class ITokenSaver(ABC):
    """Token保存接口"""
    @abstractmethod
    def save(self, token: str, uid: int, token_age: int):
        """保存token"""


class ISqlUserinfoGetter(IContextManager):
    """数据库用户信息获取接口"""
    @abstractmethod
    def get(self, uid: int):
        """获取用户信息"""

    @property
    @abstractmethod
    def username(self) -> str:
        """用户名"""

    @property
    @abstractmethod
    def email(self) -> str:
        """邮箱"""


class ISqlUserinfoUpdater(IContextManager):
    """数据库用户信息更新器接口"""
    @abstractmethod
    def set(self, uid: int, username: str, email: str):
        """设置用户名及邮箱"""


class ISqlTokenGetter(IContextManager):
    """数据库token获取接口"""
    @abstractmethod
    def get(self, token: str):
        """获取uid及exp"""

    @property
    @abstractmethod
    def uid(self) -> int:
        """获取uid"""

    @property
    @abstractmethod
    def exp(self) -> int:
        """获取token过期时间"""


class ISqlTokenSaver(IContextManager):
    """数据库token保存接口"""
    @abstractmethod
    def save(self, token: str, uid: int, exp: int):
        """保存token"""
