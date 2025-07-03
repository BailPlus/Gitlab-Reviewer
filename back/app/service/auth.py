from typing import override
from httpx import AsyncClient
from ..interface.auth import (
    GitlabTokenGetter as _GitlabTokenGetter,
    GitlabUserinfoGetter as _GitlabUserinfoGetter
)
from ..core.config import settings

class GitlabTokenGetter(_GitlabTokenGetter):
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
                    "client_id": settings.gitlab_appid,
                    "client_secret": settings.gitlab_appsecret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.gitlab_oauth_redirect_url
                }
            )
        token_info = token_resp.raise_for_status().json()
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


class GitlabUserinfoGetter(_GitlabUserinfoGetter):
    _username: str
    _email: str

    @override
    async def get_userinfo(self, token: str):
        async with AsyncClient() as client:
            userinfo_resp = await client.get(
                url=f"{settings.gitlab_url+'/api/v4/user'}",
                headers={"Authorization": f"Bearer {token}"}
            )
        userinfo = userinfo_resp.raise_for_status().json()
        self._username = userinfo["username"]
        self._email = userinfo["email"]
    
    @property
    @override
    def username(self):
        return self._username
    
    @property
    @override
    def email(self):
        return self._email
