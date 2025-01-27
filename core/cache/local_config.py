import yaml

from core.log.logger import INFO
from core.exceptions import ValueNotFoundError

_config = {}


class ConfigHandler:
    @staticmethod
    def get_config(key):
        try:
            return _config[key]
        except KeyError:
            raise ValueNotFoundError(f"{key}未找到，请检查是否将该数据存入")

    @staticmethod
    def update_cache(*, key, value):
        _config[key] = value

    @staticmethod
    def keys():
        return _config.keys()

    @staticmethod
    def to_string():
        res = ""
        for k, v in _config.items():
            res += f"{k}:{v} <br>"
        return res

    @staticmethod
    def get_config_dict():
        return _config

    @staticmethod
    def init_config_cache(env):
        with open(env, "r", encoding='utf-8') as file:
            data = yaml.safe_load(file)
        for k, v in data.items():
            if k == "config":
                for config_name, config_value in v.items():
                    INFO.logger.info(f"设置配置: {config_name} = {config_value}")
                    ConfigHandler.update_cache(key=config_name, value=config_value)
