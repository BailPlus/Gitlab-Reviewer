from . import BaseOutput
from pydantic import BaseModel


class LoginOutput(BaseOutput):
    """登录回调输出"""
    data: BaseModel = type('',(BaseModel,),{})()

class PartialProfileOutput(BaseModel):
    """用户信息输出"""
    username: str
    email: str

class ProfileOutput(BaseOutput):
    """用户信息输出"""
    data: PartialProfileOutput
