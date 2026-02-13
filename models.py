"""Fast Note Sync Service — 响应模型

使用标准库 dataclasses 定义，每个模型附带 raw 字段保留服务端原始 dict。
from_dict() 对未知字段容错：后端新增字段不会导致解析报错。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Pager
# ---------------------------------------------------------------------------

@dataclass
class Pager:
    page: int
    page_size: int
    total_rows: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Pager:
        return cls(
            page=d.get("page", 1),
            page_size=d.get("pageSize", 10),
            total_rows=d.get("totalRows", 0),
            raw=d,
        )


# ---------------------------------------------------------------------------
# PaginatedResponse — 泛型分页包装
# ---------------------------------------------------------------------------

@dataclass
class PaginatedResponse(Generic[T]):
    list: list[T]
    pager: Pager
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

@dataclass
class UserInfo:
    uid: int
    email: str
    username: str
    token: str
    avatar: str
    updated_at: str
    created_at: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> UserInfo:
        return cls(
            uid=d.get("uid", 0),
            email=d.get("email", ""),
            username=d.get("username", ""),
            token=d.get("token", ""),
            avatar=d.get("avatar", ""),
            updated_at=d.get("updatedAt", ""),
            created_at=d.get("createdAt", ""),
            raw=d,
        )


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

@dataclass
class VersionInfo:
    version: str
    git_tag: str
    build_time: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> VersionInfo:
        return cls(
            version=d.get("version", ""),
            git_tag=d.get("gitTag", ""),
            build_time=d.get("buildTime", ""),
            raw=d,
        )


# ---------------------------------------------------------------------------
# WebGUI Config
# ---------------------------------------------------------------------------

@dataclass
class WebGUIConfig:
    font_set: str
    register_is_enable: bool
    admin_uid: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WebGUIConfig:
        return cls(
            font_set=d.get("fontSet", ""),
            register_is_enable=d.get("registerIsEnable", False),
            admin_uid=d.get("adminUid", 0),
            raw=d,
        )


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

@dataclass
class VaultInfo:
    id: int
    vault: str
    note_count: int
    note_size: int
    file_count: int
    file_size: int
    size: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> VaultInfo:
        return cls(
            id=d.get("id", 0),
            vault=d.get("vault", ""),
            note_count=d.get("noteCount", 0),
            note_size=d.get("noteSize", 0),
            file_count=d.get("fileCount", 0),
            file_size=d.get("fileSize", 0),
            size=d.get("size", 0),
            raw=d,
        )


# ---------------------------------------------------------------------------
# Note
# ---------------------------------------------------------------------------

@dataclass
class NoteListItem:
    """笔记列表中的条目（不含 content）"""
    id: int
    action: str
    path: str
    path_hash: str
    version: int
    ctime: int
    mtime: int
    updated_timestamp: int
    updated_at: str
    created_at: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> NoteListItem:
        return cls(
            id=d.get("id", 0),
            action=d.get("action", ""),
            path=d.get("path", ""),
            path_hash=d.get("pathHash", ""),
            version=d.get("version", 0),
            ctime=d.get("ctime", 0),
            mtime=d.get("mtime", 0),
            updated_timestamp=d.get("updatedTimestamp", 0),
            updated_at=d.get("updatedAt", ""),
            created_at=d.get("createdAt", ""),
            raw=d,
        )


@dataclass
class NoteDetail:
    """单条笔记完整内容"""
    id: int
    path: str
    path_hash: str
    content: str
    content_hash: str
    file_links: dict[str, str]
    version: int
    ctime: int
    mtime: int
    updated_timestamp: int
    updated_at: str
    created_at: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> NoteDetail:
        return cls(
            id=d.get("id", 0),
            path=d.get("path", ""),
            path_hash=d.get("pathHash", ""),
            content=d.get("content", ""),
            content_hash=d.get("contentHash", ""),
            file_links=d.get("fileLinks", {}),
            version=d.get("version", 0),
            ctime=d.get("ctime", 0),
            mtime=d.get("mtime", 0),
            updated_timestamp=d.get("updatedTimestamp", 0),
            updated_at=d.get("updatedAt", ""),
            created_at=d.get("createdAt", ""),
            raw=d,
        )


@dataclass
class NoteInfo:
    """创建/更新/恢复笔记后的响应"""
    id: int
    path: str
    path_hash: str
    content: str
    content_hash: str
    version: int
    ctime: int
    mtime: int
    last_time: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> NoteInfo:
        return cls(
            id=d.get("id", 0),
            path=d.get("path", ""),
            path_hash=d.get("pathHash", ""),
            content=d.get("content", ""),
            content_hash=d.get("contentHash", ""),
            version=d.get("version", 0),
            ctime=d.get("ctime", 0),
            mtime=d.get("mtime", 0),
            last_time=d.get("lastTime", 0),
            raw=d,
        )


# ---------------------------------------------------------------------------
# Note History
# ---------------------------------------------------------------------------

@dataclass
class HistoryListItem:
    """历史列表条目"""
    id: int
    note_id: int
    vault_id: int
    path: str
    client_name: str
    version: int
    created_at: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> HistoryListItem:
        return cls(
            id=d.get("id", 0),
            note_id=d.get("noteId", 0),
            vault_id=d.get("vaultId", 0),
            path=d.get("path", ""),
            client_name=d.get("clientName", ""),
            version=d.get("version", 0),
            created_at=d.get("createdAt", ""),
            raw=d,
        )


@dataclass
class DiffItem:
    """Diff 结果中的单个条目"""
    type: int       # -1=删除, 0=相等, 1=插入
    text: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DiffItem:
        return cls(
            type=d.get("Type", 0),
            text=d.get("Text", ""),
        )


@dataclass
class HistoryDetail:
    """历史详情（含 diffs 和完整内容）"""
    id: int
    note_id: int
    vault_id: int
    path: str
    diffs: list[DiffItem]
    content: str
    content_hash: str
    client_name: str
    version: int
    created_at: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> HistoryDetail:
        return cls(
            id=d.get("id", 0),
            note_id=d.get("noteId", 0),
            vault_id=d.get("vaultId", 0),
            path=d.get("path", ""),
            diffs=[DiffItem.from_dict(x) for x in d.get("diffs", [])],
            content=d.get("content", ""),
            content_hash=d.get("contentHash", ""),
            client_name=d.get("clientName", ""),
            version=d.get("version", 0),
            created_at=d.get("createdAt", ""),
            raw=d,
        )


# ---------------------------------------------------------------------------
# Admin Config
# ---------------------------------------------------------------------------

@dataclass
class AdminConfig:
    font_set: str
    register_is_enable: bool
    file_chunk_size: str
    soft_delete_retention_time: str
    upload_session_timeout: str
    history_keep_versions: int
    admin_uid: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AdminConfig:
        return cls(
            font_set=d.get("fontSet", ""),
            register_is_enable=d.get("registerIsEnable", False),
            file_chunk_size=d.get("fileChunkSize", ""),
            soft_delete_retention_time=d.get("softDeleteRetentionTime", ""),
            upload_session_timeout=d.get("uploadSessionTimeout", ""),
            history_keep_versions=d.get("historyKeepVersions", 0),
            admin_uid=d.get("adminUid", 0),
            raw=d,
        )
