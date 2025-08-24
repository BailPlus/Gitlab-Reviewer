from unittest import TestCase
from pprint import pprint
from app.db.analysis import *
from app.service.repositories import get_repo_by_id

REPO_ID = 1


class TestSqlRepoAnalysisGetter(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for _ in range(5):
            create_analysis(repo_id=REPO_ID)

    # def test_get_analysis(self):
    #     getter = SqlRepoAnalysisGetter(engine=engine)
    #     for i in getter.get_analysis_history(repo_id=1):
    #         obj = getter.get_analysis(i)
    #         print(obj, obj.created_at)
    #     self.assertTrue(input('请手动评判 >'))

    def test_get_analysis_history(self):
        res = get_analysis_history(repo_id=REPO_ID)
        self.assertEqual(len(res), 11)
        pprint(res)
        for i in res:
            self.assertIsInstance(i, int)
        self.assertEqual(get_repo_by_id(repo_id=REPO_ID).analysis_id, res[0])

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     os.remove(SQLITE_PATH)
