# Fast Note Sync — Python Client

[Fast Note Sync Service](https://github.com/haierkeys/fast-note-sync-service) 的 Python 客户端，覆盖 REST API 全部 20 个接口端点。

## 关联项目与前置条件

| 项目 | 说明 |
|------|------|
| **服务端** | [haierkeys/fast-note-sync-service](https://github.com/haierkeys/fast-note-sync-service) |
| **关联版本** | [v1.15.7](https://github.com/haierkeys/fast-note-sync-service/releases/tag/1.15.7)（Releases） |
| **客户端插件** | [Obsidian Fast Note Sync Plugin](https://github.com/haierkeys/obsidian-fast-note-sync)（可选） |

**使用本客户端前，请确保：**

1. **已部署 Fast Note Sync Service** — 通过 Docker、一键脚本或二进制文件完成部署，服务正常运行在 `http://{host}:9000`。部署方式参见[服务端 README](https://github.com/haierkeys/fast-note-sync-service#-quick-deployment)。
2. **已注册账号** — 通过 Web 管理面板（`http://{host}:9000`）完成首次注册，获得用户名和密码。
3. **网络可达** — 运行本客户端的机器能访问服务端地址和端口。

---

> **AI Agent Skill 配置提醒**
>
> 本项目附带 AI Agent Skill 文件（`SKILL.md` + `api-reference.md`），可让 AI 编码助手自动理解并使用本客户端。
> **你需要将 Skill 文件复制/链接到对应工具的指定位置才能生效。** 详见下方 [AI Agent Skill 配置](#ai-agent-skill-配置) 章节。

---

## 安装

```bash
pip install requests
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

> 仅依赖 `requests`，响应模型使用标准库 `dataclasses`，无额外依赖。
> 兼容 Python 3.9+。

## 快速开始

```python
from pyclient import FastNoteClient

client = FastNoteClient("http://localhost:9000")
client.login("admin", "password123")

# 创建一条笔记
note = client.create_note("my-vault", "hello.md", content="# Hello World")

# 读取
detail = client.get_note("my-vault", "hello.md")
print(detail.content)
```

## 认证

客户端支持两种认证方式：

```python
# 方式一：登录获取 token（自动保存到 session）
client.login("admin", "password123")

# 方式二：直接注入已有 token
client.set_token("eyJhbGciOi...")
```

登录或 `set_token()` 后，后续所有请求自动携带 `Authorization` 头。

## API 一览

### 公开接口（无需认证）

| 方法 | 对应接口 | 说明 |
|------|---------|------|
| `register(email, username, password, confirm_password)` | `POST /api/user/register` | 用户注册 |
| `login(credentials, password)` | `POST /api/user/login` | 用户登录 |
| `get_version()` | `GET /api/version` | 获取服务端版本 |
| `get_webgui_config()` | `GET /api/webgui/config` | 获取 WebGUI 配置 |

### 用户

| 方法 | 对应接口 | 说明 |
|------|---------|------|
| `get_user_info()` | `GET /api/user/info` | 获取当前用户信息 |
| `change_password(old, new, confirm)` | `POST /api/user/change_password` | 修改密码 |

### Vault（仓库）

| 方法 | 对应接口 | 说明 |
|------|---------|------|
| `list_vaults()` | `GET /api/vault` | 获取仓库列表 |
| `create_vault(name)` | `POST /api/vault` | 创建仓库 |
| `update_vault(id, name)` | `POST /api/vault` | 更新仓库名称 |
| `delete_vault(id)` | `DELETE /api/vault` | 删除仓库 |

### Note（笔记）

| 方法 | 对应接口 | 说明 |
|------|---------|------|
| `list_notes(vault, keyword?, page?, page_size?)` | `GET /api/notes` | 笔记列表 / FTS 全文搜索 |
| `get_note(vault, path)` | `GET /api/note` | 获取单条笔记 |
| `create_note(vault, path, content)` | `POST /api/note` | 创建笔记 |
| `update_note(vault, path, content)` | `POST /api/note` | 更新笔记 |
| `delete_note(vault, path)` | `DELETE /api/note` | 删除笔记 |
| `get_note_file(vault, path)` | `GET /api/note/file` | 获取附件原始内容 |
| `iter_all_notes(vault)` | - | 自动翻页遍历所有笔记 |

### Note History（笔记历史）

| 方法 | 对应接口 | 说明 |
|------|---------|------|
| `list_note_histories(vault, path)` | `GET /api/note/histories` | 历史版本列表 |
| `get_note_history(history_id)` | `GET /api/note/history` | 历史详情（含 diff） |
| `restore_note_from_history(vault, history_id)` | `PUT /api/note/history/restore` | 从历史版本恢复 |

### Admin（管理员）

| 方法 | 对应接口 | 说明 |
|------|---------|------|
| `get_admin_config()` | `GET /api/admin/config` | 获取管理配置 |
| `update_admin_config(**kwargs)` | `POST /api/admin/config` | 更新管理配置 |

## 使用示例

### 笔记 CRUD

```python
from pyclient import FastNoteClient

client = FastNoteClient("http://localhost:9000")
client.login("admin", "password123")

# 创建
note = client.create_note("my-vault", "notes/todo.md", content="# TODO\n\n- [ ] 第一件事")

# 读取
detail = client.get_note("my-vault", "notes/todo.md")
print(detail.content)

# 更新
client.update_note("my-vault", "notes/todo.md", content="# TODO\n\n- [x] 第一件事")

# 删除
client.delete_note("my-vault", "notes/todo.md")
```

### 全文搜索

```python
# 使用 FTS5 全文搜索
results = client.list_notes("my-vault", keyword="会议纪要")
for note in results.list:
    print(f"{note.path} ({note.action})")

print(f"共 {results.pager.total_rows} 条匹配")
```

### 自动翻页遍历

```python
# 无需手动处理分页
for note in client.iter_all_notes("my-vault"):
    print(note.path)

# 也支持带搜索条件翻页
for note in client.iter_all_notes("my-vault", keyword="日记"):
    print(note.path)
```

### 笔记历史与恢复

```python
# 查看历史版本列表
histories = client.list_note_histories("my-vault", "notes/important.md")
for h in histories.list:
    print(f"version={h.version} by={h.client_name} at={h.created_at}")

# 查看某个历史版本的 diff
detail = client.get_note_history(histories.list[0].id)
for diff in detail.diffs:
    prefix = {-1: "- ", 0: "  ", 1: "+ "}.get(diff.type, "? ")
    print(f"{prefix}{diff.text}")

# 恢复到历史版本
client.restore_note_from_history("my-vault", histories.list[0].id)
```

### 访问原始响应数据

每个响应模型都附带 `raw` 字段，保存服务端返回的原始 dict。当服务端新增字段时，可以直接从 `raw` 中获取：

```python
detail = client.get_note("my-vault", "hello.md")

# 使用模型字段
print(detail.content)

# 访问原始数据（服务端新增字段不会丢失）
print(detail.raw)
print(detail.raw.get("someNewField"))
```

## 异常处理

所有 API 错误会根据错误码自动映射到具体异常子类：

```python
from pyclient import (
    FastNoteClient,
    FastNoteAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)

client = FastNoteClient("http://localhost:9000")

try:
    client.login("wrong_user", "wrong_pass")
except AuthenticationError as e:
    print(f"认证失败: {e.message} (code={e.code})")
except NotFoundError as e:
    print(f"资源不存在: {e.message}")
except ValidationError as e:
    print(f"参数错误: {e.message}, 详情: {e.details}")
except FastNoteAPIError as e:
    print(f"API 错误: {e}")
```

错误码与异常类的映射关系：

| 错误码 | 异常类 | 说明 |
|-------|-------|------|
| 507, 508 | `AuthenticationError` | 未登录 / session 过期 |
| 414, 428 | `NotFoundError` | 仓库或笔记不存在 |
| 505 | `ValidationError` | 参数验证失败 |
| 445 | `PermissionError_` | 需要管理员权限 |
| 405 | `RegistrationClosedError` | 注册已关闭 |
| 407 | `UserNotFoundError` | 用户不存在 |
| 408 | `UserExistsError` | 用户已存在 |
| 其他 | `FastNoteAPIError` | 通用错误基类 |

## 常见踩坑

### 1. Authorization 头必须带 `Bearer` 前缀

REST API 文档写的是 `Authorization: {token}`，但服务端实际要求 **`Authorization: Bearer {token}`**。如果你直接把裸 token 放在 `Authorization` 头里，所有需要认证的接口都会返回 `307 - Not logged in`。

本客户端已处理：`login()` 和 `set_token()` 会自动添加 `Bearer ` 前缀，你不需要手动拼接。

```python
# 正确 — 传入裸 token，客户端自动加 Bearer
client.set_token("eyJhbGciOi...")

# 也正确 — 已经带了 Bearer 前缀，不会重复添加
client.set_token("Bearer eyJhbGciOi...")

# 如果你用 curl 或其他 HTTP 工具直接调用，必须手动加：
# curl -H "Authorization: Bearer eyJhbGciOi..." https://your-server/api/user/info
```

### 2. `pathHash` / `contentHash` 不要在客户端计算

文档提到这两个字段使用 "32 位哈希算法（FNV-1a 或类似）"，但描述不绝对。服务端会自动生成，客户端传空即可。**强行在客户端计算可能因算法不一致导致数据冲突。**

## 配置项

```python
client = FastNoteClient(
    base_url="http://localhost:9000",   # 服务地址
    timeout=30,                          # 请求超时（秒）
)
```

## Smoke Test

项目附带一个端到端验证脚本，可快速验证服务连通性：

```bash
# 使用默认参数
python examples/smoke_test.py

# 指定服务地址和账号
python examples/smoke_test.py --url http://10.0.0.1:9000 --user admin --password 123456

# 使用已有 token
python examples/smoke_test.py --url http://10.0.0.1:9000 --token "eyJhbGciOi..."
```

## AI Agent Skill 配置

本项目包含 `SKILL.md` 和 `api-reference.md`，它们是 AI 编码助手的"技能文件"，让 Agent 能自动理解本客户端的全部 API 并正确调用。

**你需要将 Skill 文件放到对应工具能识别的位置，否则不会生效。**

### 各工具的 Skill 建议位置

| AI 工具 | Skill 放置位置 | 说明 |
|---------|---------------|------|
| **Cursor** | `~/.cursor/skills/fast-note-client/SKILL.md` | 个人级，所有项目可用 |
| **Cursor (项目级)** | `<project>/.cursor/skills/fast-note-client/SKILL.md` | 仅当前项目生效，可随仓库共享 |
| **Claude Code (Anthropic)** | `<project>/AGENTS.md` 或 `<project>/.claude/skills/SKILL.md` | 放在项目根目录或 `.claude/` 下 |
| **Codex (OpenAI)** | `<project>/AGENTS.md` 或 `~/.codex/skills/fast-note-client/SKILL.md` | 个人级或项目级 |
| **Gemini CLI (Google)** | `<project>/GEMINI.md` 或 `~/.gemini/skills/SKILL.md` | 项目根目录或全局配置 |
| **OpenClaw / 其他** | `<project>/.ai/skills/SKILL.md` 或项目根目录 `SKILL.md` | 大多数工具会扫描项目根目录 |

### 快速配置（以 Cursor 为例）

```bash
# 方式一：个人级（所有项目可用）
mkdir -p ~/.cursor/skills/fast-note-client
cp SKILL.md api-reference.md ~/.cursor/skills/fast-note-client/

# 方式二：项目级（仅当前项目，可 git 提交共享）
mkdir -p .cursor/skills/fast-note-client
cp SKILL.md api-reference.md .cursor/skills/fast-note-client/
```

### 通用做法

如果你使用的工具支持 `AGENTS.md`（如 Claude Code、Codex），可以直接在项目根目录创建 `AGENTS.md` 并引用：

```markdown
## Skills

- See [SKILL.md](SKILL.md) for Fast Note Sync Python Client usage
- API reference: [api-reference.md](api-reference.md)
```

> **提示**：`SKILL.md` 和 `api-reference.md` 必须一起复制，因为 `SKILL.md` 通过相对路径引用了 `api-reference.md`。

## 文件结构

```
pyclient/
├── SKILL.md           # AI Agent Skill 主文件
├── api-reference.md   # AI Agent Skill API 参考（SKILL.md 引用）
├── README.md          # 本文档
├── __init__.py        # 包入口，导出所有公共接口
├── client.py          # FastNoteClient 核心类
├── models.py          # dataclass 响应模型
├── exceptions.py      # 异常体系
└── requirements.txt   # Python 依赖
examples/
└── smoke_test.py      # 端到端验证脚本
```

## License

MIT
