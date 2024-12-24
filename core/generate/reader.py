import os
import yaml
from typing import Dict, List
from dacite import from_dict

from core.models.model import Case, Data
from core.utils.exceptions.exceptions import DuplicateCaseError


class ReaderCase:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def get_all_yaml_files(self) -> List[str]:
        yaml_filepaths = []
        for root, dirs, files in os.walk(self.folder_path):
            for _file_path in files:
                path = os.path.join(root, _file_path)
                if 'yaml' in path or '.yml' in path:
                    yaml_filepaths.append(path)
        return yaml_filepaths

    def get_all_cases(self) -> Dict[str, Case]:
        cases = {}
        yaml_filepaths = self.get_all_yaml_files()
        for filepath in yaml_filepaths:
            new_cases = self.read_yaml(filepath)

            # 需要判断用来名字是否存在，如果存在相同的则抛异常
            if common_keys := set(cases.keys()) & set(new_cases.keys()):
                raise DuplicateCaseError(common_keys)
            cases = {**cases, **new_cases}
        return cases

    @staticmethod
    def read_yaml(file_path) -> Dict[str, Case]:
        case_dict = {}
        if not os.path.exists(file_path):
            return case_dict

        data = open(file_path, 'r', encoding='utf-8')
        for k, v in yaml.load(data, Loader=yaml.FullLoader).items():
            case_dict[k] = from_dict(data_class=Case, data=v)

        return case_dict
