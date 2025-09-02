from app.openai.openai import generate_repo_analysis
from app.service.auth import verify_gitlab_token


# 在 back 目录下运行 python -m tests.test_openai
generate_repo_analysis(
        gl=verify_gitlab_token("a9495e507d4550c89fb3b2a1890fef0aec11c81eee0823fa554d4e114178a16c"),
        project_id=3,
        ref="main"
)