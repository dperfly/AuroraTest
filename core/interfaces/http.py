import json

from core.logger import INFO, ERROR
from core.model import Case, DataType, Response

import requests


class HTTPRequest:
    def __init__(self, new_case: Case):
        self.new_case = new_case

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
                headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
            response = requests.request(method, uri, data=body, headers=headers)
        INFO.logger.info(f"response status code:{response.status_code}")
        INFO.logger.info(f"response text:{response.text}")
        # 尝试解析JSON
        try:
            json_data = response.json()
            data = json_data
        except ValueError:
            data = response.text
        resp = Response(data=data, headers=dict(response.headers), status_code=response.status_code)

        return resp
