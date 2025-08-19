import json

from typing import Callable

from core.model import Case

from mako.template import Template


class DictToClass:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


class CaseRender:
    """
    用于解析case中的参数化内容
    """

    def __init__(self, case: Case, cache: dict, funcs: Callable):
        self.case = case
        self.cache = cache
        self.funcs = funcs

    def render(self) -> Case:
        temp = Template(json.dumps(self.case.model_dump()))
        res = temp.render(cache=DictToClass(self.cache), func=self.funcs)
        dicts = json.loads(res)

        return Case.model_validate(dicts)