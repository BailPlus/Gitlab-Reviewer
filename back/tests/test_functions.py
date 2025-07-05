from app.openai.functions import *

# 在 back 目录下运行 python -m tests.test_functions
result = get_file_content("702fb4799e30569761592474feb158756464a1f9468bff9394e1866f21ddb18c", 1, "main",
                          "README.md")
print(f"File content: {result}")