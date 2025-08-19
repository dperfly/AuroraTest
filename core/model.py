import enum
from dataclasses import dataclass
from typing import Union, List, Dict, Any, Final, Optional
from pydantic import BaseModel
from pydantic.fields import Field

# 虚拟节点，即所有用例的根
VIRTUAL_NODE: Final = "_"
EXTRACT_DELIMITER: Final[str] = "->"
INIT_CACHE: Final[str] = "init_cache"
ENV: Final[str] = "env"
MYSQL: Final[str] = "mysql"
REDIS: Final[str] = "redis"


class InterType(enum.Enum):
    HTTP = "HTTP"
    MYSQL = "MYSQL"
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


class Case(BaseModel):
    desc: str = Field(default="", description="用例功能描述")
    plc: Union[str, None] = Field(default=None, description="用例的逻辑控制器，支持python格式的写法的for range循环")
    inter_type: str = Field(default=InterType.HTTP, description="接口类型HTTP、WS、MYSQL、REDIS")
    domain: str = Field(default="", description="接口的domain,需要包含协议类型例如https://127.0.0.1")
    url: str = Field(default="", description="接口的url路径")
    method: str = Field(default="GET", description="接口的method")
    headers: Dict[str, Union[str, List[str]]] = Field(default_factory=lambda: {},
                                                      description="接口的header，字典形式表示")
    data: Data = Field(default_factory=lambda: Data(data_type="FORM", body=""), description="接口请求的数据")
    extracts: Dict[str, str] = Field(default_factory=lambda: {}, description="接口请求的提取器，为字典形式表示")
    asserts: Dict[str, Union[int, str]] = Field(default_factory=lambda: {},
                                                description="接口请求的断言器，为字典形式表示")
    before_cases: List[str] = Field(default_factory=lambda: [],
                                    description="接口请求的前置用例，在执行该条case前需要先执行完before_cases中的所有请求")

    def __str__(self):
        return self.model_dump_json(indent=2)


# TODO 路径过于复杂，jsonpath写的不是很顺畅
#  eg: $.response.data.data.accessToken.tokenValue 其中response.data 有些多余

class Response(BaseModel):
    data: Any = Field(default=None, description="响应返回的数据")
    headers: Dict[str, Union[str, List[str]]] = Field(default=None, description="响应headers")
    status_code: int = Field(default=None, description="响应状态码")


class RespData(BaseModel):
    request: Case
    response: Response


class SelectCase(BaseModel):
    """ 用例过滤条件, 用于筛选用例 """
    case_names: List[str] = Field(default=[], description="通过用例名称进行过滤")
    file_names: List[str] = Field(default=[], description="通过文件名称进行过滤")
    dir_names: List[str] = Field(default=[], description="通过目录名称进行过滤")


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
    method: str = 'GET'  # 'get', 'post', 'put', 'delete', etc.
    status: str = 'passed'  # 'passed', 'failed', 'skipped'
    params: List[ReportParam] = Field(default_factory=lambda: [])
    headers: List[ReportHeader] = Field(default_factory=lambda: [])
    logs: List[ReportLogEntry] = Field(default_factory=lambda: [])
    request: Any = None
    response: Any = None
    assertions: List[ReportAssertion] = Field(default_factory=lambda: [])


class TestSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0


class TestReport(BaseModel):
    start_time: str = None
    summary: TestSummary = Field(default_factory=TestSummary)
    test_cases: List[TestCaseRunResult] = Field(default_factory=lambda: [])


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

