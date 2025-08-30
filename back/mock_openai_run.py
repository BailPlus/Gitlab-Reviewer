from fastapi import Request
from fastapi.responses import PlainTextResponse
from app.openai import openai
from app.service import auth as service_auth
from app import app
from app.core.config import settings
import uvicorn, json


if settings.gitlab_oauth_redirect_url:
    service_auth.OAUTH_REDIRECT_URL = settings.gitlab_oauth_redirect_url

# def mock_openai_generate_repo_analysis(gl, project_id, ref):
#     return f'正在模拟对仓库ID {project_id} 分支 {ref} 的分析结果'
# openai.generate_repo_analysis = mock_openai_generate_repo_analysis

# def mock_openai_generate_commit_review(gl, project_id, before_sha, after_sha):
#     return json.dumps({
#         'info': f'正在模拟对仓库ID {project_id} 从 {before_sha} 到 {after_sha} 的分析结果',
#         'suggestion': {},
#         'level': 3
#     }, ensure_ascii=False)
# openai.generate_commit_review = mock_openai_generate_commit_review

# def mock_openai_generate_mr_review(gl, project_id, mr_iid, pipeline_result):
#     return json.dumps({
#         'info': f'正在模拟对仓库ID {project_id} 的 {mr_iid} 号合并请求的分析结果',
#         'suggestion': {},
#         'level': 3
#     }, ensure_ascii=False)
# openai.generate_mr_review = mock_openai_generate_mr_review

@app.middleware('http')
async def show_pkg(request, call_next):
    print(request.headers)
    return await call_next(request)

@app.get('/testai')
async def testai(request: Request):
    if request.headers.get('secret') != 'TestAiSecret_;fal fjrgae earkjg laerkjg':
        return PlainTextResponse('Invalid Secret')
    return PlainTextResponse(str(
        openai.OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url).chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "user", "content": "你是谁"},
            ],
        )
    ))


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)
