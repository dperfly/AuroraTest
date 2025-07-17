from typing import Dict

from jsonpath import jsonpath

from core.exception import ValueNotFoundError


def jsonpath_plus(obj: Dict, expr: str):
    my_json_paths = expr.split("|")
    _jsonpath_data = jsonpath(obj, my_json_paths[0])
    # 判断是否正常提取到数据，如未提取到，则抛异常
    if _jsonpath_data is False:
        raise ValueNotFoundError(
            f"jsonpath提取失败！\n 提取的数据: {obj} \n jsonpath规则: {expr}"
        )

    # 对提取到的数进行拆分
    def custom_extract(data, fields):
        if data is None:
            return
        if isinstance(data, list):
            result = []
            for item in data:
                extracted_item = {}
                for field in fields:
                    extracted_item[field] = item.get(field)
                result.append(extracted_item)
            return result

        if isinstance(data, dict):
            result_dict = {}
            for k, v in data.items():
                if k in fields:
                    result_dict[k] = v
            return result_dict
        raise ValueNotFoundError(f"类型错误，请检查jsonpath提取器是否正确：{expr}")

    # 当存在 | 时进行处理
    # 需要注意这里的数据格式为：[[{"a":"1"}]],需要解包并装包
    if len(my_json_paths) > 1:
        res = []
        for data in _jsonpath_data:
            res.append(custom_extract(data, my_json_paths[1].replace("，", ",").split(",")))
        return res

    return _jsonpath_data
