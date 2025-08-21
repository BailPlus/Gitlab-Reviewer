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


def save_userinfo(uid: int, username: str, email: str):
    session = get_session()
    if user := session.get(User, uid):
        user.username = username
        user.email = email
        session.add(user)
    else:
        session.add(User(
            id=uid,
            username=username,
            email=email
        ))
    session.commit()


def get_token_obj(token: str) -> Token:
    with get_session() as session:
        token_obj = session.get(Token, token)
        token_obj and token_obj.user # pyright: ignore[reportUnusedExpression]
    if token_obj is None:
        raise InvalidGitlabToken
    return token_obj


def save_token(token: str, uid: int, exp: int):
    session = get_session()
    assert (user_obj := session.get(User, uid))
    token_obj = Token(
        token=token,
        user=user_obj,
        exp=exp
    ) # pyright: ignore[reportCallIssue]
    session.add(token_obj)
    session.commit()
    session.refresh(token_obj)
    session.close()
    return token_obj


def delete_token(token: Token):
    session = get_session()
    token = session.merge(token)
    session.delete(token)
    session.commit()
    session.close()
