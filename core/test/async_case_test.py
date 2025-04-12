from core.case.runcase import AsyncRunCase

from core.test.test_data import local_cache, TestFunc, raw_data


def test_async_case_test():
    AsyncRunCase(raw_data=raw_data, cache=local_cache.get_all_cache(), hook_func=TestFunc).run()
