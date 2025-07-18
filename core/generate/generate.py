import copy
import json
import os
from collections import defaultdict
from typing import Dict

from dacite import from_dict
from mako.template import Template
from dataclasses import asdict, dataclass

from core.exception import GenerateCaseError
from core.generate.reader import ReaderCase
from core.model import Case, SelectCase, VIRTUAL_NODE
from core.utils.path import data_path


class DictToClass:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


class Parametric:
    """case参数化"""

    def __init__(self, cache: dict, func: callable):
        self.cache = cache
        self.func = func

    def use_params(self, case: Case) -> Case:
        """参数化"""
        json_str = json.dumps(asdict(case))
        temp = Template(json_str)
        json_str = temp.render(cache=DictToClass(self.cache), func=self.func)
        dicts = json.loads(json_str)
        return from_dict(data_class=Case, data=dicts)


@dataclass
class CaseCacheMap:
    used: list[str]
    generated: list[str]
    before_cases: list[str]


class TestCaseAutomaticGeneration:
    """
    1.读取每个yaml的 file_name 和 file_content
    2.遍历每一个yaml文件
        （1）获取到fileName和caseName 的map关系
        （2）拿到所有case中使用缓存的名字
        （3）拿到所有case中生产缓存的名字 extracts的key
    3.将环境config作为__init_cache
    4.消消乐，确定是否有case中的缓存没有办法取到,同时获取到用例之间的先后顺序关系
        （1）显式的依赖关系：before_case
        （2）隐式的依赖关系：${cache.x}
    5.没有使用cache的case会先运行，使用了cache的case需要等待对应的cache已经存在于cache中才可以进行执行,通过order来判断
      需要借助pytest_order插件实现? 这种方式后面可能无法并发运行

    """

    def __init__(self, raw_data=None, select_cases: SelectCase = None):
        # 每个yaml的 绝对路径 和 该文件的所有Case对象 的map集合
        if raw_data is None:
            self.raw_data = ReaderCase(data_path()).get_all_cases()
        else:
            self.raw_data: Dict[str, Dict[str, Case]] = raw_data
        # file_dir + "_" + yaml_name 和 case_name 的映射关系
        self.yaml_cases: Dict[str, set[str]] = {}
        # 每个case使用到的缓存和生成的缓存
        self.cases_use_cache_dict: dict[str, CaseCacheMap] = {}
        # 用例关系网 key -> values
        self.cases_graph_map: dict[str, set[str]] = {}
        # 所有 case 字典
        self.all_case_map: dict[str, Case] = {}
        # caseName 对应的文件
        self.cases_file_group: Dict[str, str] = {}

        for file_ab_path, file_cases in self.raw_data.items():
            # 获取到fileName和caseName 的map关系
            yaml_name = os.path.splitext(os.path.split(file_ab_path)[-1])[0]
            dir_name = os.path.split(os.path.split(file_ab_path)[0])[-1]
            cases_name = set(file_cases.keys())
            self.yaml_cases[dir_name + "_" + yaml_name] = cases_name

            for case_name, case_value in file_cases.items():
                # 添加到all_case_map
                self.all_case_map[case_name] = case_value
                self.cases_file_group[case_name] = dir_name
                # 拿到所有case中使用缓存的名字和生成缓存的名字
                used_caches = ReaderCase.get_cache_name(str(case_value))
                generated_caches = list(case_value.extracts.keys())

                # 拿到用例之间的显式依赖关系
                for before_case in case_value.before_cases:
                    if self.cases_graph_map.get(before_case):
                        self.cases_graph_map[before_case].add(case_name)
                    else:
                        self.cases_graph_map[before_case] = {case_name, }
                else:
                    # 用例没有before_case 则归为 VIRTUAL_NODE 下
                    if not self.cases_graph_map.get(VIRTUAL_NODE):
                        self.cases_graph_map[VIRTUAL_NODE] = {case_name, }
                    else:
                        self.cases_graph_map[VIRTUAL_NODE].add(case_name)

                self.cases_use_cache_dict[case_name] = CaseCacheMap(used=used_caches, generated=generated_caches,
                                                                    before_cases=case_value.before_cases)

        # 完善cases_graph_map, 找到隐式关系网
        for generated_case_name, generated_case_cache_map in self.cases_use_cache_dict.items():
            # 通过当前用例可以产生的数据找到所有使用该数据的case
            for used_case_name, used_case_cache_map in self.cases_use_cache_dict.items():
                if generated_case_name != used_case_name and bool(
                        set(generated_case_cache_map.generated) & set(used_case_cache_map.used)):
                    if self.cases_graph_map.get(generated_case_name):
                        self.cases_graph_map[generated_case_name].add(used_case_name)
                    else:
                        self.cases_graph_map[generated_case_name] = {used_case_name, }

        # 过滤需要执行的case
        def select_cases_helper(cases_graph_map: dict[str, set[str]]):
            """
            cases_graph_map: 用例关系图
            通过select_cases来过滤case，从而指定需要执行的case，而不是全部执行
            """
            # 1.将case_files和case_dirs转换为case_names 并添加到used_cases中
            used_cases = set()
            if select_cases:
                for yaml_case in self.yaml_cases.keys():
                    dir_name, file_name = yaml_case.split("_")[0], str.join("_", yaml_case.split("_")[1:])
                    if dir_name in select_cases.dir_names or file_name in select_cases.file_names:
                        used_cases = used_cases.union(set(self.yaml_cases[yaml_case]))
                used_cases = used_cases.union(set(select_cases.case_names))
            # 2.过滤case_name,生产新的cases_graph_map
            new_cases_graph_map = {}

            while used_cases:
                next_cases = set()
                for k, v in cases_graph_map.items():

                    for used_case in used_cases:
                        if used_case == VIRTUAL_NODE:
                            continue
                        if used_case in v:
                            if new_cases_graph_map.get(k):
                                new_cases_graph_map[k].add(used_case)
                            else:
                                new_cases_graph_map[k] = {used_case,}
                            # 添加本轮所有的父节点，下一轮继续使用
                            next_cases.add(k)
                used_cases = next_cases
            return new_cases_graph_map if new_cases_graph_map else cases_graph_map

        self.cases_graph_map = select_cases_helper(self.cases_graph_map)


    def get_cases_graph_map(self):
        return self.cases_graph_map

    def get_case_runner_order(self):
        """获取用例执行顺序关系,数字大的是先执行的用例，如果需要结合pytest order插件，需要反转一下"""
        # 序号桶
        barrels: dict[int, set[str]] = defaultdict(set)

        # 这里进行深拷贝，为了不对self.cases_graph_map产生影响，选择复制一份
        graph = copy.deepcopy(self.cases_graph_map)

        cur = 1
        while True:
            copy_graph = copy.deepcopy(graph)
            if not copy_graph:
                break

            # 需要对before进行处理,before对应的after是空的时，添加到桶中
            for before_case, after_cases_name in copy_graph.items():
                if len(after_cases_name) == 0:
                    # 处理没有依赖关系的before_case
                    graph.pop(before_case)
                    barrels[cur].add(before_case)
            copy_graph = copy.deepcopy(graph)

            for before_case, after_cases_name in copy_graph.items():
                # 对已经提取的数据进行删除清理操作
                tmp = set()
                # 针对after处理
                for after_case_name in after_cases_name:
                    # 如果case_name不存在于key中，说明是最后执行的testcase，进行添加到序号桶中，然后标记这个case_name已经清除了
                    if copy_graph.get(after_case_name) is None or len(copy_graph.get(after_case_name)) == 0:
                        barrels[cur].add(after_case_name)
                    else:
                        tmp.add(after_case_name)
                graph[before_case] = tmp
            # 如果桶里边没东西，说明存在环状相互引用的结构
            if len(barrels[cur]) == 0:
                raise GenerateCaseError(f"引用关系存在环,{copy_graph}")

            cur += 1

        return barrels

    def get_all_case_name(self):
        res = []
        for cases in self.raw_data.values():
            for k in cases.keys():
                res.append(k)
        return res

    def get_all_case_map(self) -> dict[str, Case]:
        return self.all_case_map

    def get_all_edges(self):
        res: list[tuple] = []
        for before, afters in self.cases_graph_map.items():
            for after in afters:
                res.append((before, after))
        return res

    def get_all_cases(self):
        res = {}
        for cases in self.raw_data.values():
            for k, v in cases.items():
                res[k] = v
        return res

    def get_case_group(self, case_name):
        return self.cases_file_group.get(case_name,"未分组")