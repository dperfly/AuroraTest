import asyncio

from core.interfaces.ws import WSRequest
from core.models.model import Case, Data


def test_ws_request():
    async def main():
        # WebSocket服务器地址
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

        # body 就是message ，当inter_type = ws 时 body = list时进行for each操作，否则body当一个处理
        # 创建WebSocket客户端并运行
        client = WSRequest(case)
        await client.run(case.data.body, client.should_continue())

    asyncio.get_event_loop().run_until_complete(main())
