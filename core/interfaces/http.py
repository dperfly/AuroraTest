from core.log.logger import INFO
from core.models.model import Case, DataType, Response

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
        if data_type == DataType.JSON:
            body = body if body else {}
            response = requests.request(method, uri, json=body, headers=headers)
        else:
            response = requests.request(method, uri, data=body, headers=headers)
        INFO.logger.info(f"response status code:{response.status_code}")
        INFO.logger.info(f"response text:{response.text}")
        resp = Response(data=response.text, headers=dict(response.headers), status_code=response.status_code)

        return resp
