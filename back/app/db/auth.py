from ..model.users import User
from ..model.tokens import Token
from ..errors.auth import *
from . import get_session

__all__ = [
    'save_userinfo',
    'save_token',
    'get_token_obj',
    'delete_token',
]


def save_userinfo(uid: int, username: str, email: str) -> bool:
    """返回值：是否注册过"""
    with get_session() as session:
        if user := session.get(User, uid):
            registered = True
            user.username = username
            user.email = email
            session.add(user)
        else:
            registered = False
            session.add(User(
                id=uid,
                username=username,
                email=email
            ))
        session.commit()
    return registered


def get_token_obj(token: str) -> Token:
    with get_session() as session:
        token_obj = session.get(Token, token)
        token_obj and token_obj.user # pyright: ignore[reportUnusedExpression]
    if token_obj is None:
        raise InvalidGitlabToken
    return token_obj


def save_token(token: str, uid: int, exp: int):
    with get_session() as session:
        assert session.get(User, uid)   # 确保用户存在
        token_obj = Token(
            token=token,
            user_id=uid,
            exp=exp
        )
        session.add(token_obj)
        session.commit()
        session.refresh(token_obj)
        session.close()
    return token_obj


def delete_token(token: Token):
    with get_session() as session:
        token = session.merge(token)    # 将model附加到session
        session.delete(token)
        session.commit()
        session.close()
