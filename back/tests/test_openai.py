from app.openai.openai import generate_repo_analysis
from app.service.auth import verify_gitlab_token


# 在 back 目录下运行 python -m tests.test_openai
generate_repo_analysis(
        gl=verify_gitlab_token("9e2609aa7e93daf111b4a0eae3f86868477557c2c85eb6ffe4c853f86c4f6b42"),
        project_id=4,
        ref="main"
)