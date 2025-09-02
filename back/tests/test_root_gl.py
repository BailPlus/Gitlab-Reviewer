from unittest import TestCase
from app.service.auth import get_root_gitlab_obj
from gitlab import Gitlab


class TestGetRootGitlabObj(TestCase):
    def test_get_root_gitlab_obj(self):
        gl = get_root_gitlab_obj()
        self.assertIsInstance(gl, Gitlab)
        self.assertEqual(gl.user.id, 1) # type: ignore
