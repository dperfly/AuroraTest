import websockets

from core.asserts.asserts import Asserts
from core.models.model import Case


class WSRequest:
    def __init__(self, new_case: Case):
        self.new_case = new_case
        self.uri = self.new_case.domain + self.new_case.url
        self.websocket = None

    async def connect(self):
        """连接到WebSocket服务器"""
        self.websocket = await websockets.connect(self.uri)
        print("Connected to WebSocket server")

    async def send(self, message):
        """发送消息到WebSocket服务器"""
        if self.websocket:
            await self.websocket.send(message)
            print(f"Sent: {message}")

    async def receive(self):
        """接收WebSocket服务器的响应"""
        if self.websocket:
            response = await self.websocket.recv()
            print(f"Received: {response}")
            return response
        return None

    async def close(self):
        """关闭WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            print("WebSocket connection closed")

    async def run(self, messages, stop_condition):
        """
        运行WebSocket客户端
        :param messages: 要发送的消息列表
        :param stop_condition: 停止条件函数，接收响应并返回布尔值
        """
        await self.connect()

        try:
            for message in messages:
                await self.send(message)
                response = await self.receive()

                # 检查是否满足停止条件
                if stop_condition(response):
                    print("Stop condition met. Closing connection.")
                    break
        finally:
            await self.close()

    def send_request(self, stop_condition):
        self.run(self.new_case.data.body, stop_condition)

    def should_continue(self):
        def stop_condition(response) -> bool:
            """断言结果"""
            return Asserts.assert_response(response, self.new_case.asserts)

        return stop_condition
