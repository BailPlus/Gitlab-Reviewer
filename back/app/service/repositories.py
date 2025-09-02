from urllib.parse import urljoin
from . import auth, analysis
from ..model.repositories import Repository
from ..model.tokens import Token
from ..service import analysis
from ..db import repositories as db
from ..errors.auth import PermissionDenied
from ..errors.repositories import *
from ..core.config import settings
import gitlab.exceptions

__all__ = [
    'get_user_binded_repos',
    'bind_repo',
    'unbind_repo'
]


def get_user_binded_repos(user_id: int) -> list[Repository]:
    return db.get_user_binded_repos(user_id)


def bind_repo(token: Token, repo_id: int):
    # 验证仓库存在且有访问权限
    gl = auth.verify_gitlab_token(token.token)
    try:
        gl.projects.get(repo_id)
    except gitlab.exceptions.GitlabGetError as e:
        raise RepoNotExist from e

    # 检查仓库是否被该用户绑定过
    for repo in get_user_binded_repos(token.user.id):
        if repo.id == repo_id:
            raise RepoAlreadyBinded

    # 添加仓库
    try:
        repo = _get_repo_by_id(repo_id)
    except RepoNotExist:
        webhook_id = _create_repo_webhook(token, repo_id)
        repo = Repository(
            id=repo_id,
            webhook_id=webhook_id,
        )
        _add_repo_into_db(repo)
    _bind_repo_with_user(repo.id, token.user.id)

    # 进行分析
    analysis.analyze(token, repo_id)


def unbind_repo(token: Token, repo_id: int):
    for repo in get_user_binded_repos(token.user_id):
        if repo.id == repo_id:
            break
    else:
        raise PermissionDenied(info='这不是你的仓库')
    is_to_delete = db.unbind(token.user_id, repo_id)
    if is_to_delete:    # 删除webhook
        gl = auth.verify_gitlab_token(token.token)
        try:    # 防止提前手动删除后出现bug
            gl.projects.get(repo_id).hooks.delete(repo.webhook_id)  # XXX: 可能会报不存在的orm对象
        except Exception:
            pass


def _get_repo_by_id(repo_id: int) -> Repository:
    return db.get_repo_by_id(repo_id)


def _add_repo_into_db(repo: Repository):
    db.add_repo_into_db(repo)


def _bind_repo_with_user(repo_id: int, user_id: int):
    db.bind_repo_with_user(repo_id, user_id)


def _create_repo_webhook(token: Token, repo_id: int) -> int:
    webhook_id = auth.verify_gitlab_token(token.token).projects.get(repo_id).hooks.create({
        'url': urljoin(settings.self_url, '/api/webhooks/gitlab'),
        'push_events': True,
        'merge_requests_events': True,
        'pipeline_events': True,
        'token': settings.gitlab_webhook_token
    }).get_id()
    assert isinstance(webhook_id, int)
    return webhook_id
