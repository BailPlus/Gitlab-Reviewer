from pydantic import BaseModel, Field


class ProfileOutput(BaseModel):
    """用户信息输出"""
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱")
