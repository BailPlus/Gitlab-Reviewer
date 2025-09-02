from pydantic import BaseModel, Field


class MrReviewOutput(BaseModel):
    """merge_request评审结果"""
    review: str = Field(description="merge_request评审结果")
    created_at: int = Field(description="创建时间")
