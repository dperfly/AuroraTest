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
  plc: for _ in range(len($cache{loopNum})) #  while $cache{_loop} / if $config{_env} = "dev"
  inter_type: http  # 协议类型 http(s) / ws(s) / sql / redis ...
  domain: ${_domain}
  url: /login
  method: GET / POST ...
  header:
    token: $cache{_token}
  data: #用于数据的发送 字典、字符串等
    data_type: json / text / params / file
    body:
      uuid: $func{get_uuid()} # 自定义方法的使用
      file: $file{image.jpg}  # 用于文件上传
  asserts:
    status: resp$.status = 200
    code: resp$.data.code = 0
  extracts:
    token: resp$.header.set_cookie.token   # 提取请求中的token并以token的名字存入缓存
    uuid: req$.data.uuid # 从请求中的data提取uuid
  before_case: # 用于强制用例关联关系的创建
    - beforeCaseName
```

    