# API Reference

Complete method signatures for `FastNoteClient`. All methods are instance methods on `FastNoteClient`.

---

## Constructor

```python
FastNoteClient(base_url: str = "http://localhost:9000", timeout: int = 30)
```

## Token Management

| Method | Description |
|--------|-------------|
| `set_token(token: str) -> None` | Inject token directly into session headers |
| `token -> str \| None` | Property: current Authorization token |

---

## Public Endpoints (No Auth)

### register

```python
register(email: str, username: str, password: str, confirm_password: str) -> UserInfo
```

`POST /api/user/register` (Form). Auto-sets token on success.

### login

```python
login(credentials: str, password: str) -> UserInfo
```

`POST /api/user/login` (Form). `credentials` is username or email. Auto-sets token on success.

### get_version

```python
get_version() -> VersionInfo
```

`GET /api/version`. Returns `VersionInfo` with `version`, `git_tag`, `build_time`.

### get_webgui_config

```python
get_webgui_config() -> WebGUIConfig
```

`GET /api/webgui/config`. Returns `WebGUIConfig` with `font_set`, `register_is_enable`, `admin_uid`.

---

## User

### get_user_info

```python
get_user_info() -> UserInfo
```

`GET /api/user/info`. Returns current user's profile.

**UserInfo fields**: `uid`, `email`, `username`, `token`, `avatar`, `updated_at`, `created_at`, `raw`.

### change_password

```python
change_password(old_password: str, password: str, confirm_password: str) -> dict
```

`POST /api/user/change_password` (Form). Returns raw data dict (usually empty on success, code=5).

---

## Vault

### list_vaults

```python
list_vaults() -> list[VaultInfo]
```

`GET /api/vault`. Returns all vaults for the authenticated user.

**VaultInfo fields**: `id`, `vault`, `note_count`, `note_size`, `file_count`, `file_size`, `size`, `raw`.

### create_vault

```python
create_vault(vault_name: str) -> VaultInfo
```

`POST /api/vault` (JSON). Creates a new vault.

### update_vault

```python
update_vault(vault_id: int, vault_name: str) -> VaultInfo
```

`POST /api/vault` (JSON with `id`). Renames an existing vault.

### delete_vault

```python
delete_vault(vault_id: int) -> dict
```

`DELETE /api/vault` (Query param `id`). Returns empty dict on success.

---

## Note

### list_notes

```python
list_notes(
    vault: str,
    *,
    keyword: str | None = None,
    is_recycle: bool | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[NoteListItem]
```

`GET /api/notes` (Query). Supports FTS5 full-text search via `keyword`.

**NoteListItem fields**: `id`, `action`, `path`, `path_hash`, `version`, `ctime`, `mtime`, `updated_timestamp`, `updated_at`, `created_at`, `raw`.

**PaginatedResponse fields**: `list` (items), `pager` (Pager), `raw`.

**Pager fields**: `page`, `page_size`, `total_rows`, `raw`.

### get_note

```python
get_note(
    vault: str,
    path: str,
    *,
    is_recycle: bool | None = None,
) -> NoteDetail
```

`GET /api/note` (Query). Returns full note content.

**NoteDetail fields**: `id`, `path`, `path_hash`, `content`, `content_hash`, `file_links`, `version`, `ctime`, `mtime`, `updated_timestamp`, `updated_at`, `created_at`, `raw`.

### create_note

```python
create_note(
    vault: str,
    path: str,
    content: str = "",
    **kwargs,
) -> NoteInfo
```

`POST /api/note` (JSON). Optional kwargs: `ctime`, `mtime` (millisecond timestamps).

### update_note

```python
update_note(
    vault: str,
    path: str,
    content: str,
    **kwargs,
) -> NoteInfo
```

`POST /api/note` (JSON). Same endpoint as create. Optional kwargs: `srcPath` (for rename), `ctime`, `mtime`.

**NoteInfo fields**: `id`, `path`, `path_hash`, `content`, `content_hash`, `version`, `ctime`, `mtime`, `last_time`, `raw`.

### delete_note

```python
delete_note(vault: str, path: str) -> dict
```

`DELETE /api/note` (Query params). Returns deleted note info as dict.

### get_note_file

```python
get_note_file(vault: str, path: str) -> bytes
```

`GET /api/note/file` (Query). Returns raw file content as bytes (not JSON). Content-Type auto-detected by server.

### iter_all_notes

```python
iter_all_notes(
    vault: str,
    *,
    keyword: str | None = None,
    is_recycle: bool | None = None,
    page_size: int = 50,
) -> Generator[NoteListItem, None, None]
```

Convenience generator that auto-paginates through all notes. Yields `NoteListItem` one by one.

---

## Note History

### list_note_histories

```python
list_note_histories(
    vault: str,
    path: str,
    *,
    is_recycle: bool | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[HistoryListItem]
```

`GET /api/note/histories` (Query).

**HistoryListItem fields**: `id`, `note_id`, `vault_id`, `path`, `client_name`, `version`, `created_at`, `raw`.

### get_note_history

```python
get_note_history(history_id: int) -> HistoryDetail
```

`GET /api/note/history` (Query param `id`). Returns diff and full content of a version.

**HistoryDetail fields**: `id`, `note_id`, `vault_id`, `path`, `diffs`, `content`, `content_hash`, `client_name`, `version`, `created_at`, `raw`.

**DiffItem fields**: `type` (-1=delete, 0=equal, 1=insert), `text`.

### restore_note_from_history

```python
restore_note_from_history(vault: str, history_id: int) -> NoteInfo
```

`PUT /api/note/history/restore` (JSON). Restores note to the specified version. Current content is auto-saved as a new history entry.

---

## Admin

### get_admin_config

```python
get_admin_config() -> AdminConfig
```

`GET /api/admin/config`. Requires admin privileges.

**AdminConfig fields**: `font_set`, `register_is_enable`, `file_chunk_size`, `soft_delete_retention_time`, `upload_session_timeout`, `history_keep_versions`, `admin_uid`, `raw`.

### update_admin_config

```python
update_admin_config(**kwargs) -> AdminConfig
```

`POST /api/admin/config` (JSON). Partial update -- pass only fields to change. Accepts camelCase keys matching the server API:

| Key | Type | Description |
|-----|------|-------------|
| `fontSet` | str | Font setting |
| `registerIsEnable` | bool | Enable registration |
| `fileChunkSize` | str | File chunk size (e.g. "512KB") |
| `softDeleteRetentionTime` | str | Soft delete retention (e.g. "7d") |
| `uploadSessionTimeout` | str | Upload session timeout (e.g. "1d") |
| `historyKeepVersions` | int | Max history versions to keep |
| `adminUid` | int | Admin user ID |

---

## Exceptions

All exceptions inherit from `FastNoteAPIError(code, message, details)`.

| Exception | Codes | When |
|-----------|-------|------|
| `AuthenticationError` | 507, 508 | Not logged in / session expired |
| `NotFoundError` | 414, 428 | Vault or note not found |
| `ValidationError` | 505 | Invalid parameters |
| `PermissionError_` | 445 | Admin required |
| `RegistrationClosedError` | 405 | Registration disabled |
| `UserNotFoundError` | 407 | User does not exist |
| `UserExistsError` | 408 | User already exists |
| `FastNoteAPIError` | other | Catch-all base class |

Exception attributes: `e.code` (int), `e.message` (str), `e.details` (list[str]).
