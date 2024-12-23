import enum
from dataclasses import dataclass
from typing import Union, List, Dict, Any


@dataclass
class Data:
    data_type: str
    body: Any


@dataclass
class Case:
    plc: str
    inter_type: str
    domain: str
    url: str
    method: str
    headers: Dict[str, Union[str, List[str]]]
    data: Data
    extracts: Dict[str, str]
    asserts: Dict[str, str]
    before_case: List[str]


class MethodType(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class DataType(enum.Enum):
    JSON = "JSON"
    FORM = "FORM"
    XML = "XML"
    TEXT = "TEXT"
    BINARY = "BINARY"
    FILE = "FILE"
    MULTIPART = "MULTIPART"


class InterType(enum.Enum):
    HTTP = "HTTP"
    MySQL = "MySQL"
    REDIS = "REDIS"
    WS = "WS"
