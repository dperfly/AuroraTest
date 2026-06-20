"""AuroraTest backend API routes."""
import os
import json
import yaml
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import hook_func
from core.case.runcase import AsyncRunCase
from core.generate.reader import ReaderCase
from core.cache import CacheHandler
from core.html_report import CompactHTMLTestReportGenerator
from core.model import SelectCase, TestReport, Case
from core.utils.path import hook_backup_path

# ==================== 配置 ====================
SECRET_KEY = "auroratest-secret-key-2024-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

TESTCASE_FOLDER = "testcase"
CONFIG_FILE = "conf.yaml"
REPORT_FOLDER = os.path.join("log", "reports")

# ==================== 路由 ====================
router = APIRouter()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# 模拟用户数据库
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "hashed_password": pwd_context.hash("admin123"),
        "disabled": False,
    }
}

# ==================== 数据模型 ====================
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class TestCaseItem(BaseModel):
    name: str
    path: str
    desc: Optional[str] = None
    inter_type: Optional[str] = None


class TestCaseFile(BaseModel):
    filename: str
    path: str
    cases: List[TestCaseItem]


class TestCaseDetail(BaseModel):
    name: str
    file_path: str
    content: Dict


class ExecuteRequest(BaseModel):
    case_names: List[str] = []
    file_names: List[str] = []
    dir_names: List[str] = []


class DirectoryCreateRequest(BaseModel):
    path: str


class YamlFileCreateRequest(BaseModel):
    path: str


class HookFileSaveRequest(BaseModel):
    content: str


# ==================== 认证相关函数 ====================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user["disabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def testcase_path(relative_path: str) -> Path:
    normalized_path = relative_path.strip().replace("\\", "/").lstrip("/")
    if not normalized_path:
        raise HTTPException(status_code=400, detail="Path is required")

    base_path = Path(TESTCASE_FOLDER).resolve()
    target_path = (base_path / normalized_path).resolve()
    if base_path not in target_path.parents and target_path != base_path:
        raise HTTPException(status_code=400, detail="Invalid path")
    return target_path


# ==================== API 路由 ====================

@router.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录获取token"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/api/users/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.get("/api/testcases")
async def get_testcases(current_user: dict = Depends(get_current_active_user)):
    """获取所有测试用例列表"""
    try:
        result = []
        # 直接从文件系统读取，避免 Case 对象转换问题
        testcase_dir = Path(TESTCASE_FOLDER)
        for yaml_file in testcase_dir.rglob("*.yaml"):
            rel_path = str(yaml_file.relative_to(testcase_dir))
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}

                file_item = {
                    "filename": os.path.basename(rel_path),
                    "path": rel_path,
                    "cases": []
                }

                for case_name, case_data in data.items():
                    if isinstance(case_data, dict):
                        file_item["cases"].append({
                            "name": case_name,
                            "desc": case_data.get("desc", ""),
                            "inter_type": case_data.get("inter_type", "http")
                        })
                    else:
                        # 如果是 Case 对象，尝试转换
                        case_dict = case_data.model_dump() if hasattr(case_data, 'model_dump') else {}
                        file_item["cases"].append({
                            "name": case_name,
                            "desc": case_dict.get("desc", ""),
                            "inter_type": case_dict.get("inter_type", "http")
                        })

                result.append(file_item)
            except Exception as e:
                print(f"Error reading {yaml_file}: {e}")
                continue
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/testcase-dirs")
async def get_testcase_dirs(current_user: dict = Depends(get_current_active_user)):
    """获取 testcase 下的所有目录"""
    testcase_dir = Path(TESTCASE_FOLDER)
    dirs = ["."]
    if testcase_dir.exists():
        for item in testcase_dir.rglob("*"):
            if item.is_dir():
                dirs.append(str(item.relative_to(testcase_dir)))
    return dirs


@router.post("/api/testcase-dirs")
async def create_testcase_dir(
    req: DirectoryCreateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """在 testcase 下创建目录"""
    target_path = testcase_path(req.path)
    if target_path.exists() and not target_path.is_dir():
        raise HTTPException(status_code=400, detail="Path exists and is not a directory")
    target_path.mkdir(parents=True, exist_ok=True)
    return {"success": True, "path": str(target_path.relative_to(Path(TESTCASE_FOLDER).resolve()))}


@router.post("/api/testcase-files")
async def create_testcase_yaml_file(
    req: YamlFileCreateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """在 testcase 下创建 YAML 文件"""
    file_path = req.path.strip().replace("\\", "/")
    if not file_path.endswith((".yaml", ".yml")):
        file_path = f"{file_path}.yaml"

    target_path = testcase_path(file_path)
    if target_path.exists():
        raise HTTPException(status_code=400, detail="YAML file already exists")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("{}\n", encoding="utf-8")
    return {"success": True, "path": str(target_path.relative_to(Path(TESTCASE_FOLDER).resolve()))}


@router.get("/api/testcases/{file_path:path}/{case_name}")
async def get_testcase_detail(
    file_path: str,
    case_name: str,
    current_user: dict = Depends(get_current_active_user)
):
    """获取单个测试用例详情"""
    try:
        full_path = os.path.join(TESTCASE_FOLDER, file_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if case_name not in data:
            raise HTTPException(status_code=404, detail="TestCase not found")

        return {
            "name": case_name,
            "file_path": file_path,
            "content": data[case_name]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/testcases/{file_path:path}")
async def create_testcase(
    file_path: str,
    case_data: Dict,
    current_user: dict = Depends(get_current_active_user)
):
    """创建测试用例"""
    try:
        full_path = os.path.join(TESTCASE_FOLDER, file_path)

        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 读取现有文件或创建新文件
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        case_name = case_data.pop("name")
        data[case_name] = case_data

        with open(full_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        return {"success": True, "message": "TestCase created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/testcases/{file_path:path}/{case_name}")
async def update_testcase(
    file_path: str,
    case_name: str,
    case_data: Dict,
    current_user: dict = Depends(get_current_active_user)
):
    """更新测试用例"""
    try:
        full_path = os.path.join(TESTCASE_FOLDER, file_path)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        if case_name not in data:
            raise HTTPException(status_code=404, detail="TestCase not found")

        # 如果name改变了，需要删除旧的
        new_name = case_data.pop("name", case_name)
        if new_name != case_name:
            del data[case_name]
            case_name = new_name

        data[case_name] = case_data

        with open(full_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        return {"success": True, "message": "TestCase updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/testcases/{file_path:path}/{case_name}")
async def delete_testcase(
    file_path: str,
    case_name: str,
    current_user: dict = Depends(get_current_active_user)
):
    """删除测试用例"""
    try:
        full_path = os.path.join(TESTCASE_FOLDER, file_path)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        if case_name not in data:
            raise HTTPException(status_code=404, detail="TestCase not found")

        del data[case_name]

        with open(full_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        return {"success": True, "message": "TestCase deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/execute")
async def execute_tests(
    req: ExecuteRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """执行测试用例"""
    try:
        # 读取用例
        raw_data = ReaderCase(folder_path=TESTCASE_FOLDER).get_all_cases()

        # 读取配置
        config = CacheHandler()
        config.init_config_cache(CONFIG_FILE)

        # 选择要执行的用例
        select_cases = SelectCase(
            case_names=req.case_names,
            file_names=req.file_names,
            dir_names=req.dir_names
        )

        # 执行测试
        runner = AsyncRunCase(
            raw_data=raw_data,
            cache=config.get_config_dict(),
            hook_func=hook_func.HookFunc,
            select_cases=select_cases
        )
        report = await runner.fastapi_run()
        report_data = report.model_dump()

        report_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        report_dir = Path(REPORT_FOLDER)
        report_dir.mkdir(parents=True, exist_ok=True)
        html_report_path = report_dir / f"{report_id}.html"
        json_report_path = report_dir / f"{report_id}.json"

        html_content = CompactHTMLTestReportGenerator(report_data).generate_report()
        html_report_path.write_text(html_content, encoding="utf-8")
        Path("html_report.html").write_text(html_content, encoding="utf-8")

        record = {
            "id": report_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": report_data.get("summary", {}),
            "select_cases": req.model_dump(),
            "html_path": str(html_report_path),
            "json_path": str(json_report_path),
            "report": report_data
        }
        json_report_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        report_data["report_id"] = report_id
        report_data["created_at"] = record["created_at"]
        report_data["html_report"] = html_content

        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/config")
async def get_config(current_user: dict = Depends(get_current_active_user)):
    """获取配置信息"""
    try:
        config = CacheHandler()
        config.init_config_cache(CONFIG_FILE)
        return config.get_config_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/hook-file")
async def get_hook_file(current_user: dict = Depends(get_current_active_user)):
    """读取 hook_func.py 文件内容"""
    hook_path = Path("hook_func.py")
    if not hook_path.exists():
        raise HTTPException(status_code=404, detail="hook_func.py not found")
    return {
        "content": hook_path.read_text(encoding="utf-8"),
        "modified_time": datetime.fromtimestamp(hook_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }


@router.post("/api/hook-file/validate")
async def validate_hook_file(req: HookFileSaveRequest, current_user: dict = Depends(get_current_active_user)):
    """校验 hook_func.py 内容语法"""
    try:
        compile(req.content, "hook_func.py", "exec")
        return {"success": True, "message": "语法校验通过"}
    except SyntaxError as e:
        return {
            "success": False,
            "message": f"第 {e.lineno} 行: {e.msg}",
            "line": e.lineno,
            "offset": e.offset
        }


@router.put("/api/hook-file")
async def save_hook_file(req: HookFileSaveRequest, current_user: dict = Depends(get_current_active_user)):
    """保存 hook_func.py 文件内容"""
    try:
        compile(req.content, "hook_func.py", "exec")
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"第 {e.lineno} 行: {e.msg}")

    hook_path = Path("hook_func.py")
    backup_path = Path(hook_backup_path()) / f"hook_func.py.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if hook_path.exists():
        backup_path.write_text(hook_path.read_text(encoding="utf-8"), encoding="utf-8")
    hook_path.write_text(req.content, encoding="utf-8")
    return {"success": True, "message": "保存成功", "backup": str(backup_path)}


@router.get("/api/variables")
async def get_variables(current_user: dict = Depends(get_current_active_user)):
    """获取可用的变量列表用于自动补全"""
    try:
        variables = []

        # 1. 从配置文件中获取 cache 变量
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # init_cache 变量
        if 'init_cache' in config:
            for key in config['init_cache'].keys():
                variables.append({
                    'type': 'cache',
                    'name': f'${{cache.{key}}}',
                    'value': str(config['init_cache'][key]),
                    'description': f'Cache variable: {key}'
                })

        # 2. 环境变量 mysql
        if 'env' in config and 'mysql' in config['env']:
            for key in config['env']['mysql'].keys():
                variables.append({
                    'type': 'cache',
                    'name': f'${{cache.mysql.{key}}}',
                    'description': f'MySQL config: {key}'
                })

        # 3. 环境变量 redis
        if 'env' in config and 'redis' in config['env']:
            for key in config['env']['redis'].keys():
                variables.append({
                    'type': 'cache',
                    'name': f'${{cache.redis.{key}}}',
                    'description': f'Redis config: {key}'
                })

        # 4. Hook 函数
        import hook_func
        for attr_name in dir(hook_func.HookFunc):
            if not attr_name.startswith('_') and callable(getattr(hook_func.HookFunc, attr_name)):
                variables.append({
                    'type': 'func',
                    'name': f'${{func.{attr_name}()}}',
                    'description': f'Custom function: {attr_name}'
                })

        # 5. 常用断言操作符
        operators = ['eq', 'neq', 'in', 'notin', 'gt', 'lt', 'gte', 'lte', 'isnull', 'regex', 'start', 'end', 'len', 'bool']
        for op in operators:
            variables.append({
                'type': 'assert',
                'name': f'{op}_',
                'description': f'Assert operator: {op}'
            })

        # 6. 提取路径示例
        extract_paths = [
            ('$.data', 'response data field'),
            ('$.response.data', 'full response data path'),
            ('$.headers', 'response headers'),
            ('$.token', 'response token field')
        ]
        for path, desc in extract_paths:
            variables.append({
                'type': 'extract',
                'name': path,
                'description': f'JSONPath: {desc}'
            })

        return variables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/reports")
async def get_report_history(current_user: dict = Depends(get_current_active_user)):
    """获取每次执行的报告历史"""
    report_dir = Path(REPORT_FOLDER)
    if not report_dir.exists():
        return []

    reports = []
    for json_file in report_dir.glob("*.json"):
        try:
            record = json.loads(json_file.read_text(encoding="utf-8"))
            html_path = Path(record.get("html_path", ""))
            reports.append({
                "id": record.get("id", json_file.stem),
                "created_at": record.get("created_at", ""),
                "summary": record.get("summary", {}),
                "select_cases": record.get("select_cases", {}),
                "size": html_path.stat().st_size if html_path.exists() else 0
            })
        except Exception as e:
            print(f"Error reading report {json_file}: {e}")
    return sorted(reports, key=lambda item: item.get("created_at", ""), reverse=True)


@router.get("/api/reports/{report_id}")
async def get_report_detail(report_id: str, current_user: dict = Depends(get_current_active_user)):
    """获取指定执行记录的 HTML 报告"""
    json_path = Path(REPORT_FOLDER) / f"{report_id}.json"
    html_path = Path(REPORT_FOLDER) / f"{report_id}.html"
    if not json_path.exists() or not html_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    record = json.loads(json_path.read_text(encoding="utf-8"))
    return {
        "id": report_id,
        "content": html_path.read_text(encoding="utf-8"),
        "created_at": record.get("created_at", ""),
        "summary": record.get("summary", {}),
        "select_cases": record.get("select_cases", {}),
        "size": html_path.stat().st_size
    }


@router.get("/api/report/html")
async def get_html_report(current_user: dict = Depends(get_current_active_user)):
    """获取最新 HTML 测试报告"""
    reports = await get_report_history(current_user)
    if reports:
        return await get_report_detail(reports[0]["id"], current_user)

    report_path = "html_report.html"
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="HTML report not found")

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        "id": "latest",
        "content": content,
        "created_at": datetime.fromtimestamp(os.path.getmtime(report_path)).strftime("%Y-%m-%d %H:%M:%S"),
        "modified_time": datetime.fromtimestamp(os.path.getmtime(report_path)).strftime("%Y-%m-%d %H:%M:%S"),
        "size": os.path.getsize(report_path)
    }


@router.get("/api/graph/data")
async def get_graph_data(current_user: dict = Depends(get_current_active_user)):
    """获取测试用例依赖关系图数据"""
    try:
        from core.generate.reader import ReaderCase
        from core.generate.generate import TestCaseAutomaticGeneration

        raw_data = ReaderCase(folder_path="testcase").get_all_cases()
        t = TestCaseAutomaticGeneration(raw_data)
        nodes = t.get_all_case_name()
        edges = t.get_all_edges()
        all_cases = t.get_all_cases()
        barrels = t.get_case_runner_order()

        # 生成节点位置信息
        node_positions = {}
        barrel_len = max(barrels) if barrels else 0
        x_step = (2.85 - 1.15) / (barrel_len + 1) if barrel_len > 0 else 0
        x_init = 1.15
        cur_x_step = 0

        for barrel_index in range(barrel_len - 1, 0, -1):
            cur_barrel = barrels[barrel_index]
            for node in cur_barrel:
                import random
                node_positions[node] = (float(x_init + x_step * cur_x_step), random.uniform(1.15, 2.85))
            cur_x_step += 1

        # 构建用例详细信息字典
        case_details = {}
        for name, case in all_cases.items():
            if hasattr(case, 'model_dump'):
                case_details[name] = case.model_dump()
            elif isinstance(case, dict):
                case_details[name] = case
            else:
                case_details[name] = str(case)

        return {
            "nodes": list(nodes),
            "edges": [list(edge) for edge in edges],
            "node_positions": node_positions,
            "case_details": case_details,
            "barrels": {k: list(v) for k, v in barrels.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/reports/{report_id}/download")
async def download_report_by_id(report_id: str, current_user: dict = Depends(get_current_active_user)):
    """下载指定执行记录的 HTML 报告"""
    report_path = Path(REPORT_FOLDER) / f"{report_id}.html"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="HTML report not found")

    return FileResponse(
        report_path,
        media_type="text/html",
        filename=f"test_report_{report_id}.html"
    )


@router.get("/api/report/download")
async def download_html_report(current_user: dict = Depends(get_current_active_user)):
    """下载最新 HTML 测试报告"""
    reports = await get_report_history(current_user)
    if reports:
        return await download_report_by_id(reports[0]["id"], current_user)

    report_path = "html_report.html"
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="HTML report not found")

    return FileResponse(
        report_path,
        media_type="text/html",
        filename=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
