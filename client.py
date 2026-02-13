"""Fast Note Sync Service — Python Client

覆盖 REST API 文档中全部 20 个接口端点。
Form/JSON 编码按文档严格区分，pathHash/contentHash 由服务端自动生成。
"""

from __future__ import annotations

from typing import Any, Generator

import requests

from .exceptions import raise_for_api_error
from .models import (
    AdminConfig,
    HistoryDetail,
    HistoryListItem,
    NoteDetail,
    NoteInfo,
    NoteListItem,
    Pager,
    PaginatedResponse,
    UserInfo,
    VaultInfo,
    VersionInfo,
    WebGUIConfig,
)


class FastNoteClient:
    """Fast Note Sync Service REST API 客户端。

    用法::

        client = FastNoteClient("http://localhost:9000")
        client.login("admin", "password123")
        notes = client.list_notes("my-vault")
    """

    def __init__(self, base_url: str = "http://localhost:9000", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    # ------------------------------------------------------------------
    # Token 管理
    # ------------------------------------------------------------------

    def set_token(self, token: str) -> None:
        """外部注入 token，无需调用 login()。

        自动添加 Bearer 前缀（如果未包含）。
        """
        if token and not token.startswith("Bearer "):
            token = f"Bearer {token}"
        self.session.headers["Authorization"] = token

    @property
    def token(self) -> str | None:
        """当前使用的 token（含 Bearer 前缀）。"""
        return self.session.headers.get("Authorization")

    # ------------------------------------------------------------------
    # 内部请求方法
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        form: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """统一发送请求并解析响应。

        Args:
            method: HTTP 方法 (GET/POST/PUT/DELETE)
            endpoint: API 路径，如 "/user/login"
            params: URL query 参数
            form: application/x-www-form-urlencoded 表单数据
            json: application/json 请求体

        Returns:
            响应中的 data 字段（dict）

        Raises:
            FastNoteAPIError 或其子类
            requests.HTTPError: HTTP 层面错误
        """
        url = f"{self.base_url}/api{endpoint}"
        resp = self.session.request(
            method,
            url,
            params=params,
            data=form,
            json=json,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        body = resp.json()
        if not body.get("status"):
            raise_for_api_error(
                body.get("code", 0),
                body.get("message", "Unknown error"),
                body.get("details"),
            )
        return body.get("data")

    def _request_raw(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """发送请求并返回原始 Response 对象（用于文件下载等非 JSON 接口）。"""
        url = f"{self.base_url}/api{endpoint}"
        resp = self.session.request(
            method, url, params=params, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp

    # ==================================================================
    # 公开接口（无需认证）
    # ==================================================================

    # 1. 用户注册
    def register(
        self,
        email: str,
        username: str,
        password: str,
        confirm_password: str,
    ) -> UserInfo:
        """POST /api/user/register — 用户注册。

        注册成功后自动设置 token。
        """
        data = self._request("POST", "/user/register", form={
            "email": email,
            "username": username,
            "password": password,
            "confirmPassword": confirm_password,
        })
        user = UserInfo.from_dict(data)
        if user.token:
            self.set_token(user.token)
        return user

    # 2. 用户登录
    def login(self, credentials: str, password: str) -> UserInfo:
        """POST /api/user/login — 用户登录。

        登录成功后自动设置 token，后续请求无需手动携带。

        Args:
            credentials: 用户名或邮箱
            password: 密码
        """
        data = self._request("POST", "/user/login", form={
            "credentials": credentials,
            "password": password,
        })
        user = UserInfo.from_dict(data)
        if user.token:
            self.set_token(user.token)
        return user

    # 3. 获取服务端版本
    def get_version(self) -> VersionInfo:
        """GET /api/version — 获取服务端版本信息。"""
        data = self._request("GET", "/version")
        return VersionInfo.from_dict(data)

    # 4. 获取 WebGUI 配置
    def get_webgui_config(self) -> WebGUIConfig:
        """GET /api/webgui/config — 获取 WebGUI 配置。"""
        data = self._request("GET", "/webgui/config")
        return WebGUIConfig.from_dict(data)

    # ==================================================================
    # 需认证接口 — 用户相关
    # ==================================================================

    # 6. 获取用户信息
    def get_user_info(self) -> UserInfo:
        """GET /api/user/info — 获取当前登录用户信息。"""
        data = self._request("GET", "/user/info")
        return UserInfo.from_dict(data)

    # 7. 修改密码
    def change_password(
        self,
        old_password: str,
        password: str,
        confirm_password: str,
    ) -> dict[str, Any]:
        """POST /api/user/change_password — 修改密码。

        返回原始响应 data（通常为空，成功 code=5）。
        """
        data = self._request("POST", "/user/change_password", form={
            "oldPassword": old_password,
            "password": password,
            "confirmPassword": confirm_password,
        })
        return data

    # ==================================================================
    # 需认证接口 — Vault CRUD
    # ==================================================================

    # 8. 获取仓库列表
    def list_vaults(self) -> list[VaultInfo]:
        """GET /api/vault — 获取所有仓库列表。"""
        data = self._request("GET", "/vault")
        if data is None:
            return []
        if isinstance(data, list):
            return [VaultInfo.from_dict(v) for v in data]
        # 兼容可能的包装格式
        return [VaultInfo.from_dict(v) for v in data.get("list", data)]

    # 9. 创建仓库
    def create_vault(self, vault_name: str) -> VaultInfo:
        """POST /api/vault — 创建仓库。"""
        data = self._request("POST", "/vault", json={
            "vault": vault_name,
        })
        return VaultInfo.from_dict(data)

    # 9. 更新仓库
    def update_vault(self, vault_id: int, vault_name: str) -> VaultInfo:
        """POST /api/vault — 更新仓库名称。"""
        data = self._request("POST", "/vault", json={
            "id": vault_id,
            "vault": vault_name,
        })
        return VaultInfo.from_dict(data)

    # 10. 删除仓库
    def delete_vault(self, vault_id: int) -> dict[str, Any]:
        """DELETE /api/vault — 删除仓库。"""
        data = self._request("DELETE", "/vault", params={"id": vault_id})
        return data or {}

    # ==================================================================
    # 需认证接口 — Note CRUD
    # ==================================================================

    # 11. 获取笔记列表
    def list_notes(
        self,
        vault: str,
        *,
        keyword: str | None = None,
        is_recycle: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[NoteListItem]:
        """GET /api/notes — 获取笔记列表（支持 FTS 全文搜索）。

        Args:
            vault: 仓库名称
            keyword: 搜索关键词（使用 FTS5 全文搜索）
            is_recycle: 是否查询回收站
            page: 页码
            page_size: 每页数量（最大 100）
        """
        params: dict[str, Any] = {
            "vault": vault,
            "page": page,
            "page_size": page_size,
        }
        if keyword is not None:
            params["keyword"] = keyword
        if is_recycle is not None:
            params["isRecycle"] = str(is_recycle).lower()
        data = self._request("GET", "/notes", params=params)
        items = [NoteListItem.from_dict(n) for n in (data.get("list") or [])]
        pager = Pager.from_dict(data.get("pager", {}))
        return PaginatedResponse(list=items, pager=pager, raw=data)

    # 12. 获取单条笔记
    def get_note(
        self,
        vault: str,
        path: str,
        *,
        is_recycle: bool | None = None,
    ) -> NoteDetail:
        """GET /api/note — 获取单条笔记（含完整内容）。"""
        params: dict[str, Any] = {"vault": vault, "path": path}
        if is_recycle is not None:
            params["isRecycle"] = str(is_recycle).lower()
        data = self._request("GET", "/note", params=params)
        return NoteDetail.from_dict(data)

    # 13. 创建笔记
    def create_note(
        self,
        vault: str,
        path: str,
        content: str = "",
        **kwargs: Any,
    ) -> NoteInfo:
        """POST /api/note — 创建笔记。

        Args:
            vault: 仓库名称
            path: 笔记路径
            content: 笔记内容（Markdown）
            **kwargs: 可选参数 (ctime, mtime 等)
        """
        payload: dict[str, Any] = {
            "vault": vault,
            "path": path,
            "content": content,
        }
        payload.update(kwargs)
        data = self._request("POST", "/note", json=payload)
        return NoteInfo.from_dict(data)

    # 13. 更新笔记（与创建共用同一端点）
    def update_note(
        self,
        vault: str,
        path: str,
        content: str,
        **kwargs: Any,
    ) -> NoteInfo:
        """POST /api/note — 更新笔记内容。

        Args:
            vault: 仓库名称
            path: 笔记路径
            content: 新的笔记内容
            **kwargs: 可选参数 (srcPath, ctime, mtime 等)
        """
        payload: dict[str, Any] = {
            "vault": vault,
            "path": path,
            "content": content,
        }
        payload.update(kwargs)
        data = self._request("POST", "/note", json=payload)
        return NoteInfo.from_dict(data)

    # 14. 删除笔记
    def delete_note(self, vault: str, path: str) -> dict[str, Any]:
        """DELETE /api/note — 删除笔记。

        返回被删除的笔记信息。
        """
        data = self._request("DELETE", "/note", params={
            "vault": vault,
            "path": path,
        })
        return data or {}

    # 15. 获取笔记/附件原始内容
    def get_note_file(self, vault: str, path: str) -> bytes:
        """GET /api/note/file — 获取文件原始内容（非 JSON，直接返回 bytes）。"""
        resp = self._request_raw("GET", "/note/file", params={
            "vault": vault,
            "path": path,
        })
        return resp.content

    # ------------------------------------------------------------------
    # 分页便利方法
    # ------------------------------------------------------------------

    def iter_all_notes(
        self,
        vault: str,
        *,
        keyword: str | None = None,
        is_recycle: bool | None = None,
        page_size: int = 50,
    ) -> Generator[NoteListItem, None, None]:
        """自动翻页遍历仓库中所有笔记的生成器。

        用法::

            for note in client.iter_all_notes("my-vault"):
                print(note.path)
        """
        page = 1
        while True:
            result = self.list_notes(
                vault,
                keyword=keyword,
                is_recycle=is_recycle,
                page=page,
                page_size=page_size,
            )
            yield from result.list
            if page * result.pager.page_size >= result.pager.total_rows:
                break
            page += 1

    # ==================================================================
    # 需认证接口 — Note History
    # ==================================================================

    # 16. 获取笔记历史列表
    def list_note_histories(
        self,
        vault: str,
        path: str,
        *,
        is_recycle: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[HistoryListItem]:
        """GET /api/note/histories — 获取笔记历史版本列表。"""
        params: dict[str, Any] = {
            "vault": vault,
            "path": path,
            "page": page,
            "page_size": page_size,
        }
        if is_recycle is not None:
            params["isRecycle"] = str(is_recycle).lower()
        data = self._request("GET", "/note/histories", params=params)
        items = [HistoryListItem.from_dict(h) for h in (data.get("list") or [])]
        pager = Pager.from_dict(data.get("pager", {}))
        return PaginatedResponse(list=items, pager=pager, raw=data)

    # 17. 获取历史详情
    def get_note_history(self, history_id: int) -> HistoryDetail:
        """GET /api/note/history — 获取某个历史版本的详细信息（含 diffs 和完整内容）。"""
        data = self._request("GET", "/note/history", params={"id": history_id})
        return HistoryDetail.from_dict(data)

    # 18. 从历史版本恢复笔记
    def restore_note_from_history(
        self,
        vault: str,
        history_id: int,
    ) -> NoteInfo:
        """PUT /api/note/history/restore — 将笔记恢复到指定的历史版本。

        恢复操作会自动保存当前内容为新的历史版本。
        """
        data = self._request("PUT", "/note/history/restore", json={
            "vault": vault,
            "historyId": history_id,
        })
        return NoteInfo.from_dict(data)

    # ==================================================================
    # 需认证接口 — Admin
    # ==================================================================

    # 19. 获取管理配置
    def get_admin_config(self) -> AdminConfig:
        """GET /api/admin/config — 获取管理配置（需管理员权限）。"""
        data = self._request("GET", "/admin/config")
        return AdminConfig.from_dict(data)

    # 20. 更新管理配置
    def update_admin_config(self, **kwargs: Any) -> AdminConfig:
        """POST /api/admin/config — 更新管理配置（需管理员权限）。

        可传入任意配置字段，如::

            client.update_admin_config(
                registerIsEnable=True,
                historyKeepVersions=200,
            )
        """
        data = self._request("POST", "/admin/config", json=kwargs)
        return AdminConfig.from_dict(data)

    # ------------------------------------------------------------------
    # 便利方法
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        authed = "已认证" if self.token else "未认证"
        return f"<FastNoteClient base_url={self.base_url!r} {authed}>"
