from core.models.model import Case


class HookBase:
    case: Case = None

    @classmethod
    def before_case(cls) -> None:
        pass

    @classmethod
    def after_case(cls) -> None:
        pass
