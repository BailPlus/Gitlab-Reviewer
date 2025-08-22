from pydantic import BaseModel, Field


class GetReviewOutput(BaseModel):
    review: str = Field(description="commit评审结果")
    created_at: int = Field(description="创建时间")
