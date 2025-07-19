from typing import override
from httpx import AsyncClient
from gitlab import Gitlab
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
from ..core.config import settings
from ..errors.auth import *
import time, gitlab.exceptions


class GitlabTokenGetter(IGitlabTokenGetter):
    """获取token"""
    _token: str
    _token_age: int

    @override
    async def get_token(self, code: str):
        """获取token"""
        async with AsyncClient() as client:
            token_resp = await client.post(
                settings.gitlab_url + "/oauth/token",
                data={
                    "client_id": settings.gitlab_client_id,
                    "client_secret": settings.gitlab_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.gitlab_oauth_redirect_url
                }
            )
        if token_resp.status_code != 200:
            raise InvalidGitlabOauthCode(info=token_resp.text)
        token_info = token_resp.json()
        self._token = token_info["access_token"]
        self._token_age = token_info["expires_in"]

    @property
    @override
    def token(self) -> str:
        return self._token

    @property
    @override
    def token_age(self) -> int:
        return self._token_age


class GitlabUserinfoGetter(IGitlabUserinfoGetter):
    """获取新用户的Gitlab信息"""
    gl: Gitlab

    def __init__(self, gl: Gitlab):
        self.gl = gl

    @override
    async def get(self, token: str):
        """获取用户信息"""
        self.gl.oauth_token = token
        self.gl._set_auth_info()
        try:
            self.gl.auth()
        except gitlab.exceptions.GitlabAuthenticationError as e:
            raise InvalidGitlabToken from e

    @property
    @override
    def uid(self):
        if not self.gl.user:
            raise SyntaxError("请先调用 get 方法")
        return self.gl.user.id

    @property
    @override
    def username(self):
        if not self.gl.user:
            raise SyntaxError("请先调用 get 方法")
        return self.gl.user.username

    @property
    @override
    def email(self):
        if not self.gl.user:
            raise SyntaxError("请先调用 get 方法")
        return self.gl.user.email


class UserinfoGetter(IUserinfoGetter):
    sql_userinfo_getter: ISqlUserinfoGetter
    _username: str
    _email: str

    def __init__(self, sql_userinfo_getter: ISqlUserinfoGetter):
        self.sql_userinfo_getter = sql_userinfo_getter

    @override
    def get(self, uid: int):
        self.sql_userinfo_getter.get(uid)
        self._username = self.sql_userinfo_getter.username
        self._email = self.sql_userinfo_getter.email

    @property
    @override
    def username(self) -> str:
        if not hasattr(self, "_username"):
            raise SyntaxError('请先调用 get 方法')
        return self._username

    @property
    @override
    def email(self) -> str:
        if not hasattr(self, "_email"):
            raise SyntaxError('请先调用 get 方法')
        return self._email


class UserinfoSetter(IUserinfoSetter):
    sql_userinfo_updater: ISqlUserinfoUpdater
    uid: int    # 用户id

    def __init__(self, sql_userinfo_updater: ISqlUserinfoUpdater):
        self.sql_userinfo_updater = sql_userinfo_updater

    @override
    def init(self, uid:int):
        self.uid = uid

    @override
    def set(self, username: str, email: str):
        if not hasattr(self, 'uid'):
            raise SyntaxError("请先初始化")
        with self.sql_userinfo_updater:
            self.sql_userinfo_updater.set(self.uid, username, email)


class TokenGetter(ITokenGetter):
    sql_token_getter: ISqlTokenGetter

    def __init__(self, sql_token_getter: ISqlTokenGetter):
        self.sql_token_getter = sql_token_getter

    @override
    def get(self, token: str) -> int:
        self.sql_token_getter.get(token)
        if time.time() > self.sql_token_getter.exp:
            raise InvalidGitlabToken
        return self.sql_token_getter.uid


class TokenSaver(ITokenSaver):
    sql_token_saver: ISqlTokenSaver

    def __init__(self, sql_token_manager: ISqlTokenSaver):
        self.sql_token_saver = sql_token_manager

    @override
    def save(self, token: str, uid: int, token_age: int):
        exp = int(time.time()) + token_age
        with self.sql_token_saver:
            self.sql_token_saver.save(token, uid, exp)
