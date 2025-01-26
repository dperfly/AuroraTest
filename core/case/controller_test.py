from core.case.controller import CaseController
from core.case.render import CaseRender
from core.generate.reader import ReaderCase
from core.models.model import Case, Data, MethodType, DataType, InterType


def test_controller():
    class TestFunc:
        @staticmethod
        def get_image(name):
            return f"{name}图片"

        @staticmethod
        def add(a, b):
            return a + b

    old_c = Case(
        plc="for _ in range(${cache.loopNum})",
        inter_type="http",
        domain="${cache._domain}",
        url="/",
        method="get",
        headers={},
        data=Data(data_type="text", body={}),
        asserts={"status": "resp$.status == 200", "code": "resp$.data.code == 0"},
        extracts={"token": "resp$.header.set_cookie.token", "uuid": "req$.data.uuid"},
        before_case=["beforeCaseName"]
    )
    print(old_c)
    cache = {"loopNum": "10", "_domain": "http://10.70.70.96"}
    CaseController(old_case=old_c, cache=cache, func=TestFunc).controller()
