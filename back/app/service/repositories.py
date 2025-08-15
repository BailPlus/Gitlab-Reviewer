from . import auth
from ..model.repositories import Repository
from ..model.tokens import Token
from ..service import analysis
from ..db import repositories as db
from ..errors.auth import PermissionDenied
from ..errors.repositories import *
import gitlab.exceptions

__all__ = [
    'get_user_binded_repos',
    'bind_repo',
    'unbind_repo'
]


def get_user_binded_repos(user_id: int) -> list[Repository]:
    return db.get_user_binded_repos(user_id)


def get_repo_by_id(repo_id: int) -> Repository:
    return db.get_repo_by_id(repo_id)


def add_repo_into_db(repo: Repository):
    db.add_repo_into_db(repo)


def bind_repo_with_user(repo_id: int, user_id: int):
    db.bind_repo_with_user(repo_id, user_id)


def bind_repo(token: Token, repo_name: str):
    # 获取仓库id
    gl = auth.verify_gitlab_token(token.token)
    try:
        repo_id = gl.projects.get(repo_name).id
    except gitlab.exceptions.GitlabGetError as e:
        raise RepoNotExist from e

    # 检查仓库是否绑定过
    for repo in get_user_binded_repos(token.user.id):
        if repo.id == repo_id:
            raise RepoAlreadyBinded

    # 添加仓库
    try:
        repo = get_repo_by_id(repo_id)
    except RepoNotExist:
        repo = Repository(id=repo_id)
        add_repo_into_db(repo)
        # TODO # analysis.create_analysis(repo_id)
    bind_repo_with_user(repo.id, token.user.id)

    # 创建分析线程并定义回调。等待AI组提供RepoAnalizer
    '''        
    analizer = get_repo_analyzer(repo_id)   # 在core.analysis中定义这个工厂函数，用于创建RepoAnalizer对象
    @analizer.ondone
    def callback(result: str):
        sql_repo_analysis_setter.set(repo_id, result)
    @analizer.onfail
    def callback_fail(result: str):
        sql_repo_analysis_setter.set_failed(repo_id)
    Thread(target=analizer.analyze).start()
    '''


def unbind_repo(user_id: int, repo_id: int):
    for repo in get_user_binded_repos(user_id):
        if repo.id == repo_id:
            break
    else:
        raise PermissionDenied(info='这不是你的仓库')
    db.unbind(user_id, repo_id)
