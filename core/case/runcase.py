import asyncio

from core.case.controller import CaseController
from core.generate.generate import TestCaseAutomaticGeneration
from core.log.logger import INFO


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

    async def __async_semaphore_run(self, case_name, semaphore):
        async with semaphore:
            if case := self.all_case_map.get(case_name):
                INFO.logger.info(f"run case:{case_name}")
                CaseController(old_case=case, cache=self.cache, func=self.hook_func).controller()

    async def __run_case(self):
        for order in self.sorted_orders:
            semaphore = asyncio.Semaphore(5)
            tasks = [self.__async_semaphore_run(case_name, semaphore) for case_name in self.barrels[order]]
            await asyncio.gather(*tasks)

    def run(self):
        asyncio.run(self.__run_case())
