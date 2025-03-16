from core.case.render import CaseRender
from core.interfaces.http import HTTPRequest
from core.models.model import Case, InterType
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

    def run_case(self):
        res = None
        api_type = self.new_case.inter_type.upper()

        # 这里进行不同类型的请求
        if InterType[api_type] == InterType.HTTP:
            res = HTTPRequest(new_case=self.new_case).send_request()

        res['request'] = asdict(self.new_case)

        return res

    def controller(self):

        if self.new_case.plc:
            # 存在循环控制器
            @loop_control(self.new_case.plc, timeout=60, asserts=self.new_case.asserts)
            def run():
                return self.run_case()

            res = run()
        else:
            res = self.run_case()
            Asserts.assert_response(res, self.new_case)

        Extracts.extracts_response(res, self.new_case)
