from core.case.render import CaseRender
from core.generate.reader import ReaderCase
from core.models.model import Case, Data, MethodType, DataType, InterType


def test_render_case():
    class TestFunc:
        @staticmethod
        def get_image(name):
            return f"{name}图片"

        @staticmethod
        def add(a, b):
            return a + b

    old_c = Case(
        plc="for _ in range(len(${cache.loopNum}))",
        inter_type="http",
        domain="${cache._domain}",
        url="/login",
        method="get",
        headers={"token": "${cache._token}"},
        data=Data(data_type="json",
                  body={"uuid": " ${func.add(1,1)}", "file": "${func.get_image('image.jpg')}"}),
        asserts={"status": "resp$.status == 200", "code": "resp$.data.code == 0"},
        extracts={"token": "resp$.header.set_cookie.token", "uuid": "req$.data.uuid"},
        before_case=["beforeCaseName"]
    )
    print(old_c)
    cache = {"loopNum": "10", "_domain": "http://www.baidu.com", "_token": "11sdfsa3245sadsd",
             "image": "hello"}

    new_c = CaseRender(case=old_c, cache=cache, funcs=TestFunc).render()
    print(new_c)
