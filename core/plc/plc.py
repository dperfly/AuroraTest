import functools
import json
import threading

from core.utils.exceptions.exceptions import IFException, WhileException


def loop_control(plc_str, timeout=None, asserts=None):
    """
    接受类似 "for _ in range(10)" 的字符串并动态执行，并添加超时时间
    :param iterable_str: 类似 "for _ in range(10)" 的字符串
    :param timeout: 超时时间，单位为秒。如果设置为 None，则不限制时间。
    while True :会根据断言结果进行判断是否需要进行循环，如果在timeout之前未断言成功则结束循环返回最后一次的执行结果
    for : for循环不会进行结果判断，做指定次数的循环，然后返回最后一次的结果，希望用于”post“请求
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            is_while_true = False
            stop_event = threading.Event()  # 用于指示何时停止
            if plc_str.startswith("if"):
                raise IFException
            if plc_str.startswith("while "):
                is_while_true = True
            if is_while_true and timeout is None:
                raise WhileException
            loop_control_str = plc_str
            result_container = {"res": None}  # 用字典存储返回值

            def target():
                exec(f"""
{loop_control_str}:
    result_container['res'] = func(*args, **kwargs)
    if stop_event.is_set():
        break
    try:
        if is_while_true:
            break
    except:
        pass
                """, {
                    "func": func,
                    "args": args,
                    "kwargs": kwargs,
                    "stop_event": stop_event,
                    "asserts": asserts,
                    "result_container": result_container,
                    "is_while_true": is_while_true,
                })

            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout)  # 等待指定的超时时间

            if thread.is_alive():
                stop_event.set()  # 触发事件，通知目标线程停止

            return result_container["res"]  # 返回存储在字典中的结果

        return wrapper

    return decorator
