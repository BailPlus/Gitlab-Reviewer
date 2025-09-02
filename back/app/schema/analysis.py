from typing import Optional
from pydantic import BaseModel, Field


class PostAnalysisInput(BaseModel):
    """ 提交分析的输入参数"""
    repo_id: int = Field(description="待分析的仓库id")
    branch: Optional[str] = Field(default=None, description="待分析的分支，为空则分析默认分支")


class GetAnalysisOutput(BaseModel):
    """获取分析结果输出参数"""
    result: str = Field(description="分析结果")
    score: float = Field(description="分析得分")
    analyze_time: int = Field(description="分析时间戳")


class GetAnalysisHistoryOutput(BaseModel):
    """获取分析历史输入参数"""
    analysis_history: list[int] = Field(description="历史分析id，按照时间逆序排列")
