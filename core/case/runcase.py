import asyncio
from core.case.controller import CaseController
from core.generate.generate import TestCaseAutomaticGeneration
from core.log.logger import INFO, ERROR


class AsyncRunCase:
    def __init__(self, raw_data, cache, hook_func):
        self.cache = cache
        self.hook_func = hook_func
        t_c_a_g = TestCaseAutomaticGeneration(raw_data)
        # 这里我们弄个桶模式，每一个桶从编号小到编号大逐个运行，同一个桶中的case支持并发运行，需要同一个桶中的case全部执行完成，再运行下一个桶的case
        self.barrels = t_c_a_g.get_case_runner_order()
        INFO.logger.info(f"Barrels:{self.barrels.items()}")
        self.sorted_orders = sorted(self.barrels.keys(), reverse=True)
        INFO.logger.info(f"sorted_orders:{self.sorted_orders}")
        self.all_case_map = t_c_a_g.get_all_case_map()
        self.global_semaphore = asyncio.Semaphore(5)  # 全局并发控制

        INFO.logger.info(f"Execution order - Barrels: {self.barrels.items()}")
        INFO.logger.info(f"Sorted priority orders: {self.sorted_orders}")

    async def __async_run_case(self, case_name):
        """带错误处理和资源控制的单个用例执行"""
        try:
            async with self.global_semaphore:
                if case := self.all_case_map.get(case_name):
                    INFO.logger.info(f"Running case: {case_name}")
                    # 假设已实现异步版本的controller
                    await CaseController(old_case=case, cache=self.cache, func=self.hook_func).controller()
        except Exception as e:
            ERROR.logger.error(f"Case {case_name} failed: {str(e)}")
            # 可选：将错误信息存入self.cache供后续用例使用
            self.cache[f"{case_name}_error"] = str(e)

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
