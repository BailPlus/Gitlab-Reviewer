from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, ForeignKey
from . import TimestampMixin


class RepositoryBinding(TimestampMixin, SQLModel, table=True):
    __tablename__ = "repository_bindings" # type: ignore
    id: int = Field(default=None, primary_key=True, description='仓库绑定记录id')
    user_id: int = Field(sa_column=Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    ), description='用户id')
    repo_id: int = Field(sa_column=Column(
        Integer,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False
    ), description='仓库id')
