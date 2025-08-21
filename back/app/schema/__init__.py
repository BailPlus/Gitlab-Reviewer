from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseOutput(BaseModel, Generic[T]):
    status: int = Field(default=0, description="应用内状态码")
    info: str = Field(default="ok", description="状态信息")
    data: T = Field(description="返回数据")


class EmptyOutput(BaseOutput[None]):
    data: None = Field(default=None)
