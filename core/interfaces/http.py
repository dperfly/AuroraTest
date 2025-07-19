import json

from core.logger import info_log, error_log
from core.model import Case, DataType, Response, ContentType, TestCaseRunResult, ReportHeader

import requests


class HTTPRequest:
    def __init__(self, new_case: Case,test_run_result: TestCaseRunResult):
        self.new_case = new_case
        self.test_run_result = test_run_result

    def send_request(self):
        method = self.new_case.method
        uri = self.new_case.domain + self.new_case.url
        headers = self.new_case.headers
        data_type = self.new_case.data.data_type
        body = self.new_case.data.body
        info_log(self.new_case, self.test_run_result)
        if data_type == DataType.JSON.value:
            # 如果是字符串则尝试转换成字典
            try:
                if isinstance(body, str):
                    body = json.loads(body)
            except json.decoder.JSONDecodeError:
                error_log(f"JSONDecodeError: {body}",test_run_result=self.test_run_result)
            response = requests.request(method, uri, json=body, headers=headers)
        else:
            # TODO 需要优化不同的headers
            if data_type == DataType.FORM.value:
                headers["Content-Type"] = ContentType.APPLICATION_FORM_URLENCODED.value
            response = requests.request(method, uri, data=body, headers=headers)
        info_log(f"response status code:{response.status_code}", self.test_run_result)
        info_log(f"response text:{response.text}", self.test_run_result)
        # 尝试解析JSON
        try:
            json_data = response.json()
            data = json_data
        except ValueError:
            data = response.text
        resp = Response(data=data, headers=dict(response.headers), status_code=response.status_code)

        # 添加运行结果
        self.test_run_result.api_name = self.new_case.desc
        self.test_run_result.name = self.new_case.desc
        self.test_run_result.request = self.new_case.data.body
        self.test_run_result.url = self.new_case.domain + self.new_case.url
        self.test_run_result.method = self.new_case.method
        self.test_run_result.headers = [ReportHeader(name=k,value=v) for k,v in self.new_case.headers.items()]
        self.test_run_result.response = data

        return resp
