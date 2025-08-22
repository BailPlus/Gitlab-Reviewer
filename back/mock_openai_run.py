from fastapi import Request
from fastapi.responses import HTMLResponse
from app.openai import openai
from app.service.auth import get_token_from_cookie
from app.errors.auth import InvalidGitlabToken
from app import app
import uvicorn


def mock_openai_generate_repo_analysis(gl, project_id, ref):
    return f'正在模拟对仓库ID {project_id} 分支 {ref} 的分析结果'
openai.generate_repo_analysis = mock_openai_generate_repo_analysis

def mock_openai_generate_commit_review(gl, project_id, before_sha, after_sha):
    return f'正在模拟对仓库ID {project_id} 从 {before_sha} 到 {after_sha} 的分析结果'
openai.generate_commit_review = mock_openai_generate_commit_review

# patch_app
# @app.get("/")
# async def root(request: Request):
#     try:
#         get_token_from_cookie(request)
#     except InvalidGitlabToken:
#         return HTMLResponse('<meta http-equiv="refresh" content="1; url=/_/auth/login">即将登录')
#     else:
#         return HTMLResponse('<meta http-equiv="refresh" content="1; url=/docs">即将到/docs')
@app.middleware('http')
async def show_pkg(request, call_next):
    print(request.headers)
    return await call_next(request)

if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)
