from fastapi import APIRouter, Response, Request
from fastapi.responses import RedirectResponse
from ..schema import BaseOutput, auth as auth_models
from ..core.config import settings
from ..service.auth import (
    login,
    logout,
    get_token_from_cookie
)

router = APIRouter(prefix='/_/auth')


@router.get('/login')
async def login_redirect_to_gitlab():
    """登录"""
    return RedirectResponse(url=settings.gitlab_url + '/oauth/authorize?client_id=' + settings.gitlab_client_id + '&redirect_uri=' + settings.gitlab_oauth_redirect_url + '&response_type=code&scope=api')


@router.get('/callback')
async def login_callback(code: str):
    """回调"""
    token_obj = await login(code)
    response = RedirectResponse(url='/')
    response.set_cookie(
        key='token',
        value=token_obj.token,
        max_age=token_obj.exp,
        samesite='strict'
    )
    return response


@router.post('/logout')
async def logout_route(request: Request, response: Response):
    """登出"""
    token = get_token_from_cookie(request)
    logout(token)
    response.delete_cookie('token')
    return RedirectResponse(url='/login')


@router.get('/profile',response_model=BaseOutput[auth_models.ProfileOutput])
async def profile(request: Request):
    """获取用户信息"""
    token = get_token_from_cookie(request)
    return BaseOutput(data=auth_models.ProfileOutput(
        username=token.user.username,
        email=token.user.email
    ))
