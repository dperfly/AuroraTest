import json
import re
from typing import Any
import jsonpath

from core.cache import CacheHandler
from core.model import Case, InterType, EXTRACT_DELIMITER


def regex(result, regex_pattern) -> Any:
    if isinstance(result, list):
        # 如果是列表，对每个元素应用正则
        return [re.findall(regex_pattern, str(item)) for item in result]
    else:
        # 如果是单个值，直接应用正则
        return re.findall(regex_pattern, str(result))


def ex(resp, json_path, regex_pattern=None) -> Any:
    """
    从 HTTP 响应中提取字段，并支持正则匹配。

    Args:
        resp: HTTP 响应数据（可以是 dict、list 或 JSON 字符串）。
        json_path: JSONPath 表达式（如 "$.data.items[*].name"）。
        regex_pattern: 可选的正则表达式（如 r"\d{3}-\d{4}"）。

    Returns:
        提取后的数据（可能经过正则过滤）。
    """
    res = jsonpath.jsonpath(json.loads(json.dumps(resp)), json_path)
    if res:
        res = res[0] if len(res) == 1 else res

    return res

def extract_res(run_res,paths) -> Any:
    # 通过 "->" 对提取器进行分割
    path_list = paths.split(EXTRACT_DELIMITER)
    value = run_res
    for path in path_list:
            if path.startswith("$"):
                value = ex(run_res, path)
            else:
                value = regex(value, path)
    return value

class Extracts:
    """
    文档
    $.status    -> resp返回的数据是json 可以直接进行$.status 提取
    req$.headers.token  -> 请求header中的 token
    $.headers.token -> \d+ --> 从resp中的header中提取token，并通过regex提取其中的数字
    """

    @classmethod
    def extracts_response(cls, run_res, case: Case):
        for name, paths in case.extracts.items():
            if case.inter_type.upper() == InterType.HTTP.value or case.inter_type == InterType.WS.value:
                value = extract_res(run_res, paths)
                CacheHandler.update_cache(key=name, value=value)
            else:
                raise TypeError("不支持的接口类型")