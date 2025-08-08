import data_store
from icecream import ic


class TestDataStore:
    def test_put_object_v2(self):
        store = data_store.ObjectStore()
        print("put_object_v2")
        res = store.put_object_v2(
            data=b"test",
            key="test.txt",
            bucket="test-v2-functions",
        )
        ic(res)
        assert res
