class DuplicateCaseError(Exception):
    """同名异常"""

    def __init__(self, common_keys):
        self.common_keys = common_keys
        super().__init__(common_keys)

    def __str__(self):
        return f"The key exists with the same case_name: {self.common_keys}"


class IFException(Exception):
    Exception("不支持if,仅支持for 和while 语句, 如果想使用if 请使用is_run")


class WhileException(Exception):
    Exception("while True 需要结合timeout使用,否则将陷入死循环！")
