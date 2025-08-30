from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .api import (
    auth,
    repositories,
    analysis,
    commits,
    notifications,
    merge_requests
)
from .errors import GitlabReviewerException

app = FastAPI()
app.include_router(auth.router)
app.include_router(repositories.router)
app.include_router(analysis.router)
app.include_router(commits.webhook_router)
app.include_router(commits.router)
app.include_router(notifications.router)
app.include_router(merge_requests.router)

@app.exception_handler(GitlabReviewerException)
async def gitlab_reviewer_exception_handler(request, exc: GitlabReviewerException):
    return JSONResponse(
        status_code=exc.code,
        content=exc.details.model_dump()
    )
