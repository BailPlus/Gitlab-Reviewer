from abc import ABC, abstractmethod

class GitlabTokenGetter(ABC):
    """gitlab token获取器接口"""
    @abstractmethod
    async def get_token(self, code: str):
        """获取token"""

    @property
    @abstractmethod
    def token(self):
        """返回token"""

    @property
    @abstractmethod
    def token_age(self):
        """返回token有效期"""


class GitlabUserinfoGetter(ABC):
    """gitlab用户信息获取器接口"""
    @abstractmethod
    async def get_userinfo(self, token: str):
        """获取用户信息"""

    @property
    @abstractmethod
    def username(self) -> str:
        """返回用户名"""
    
    @property
    @abstractmethod
    def email(self) -> str:
        """返回用户邮箱"""
