from app.openai.openai import generate_repo_analysis

# 在 back 目录下运行 python -m tests.test_openai
generate_repo_analysis(
        oauth_token="702fb4799e30569761592474feb158756464a1f9468bff9394e1866f21ddb18c",
        project_id=1,
        ref="main"
)