# AuroraTest

AuroraTest 是一个轻量级、功能强大的接口自动化测试框架，专为高效的API测试与验证而设计。它支持自动化调度和执行测试用例，确保API在不同场景下的稳定性与可靠性。

# 框架的优势

1. 支持并发运行
2. 执行打印用例依赖关系图、打印参数化
3. 支持debug指定的测试用例，并根据该条用例自动找出所有的前置用例，并运行
4. 支持逻辑控制器
5. 可以自定义方法，用于获取时间、md5等方法$func{}
6. 将http、ws、sql、redis等定义为测试步骤，而不是前置后置条件
7. 支持失败用例，终止对应的测试流程，后续流程跳过
8. 更好的协议扩展性

# 用例结构定义

```yaml
login:
  inter_type: http
  domain: ${cache._domain}
  url: /auth/oauth2/token
  method: POST
  headers:
    tenantkey: ${cache._tenant}
    authorization: ${cache._authorization}
  data:
    data_type: FORM
    body: grant_type=password&tenantKey=${cache._tenant}&username=${cache._username}&password=${func.hash_password(cache._password)}&captcha=
  extracts:
    token: $.response.data.data.accessToken.tokenValue
```

# HOOK_FUNC

```python
import base64
from core.plc.hook_base import HookBase


class HookFunc(HookBase):
    case = None  # 这是当前正在执行的测试用例的参数信息，执行对其进行动态修改

    @classmethod
    def add_headers(cls):
        # 对case中的header进行添加"key" 操作
        cls.case.headers["key"] = "value"

    @staticmethod
    def hash_password(password: str) -> str:
        # 这是一个简单的加密示例，可以在编写测试用例时通过 ${func.hash_password("your_password")} 进行引用
        return base64.b64encode(password.encode("utf-8")).decode("utf-8")

    @classmethod
    def before_case(cls) -> None:
        """
        每个用例运行之前运行
        """
        # 对每一个测试用例均进行add_headers操作
        HookFunc.add_headers()

    @classmethod
    def after_case(cls) -> None:
        """
        每个用例运行之后运行
        """
        pass

```

# 快速运行

```python
import hook_func
from core.case.runcase import AsyncRunCase
from core.generate.reader import ReaderCase
from core.cache.local_config import ConfigHandler

# 读取case的目录
raw_data = ReaderCase(folder_path="data").get_all_cases()

# 读取配置的config文件
config = ConfigHandler()
config.init_config_cache("conf.yaml")

# 钩子函数，用于在测试过程中执行
hk = hook_func.HookFunc

AsyncRunCase(raw_data=raw_data, cache=config.get_config_dict(),
             hook_func=hk).run()

```