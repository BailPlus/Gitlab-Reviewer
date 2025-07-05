from fastapi import Depends
from gitlab import Gitlab
from .auth import get_logged_gitlab_obj
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlRepoGetter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoBinder,
    ISqlRepoAnalysisSetter,
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
    SqlRepoBinder,
    SqlRepoAnalysisSetter,
    SqlRepoDeleter
)


def get_sql_repo_getter() -> ISqlRepoGetter:
    return SqlRepoGetter(engine)

def get_sql_userrepo_getter() -> ISqlUserRepoGetter:
    return SqlUserRepoGetter(engine)

def get_sql_repo_adder() -> ISqlRepoAdder:
    return SqlRepoAdder(engine)

def get_sql_repo_binder() -> ISqlRepoBinder:
    return SqlRepoBinder(engine)

def get_sql_repo_analysis_setter() -> ISqlRepoAnalysisSetter:
    return SqlRepoAnalysisSetter(engine)

def get_sql_repo_deleter() -> ISqlRepoDeleter:
    return SqlRepoDeleter(engine)

def get_repo_getter(
    sql_userrepo_getter: ISqlUserRepoGetter = Depends(get_sql_userrepo_getter)
) -> IRepoGetter:
    return RepoGetter(sql_userrepo_getter)

def get_repo_adder(
    gl: Gitlab = Depends(get_logged_gitlab_obj),
    sql_repo_getter: ISqlRepoGetter = Depends(get_sql_repo_getter),
    sql_userrepo_getter: ISqlUserRepoGetter = Depends(get_sql_userrepo_getter),
    sql_repo_adder: ISqlRepoAdder = Depends(get_sql_repo_adder),
    sql_repo_binder: ISqlRepoBinder = Depends(get_sql_repo_binder),
    sql_repo_analysis_setter: ISqlRepoAnalysisSetter = Depends(get_sql_repo_analysis_setter)
) -> IRepoAdder:
    return RepoAdder(gl, sql_repo_getter, sql_userrepo_getter, sql_repo_adder, sql_repo_binder, sql_repo_analysis_setter)

def get_repo_deleter(
    sql_userrepo_getter: ISqlUserRepoGetter = Depends(get_sql_userrepo_getter),
    sql_repo_deleter: ISqlRepoDeleter = Depends(get_sql_repo_deleter)
) -> IRepoDeleter:
    return RepoDeleter(sql_userrepo_getter, sql_repo_deleter)
