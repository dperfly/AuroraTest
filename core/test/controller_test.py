from core.case.controller import CaseController
from core.generate.generate import TestCaseAutomaticGeneration
from core.test.test_data import cache, TestFunc, raw_data


def test_controller():
    t_c_a_g = TestCaseAutomaticGeneration(raw_data)
    order = t_c_a_g.get_case_runner_order()
    all_case_map = t_c_a_g.get_all_case_map()
    for index in range(max(order.keys()), 0, -1):
        for case_name in order.get(index):
            case = all_case_map.get(case_name)
            print(f"\nrun case order: {index},case_name={case_name}")
            CaseController(old_case=case, cache=cache, func=TestFunc).controller()
