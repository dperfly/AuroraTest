from typing import Callable
from core.case.render import CaseRender
from core.steps.http import HTTPRequest
from core.steps.mysql import MysqlRequest
from core.steps.ws import WSRequest
from core.model import Case, InterType, RespData, TestCaseRunResult, TestSummary
from core.plc import loop_control
from core.asserts import Asserts
from core.extracts import Extracts
from dataclasses import asdict


class CaseController:
    """
    单个case根据inter_type进行执行的工厂方法
    """

    def __init__(self, old_case: Case, cache: dict, func: Callable, test_run_result: TestCaseRunResult,
                 summary: TestSummary):
        self.cache = cache
        self.func = func
        self.func.case = old_case
        # before hook 对self.func.case进行操作,如果结合plc进行循环操作，只处理一次。
        if hasattr(self.func, "before_case"):
            self.func.before_case()
        self.new_case = CaseRender(self.func.case, cache, func).render()
        self.test_run_result = test_run_result
        self.test_summary = summary

    async def __run_case_async(self):
        """异步执行逻辑"""
        res = None
        api_type = self.new_case.inter_type.upper()

        # 这里进行不同类型的请求
        if InterType[api_type] == InterType.HTTP:
            res = HTTPRequest(new_case=self.new_case, test_run_result=self.test_run_result).send_request()
        elif InterType[api_type] == InterType.WS:
            ws_client = WSRequest(new_case=self.new_case, test_run_result=self.test_run_result)
            res = await ws_client.send_request_async(ws_client.should_continue())
        elif InterType[api_type] == InterType.MySQL:
            res = MysqlRequest(new_case=self.new_case, test_run_result=self.test_run_result)

        return asdict(RespData(request=self.new_case, response=res))

    async def controller(self):
        if self.new_case.plc:
            # 存在循环控制器
            @loop_control(self.new_case.plc, timeout=60, case=self.new_case, test_run_result=self.test_run_result)
            async def run():
                return await self.__run_case_async()

            res = await run()
        else:
            res = await self.__run_case_async()

        self.test_summary.total += 1
        if Asserts.assert_response(res, self.new_case, self.test_run_result):
            self.test_summary.passed += 1
        else:
            self.test_summary.failed += 1

        # after hook
        if hasattr(self.func, "after_case"):
            self.func.after_case()

        Extracts.extracts_response(res, self.new_case)
        return res
