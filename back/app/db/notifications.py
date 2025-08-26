from sqlmodel import select, and_
from . import get_session
from ..model.notification_settings import NotificationSettings
from ..model.users import User
from ..model.repository_bindings import RepositoryBinding


def get_notification_settings(user_id: int) -> NotificationSettings:
    with get_session() as session:
        return session.exec(
            select(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
        ).one()
    

def update_notification_settings(model: NotificationSettings):
    user_id = model.user_id
    with get_session() as session:
        if (
            existing_model := session.exec(
                select(NotificationSettings)
                .filter_by(user_id = user_id)
            ).one_or_none() # 考虑到新注册用户可能会没有记录
        ) is not None:
            session.delete(existing_model)
            session.commit()
        session.add(model)
        session.commit()
        session.refresh(model)


def get_notification_emails(repo_id: int, level: int) -> list[str]:
    with get_session() as session:
        return list(session.exec(
            select(User.email)
            .join(RepositoryBinding, and_(User.id == RepositoryBinding.user_id))
            .join(NotificationSettings, and_(User.id == NotificationSettings.user_id))
            .where(RepositoryBinding.repo_id == repo_id)
            .where(level >= NotificationSettings.notify_level)
            .where(NotificationSettings.email_enabled == True)
        ).all())


def get_notification_webhooks(repo_id: int, level: int) -> list[NotificationSettings]:
    with get_session() as session:
        return list(session.exec(
            select(NotificationSettings)
            .join(RepositoryBinding, and_(NotificationSettings.user_id == RepositoryBinding.user_id))
            .where(RepositoryBinding.repo_id == repo_id)
            .where(level >= NotificationSettings.notify_level)
            .where(NotificationSettings.webhook_enabled == True)
        ).all())
