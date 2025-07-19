import asyncio

import websockets
from core.asserts import Asserts
from core.logger import info_log,warring_log
from core.model import Case, TestCaseRunResult, ReportHeader


class WSRequest:
    def __init__(self, new_case: Case, test_run_result: TestCaseRunResult):
        self.new_case = new_case
        self.uri = self.new_case.domain + self.new_case.url
        self.websocket = None
        self.response_rows = []
        self.test_run_result = test_run_result

    async def connect(self):
        """连接到WebSocket服务器"""
        self.websocket = await websockets.connect(self.uri)
        warring_log("Connected to WebSocket server",self.test_run_result)

    async def send(self, message):
        """发送消息到WebSocket服务器"""
        if self.websocket:
            await self.websocket.send(message)
            info_log(f"WebSocket Sent: {message}", self.test_run_result)

    async def receive(self):
        """接收WebSocket服务器的响应"""
        if self.websocket:
            response = await self.websocket.recv()
            info_log(f"WebSocket Received: {response}", self.test_run_result)
            return response
        return None

    async def close(self):
        """关闭WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            warring_log(f"WebSocket connection closed", self.test_run_result)

    async def run(self, messages, stop_condition):
        """
        运行WebSocket客户端
        :param messages: 要发送的消息列表
        :param stop_condition: 停止条件函数，接收响应并返回布尔值
        """
        await self.connect()
        info_log(self.new_case, self.test_run_result)
        try:
            for message in messages:
                await self.send(message)
                response = await self.receive()
                self.response_rows.append(response)
                if stop_condition(response):
                    warring_log(f"Stop condition met. Closing connection.", self.test_run_result)
                    return
        finally:
            await self.close()

    async def send_request_async(self, stop_condition):
        """异步调用方式"""
        await self.run(self.new_case.data.body, stop_condition)
        return self.response_rows

    def send_request(self, stop_condition):
        """兼容同步和异步调用的方式"""
        # 添加运行结果
        self.test_run_result.api_name = self.new_case.desc
        self.test_run_result.name = self.new_case.desc
        self.test_run_result.request = self.new_case.data.body
        self.test_run_result.url = self.new_case.domain + self.new_case.url
        self.test_run_result.method = self.new_case.method
        self.test_run_result.headers = [ReportHeader(name=k,value=v) for k,v in self.new_case.headers.items()]

        async def run():
            await self.run(self.new_case.data.body, stop_condition)

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(run())  # 异步环境，后台运行
        except RuntimeError:
            asyncio.run(run())  # 同步环境，直接运行

        self.test_run_result.response = self.response_rows
        return self.response_rows

    def should_continue(self):
        def stop_condition(response) -> bool:
            """断言结果"""
            return Asserts.assert_response(response, self.new_case)

        return stop_condition
