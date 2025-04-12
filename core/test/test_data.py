from core.cache.local_cache import CacheHandler
from core.models.model import Case, Data

local_cache = CacheHandler()
local_cache.update_cache(cache_name="loopNum", value="2")
local_cache.update_cache(cache_name="_domain", value="http://10.99.99.96")
local_cache.update_cache(cache_name="token", value="i am token")


class TestFunc:
    @staticmethod
    def get_image(name):
        return f"{name}图片"

    @staticmethod
    def add(a, b):
        return a + b


raw_data = dict()
raw_data['file-login'] = {
    "login": Case(**{
        "plc": 'for _ in range(1)',
        'inter_type': "HTTP",
        'domain': "${cache._domain}",
        'url': '/',
        'method': "GET",
        'headers': {'token': 'test'},
        'data': Data(**{"data_type": "json", "body": {"test": "test"}}),
        'extracts': {'token': 'resp$.header.set_cookie.token'},
        'asserts': {'status': 'resp$.status = 200'},
        'before_cases': []
    })}
raw_data['file-case1'] = {
    "case1": Case(**{
        "plc": 'for _ in range(${cache.loopNum})',
        'inter_type': "HTTP",
        'domain': "${cache._domain}",
        'url': '/',
        'method': "GET",
        'headers': {'token': '${cache.token}'},
        'data': Data(**{"data_type": "json", "body": {"test": "test"}}),
        'extracts': {},
        'asserts': {'status': 'resp$.status = 200'},
        'before_cases': []
    }),
    "case2": Case(**{
        "plc": 'for _ in range(${cache.loopNum})',
        'inter_type': "HTTP",
        'domain': "${cache._domain}",
        'url': '/',
        'method': "GET",
        'headers': {'token': '${cache.token}'},
        'data': Data(data_type="json",
                     body={"uuid": " ${func.add(1,1)}", "file": "${func.get_image('image.jpg')}"}),
        'extracts': {},
        'asserts': {'status': 'resp$.status = 200'},
        'before_cases': ['case1']
    }),
    "case3": Case(**{
        "plc": 'for _ in range(3)',
        'inter_type': "HTTP",
        'domain': "${cache._domain}",
        'url': '/',
        'method': "GET",
        'headers': {'token': '${cache.token}'},
        'data': Data(**{"data_type": "json", "body": {"test": "test"}}),
        'extracts': {},
        'asserts': {'status': 'resp$.status = 200'},
        'before_cases': ["case2"]
    })}

raw_data['file-ws-case3'] = {
    "ws-case1": Case(**{
        "plc": 'for _ in range(1)',
        'inter_type': "WS",
        'domain': "ws://localhost:8765",
        'url': '/',
        'method': "GET",
        'headers': {'token': 'test'},
        'data': Data(
            **{"data_type": "json", "body": ['{"test": "test1"}', '{"test": "test2"}', '{"test": "test3"}']}),
        'extracts': {'token': 'resp$.header.set_cookie.token'},
        'asserts': {'status': 'resp$.status = 200'},
        'before_cases': []
    })
}