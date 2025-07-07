from openai import OpenAI
import json
from .functions import *
from ..core.config import settings

client = OpenAI(
    base_url=settings.openai_base_url,
    api_key=settings.openai_api_key,
)

def function_call(messages: list, oauth_token: str) -> str:
    """
    方便复用function call流程
    """
    while True:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=tools,
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

                # 仅在函数参数中包含 'oauth_token' 时才注入
                if "oauth_token" in function_map[name].__code__.co_varnames:
                    args["oauth_token"] = oauth_token
                print(f"调用函数: {name}, 参数: {args}")
                result = function_map[name](**args)
                print(f"函数执行结果: {result}")
                # 把执行结果塞回对话
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            continue

        print(msg.content)
        break
    return msg.content
def generate_repo_analysis(oauth_token: str, project_id: int, ref: str = None) -> str:
    """
    Generate a detailed analysis of the GitLab repository.
    """
    messages = [{"role": "user", "content": f"帮我全方位详细分析项目 project_id为{project_id} 这个仓库，分支为 {ref}，你可以读取仓库文件，给出分析报告。"}]
    return function_call(messages, oauth_token)



def generate_commit_review(oauth_token: str, project_id: int, commit_id: str) -> str:
    """
    Generate a detailed review of a specific commit in the GitLab repository.
    """
    pass