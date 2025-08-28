from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from . import TimestampMixin


class WebhookLog(TimestampMixin, SQLModel, table=True):
    __tablename__ = "webhook_logs" # pyright: ignore[reportAssignmentType]
    id: int = Field(default=None, primary_key=True)
    data: str = Field(sa_column=Column(Text), description='收到的webhook数据')
