import json
from typing import Any
import jsonpath

from core.cache.local_cache import CacheHandler
from core.models.model import Case, InterType


def ex_http(resp, path) -> Any:
    """
    从 HTTP 请求、响应、头部等数据中提取字段。
    """
    res = jsonpath.jsonpath(json.loads(json.dumps(resp)), path)
    if res:
        res = res[0] if len(res) == 1 else res
    return res


def ex_ws(resp, path) -> Any:
    """
    TODO 从 ws 请求、响应、头部等数据中提取字段。
    """
    res = jsonpath.jsonpath(json.loads(json.dumps(resp)), path)
    if res:
        res = res[0] if len(res) == 1 else res

    return res


class Extracts:
    """
    文档
    resp$.status    -> resp返回的数据是json 可以直接进行$.status 提取
    req$.headers.token  -> 请求header中的 token
    """

    @classmethod
    def extracts_response(cls, run_res, case: Case):
        for name, path in case.extracts.items():
            if case.inter_type == InterType.HTTP.value:
                value = ex_http(run_res, path)
                CacheHandler.update_cache(cache_name=name, value=value)
            if case.inter_type == InterType.WS.value:
                value = ex_ws(run_res, path)
                CacheHandler.update_cache(cache_name=name, value=value)
