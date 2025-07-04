from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .api import auth
from .errors import GitlabReviewerException

app = FastAPI()
app.include_router(auth.router)

@app.exception_handler(GitlabReviewerException)
async def gitlab_reviewer_exception_handler(request, exc: GitlabReviewerException):
    return JSONResponse(
        status_code=exc.code,
        content=exc.details.model_dump()
    )
