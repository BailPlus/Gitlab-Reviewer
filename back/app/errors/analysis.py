from.import GitlabReviewerException


class AnanysisException(GitlabReviewerException):
    code = 500
    status = 3
    info = "仓库分析相关异常"


class PendingAnalysis(AnanysisException):
    code = 202
    status = 301
    info = "项目正在分析中"


class FailedAnalysis(AnanysisException):
    code = 500
    status = 302
    info = "项目分析失败"


class AnalysisNotExist(AnanysisException):
    code = 404
    status = 303
    info = "项目分析不存在"
