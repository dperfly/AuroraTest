from core.models.model import Case, Data, MethodType, DataType, InterType


def test_case_model():
    c = Case(**{
        "plc": 'for _ in range(10)',
        'inter_type': InterType.HTTP,
        'domain': 'www.baidu.com',
        'url': '/html/body/main',
        'method': MethodType.GET,
        'headers': {'token': 'test'},
        'data': Data(**{"data_type": DataType.JSON, "body": {"test": "test"}}),
        'extracts': {'token': 'resp$.header.set_cookie.token'},
        'asserts': {'status': 'resp$.status = 200'},
        'before_case': 'login'
    })
    assert c.plc == 'for _ in range(10)'
    assert c.inter_type == InterType.HTTP
    assert c.domain == 'www.baidu.com'
    assert c.url == '/html/body/main'
    assert c.method == MethodType.GET
    assert c.headers['token'] == 'test'
    assert c.data.data_type == DataType.JSON
    assert c.data.body == {"test": "test"}
    assert c.extracts['token'] == 'resp$.header.set_cookie.token'
    assert c.asserts == {'status': 'resp$.status = 200'}
    assert c.before_case == 'login'
