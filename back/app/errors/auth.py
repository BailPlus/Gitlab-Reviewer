from . import GitlabReviewerException

class AuthException(GitlabReviewerException):
    code = 500
    status = 1
    info = "认证异常"

class InvalidGitlabOauthCode(AuthException):
    code = 400
    status = 101
    info = "无效的gitlab oauth code"

class InvalidGitlabToken(AuthException):
    code = 401
    status = 102
    info = "无效的gitlab token"

class PermissionDenied(AuthException):
    code = 403
    status = 103
    info = "权限不足"

class InvalidGitlabWebhookToken(AuthException):
    code = 401
    status = 104
    info = "无效的gitlab webhook token"
