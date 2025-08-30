from threading import Thread
from ..db import merge_requests as db
from ..model import ReviewStatus
from ..model.tokens import Token
from ..model.mr_reviews import MrReview
from . import auth, notifications
from ..openai import openai
from ..errors.review import *
import json, logging, io

__all__ = [
    "handle_pipeline_event",
    "get_mr_review",
]
JOBS = {    # job name -> files
    'megalinter': ['megalinter-reports/copy-paste/html/jscpd-report.json'],
    'semgrep': ['semgrep.json'],
}


def handle_pipeline_event(data: dict):
    """从流水线中获取代码检查结果，并交给AI进行评析"""
    logging.info("收到流水线事件")

    # 获取流水线信息
    gl = auth.get_root_gitlab_obj()
    project = gl.projects.get(data['project']['id'])
    pipeline = project.pipelines.get(data['object_attributes']['id'])
    if pipeline.status not in ['success', 'failed']:
        logging.info("跳过未完成的流水线")
        return

    if (merge_requests := project.mergerequests.list(pipeline_id=pipeline.id)):
        mr_iid = merge_requests[0].iid
    else:
        logging.warning("没有找到对应的merge request")
        return
    jobs = pipeline.jobs.list()
    # 处理流水线结果
    job_results: dict[str, dict[str, str]] = {}
    for pipeline_job in jobs:
        if pipeline_job.name not in JOBS:
            logging.info(f'跳过未知的流水线任务：{pipeline_job.name}')
            continue
        logging.info(f"正在处理{pipeline_job.name}")
        job = project.jobs.get(pipeline_job.id)
        job_results[job.name] = {}
        for filename in JOBS[job.name]:
            logging.info(f"正在下载文件：{filename}")
            try:
                job_results[job.name][filename] = job.artifact(filename).decode()
            except Exception as e:
                logging.error(f"下载{filename}失败: {e}")
    logging.debug("流水线处理结果：")
    logging.debug(job_results)

    # 生成代码检查结果
    Thread(target=_review_thread, args=(project.id, mr_iid, job_results)).start()


def get_mr_review(token: Token, repo_id: int, merge_request_id: int) -> MrReview:
    auth.check_repo_permission(token.user.id, repo_id)
    review = db.get_mr_review(repo_id, merge_request_id)
    match review.status:
        case ReviewStatus.PENDING:
            raise PendingReview
        case ReviewStatus.FAILED:
            raise FailedReview
        case ReviewStatus.COMPLETED:
            return review


def _create_pending_review(repo_id: int, mr_iid: int) -> MrReview:
    return db.create_review(repo_id, mr_iid)


def _finish_review(review: MrReview, review_json: str):
    db.update_review(review, ReviewStatus.COMPLETED, review_json)


def _fail_review(review: MrReview):
    db.update_review(review, ReviewStatus.FAILED)


def _verify_review_json_validity(review_json: str):
    review_dict = json.loads(review_json)
    assert 'info' in review_dict and 'suggestion' in review_dict and 'level' in review_dict


def _review_thread(repo_id: int, mr_iid: int, pipeline_result: dict):
    review = _create_pending_review(repo_id, mr_iid)
    gl = auth.get_root_gitlab_obj()
    try:
        review_json = openai.generate_mr_review(gl, repo_id, mr_iid, pipeline_result)
        _verify_review_json_validity(review_json)
    except Exception as e:
        logging.error(f"Failed to generate commit review: {e}")
        _fail_review(review)
    else:
        _finish_review(review, review_json)
        notifications.NotifyMethod.send_all(repo_id, review_json)
