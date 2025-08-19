import pymysql
from pymysql.err import MySQLError
from sshtunnel import SSHTunnelForwarder

from core.cache import CacheHandler
from core.exception import MySQLConfigNotFoundError
from core.steps.base import StepBase
from core.model import Case, TestCaseRunResult, Response, MySQLConfig


class MysqlInit:
    _instance = None
    _tunnel = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_connection()

    def _initialize_connection(self):
        """初始化数据库连接"""
        mysql_config = CacheHandler.get_mysql_config()
        if not mysql_config:
            raise MySQLConfigNotFoundError

        try:
            # SSH隧道处理
            if mysql_config.ssh:
                ssh = mysql_config.ssh
                self._tunnel = SSHTunnelForwarder(
                    ssh_address_or_host=(ssh.ip, ssh.port),
                    ssh_username=ssh.username,
                    ssh_password=ssh.password,
                    ssh_pkey=ssh.pkey,
                    remote_bind_address=(mysql_config.ip, mysql_config.port),
                    local_bind_address=('127.0.0.1', 0)
                )
                self._tunnel.start()
                db_host, db_port = '127.0.0.1', self._tunnel.local_bind_port
            else:
                db_host, db_port = mysql_config.ip, mysql_config.port

            # 建立连接
            self._connection = pymysql.connect(
                host=db_host,
                port=db_port,
                user=mysql_config.username,
                password=mysql_config.password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self._initialized = True

        except Exception as e:
            self.close()
            raise ConnectionError(f"MySQL connection failed: {str(e)}")

    @property
    def connection(self) -> pymysql.Connection:
        """获取数据库连接"""
        if not self._initialized or not self._connection:
            raise ConnectionError("MySQL connection not initialized")
        return self._connection

    def close(self):
        """关闭连接和隧道"""
        if hasattr(self, '_connection') and self._connection:
            try:
                if self._connection.open:
                    self._connection.close()
            except:
                pass
            finally:
                self._connection = None

        if self._tunnel:
            try:
                self._tunnel.stop()
            except:
                pass
            finally:
                self._tunnel = None
        self._initialized = False

    def __del__(self):
        self.close()


class MysqlRequest(StepBase):
    def __init__(self, new_case: Case, test_run_result: TestCaseRunResult):
        super().__init__(new_case, test_run_result)
        try:
            self.connection = MysqlInit().connection
        except Exception as e:
            self.test_run_result.response = str(e)

    def send_request(self):
        self.set_request_log()
        # 如果有连接上的错误直接返回
        if self.test_run_result.response:
            return Response(data=self.test_run_result.response)

        try:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(self.new_case.data.body)

                    if str(self.new_case.data.body.lower()).startswith('select'):
                        results = cursor.fetchall()
                        # 如果只有1行则解包
                        if len(results) == 1:
                            results = results[0]
                        self.test_run_result.response = results
                        return Response(data=results)
                    else:
                        self.connection.commit()
                        self.test_run_result.response = cursor.rowcount
                        return Response(data=cursor.rowcount)

                except MySQLError as e:
                    self.connection.rollback()
                    self.test_run_result.response = str(e)
                    return Response(data=str(e))

        except Exception as e:
            self.test_run_result.response = str(e)
            return Response(data=str(e))
