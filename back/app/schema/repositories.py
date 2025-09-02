from pydantic import BaseModel, Field


class GetRepositoriesOutput(BaseModel):
    """获取用户绑定仓库列表的单个仓库输出"""
    id: int = Field(description="仓库id")
    analysis_id: int = Field(description="仓库对应的分析id")


class AddRepositoryInput(BaseModel):
    """绑定新仓库输入"""
    repo_id: int = Field(description="待绑定的仓库id")
