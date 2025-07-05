from . import GitlabReviewerException


class RepoException(GitlabReviewerException):
    code = 500
    status = 2
    info = "仓库相关异常"

class RepoNotExist(RepoException):
    code = 404
    status = 201
    info = "仓库不存在"
