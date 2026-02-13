"""Fast Note Sync Service — Python Client

用法::

    from pyclient import FastNoteClient

    client = FastNoteClient("http://localhost:9000")
    client.login("admin", "password123")
    notes = client.list_notes("my-vault")
"""

from .client import FastNoteClient
from .exceptions import (
    AuthenticationError,
    FastNoteAPIError,
    NotFoundError,
    PermissionError_,
    RegistrationClosedError,
    UserExistsError,
    UserNotFoundError,
    ValidationError,
)
from .models import (
    AdminConfig,
    DiffItem,
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

__all__ = [
    # Client
    "FastNoteClient",
    # Exceptions
    "FastNoteAPIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "PermissionError_",
    "RegistrationClosedError",
    "UserExistsError",
    "UserNotFoundError",
    # Models
    "AdminConfig",
    "DiffItem",
    "HistoryDetail",
    "HistoryListItem",
    "NoteDetail",
    "NoteInfo",
    "NoteListItem",
    "Pager",
    "PaginatedResponse",
    "UserInfo",
    "VaultInfo",
    "VersionInfo",
    "WebGUIConfig",
]
