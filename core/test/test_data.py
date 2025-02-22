from core.models.model import Case, Data

cache = {"loopNum": "2", "_domain": "http://10.70.70.96", "token": "i am token"}


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


ws_raw = dict()
ws_raw['file-login'] = {
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