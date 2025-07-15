from unittest import TestCase
from pprint import pprint
from app.db.analysis import (
    SqlRepoAnalysisGetter,
    SqlRepoAnalysisSetter
)
from app.db.repositories import SqlRepoGetter, SqlRepoAdder, SqlRepoBinder
from app.db import engine
import os

SQLITE_PATH = '.test.db'


class TestSqlRepoAnalysisGetter(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        SqlRepoAdder(engine).add(repo_id=1)
        SqlRepoBinder(engine).bind(user_id=1, repo_id=1)
        setter = SqlRepoAnalysisSetter(engine=engine)
        for _ in range(5):
            setter.add(repo_id=1)

    def test_get_analysis(self):
        getter = SqlRepoAnalysisGetter(engine=engine)
        for i in getter.get_analysis_history(repo_id=1):
            obj = getter.get_analysis(i)
            print(obj, obj.created_at)
        self.assertTrue(input('请手动评判 >'))

    def test_get_analysis_history(self):
        getter = SqlRepoAnalysisGetter(engine=engine)
        res = getter.get_analysis_history(repo_id=1)
        pprint(res)
        for i in res:
            self.assertIsInstance(i, int)
        repo_getter = SqlRepoGetter(engine=engine)
        self.assertEqual(repo_getter.get(1).analysis_id, res[0])

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(SQLITE_PATH)
