class DuplicateCaseError(Exception):
    """同名异常"""

    def __init__(self, common_keys):
        self.common_keys = common_keys
        super().__init__(common_keys)

    def __str__(self):
        return f"The key exists with the same case_name: {self.common_keys}"
