import enum
from dataclasses import dataclass, field
from typing import Union, List, Dict, Any, Text, Optional, Final

# 虚拟节点，即所有用例的根
VIRTUAL_NODE: Final = "_"
EXTRACT_DELIMITER: Final[str] = "->"
INIT_CACHE : Final[str] = "init_cache"

class InterType(enum.Enum):
    HTTP = "HTTP"
    MySQL = "MySQL"
    REDIS = "REDIS"
    WS = "WS"


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


class ContentType(enum.Enum):
    # 常见的文本类型
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    TEXT_CSS = "text/css"
    TEXT_JAVASCRIPT = "text/javascript"

    # 常见的应用类型
    APPLICATION_JSON = "application/json"
    APPLICATION_XML = "application/xml"
    APPLICATION_FORM_URLENCODED = "application/x-www-form-urlencoded"
    APPLICATION_JAVASCRIPT = "application/javascript"
    APPLICATION_PDF = "application/pdf"
    APPLICATION_ZIP = "application/zip"


@dataclass
class Data:
    data_type: str
    body: Any

    def __str__(self):
        return f"data_type:{self.data_type} body:{self.body}\n"


@dataclass
class Case:
    desc: str = ""
    plc: Union[str, None] = None
    inter_type: str = "HTTP"
    domain: str = None
    url: str = None
    method: str = "GET"
    headers: Dict[str, Union[str, List[str]]] = field(default_factory=lambda: {})
    data: Data = field(default_factory=lambda: Data(data_type="FORM", body=""))
    extracts: Dict[str, str] = field(default_factory=lambda: {})
    asserts: Dict[str, str] = field(default_factory=lambda: {})
    before_cases: List[str] = field(default_factory=lambda: [])

    def __str__(self):
        headers = [f"{k}:{v}" for k, v in self.headers.items()]
        extracts = [f"{k}:{v}" for k, v in self.extracts.items()]
        asserts = [f"{k}:{v}" for k, v in self.asserts.items()]
        res = f"""                                                              
|---------------|-------------------------------------------------------------------
| desc          | {self.desc}  
| domain        | {self.domain}                                                     
| url           | {self.url}                                                        
| method        | {self.method}                                                     
| headers       | {headers}                                                         
| data          | {self.data.data_type}:{self.data.body}
| plc           | {self.plc}                                                        
| inter_type    | {self.inter_type}                                                 
| extracts      |{extracts}                                                         
| asserts       |{asserts}                                                          
|---------------|-------------------------------------------------------------------"""
        return res


@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text


@enum.unique
class AllureAttachmentType(enum.Enum):
    """allure 文件类型"""
    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"
    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"
    PDF = "pdf"

# TODO 路径过于复杂，jsonpath写的不是很顺畅
#  eg: $.response.data.data.accessToken.tokenValue 其中response.data 有些多余

@dataclass
class Response:
    data: Any
    headers: Dict[str, Union[str, List[str]]]
    status_code: int


@dataclass
class RespData:
    request: Case
    response: Response


@dataclass
class SelectCase:
    """ 用例过滤条件, 用于筛选用例 """
    case_names: List[str] = field(default_factory=lambda: [])
    file_names: List[str] = field(default_factory=lambda: [])
    dir_names: List[str] = field(default_factory=lambda: [])
