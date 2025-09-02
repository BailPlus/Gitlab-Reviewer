from sqlmodel import SQLModel, Field
from typing import Optional
from . import TimestampMixin


class NotificationSettings(SQLModel, TimestampMixin, table=True):
    __tablename__ = "notification_settings" # pyright: ignore[reportAssignmentType]
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id", ondelete="CASCADE", unique=True)
    notify_level: int = Field(default=0, description="通知级别")
    email_enabled: bool = Field(default=False, description="是否通过邮件通知")
    webhook_enabled: bool = Field(default=False, description="是否通过webhook通知")
    webhook_url: Optional[str] = Field(default=None, description="webhook地址")
    webhook_secret: Optional[str] = Field(default=None, description="webhook防伪密钥")
