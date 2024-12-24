import json

from dacite import from_dict
from mako.template import Template
from dataclasses import asdict
from core.models.model import Case


class DictToClass:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


class Parametric:
    def __init__(self, cache: dict, func: callable):
        self.cache = cache
        self.func = func

    def use_params(self, case: Case) -> Case:
        """参数化"""
        json_str = json.dumps(asdict(case))
        temp = Template(json_str)
        json_str = temp.render(cache=DictToClass(self.cache), func=self.func)
        dicts = json.loads(json_str)
        return from_dict(data_class=Case, data=dicts)
