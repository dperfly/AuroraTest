import asyncio
import websockets
from core.asserts.asserts import Asserts
from core.log.logger import INFO, WARNING
from core.models.model import Case


class WSRequest:
    def __init__(self, new_case: Case):
        self.new_case = new_case
        self.uri = self.new_case.domain + self.new_case.url
        self.websocket = None
        self.response_rows = []

    async def connect(self):
        """连接到WebSocket服务器"""
        self.websocket = await websockets.connect(self.uri)
        WARNING.logger.warning("Connected to WebSocket server")

    async def send(self, message):
        """发送消息到WebSocket服务器"""
        if self.websocket:
            await self.websocket.send(message)
            INFO.logger.info(f"WebSocket Sent: {message}")

    async def receive(self):
        """接收WebSocket服务器的响应"""
        if self.websocket:
            response = await self.websocket.recv()
            INFO.logger.info(f"WebSocket Received: {response}")
            return response
        return None

    async def close(self):
        """关闭WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            WARNING.logger.warning("WebSocket connection closed")

    async def run(self, messages, stop_condition):
        """
        运行WebSocket客户端
        :param messages: 要发送的消息列表
        :param stop_condition: 停止条件函数，接收响应并返回布尔值
        """
        await self.connect()
        INFO.logger.info(self.new_case)
        try:
            for message in messages:
                await self.send(message)
                response = await self.receive()
                self.response_rows.append(response)
                if stop_condition(response):
                    WARNING.logger.warning("Stop condition met. Closing connection.")
                    return
        finally:
            await self.close()

    async def send_request_async(self, stop_condition):
        """异步调用方式"""
        await self.run(self.new_case.data.body, stop_condition)
        return self.response_rows

    def send_request(self, stop_condition):
        """兼容同步和异步调用的方式"""

        async def run():
            await self.run(self.new_case.data.body, stop_condition)

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(run())  # 异步环境，后台运行
        except RuntimeError:
            asyncio.run(run())  # 同步环境，直接运行
        return self.response_rows

    def should_continue(self):
        def stop_condition(response) -> bool:
            """断言结果"""
            return Asserts.assert_response(response, self.new_case)

        return stop_condition
