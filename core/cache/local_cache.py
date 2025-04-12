import json

from core.exceptions import ValueNotFoundError

_cache = {}


class CacheHandler:
    @staticmethod
    def get_cache(cache_data):
        try:
            return _cache[cache_data]
        except KeyError:
            raise ValueNotFoundError(f"{cache_data}的缓存数据未找到，请检查是否将该数据存入缓存中")

    @staticmethod
    def update_cache(*, cache_name, value):
        _cache[cache_name] = value

    @staticmethod
    def keys():
        return _cache.keys()

    @staticmethod
    def get_cache_json():
        return json.dumps(_cache, indent=4)

    @staticmethod
    def get_all_cache():
        return _cache
