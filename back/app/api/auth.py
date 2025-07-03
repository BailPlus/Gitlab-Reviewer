from typing import Annotated
from fastapi import APIRouter, Response, Depends, Cookie
from fastapi.responses import RedirectResponse
from ..schema import auth as models
from ..schema.cookies import CookiesSchema
from ..service.auth import GitlabTokenGetter, GitlabUserinfoGetter
from ..core.config import settings

router = APIRouter(prefix='/_/auth')


@router.get('/login')
async def login():
    """登录"""
    return RedirectResponse(url=settings.gitlab_url + '/oauth/authorize?client_id=' + settings.gitlab_appid + '&redirect_uri=' + settings.gitlab_oauth_redirect_url + '&response_type=code&scope=api')


@router.get('/callback', response_model=models.LoginOutput)
async def login_callback(
    code: str,
    response: Response,
    gitlab_token_getter: GitlabTokenGetter = Depends(GitlabTokenGetter, use_cache=False)
):
    """回调"""
    await gitlab_token_getter.get_token(code)
    response.set_cookie(
        key='token',
        value=gitlab_token_getter.token,
        max_age=gitlab_token_getter.token_age,
        samesite='strict'
    )
    return models.LoginOutput()


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie('token')
    return RedirectResponse(url='/login')


@router.get('/profile', response_model=models.ProfileOutput)
async def profile(
    cookies: Annotated[CookiesSchema, Cookie()],
    gitlab_userinfo_getter: GitlabUserinfoGetter = Depends(GitlabUserinfoGetter,use_cache=False)):
    token = cookies.token
    await gitlab_userinfo_getter.get_userinfo(token)
    return models.ProfileOutput(
        data=models.PartialProfileOutput(
            username=gitlab_userinfo_getter.username,
            email=gitlab_userinfo_getter.email
        )
    )
