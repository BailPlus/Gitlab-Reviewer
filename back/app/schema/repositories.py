from pydantic import BaseModel


class GetRepositoriesOutput(BaseModel):
    """获取用户绑定仓库列表的单个仓库输出"""
    id: int
    name: str


class AddRepositoryInput(BaseModel):
    """绑定新仓库输入"""
    repo_name: str


class AddRepositoryOutput(BaseModel):
    """绑定新仓库输出"""
    pass


class DeleteRepositoryOutput(BaseModel):
    """解绑仓库输出"""
    pass
