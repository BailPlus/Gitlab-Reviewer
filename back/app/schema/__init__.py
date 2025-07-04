from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseOutput(BaseModel, Generic[T]):
    status: int = Field(0, description="应用内状态码")
    info: str = Field("ok", description="状态信息")
    data: T
