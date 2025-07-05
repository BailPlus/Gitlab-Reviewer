from fastapi import Depends
from ..interface.repositories import (
    IRepoGetter,
    IRepoAdder,
    IRepoDeleter,
    ISqlUserRepoGetter,
    ISqlRepoAdder,
    ISqlRepoDeleter
)
from ..service.repositories import (
    RepoGetter,
    RepoAdder,
    RepoDeleter
)
from ..db import engine


