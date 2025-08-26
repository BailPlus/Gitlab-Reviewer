from enum import Enum
from pydantic_settings import BaseSettings
from gitlab import Gitlab


class SmtpEncryption(str, Enum):
    """SMTP加密方式"""
    NONE = "none"
    SSL = "ssl"
    STARTTLS = "starttls"


class Settings(BaseSettings):
    database_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    gitlab_url: str = ""
    gitlab_oauth_redirect_url: str = ""
    gitlab_client_id: str = ""
    gitlab_client_secret: str = ""
    gitlab_webhook_token: str = ""  # webhook防伪token
    gitlab_root_private_token: str = "" # gitlab root用户token，用于获取所有项目的信息
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    enable_email: bool = False
    smtp_host: str = ""
    smtp_port: int = 25
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_encryption: SmtpEncryption = SmtpEncryption.NONE
    email_from: str = ""

    class Config:
        env_file = ".env"   # 配置文件
        env_prefix = "GLRV_"    # 环境变量前缀


def get_gitlab_obj() -> Gitlab:
    """获取Gitlab实例"""
    return Gitlab(settings.gitlab_url)


# 全局实例
settings = Settings()
