from typing import Optional
from pydantic import Field
from ..schema import BaseOutput


class ExceptionDetails(BaseOutput[None]):
    """异常详情"""
    status: int = Field(default=-1, description="应用内状态码")
    info: str = Field(default="异常详情", description="状态信息")
    data: None = Field(default=None, description="数据")

class GitlabReviewerException(Exception):
    """代码评审异常基类"""
    code: int = 500
    status: int = -1
    info: str = "代码评审异常基类"
    details: ExceptionDetails

    def __init__(self,
                 code: Optional[int] = None,
                 status: Optional[int] = None,
                 info: Optional[str] = None):
        if code is not None:
            self.code = code
        if status is not None:
            self.status = status
        if info is not None:
            self.info = info
        self.details = ExceptionDetails(
            status=self.status,
            info=self.info,
            data=None
        )

    def __str__(self):
        return self.info
