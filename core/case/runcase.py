import asyncio
from dataclasses import asdict
from datetime import datetime

from core import hook_base
from core.case.controller import CaseController
from core.generate.generate import TestCaseAutomaticGeneration
from core.html_report import CompactHTMLTestReportGenerator
from core.logger import INFO, ERROR
from core.model import TestReport, TestCaseRunResult, VIRTUAL_NODE


class AsyncRunCase:
    def __init__(self, raw_data, cache, hook_func):
        self.cache = cache
        if isinstance(hook_func, type) and issubclass(hook_func, hook_base.HookBase):
            self.hook_func = hook_func
        else:
            raise TypeError('hook_func must be a subclass of hook_base.HookBase')
        self.t_c_a_g = TestCaseAutomaticGeneration(raw_data)
        # 这里我们弄个桶模式，每一个桶从编号小到编号大逐个运行，同一个桶中的case支持并发运行，需要同一个桶中的case全部执行完成，再运行下一个桶的case
        self.barrels = self.t_c_a_g.get_case_runner_order()
        INFO.logger.info(f"Barrels:{self.barrels.items()}")
        self.sorted_orders = sorted(self.barrels.keys(), reverse=True)
        INFO.logger.info(f"sorted_orders:{self.sorted_orders}")
        self.all_case_map = self.t_c_a_g.get_all_case_map()
        self.global_semaphore = asyncio.Semaphore(5)  # 全局并发控制
        INFO.logger.info(f"Execution order - Barrels: {self.barrels.items()}")
        INFO.logger.info(f"Sorted priority orders: {self.sorted_orders}")

        self.report = TestReport(start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    async def __async_run_case(self, case_name):
        """带错误处理和资源控制的单个用例执行"""
        if case_name == VIRTUAL_NODE:
            return
        test_run_result = TestCaseRunResult()
        test_run_result.case_id = case_name
        test_run_result.group = self.t_c_a_g.get_case_group(case_name)
        try:
            async with self.global_semaphore:
                if case := self.all_case_map.get(case_name):
                    INFO.logger.info(f"Running case: {case_name}")
                    # 假设已实现异步版本的controller
                    await CaseController(old_case=case, cache=self.cache, func=self.hook_func,
                                         test_run_result=test_run_result, summary=self.report.summary).controller()
        except Exception as e:
            ERROR.logger.error(f"Case {case_name} failed: {str(e)}")
            # 可选：将错误信息存入self.cache供后续用例使用
            self.cache[f"{case_name}_error"] = str(e)

        self.report.test_cases.append(test_run_result)

    async def __run_barrel(self, order):
        """并发执行同一个桶内的所有用例"""
        tasks = [
            self.__async_run_case(case_name)
            for case_name in self.barrels[order]
        ]
        await asyncio.gather(*tasks)

    async def __run_all_cases(self):
        """按优先级顺序执行所有桶"""
        for order in self.sorted_orders:
            INFO.logger.info(f"Start running cases in priority group: {order}")
            await self.__run_barrel(order)

    def run(self):
        """同步入口方法"""

        asyncio.run(self.__run_all_cases())

        generator = CompactHTMLTestReportGenerator(self.report.dict())
        generator.save_report("html_report.html")
