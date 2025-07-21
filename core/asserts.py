import re

from core.logger import info_log,warring_log
from core.model import Case, InterType, TestCaseRunResult, ReportAssertion
from core.extracts import extract_res


class Asserts:

    @classmethod
    def assert_response(cls, run_res, case: Case,test_run_result:TestCaseRunResult) -> bool:
        all_assert_res = True
        for exp, paths in case.asserts.items():
            if InterType.__members__.get(case.inter_type.upper(),None):
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
                raise ValueError(f"{exp} 中只能包含一个_或者无_,无下划线时只能用于isnull" )

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
                test_run_result.assertions.append(
                    ReportAssertion(name=f"{paths}_{exp}",passed=True,message=f"Expected: {expect_res} Actual: {value}")
                )
                test_run_result.status = "passed"
                info_log(f"✓ Assertion passed: "
                    f"Actual: {value} ({type(value).__name__}) "
                    f"{operator} "
                    f"Expected: {expect_res} ({type(expect_res).__name__}) "
                    f"| Types: {type(value).__name__} vs {type(expect_res).__name__}",test_run_result
                )
            else:
                # TODO 断言失败后续需要做什么？
                all_assert_res = False
                test_run_result.assertions.append(
                    ReportAssertion(name=f"{paths}_{exp}",passed=False,message=f"Expected: {expect_res} Actual: {value}")
                )
                test_run_result.status = "failed"
                warring_log(
                    f"✗ Assertion failed: "
                    f"Actual: {value} ({type(value).__name__}) "
                    f"{operator} "
                    f"Expected: {expect_res} ({type(expect_res).__name__}) "
                    f"| Types: {type(value).__name__} vs {type(expect_res).__name__}",test_run_result
                )
        return all_assert_res