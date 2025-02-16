import json
import time
import pytest
import requests

from core.exceptions import WhileException, IFException
from core.plc import *

from unittest.mock import Mock

from core.plc.plc import loop_control


def test_while_control():
    @loop_control("while True", timeout=2)
    def func():
        time.sleep(1)  # 模拟一些耗时操作
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = '{"res": "Success"}'
        mock_response.json.return_value = {"res": "Success"}

        return mock_response

    func()


def test_for_control():
    @loop_control("for _ in range(10)")
    def func():
        time.sleep(1)  # 模拟一些耗时操作
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = '{"res": "Success"}'
        mock_response.json.return_value = {"res": "Success"}

        return mock_response

    func()


def test_if_control():
    @loop_control("if 1==1")
    def func():
        time.sleep(1)  # 模拟一些耗时操作
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = '{"res": "Success"}'
        mock_response.json.return_value = {"res": "Success"}

        return mock_response

    with pytest.raises(IFException):
        func()


def test_while_true_control():
    @loop_control("while True")
    def func():
        time.sleep(1)  # 模拟一些耗时操作
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = '{"res": "Success"}'
        mock_response.json.return_value = {"res": "Success"}

        return mock_response

    with pytest.raises(WhileException):
        func()


def test_while_true_assert():
    asserts = {"resNum": {"jsonpath": "$.res", "type": "==", "value": "Success", "AssertType": None}}

    @loop_control("while True", asserts=asserts, timeout=600)
    def func():
        time.sleep(1)  # 模拟一些耗时操作
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = '{"res": "Success"}'
        mock_response.json.return_value = {"res": "Success"}

        return mock_response

    func()
