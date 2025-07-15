import asyncio
import functools

from core.asserts import Asserts
from core.exception import IFException, WhileException
from core.model import Case


def loop_control(plc_str, timeout=None, case=None):
    """
    接受类似 "for _ in range(10)" 的字符串并动态执行，并添加超时时间

    :param plc_str: 类似 "for _ in range(10)" 的字符串
    :param timeout: 超时时间，单位为秒。如果设置为 None，则不限制时间。

    while True :会根据断言结果进行判断是否需要进行循环，如果在timeout之前未断言成功则结束循环返回最后一次的执行结果
    for : for循环不会进行结果判断，做指定次数的循环，然后返回最后一次的结果，希望用于”post“请求
    TODO if : 暂不支持if分支语句
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if plc_str.startswith("if"):
                raise IFException
            if plc_str.startswith("while "):
                if timeout is None:
                    raise WhileException
                return await _run_while_loop(func, plc_str, timeout, case, args, kwargs)
            elif plc_str.startswith("for "):
                return await _run_for_loop(func, plc_str, args, kwargs)
            else:
                return await func(*args, **kwargs)  # 默认直接执行
        return wrapper
    return decorator

async def _run_while_loop(func, plc_str, timeout, case:Case, args, kwargs):
    """处理 while 循环逻辑"""
    loop = asyncio.get_event_loop()
    start_time = loop.time()
    result = None

    while True:
        result = await func(*args, **kwargs)
        if Asserts.assert_response(result,case):  # 如果断言成功，退出循环
            break
        if loop.time() - start_time > timeout:  # 超时退出
            break
    return result

async def _run_for_loop(func, plc_str, args, kwargs):
    """处理 for 循环逻辑"""
    # 解析 for 循环次数，例如 "for _ in range(10)" -> 10 次
    loop_count = _parse_for_loop_count(plc_str)
    result = None
    for _ in range(loop_count):
        result = await func(*args, **kwargs)
    return result

def _parse_for_loop_count(plc_str):
    """解析 for 循环次数"""
    # 示例实现：假设 plc_str 是 "for _ in range(10)"
    import re
    match = re.search(r"range\((\d+)\)", plc_str)
    if match:
        return int(match.group(1))
    # 默认执行 1 次
    return 1