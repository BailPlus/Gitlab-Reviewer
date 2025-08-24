from sqlmodel import SQLModel, create_engine, Session
from ..core.config import settings
# 以下导入仅用于SQLModel.metadata.create_all(engine)时检测到所有的表
from ..model.users import User
from ..model.tokens import Token
from ..model.repositories import Repository
from ..model.repository_bindings import RepositoryBinding
from ..model.repository_analyses import RepositoryAnalysis
from ..model.repository_metrics import RepositoryMetric
from ..model.commit_reviews import CommitReview
from ..model.commit_review_bindings import CommitReviewBinding

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)
SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)


__all__ = ["get_session"]
