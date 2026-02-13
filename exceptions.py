"""Fast Note Sync Service — 异常体系

根据 REST API 文档的错误码，自动映射到具体异常子类。
"""

from __future__ import annotations


class FastNoteAPIError(Exception):
    """API 通用错误基类"""

    def __init__(self, code: int, message: str, details: list[str] | None = None):
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(f"[{code}] {message}" + (f" | {details}" if details else ""))


class AuthenticationError(FastNoteAPIError):
    """认证相关错误 (507=尚未登录, 508=登录状态失效)"""
    pass


class NotFoundError(FastNoteAPIError):
    """资源不存在 (414=仓库不存在, 428=笔记不存在)"""
    pass


class ValidationError(FastNoteAPIError):
    """参数验证失败 (505)"""
    pass


class PermissionError_(FastNoteAPIError):
    """权限不足 (445=需要管理员权限)
    注意: 使用 PermissionError_ 避免与 Python 内置 PermissionError 冲突。
    """
    pass


class RegistrationClosedError(FastNoteAPIError):
    """用户注册已关闭 (405)"""
    pass


class UserExistsError(FastNoteAPIError):
    """用户已存在 (408)"""
    pass


class UserNotFoundError(FastNoteAPIError):
    """用户不存在 (407)"""
    pass


# 错误码 -> 异常类映射表
ERROR_CODE_MAP: dict[int, type[FastNoteAPIError]] = {
    405: RegistrationClosedError,
    407: UserNotFoundError,
    408: UserExistsError,
    414: NotFoundError,
    428: NotFoundError,
    445: PermissionError_,
    505: ValidationError,
    507: AuthenticationError,
    508: AuthenticationError,
}


def raise_for_api_error(code: int, message: str, details: list[str] | None = None) -> None:
    """根据错误码抛出对应的异常子类，未知错误码则抛出基类。"""
    exc_cls = ERROR_CODE_MAP.get(code, FastNoteAPIError)
    raise exc_cls(code, message, details)
