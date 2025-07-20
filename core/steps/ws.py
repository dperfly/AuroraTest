import asyncio
import json
from dataclasses import asdict

import websockets
from core.asserts import Asserts
from core.steps.base import StepBase
from core.logger import info_log, warring_log, error_log
from core.model import Case, TestCaseRunResult, RespData, Response


class WSRequest(StepBase):
    def __init__(self, new_case: Case, test_run_result: TestCaseRunResult):
        super().__init__(new_case, test_run_result)
        self.uri = new_case.domain + new_case.url
        self.websocket = None
        self.response_rows = []
        self.last_response = None

    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(self.uri)
            warring_log("Connected to WebSocket server",self.test_run_result)
        except ConnectionRefusedError:
            error_log("WebSocket connection refused", self.test_run_result)

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
        运行WebSocket客户端，支持处理服务端返回的多条消息
        :param messages: 要发送的消息列表
        :param stop_condition: 停止条件函数，接收响应并返回布尔值
        """
        await self.connect()
        info_log(self.new_case, self.test_run_result)
        try:
            if isinstance(messages, str):
                messages = [messages]
            for message in messages:
                await self.send(message)  # 发送一条消息
                # 持续接收消息，直到服务端停止发送或满足停止条件
                while True:
                    try:
                        data = await self.receive()  # 接收一条响应
                    except websockets.exceptions.ConnectionClosed:
                        break  # 连接关闭时退出循环

                    # 没有返回值，直接结束
                    if not data:
                        break

                    try:
                        data = json.loads(data)  # 尝试解析JSON
                    except json.decoder.JSONDecodeError:
                        pass


                    # 构造响应对象
                    resp = Response(data=data)
                    # 这里为了和其他的地方断言相同，需要这样处理
                    res = asdict(RespData(request=self.new_case, response=resp))

                    self.response_rows.append(data)
                    self.last_response = data

                    # 检查是否满足停止条件
                    if stop_condition(res):
                        warring_log("Stop condition met. Closing connection.", self.test_run_result)
                        return

        finally:
            await self.close()

    async def send_request_async(self, stop_condition):
        """异步调用方式"""

        await self.run(self.new_case.data.body, stop_condition)

        # 添加运行结果
        self.set_request_log()
        self.test_run_result.response = self.response_rows


        return Response(data=self.last_response)

    def send_request(self, stop_condition):
        """兼容同步和异步调用的方式"""
        async def run():
            await self.run(self.new_case.data.body, stop_condition)

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(run())  # 异步环境，后台运行
        except RuntimeError:
            asyncio.run(run())  # 同步环境，直接运行

        return Response(data=self.last_response)

    def should_continue(self):
        def stop_condition(response) -> bool:
            """断言结果"""
            return Asserts.assert_response(response, self.new_case,self.test_run_result)

        return stop_condition
