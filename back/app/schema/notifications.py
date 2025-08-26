from typing import Optional
from pydantic import BaseModel, Field

__all__ = ["EmailConfig", "WebhookConfig", "NotificationSettings"]


class EmailConfig(BaseModel):
    enabled: bool = Field(description="是否启用邮件通知")


class WebhookConfig(BaseModel):
    enabled: bool = Field(description="是否启用webhook通知")
    url: Optional[str] = Field(description="webhook地址")
    secret: Optional[str] = Field(description="webhook防伪密钥")


class NotificationSettings(BaseModel):
    notify_level: int = Field(description="通知级别")
    email: EmailConfig = Field(description="邮件通知设置")
    webhook: WebhookConfig = Field(description="webhook通知设置")
