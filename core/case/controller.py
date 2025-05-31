from core.case.render import CaseRender
from core.interfaces.http import HTTPRequest
from core.interfaces.ws import WSRequest
from core.models.model import Case, InterType, RespData
from core.plc.plc import loop_control
from core.asserts.asserts import Asserts
from core.extracts.extracts import Extracts
from dataclasses import asdict


class CaseController:
    """
    单个case根据inter_type进行执行的工厂方法
    """

    def __init__(self, old_case: Case, cache: dict, func: classmethod):
        self.new_case = CaseRender(old_case, cache, func).render()
        self.cache = cache
        self.func = func

    async def __run_case_async(self):
        """异步执行逻辑"""
        res = None
        api_type = self.new_case.inter_type.upper()

        # 这里进行不同类型的请求
        if InterType[api_type] == InterType.HTTP:
            res = HTTPRequest(new_case=self.new_case).send_request()
        elif InterType[api_type] == InterType.WS:
            ws_client = WSRequest(new_case=self.new_case)
            res = await ws_client.send_request_async(ws_client.should_continue())
        return asdict(RespData(request=self.new_case, response=res))

    def controller(self):

        if self.new_case.plc:
            # 存在循环控制器
            @loop_control(self.new_case.plc, timeout=60, asserts=self.new_case.asserts)
            def run():
                return self.__run_case_async()

            res = run()
        else:
            res = self.__run_case_async()
            Asserts.assert_response(res, self.new_case)

        Extracts.extracts_response(res, self.new_case)
        return res
