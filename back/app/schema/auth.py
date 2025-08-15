from pydantic import BaseModel, Field


class ProfileOutput(BaseModel):
    """用户信息输出"""
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱")


class GitlabToken(BaseModel):
    """Gitlab token
只在登录时使用，因为登录时还没有获取到用户id。
后续业务逻辑应当使用model.tokens.Token"""
    token: str = Field(description="token")
    token_age: int = Field(description="token有效期")
