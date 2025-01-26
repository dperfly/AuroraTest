from core.models.model import Case, DataType

import requests


class HTTPRequest:

    @classmethod
    def send_request(cls, case: Case):
        method = str(case.method)
        url = case.domain + case.url
        headers = case.headers
        data_type = case.data.data_type
        body = case.data.body if case.data.body else {}

        if data_type == DataType.JSON:
            response = requests.request(method, url, json=body, headers=headers)
        else:
            response = requests.request(method, url, data=body, headers=headers)

        print(response.text)
        return response
