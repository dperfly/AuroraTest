import json
from datetime import datetime

from core.logger import INFO, ERROR
from core.model import Case, DataType, Response, ContentType, TestCaseRunResult, ReportHeader, \
    ReportLogEntry

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
        INFO.logger.info(self.new_case)
        if data_type == DataType.JSON.value:
            # 如果是字符串则尝试转换成字典
            try:
                if isinstance(body, str):
                    body = json.loads(body)
            except json.decoder.JSONDecodeError:
                ERROR.logger.error(f"JSONDecodeError: {body}")
            response = requests.request(method, uri, json=body, headers=headers)
        else:
            # TODO 需要优化不同的headers
            if data_type == DataType.FORM.value:
                headers["Content-Type"] = ContentType.APPLICATION_FORM_URLENCODED.value
            response = requests.request(method, uri, data=body, headers=headers)
        INFO.logger.info(f"response status code:{response.status_code}")
        INFO.logger.info(f"response text:{response.text}")
        self.test_run_result.logs.append(
            ReportLogEntry(time=datetime.now().isoformat(), level='info', message=f"response status code:{response.status_code}")
        )
        self.test_run_result.logs.append(
            ReportLogEntry(time=datetime.now().isoformat(), level='info', message=f"response text:{response.text}")
        )
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
