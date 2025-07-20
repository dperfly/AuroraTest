from core.model import TestCaseRunResult, ReportHeader, Case


class StepBase:
    def __init__(self, new_case: Case, test_run_result: TestCaseRunResult):
        self.new_case = new_case
        self.test_run_result = test_run_result

    def set_request_log(self):
        self.test_run_result.api_name = self.new_case.desc
        self.test_run_result.name = self.new_case.desc
        self.test_run_result.request = self.new_case.data.body
        self.test_run_result.url = self.new_case.domain + self.new_case.url
        self.test_run_result.method = self.new_case.method
        self.test_run_result.headers = [ReportHeader(name=k, value=v) for k, v in self.new_case.headers.items()]