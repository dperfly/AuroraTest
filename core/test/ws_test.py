import asyncio

from core.interfaces.ws import WSRequest
from core.models.model import Case, Data


def test_ws_request():
    case = Case(**{
        "plc": 'for _ in range(1)',
        'inter_type': "HTTP",
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
    client = WSRequest(case)
    resp = client.send_request(client.should_continue())
    print(resp)
