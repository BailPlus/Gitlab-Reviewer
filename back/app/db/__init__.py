from typing import override
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import Engine
from ..core.config import settings
from ..interface import IContextManager
# 以下导入仅用于SQLModel.metadata.create_all(engine)时检测到所有的表
from ..model.users import User
from ..model.tokens import Token
from ..model.repositories import Repository
from ..model.repository_bindings import RepositoryBinding
from ..model.repository_analyses import RepositoryAnalysis

engine = create_engine(settings.database_url)
SQLModel.metadata.create_all(engine)


class SqlContextManager(IContextManager):
    session: Session

    def __init__(self, engine: Engine):
        self.session = Session(engine)

    @override
    def __enter__(self):
        return self

    @override
    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


def get_session() -> Session:
    return Session(engine)


__all__ = ["engine", "SqlContextManager", "get_session"]
