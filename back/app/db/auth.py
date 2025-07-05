from typing import override
from sqlmodel import Session
from sqlalchemy import Engine
from ..model.users import Users
from ..model.tokens import Tokens
from ..interface.auth import (
    ISqlUserinfoGetter,
    ISqlUserinfoUpdater,
    ISqlTokenGetter,
    ISqlTokenSaver
)
from ..errors.auth import *
from . import SqlContextManager


class SqlUserinfoUpdater(ISqlUserinfoUpdater, SqlContextManager):
    session: Session

    def __init__(self, engine: Engine):
        self.session = Session(engine)

    @override
    def set(self, uid: int, username: str, email: str):
        if user := self.session.get(Users, uid):
            user.username = username
            user.email = email
            self.session.add(user)
        else:
            self.session.add(Users(
                id=uid,
                username=username,
                email=email
            ))
        self.session.commit()


class SqlTokenGetter(ISqlTokenGetter, SqlContextManager):
    session: Session
    _uid: int
    _exp: int

    def __init__(self, engine: Engine):
        self.session = Session(engine)

    @override
    def get(self, token: str):
        token_info = self.session.get(Tokens, token)
        if not token_info:
            raise InvalidGitlabToken
        self._uid = token_info.user_id
        self._exp = token_info.exp

    @property
    @override
    def uid(self) -> int:
        if not hasattr(self, "_uid"):
            raise SyntaxError("请先调用get方法")
        return self._uid

    @property
    @override
    def exp(self) -> int:
        if not hasattr(self, "_exp"):
            raise SyntaxError("请先调用get方法")
        return self._exp


class SqlUserinfoGetter(ISqlUserinfoGetter, SqlContextManager):
    session: Session
    _username: str
    _email: str

    def __init__(self, engine: Engine):
        self.session = Session(engine)

    @override
    def get(self, uid: int):
        userinfo = self.session.get(Users, uid)
        if not userinfo:
            raise InvalidGitlabToken(info='我们不知道出了什么问题：你的token是有效的，但是找不到你的用户信息')
        self._username = userinfo.username
        self._email = userinfo.email

    @property
    @override
    def username(self) -> str:
        if not hasattr(self, "_username"):
            raise SyntaxError('请先调用get方法')
        return self._username

    @property
    @override
    def email(self) -> str:
        if not hasattr(self, "_username"):
            raise SyntaxError('请先调用get方法')
        return self._email


class SqlTokenSaver(ISqlTokenSaver, SqlContextManager):
    session: Session

    def __init__(self, engine: Engine):
        self.session = Session(engine)

    @override
    def save(self, token: str, uid: int, exp: int):
        self.session.add(Tokens(
            token=token,
            user_id=uid,
            exp=exp
        ))
        self.session.commit()
