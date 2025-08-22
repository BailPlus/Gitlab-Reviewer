from . import GitlabReviewerException


class CommitsException(GitlabReviewerException):
    code = 500
    status = 4
    info = "commit评审相关异常"


class PendingReview(CommitsException):
    code = 202
    status = 401
    info = "commit评审正在进行中"


class FailedReview(CommitsException):
    code = 500
    status = 402
    info = "commit评审失败"


class ReviewNotExist(CommitsException):
    code = 404
    status = 403
    info = "commit评审不存在"
