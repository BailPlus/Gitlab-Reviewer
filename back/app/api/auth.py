from typing import Annotated
from fastapi import APIRouter, Response, Depends, Cookie
from fastapi.responses import RedirectResponse
from ..schema import BaseOutput, auth as auth_models
from ..schema.cookies import CookiesSchema
from ..interface.auth import (
    IGitlabTokenGetter,
    IGitlabUserinfoGetter,
    IUserinfoGetter,
    IUserinfoSetter,
    ITokenGetter,
    ITokenSaver
)
from ..core.config import settings
from ..core.auth import (
    get_gitlab_token_getter,
    get_gitlab_userinfo_getter,
    get_userinfo_getter,
    get_userinfo_updater,
    get_token_getter,
    get_token_saver
)

router = APIRouter(prefix='/_/auth')


@router.get('/login')
async def login():
    """登录"""
    return RedirectResponse(url=settings.gitlab_url + '/oauth/authorize?client_id=' + settings.gitlab_client_id + '&redirect_uri=' + settings.gitlab_oauth_redirect_url + '&response_type=code&scope=api')


@router.get('/callback')
async def login_callback(
    code: str,
    gitlab_token_getter: IGitlabTokenGetter = Depends(get_gitlab_token_getter, use_cache=False),
    gitlab_userinfo_getter: IGitlabUserinfoGetter = Depends(get_gitlab_userinfo_getter, use_cache=False),
    gitlab_userinfo_updater: IUserinfoSetter = Depends(get_userinfo_updater, use_cache=False),
    token_saver: ITokenSaver = Depends(get_token_saver, use_cache=False),
):
    """回调"""
    # 获取token
    await gitlab_token_getter.get_token(code)
    # 获取并更新用户信息
    await gitlab_userinfo_getter.get(gitlab_token_getter.token)
    gitlab_userinfo_updater.init(gitlab_userinfo_getter.uid)
    gitlab_userinfo_updater.set(
        username=gitlab_userinfo_getter.username,
        email=gitlab_userinfo_getter.email
    )
    token_saver.save(
        token=gitlab_token_getter.token,
        uid=gitlab_userinfo_getter.uid,
        token_age=gitlab_token_getter.token_age
    )
    response = RedirectResponse(url='/')
    response.set_cookie(
        key='token',
        value=gitlab_token_getter.token,
        max_age=gitlab_token_getter.token_age,
        samesite='strict'
    )
    return response


@router.post('/logout')
async def logout(response: Response):
    """登出"""
    response.delete_cookie('token')
    return RedirectResponse(url='/login')


@router.get('/profile',response_model=BaseOutput[auth_models.ProfileOutput])
async def profile(
    cookies: Annotated[CookiesSchema, Cookie()],
    token_getter: ITokenGetter = Depends(get_token_getter,use_cache=False),
    userinfo_getter: IUserinfoGetter = Depends(get_userinfo_getter,use_cache=False)
):
    """获取用户信息"""
    token = cookies.token
    uid = token_getter.get(token)
    userinfo_getter.get(uid)
    response = auth_models.ProfileOutput(
        username=userinfo_getter.username,
        email=userinfo_getter.email
    )
    return BaseOutput(data=response) # pyright: ignore[reportCallIssue]
