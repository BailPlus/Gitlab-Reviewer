from abc import ABC, abstractmethod
from httpx import Client
from ..sdk import email as sdk_email
from ..model.notification_settings import NotificationSettings
from ..schema.notifications import NotificationSettings as NotificationSettingsSchema
from ..db import notifications as db
from ..core.config import settings
from .commits import RiskLevel
import json

__all__ = [
    "NotifyMethod",
    "get_notification_settings",
    "update_notification_settings",
    "create_default_notification_settings",
]


class NotifyMethod(ABC):
    @staticmethod
    @abstractmethod
    def send(repo_id: int, review_json: str):
        """发送通知"""

    @classmethod
    def send_all(cls, repo_id: int, review_json: str):
        for method in cls.__subclasses__():
            method.send(repo_id, review_json)


class EmailNotifyMethod(NotifyMethod):
    @staticmethod
    def send(repo_id: int, review_json: str):
        if not settings.enable_email:
            return
        review_dict = json.loads(review_json)
        dests = db.get_notification_emails(repo_id, review_dict['level'])
        if not dests:
            return
        sdk_email.send(
            to=dests,
            level=RiskLevel.from_int(review_dict['level']).name,
            message=review_dict['info']
        )


class WebhookMethod(NotifyMethod):
    @staticmethod
    def send(repo_id: int, review_json: str):
        level = json.loads(review_json)['level']
        notification_webhooks = db.get_notification_webhooks(repo_id, level)
        with Client() as client:
            for user in notification_webhooks:
                assert user.webhook_secret and user.webhook_url
                client.post(
                    user.webhook_url,
                    headers={
                        "X-Webhook-Secret": user.webhook_secret
                    },
                    json={
                        "repo_id": repo_id,
                        "review_json": review_json,
                    }
                )


def get_notification_settings(user_id: int) -> NotificationSettings:
    return db.get_notification_settings(user_id)


def update_notification_settings(user_id: int, settings: NotificationSettingsSchema):
    model = NotificationSettings(
        user_id=user_id,
        notify_level=settings.notify_level,
        email_enabled=settings.email.enabled,
        webhook_enabled=settings.webhook.enabled,
        webhook_url=settings.webhook.url,
        webhook_secret=settings.webhook.secret
    )
    db.update_notification_settings(model)


def create_default_notification_settings(user_id: int):
    model = NotificationSettings(user_id=user_id)
    db.update_notification_settings(model)
