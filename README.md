# auto-verifyer

auto-verifyer 是一个轻量级、功能强大的接口自动化测试框架，专为高效的API测试与验证而设计。它支持自动化调度和执行测试用例，确保API在不同场景下的稳定性与可靠性。

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
caseName:
  plc: for _ in range(len(${cache.loopNum}))
  inter_type: http
  domain: ${cache._domain}
  url: /login
  method: POST
  headers:
    token: ${cache._token}
  data:
    data_type: text
    body:
      uuid: ${func.add(1,1)}
      file: ${func.get_image('image.jpg')}
  asserts:
    status: resp$.status = 200
    code: resp$.data.code = 0
  extracts:
    token: resp$.header.set_cookie.token
    uuid: req$.data.uuid
  before_case:
    - beforeCaseName
```
