from typing import override
from sqlmodel import select
from ..model.repositories import Repositories
from ..interface.repositories import (
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoDeleter
)
from . import SqlContextManager
from ..errors.repositories import *


class SqlRepoGetter(SqlContextManager, ISqlRepoGetter):
    @override
    def get(self, id: int) -> Repositories:
        if not (repo := self.session.get(Repositories, id)):
            raise RepoNotExist
        return repo


class SqlUserRepoGetter(SqlContextManager, ISqlUserRepoGetter):
    @override
    def get(self, user_id: int) -> list[Repositories]:
        return list(self.session.exec(
            select(Repositories)\
                .where(Repositories.user_id == user_id)
        ).all())


class SqlRepoAdder(SqlContextManager, ISqlRepoAdder):
    @override
    def add(self, user_id: int, repo_id: int, name: str) -> None:
        self.session.add(Repositories(
            id=repo_id,
            user_id=user_id,
            name=name,
        ))
        self.session.commit()


class SqlRepoDeleter(SqlContextManager, ISqlRepoDeleter):
    @override
    def delete(self, repo_id: int) -> None:
        self.session.delete(
            self.session.get(Repositories, repo_id)
        )
        self.session.commit()
