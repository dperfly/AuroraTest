import re

from core.log.logger import INFO, WARNING
from core.models.model import Case, InterType
from core.extracts.extracts import extract_res


class Asserts:

    @classmethod
    def assert_response(cls, run_res, case: Case):

        for exp, paths in case.asserts.items():
            if case.inter_type.upper() == InterType.HTTP.value or case.inter_type == InterType.WS.value:
                # 进行结果提取
                value = extract_res(run_res, paths)
            else:
                raise TypeError("不支持的接口类型")

            # 进行判断
            exp_list = exp.split("_")
            if len(exp_list) == 2:
                operator, expect_res = exp_list
            elif len(exp_list) == 1 and exp_list[1] == "isnull":
                operator, expect_res = exp_list[0], None
            else:
                ValueError(f"{exp} 中只能包含一个_或者无_,无下划线时只能用于isnull" )

            operator_dict = {
                "eq": lambda x, y: str(x) == str(y),
                "neq": lambda x, y: str(x) != str(y),
                "in": lambda x, y: str(x) in str(y),
                "notin": lambda x, y: str(x) not in str(y),
                "gt": lambda x, y: int(y) > int(x),
                "lt": lambda x, y: int(y) < int(x),
                "gte": lambda x, y: int(y) >= int(x),
                "lte": lambda x, y: int(y) <= int(x),
                "isnull": lambda x, y: y is None,
                "regex": lambda x, y: bool(re.search(x, str(y))),
                "start": lambda x, y: str(y).startswith(str(x)),
                "end": lambda x, y: str(y).endswith(str(x)),
                "len": lambda x, y: int(x) == len(y),
                "bool": lambda x, y: bool(y) == bool(x),
            }

            if operator_dict[operator](expect_res, value):
                INFO.logger.info(
                    f"\033[32m✓ Assertion passed\033[0m: "
                    f"Actual: {value} (\033[33m{type(value).__name__}\033[0m) "
                    f"{operator} "
                    f"Expected: {expect_res} (\033[33m{type(expect_res).__name__}\033[0m) "
                    f"| Types: \033[36m{type(value).__name__}\033[0m vs \033[36m{type(expect_res).__name__}\033[0m"
                )
            else:
                # TODO 断言失败后续需要做什么？
                WARNING.logger.warning(
                    f"\033[31m✗ Assertion failed\033[0m: "
                    f"Actual: {value} (\033[33m{type(value).__name__}\033[0m) "
                    f"{operator} "
                    f"Expected: {expect_res} (\033[33m{type(expect_res).__name__}\033[0m) "
                    f"| Types: \033[36m{type(value).__name__}\033[0m vs \033[36m{type(expect_res).__name__}\033[0m"
                )
