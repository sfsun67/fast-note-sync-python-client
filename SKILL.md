---
name: fast-note-client
description: Interact with Fast Note Sync Service REST API using the Python FastNoteClient. Covers authentication, vault management, note CRUD, full-text search, note history, and admin configuration. Use when calling API endpoints, managing notes or vaults, syncing data, automating tasks, or scripting against the Fast Note Sync Service.
---

# Fast Note Client

Python client for [Fast Note Sync Service](https://github.com/haierkeys/obsidian-fast-note-sync) REST API. Requires `requests` (`pip install requests`).

## Quick Start

```python
from pyclient import FastNoteClient

client = FastNoteClient("http://localhost:9000")
client.login("admin", "password123")       # auto-saves token
notes = client.list_notes("my-vault")
```

Or inject an existing token:

```python
client = FastNoteClient("http://localhost:9000")
client.set_token("eyJhbGciOi...")
```

## Authentication

- `login(credentials, password)` -- logs in, auto-sets `Authorization` header
- `set_token(token)` -- injects token directly, skips login
- `client.token` -- read current token (property)

All subsequent requests carry the token automatically.

## Vault Management

```python
vaults = client.list_vaults()                       # list all
vault = client.create_vault("new-vault")             # create
vault = client.update_vault(vault.id, "renamed")     # rename
client.delete_vault(vault.id)                         # delete
```

Returns `VaultInfo` with fields: `id`, `vault`, `note_count`, `note_size`, `file_count`, `file_size`, `size`, `raw`.

## Note CRUD

```python
# Create
note = client.create_note("vault", "path/to/note.md", content="# Title")

# Read
detail = client.get_note("vault", "path/to/note.md")
print(detail.content)

# Update
client.update_note("vault", "path/to/note.md", content="# Updated")

# Delete
client.delete_note("vault", "path/to/note.md")

# Raw file content (bytes)
data = client.get_note_file("vault", "attachments/image.png")
```

- `create_note` / `update_note` accept `**kwargs` for optional fields (`ctime`, `mtime`, `srcPath`)
- `pathHash` / `contentHash` are computed server-side; do not pass them

## Search and Pagination

```python
# FTS full-text search
results = client.list_notes("vault", keyword="meeting notes", page=1, page_size=20)
for n in results.list:
    print(n.path)
print(f"Total: {results.pager.total_rows}")

# Auto-paginate all notes
for note in client.iter_all_notes("vault"):
    print(note.path)

# Recycle bin
deleted = client.list_notes("vault", is_recycle=True)
```

`list_notes` returns `PaginatedResponse[NoteListItem]` with `.list`, `.pager`, `.raw`.

## Note History

```python
# List history versions
histories = client.list_note_histories("vault", "path/to/note.md")

# Get detailed diff
detail = client.get_note_history(histories.list[0].id)
for diff in detail.diffs:
    prefix = {-1: "- ", 0: "  ", 1: "+ "}.get(diff.type, "? ")
    print(f"{prefix}{diff.text}")

# Restore to a historical version
client.restore_note_from_history("vault", history_id=42)
```

## Admin Configuration

```python
config = client.get_admin_config()                  # requires admin
client.update_admin_config(                          # partial update
    registerIsEnable=True,
    historyKeepVersions=200,
)
```

## Error Handling

All API errors auto-map to specific exception subclasses:

```python
from pyclient import FastNoteAPIError, AuthenticationError, NotFoundError

try:
    client.get_note("vault", "missing.md")
except NotFoundError as e:
    print(f"Not found: {e.message} (code={e.code})")
except AuthenticationError:
    print("Token expired, re-login needed")
except FastNoteAPIError as e:
    print(f"API error: {e}")
```

Error code mapping:

| Code | Exception | Meaning |
|------|-----------|---------|
| 507, 508 | `AuthenticationError` | Not logged in / session expired |
| 414, 428 | `NotFoundError` | Vault or note not found |
| 505 | `ValidationError` | Invalid parameters |
| 445 | `PermissionError_` | Admin required |
| 405 | `RegistrationClosedError` | Registration disabled |
| 407 | `UserNotFoundError` | User does not exist |
| 408 | `UserExistsError` | User already exists |

## Response Models

Every model has a `raw: dict` field preserving the original server response. Access new server fields via `obj.raw["newField"]`.

Key models: `UserInfo`, `VaultInfo`, `NoteListItem`, `NoteDetail`, `NoteInfo`, `HistoryListItem`, `HistoryDetail`, `AdminConfig`, `PaginatedResponse`, `Pager`.

## Additional Resources

- For complete method signatures and parameter details, see [api-reference.md](api-reference.md)
- Source: [client.py](client.py), [models.py](models.py), [exceptions.py](exceptions.py)
