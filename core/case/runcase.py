import asyncio

from core.case.controller import CaseController
from core.generate.generate import TestCaseAutomaticGeneration


class AsyncRunCase:
    def __init__(self, raw_data, cache, hook_func):
        self.cache = cache
        self.hook_func = hook_func
        t_c_a_g = TestCaseAutomaticGeneration(raw_data)
        self.barrels = t_c_a_g.get_case_runner_order()
        print("Barrels:", self.barrels)
        self.sorted_orders = sorted(self.barrels.keys())
        self.all_case_map = t_c_a_g.get_all_case_map()

    async def __async_semaphore_run(self, case_name, semaphore):
        async with semaphore:
            case = self.all_case_map.get(case_name)
            print("case_name:", case_name)
            CaseController(old_case=case, cache=self.cache, func=self.hook_func).controller()

    async def __run_case(self):
        for order in self.sorted_orders:
            semaphore = asyncio.Semaphore(5)
            tasks = [self.__async_semaphore_run(case_name, semaphore) for case_name in self.barrels[order]]
            await asyncio.gather(*tasks)

    def run(self):
        asyncio.run(self.__run_case())
