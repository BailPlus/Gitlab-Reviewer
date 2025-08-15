from sqlmodel import select, and_
from ..model.repositories import Repository
from ..model.repository_bindings import RepositoryBinding
from ..model.users import User
from ..errors.repositories import *
from . import get_session

__all__ = [
    'get_repo_by_id',
    'get_user_binded_repos',
    'add_repo_into_db',
    'bind_repo_with_user',
    'unbind'
]


def get_repo_by_id(repo_id: int) -> Repository:
    repo = get_session().get(Repository, repo_id)
    if repo is None:
        raise RepoNotExist
    return repo


def get_user_binded_repos(user_id: int) -> list[Repository]:
    return list(get_session().exec(
        select(Repository)
        .join(RepositoryBinding, and_(RepositoryBinding.repo_id == Repository.id))
        .where(RepositoryBinding.user_id == user_id)
    ).all())


def add_repo_into_db(repo: Repository):
    with get_session() as session:
        session.add(repo)
        session.commit()
        session.refresh(repo)
    

def bind_repo_with_user(repo_id: int, user_id: int):
    with get_session() as session:
        session.add(RepositoryBinding(
            repo_id=repo_id,
            user_id=user_id
        ))
        session.commit()


def unbind(user_id: int, repo_id: int):
    with get_session() as session:
        bind = session.exec(
            select(RepositoryBinding)
            .where(and_(
                RepositoryBinding.repo_id == repo_id,
                RepositoryBinding.user_id == user_id
            ))
        ).first()

        # 删除仓库绑定对象
        session.delete(bind)
        session.commit()

        # 检查仓库绑定计数，如果为0，则删除仓库
        remain_binds = session.exec(
            select(RepositoryBinding)
            .where(RepositoryBinding.repo_id == repo_id)
        ).all()
        if not remain_binds:
            repo = session.get(Repository, repo_id)
            if repo is not None:
                session.delete(repo)
                session.commit()
