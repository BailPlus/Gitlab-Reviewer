from typing import Optional
from openai import OpenAI
from gitlab import Gitlab
from .functions import *
from .prompt import *
from ..core.config import settings
import json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=settings.openai_base_url,
    api_key=settings.openai_api_key,
)

def function_call(messages: list, gl: Gitlab) -> str:
    """
    方便复用function call流程
    """
    while True:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=tools, # type: ignore
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg)
        # 模型要调用函数
        if msg.tool_calls:
            tool_calls = msg.tool_calls
            for tool_call in tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # 仅在函数参数中包含 'gl' 时才注入
                if "gl" in function_map[name].__code__.co_varnames:
                    args["gl"] = gl
                logger.info(f"调用函数: {name}, 参数: {args}")
                result = function_map[name](**args)
                logger.info(f"函数执行结果: \n{result}")
                # 把执行结果塞回对话
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            continue

        logger.info(f"消息内容: \n{msg.content}")
        break
    return msg.content or ""

def generate_repo_analysis(gl: Gitlab, project_id: int, ref: Optional[str] = None) -> str:
    """
    Generate a detailed analysis of the GitLab repository.
    """
    messages = [{"role": "user", "content": repo_analysis_prompt.format(project_id=project_id, ref=ref)}]
    return function_call(messages, gl)

def generate_commit_review(gl: Gitlab, project_id: int, before_sha: str, after_sha: str) -> str:
    """
    为 GitLab 仓库中的提交差异生成详细审查。
    """
    diff = get_commit_compare(gl, project_id, before_sha, after_sha)
    messages = [{"role": "user", "content": commit_review_prompt.format(project_id=project_id, diff=diff)}]
    return function_call(messages, gl)

def generate_mr_review(gl: Gitlab, project_id: int, mr_iid: int, pipeline_result: dict) -> str:
    """
    为 GitLab 仓库中的 Merge Request 差异生成详细审查。
    """
    diff = get_mr_compare(gl, project_id, mr_iid)
    messages = [{"role": "user", "content": mr_review_prompt.format(project_id=project_id, diff=diff, pipeline_result=pipeline_result)}]
    return function_call(messages, gl)
