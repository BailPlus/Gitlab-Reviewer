from fastapi import Depends
from ..interface.auth import (
    IGitlabTokenGetter,
    IGitlabUserinfoGetter,
    IUserinfoGetter,
    IUserinfoSetter,
    ITokenGetter,
    ITokenSaver,
    ISqlUserinfoGetter,
    ISqlUserinfoUpdater,
    ISqlTokenGetter,
    ISqlTokenSaver
)
from ..service.auth import (
    GitlabTokenGetter,
    GitlabUserinfoGetter,
    UserinfoGetter,
    UserinfoSetter,
    TokenGetter,
    TokenSaver
)
from ..db import engine
from ..db.auth import (
    SqlUserinfoGetter,
    SqlUserinfoUpdater,
    SqlTokenGetter,
    SqlTokenSaver
)


def get_sql_userinfo_getter() -> ISqlUserinfoGetter:
    return SqlUserinfoGetter(engine)

def get_sql_userinfo_updater() -> ISqlUserinfoUpdater:
    return SqlUserinfoUpdater(engine)

def get_sql_token_getter() -> ISqlTokenGetter:
    return SqlTokenGetter(engine)

def get_sql_token_saver() -> ISqlTokenSaver:
    return SqlTokenSaver(engine)

def get_gitlab_token_getter() -> IGitlabTokenGetter:
    return GitlabTokenGetter()

def get_gitlab_userinfo_getter() -> IGitlabUserinfoGetter:
    return GitlabUserinfoGetter()

def get_userinfo_getter(
        sql_userinfo_getter: ISqlUserinfoGetter = Depends(get_sql_userinfo_getter)
) -> IUserinfoGetter:
    return UserinfoGetter(sql_userinfo_getter)

def get_userinfo_updater(
        sql_userinfo_updater: ISqlUserinfoUpdater = Depends(get_sql_userinfo_updater)
) -> IUserinfoSetter:
    return UserinfoSetter(sql_userinfo_updater)

def get_token_getter(
        sql_token_manager: ISqlTokenGetter = Depends(get_sql_token_getter)
) -> ITokenGetter:
    return TokenGetter(sql_token_manager)

def get_token_saver(
        sql_token_manager: ISqlTokenSaver = Depends(get_sql_token_saver)
) -> ITokenSaver:
    return TokenSaver(sql_token_manager)
