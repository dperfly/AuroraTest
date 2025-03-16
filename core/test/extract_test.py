from core.cache.local_cache import CacheHandler
from core.case.controller import CaseController
from core.models.model import Data, Case
from core.test.test_data import TestFunc


def test_extract_http_json():
    case = Case(**{
        "plc": '',
        'inter_type': "HTTP",
        'domain': "http://www.baidu.com",
        'url': '/',
        'method': "GET",
        'extracts': {
            "domain": "$.request.domain",
            "data": "$.response.data"
        },
        'asserts': {'status': 'resp$.status = 200'},
        'before_cases': []
    })

    CaseController(old_case=case, cache={}, func=TestFunc).controller()
    assert CacheHandler.get_cache("domain") == "http://www.baidu.com"
    assert 'html' in CacheHandler.get_cache("data")
