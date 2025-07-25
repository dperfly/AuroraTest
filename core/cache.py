import yaml

from core.logger import info_log
from core.exception import ValueNotFoundError
from core.model import INIT_CACHE, ENV, MYSQL, MySQLConfig, REDIS

_cache = {}
_env = {}

class CacheHandler:
    @staticmethod
    def get_config(key):
        try:
            return _cache[key]
        except KeyError:
            raise ValueNotFoundError(f"{key}未找到，请检查是否将该数据存入")

    @staticmethod
    def update_cache(*, key, value):
        _cache[key] = value

    @staticmethod
    def keys():
        return _cache.keys()

    @staticmethod
    def to_string():
        res = ""
        for k, v in _cache.items():
            res += f"{k}:{v} <br>"
        return res

    @staticmethod
    def get_config_dict():
        return _cache

    @staticmethod
    def init_config_cache(env):
        with open(env, "r", encoding='utf-8') as file:
            data = yaml.safe_load(file)
        for k, v in data.items():
            if k == INIT_CACHE:
                for config_name, config_value in v.items():
                    info_log(f"设置配置: {config_name} = {config_value}")
                    CacheHandler.update_cache(key=config_name, value=config_value)
            if k == ENV:
                for config_name, config_value in v.items():
                    if config_name == MYSQL:
                        _env[MYSQL] = MySQLConfig(**config_value)

                    # if config_name == REDIS:
                    #     RedisConfig(**config_value)

    @staticmethod
    def get_mysql_config():
        return _env.get(MYSQL,None)