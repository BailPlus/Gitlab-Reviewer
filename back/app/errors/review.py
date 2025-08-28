from . import GitlabReviewerException


class ReviewException(GitlabReviewerException):
    code = 500
    status = 6
    info = "评审相关异常"


class PendingReview(ReviewException):
    code = 202
    status = 601
    info = "评审正在进行中"


class FailedReview(ReviewException):
    code = 500
    status = 602
    info = "评审失败"


class ReviewNotExist(ReviewException):
    code = 404
    status = 603
    info = "评审不存在"
