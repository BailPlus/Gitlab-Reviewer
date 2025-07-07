from pydantic_settings import BaseSettings
from gitlab import Gitlab

class Settings(BaseSettings):
    database_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    gitlab_url: str = ""
    gitlab_oauth_redirect_url: str = ""
    gitlab_client_id: str = ""
    gitlab_client_secret: str = ""

    class Config:
        env_file = ".env"   # 配置文件
        env_prefix = "GLRV_"    # 环境变量前缀


settings = Settings()

def get_gitlab_obj() -> Gitlab:
    """获取Gitlab实例"""
    return Gitlab(settings.gitlab_url)
