from core.generate.generate import TestCaseAutomaticGeneration
from core.test.test_data import raw_data


class TestCaseAutoGenerate:

    def test_graph(self):
        # raw_data = ReaderCase(data_path()).get_all_cases()
        t_c_a_g = TestCaseAutomaticGeneration(raw_data)
        map = t_c_a_g.get_cases_graph_map()
        order = t_c_a_g.get_case_runner_order()
        print(order)
