from core.models.model import Case, DataType

import requests


class HTTPRequest:

    @classmethod
    def send_request(cls, new_case: Case):
        method = new_case.method
        url = new_case.domain + new_case.url
        headers = new_case.headers
        data_type = new_case.data.data_type
        body = new_case.data.body

        if data_type == DataType.JSON:
            body = body if body else {}
            response = requests.request(method, url, json=body, headers=headers)
        else:
            response = requests.request(method, url, data=body, headers=headers)

        print(response.text)
        return response
