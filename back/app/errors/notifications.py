from . import GitlabReviewerException

class NotificationException(GitlabReviewerException):
    code = 500
    status = 5
    info = "通知异常"

class InvalidNotificationSettings(NotificationException):
    code = 400
    status = 501
    info = "无效的通知设置"
