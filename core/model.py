import enum
from dataclasses import dataclass, field
from typing import Union, List, Dict, Any, Final, Optional
from pydantic import BaseModel

# 虚拟节点，即所有用例的根
VIRTUAL_NODE: Final = "_"
EXTRACT_DELIMITER: Final[str] = "->"
INIT_CACHE: Final[str] = "init_cache"
ENV : Final[str] = "env"
MYSQL: Final[str] = "mysql"
REDIS: Final[str] = "redis"

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
    data_type: str = "JSON"
    body: Any = None

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


# TODO 路径过于复杂，jsonpath写的不是很顺畅
#  eg: $.response.data.data.accessToken.tokenValue 其中response.data 有些多余

@dataclass
class Response:
    data: Any = None
    headers: Dict[str, Union[str, List[str]]] = None
    status_code: int = None


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


# 测试报告相关数据结构
# ReportParam ReportHeader ReportLogEntry ReportAssertion TestCaseRunResult TestSummary TestReport
class ReportParam(BaseModel):
    name: str = None
    value: Union[str, int, float, bool, dict, list] = None
    type: str = None
    required: bool = None


class ReportHeader(BaseModel):
    name: str = None
    value: str = None


class ReportLogEntry(BaseModel):
    time: str = None
    level: str = None  # 'info', 'error', 'warning'
    message: str = None


class ReportAssertion(BaseModel):
    name: str = None
    passed: bool = False
    message: str = None


class TestCaseRunResult(BaseModel):
    case_id: str = None
    name: str = None
    group: str = '未分组'
    api_name: str = None
    url: str = None
    method: str = None  # 'get', 'post', 'put', 'delete', etc.
    status: str = 'passed'  # 'passed', 'failed', 'skipped'
    params: List[ReportParam] = field(default_factory=lambda: [])
    headers: List[ReportHeader] = field(default_factory=lambda: [])
    logs: List[ReportLogEntry] = field(default_factory=lambda: [])
    request: Any = None
    response: Any = None
    assertions: List[ReportAssertion] = field(default_factory=lambda: [])


class TestSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0


class TestReport(BaseModel):
    start_time: str = None
    summary: TestSummary = field(default_factory=TestSummary)
    test_cases: List[TestCaseRunResult] = field(default_factory=lambda: [])


class SSHConfig(BaseModel):
    ip: str
    username: str
    port: int = 22
    password: Optional[str] = None
    pkey: Optional[str] = None


class MySQLConfig(BaseModel):
    username: str
    password: str
    ip: str = "127.0.0.1"
    port: int = 3306
    ssh: Optional[SSHConfig] = None

