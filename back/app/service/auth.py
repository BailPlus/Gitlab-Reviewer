from httpx import AsyncClient
from gitlab import Gitlab
from fastapi import Request
from ..errors.auth import *
from ..core.config import settings
from ..schema.auth import GitlabToken
from ..model.tokens import Token
from ..errors.auth import InvalidGitlabToken
from ..db import auth as db
from . import repositories, notifications
import time, gitlab.exceptions

__all__ = [
    'get_token_from_callback_code',
    'verify_gitlab_token',
    'get_root_gitlab_obj',
    'login',
    'logout',
    'get_token_from_cookie',
    'check_repo_permission'
]


async def get_token_from_callback_code(code: str) -> GitlabToken:
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
    return GitlabToken(
        token = token_info["access_token"],
        token_age = token_info["expires_in"]
    )


def verify_gitlab_token(token: str) -> Gitlab:
    gl = Gitlab(settings.gitlab_url, oauth_token=token)
    try:
        gl.auth()
    except gitlab.exceptions.GitlabAuthenticationError as e:
        raise InvalidGitlabToken from e
    return gl


def get_root_gitlab_obj() -> Gitlab:
    root_token = settings.gitlab_root_private_token
    gl = Gitlab(settings.gitlab_url, private_token=root_token)
    try:
        gl.auth()
    except gitlab.exceptions.GitlabAuthenticationError as e:
        raise InvalidGitlabToken(info='gitlab root private token无效') from e
    return gl


async def login(code: str) -> Token:
    # 从gitlab获取token
    gl_token = await get_token_from_callback_code(code)
    gl = verify_gitlab_token(gl_token.token)

    # 从gitlab获取用户信息
    assert gl.user
    uid = gl.user.id # type: int
    username = gl.user.username
    email = gl.user.email

    # 向数据库更新用户信息
    registered = db.save_userinfo(uid, username, email)
    if not registered:
        notifications.create_default_notification_settings(uid)

    # 保存token到数据库
    exp = int(time.time()) + gl_token.token_age
    token_obj = db.save_token(gl_token.token, uid, exp)
    return token_obj


def delete_token_from_db(token: Token) -> None:
    db.delete_token(token)


def logout(token: Token):
    delete_token_from_db(token)


def get_token_obj_from_db(token: str) -> Token:
    return db.get_token_obj(token)


def get_token_from_cookie(request: Request) -> Token:
    token_str = request.cookies.get('token')
    if token_str is None:
        raise InvalidGitlabToken(info='未登录')
    token = get_token_obj_from_db(token_str)
    if token.is_expired:
        delete_token_from_db(token)
        raise InvalidGitlabToken(info='登录已过期')
    return token


def check_repo_permission(user_id: int, repo_id: int):
    """验证用户是否绑定analysis对应的仓库"""
    # XXX: 建议进行压测，在用户绑定的仓库数量很多时
    for repo in repositories.get_user_binded_repos(user_id):
        if repo.id == repo_id:
            break
    else:
        raise PermissionDenied
