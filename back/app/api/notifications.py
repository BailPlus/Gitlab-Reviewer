from fastapi import APIRouter, Request
from ..schema import BaseOutput, EmptyOutput
from ..schema.notifications import *
from ..service.auth import get_token_from_cookie
from ..service.notifications import *
from ..errors.notifications import *

router = APIRouter(prefix="/api/notifications")


@router.get("/settings", response_model=BaseOutput[NotificationSettings])
async def get_notification_settings_route(request: Request):
    token = get_token_from_cookie(request)
    settings = get_notification_settings(token.user.id)
    return BaseOutput(data=NotificationSettings(
        notify_level=settings.notify_level,
        email=EmailConfig(
            enabled=settings.email_enabled,
        ),
        webhook=WebhookConfig(
            enabled=settings.webhook_enabled,
            url=settings.webhook_url,
            secret=settings.webhook_secret,
        ),
    ))


@router.post("/settings", response_model=BaseOutput[NotificationSettings])
async def update_notification_settings_route(request: Request, user_input: NotificationSettings):
    token = get_token_from_cookie(request)
    if not 0 <= user_input.notify_level <= 3:
        raise InvalidNotificationSettings(info='非法通知级别')
    update_notification_settings(token.user.id, user_input)
    return BaseOutput(data=user_input)


# @router.post("/test", response_model=EmptyOutput)
# async def test_notification_settings_route(request: Request):
#     token = get_token_from_cookie(request)
#     test_notification_settings(token.user.id)   # XXX: 可能要做频率限制
#     return EmptyOutput()
