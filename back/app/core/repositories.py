from fastapi import Depends
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoDeleter
)
from ..service.repositories import (
    RepoGetter,
    RepoAdder,
    RepoDeleter
)
from ..db import engine
from ..db.repositories import (
    SqlRepoGetter,
    SqlUserRepoGetter,
    SqlRepoAdder,
    SqlRepoDeleter
)


def get_sql_repo_getter() -> ISqlRepoGetter:
    return SqlRepoGetter(engine)

def get_sql_userrepo_getter() -> ISqlUserRepoGetter:
    return SqlUserRepoGetter(engine)

def get_sql_repo_adder() -> ISqlRepoAdder:
    return SqlRepoAdder(engine)

def get_sql_repo_deleter() -> ISqlRepoDeleter:
    return SqlRepoDeleter(engine)

def get_repo_getter(
    sql_userrepo_getter: ISqlUserRepoGetter = Depends(get_sql_userrepo_getter)
) -> IRepoGetter:
    return RepoGetter(sql_userrepo_getter)

def get_repo_adder(
    sql_repo_adder: ISqlRepoAdder = Depends(get_sql_repo_adder)
) -> IRepoAdder:
    return RepoAdder(sql_repo_adder)

def get_repo_deleter(
    sql_repo_getter: ISqlRepoGetter = Depends(get_sql_repo_getter),
    sql_repo_deleter: ISqlRepoDeleter = Depends(get_sql_repo_deleter)
) -> IRepoDeleter:
    return RepoDeleter(sql_repo_getter, sql_repo_deleter)
