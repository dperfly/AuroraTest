# AuroraTest Web 前端使用说明

## 启动服务

```bash
python web_server.py
```

服务启动后，访问: http://localhost:8000

## 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 功能模块

### 1. 登录页面
- JWT Token 认证
- 本地存储 Token，刷新页面无需重新登录

### 2. 仪表盘
- 展示测试用例统计
- 总用例数、HTTP用例数、SQL用例数、最近执行数
- 快速导航入口

### 3. 测试用例管理
- 树状结构展示测试用例（按文件分组）
- 搜索过滤功能
- 新建测试用例
- 编辑测试用例（支持修改所有字段：描述、接口类型、domain、url、方法、plc、headers、请求数据、提取器、断言器、前置用例）
- 删除测试用例

### 4. 执行测试
- 按用例名称选择执行
- 按文件名称选择执行
- 按目录名称选择执行
- 实时显示执行状态
- 展示测试结果（通过/失败/跳过）
- 断言详情展示

### 5. 测试报告
- 展示最近执行的测试报告
- 汇总统计（总数/通过/失败/跳过）
- 可下载 JSON 格式的完整报告

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/token | 登录获取Token |
| GET | /api/users/me | 获取当前用户信息 |
| GET | /api/testcases | 获取所有测试用例列表 |
| GET | /api/testcases/{path}/{name} | 获取单个测试用例详情 |
| POST | /api/testcases/{path} | 创建测试用例 |
| PUT | /api/testcases/{path}/{name} | 更新测试用例 |
| DELETE | /api/testcases/{path}/{name} | 删除测试用例 |
| POST | /api/execute | 执行测试用例 |
| GET | /api/config | 获取配置信息 |

## 技术栈

- **后端**: FastAPI + Uvicorn
- **前端**: Vue 3 + Tailwind CSS + RemixIcon
- **认证**: JWT (JSON Web Token)

## 文件结构

```
AuroraTest/
├── web_server.py          # Web服务主文件
├── web/
│   └── index.html         # 前端页面
├── testcase/              # 测试用例目录
└── requirements.txt       # 依赖列表
```
