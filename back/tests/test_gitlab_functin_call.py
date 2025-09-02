from unittest import TestCase
from app.openai.functions import *
from app.service.auth import verify_gitlab_token

TOKEN = 'ec9670dd65a307e7d36ba2e4682ee6e905e1e80623476a3717442dbc5729eff3'


class TestGitlabFunctionCall(TestCase):
    def test_get_file(self):
        print(get_file_content(**{'project_id': 6, 'ref': 'main', 'file_path': 'server/cmd/api/main.go', 'gl': verify_gitlab_token(TOKEN)}))

