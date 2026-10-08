# NoxC2 — Hướng Dẫn & Đánh Giá Project

> Tài liệu này giải thích project cho **developer**, đánh giá trạng thái hiện tại,  
> chỉ ra điểm yếu cần sửa, và đề xuất lộ trình phát triển tối ưu.

---

## Mục Lục

1. [Thông tin project](#1-thông-tin-project)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Các thành phần chính](#3-các-thành-phần-chính)
4. [Luồng dữ liệu](#4-luồng-dữ-liệu)
5. [Đánh giá hiện tại](#5-đánh-giá-hiện-tại)
6. [Điểm cần cải thiện](#6-điểm-cần-cải-thiện)
7. [Hướng phát triển tối ưu](#7-hướng-phát-triển-tối-ưu)

---

## 1. Thông Tin Project

### Project là gì?

**NoxC2** là một **Command & Control (C2) framework** — một loại công cụ trong lĩnh vực bảo mật mạng cho phép một máy chủ (server) **điều khiển từ xa** nhiều máy tính khác (agent) thông qua mạng.

> **Mục đích:** Học thuật và nghiên cứu bảo mật. Không dùng cho mục đích tấn công thực tế.

### Cách hoạt động ở mức cao

```
Operator (bạn)
    │
    │  gõ lệnh vào terminal
    ▼
[SERVER — máy bạn]
    │
    │  HTTP (cổng 8080)
    ▼
[AGENT — máy nạn nhân (lab/test)]
    │
    │  chạy lệnh → gửi kết quả về
    ▼
[SERVER] → hiển thị kết quả
```

### Thông tin cơ bản

| Thông tin | Chi tiết |
|---|---|
| Ngôn ngữ | Python 3.14 |
| Phiên bản | v0.1.0 (đang phát triển) |
| Transport | HTTP (Flask 3.1.3 + Werkzeug 3.1.8) |
| Mã hoá | AES-256-GCM + PBKDF2-SHA256 |
| UI | rich library (bảng màu, terminal đẹp) |
| Git branch | `main` (production), `sim` (đang phát triển) |
| Hệ điều hành dev | Windows 11 Pro |

---

## 2. Kiến Trúc Hệ Thống

### Hai thành phần chính

```
┌──────────────────────────────────────────┐
│              SERVER                      │
│  Operator gõ lệnh tại đây               │
│                                          │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  │
│  │Transport│  │Serializer│  │Crypto  │  │
│  │(HTTP)   │  │(JSON)    │  │(AES-GCM│  │
│  └─────────┘  └──────────┘  └────────┘  │
│       │              │           │       │
│  ┌─────────────────────────────────┐     │
│  │         Core Server             │     │
│  │  ClientManager + ClientSession  │     │
│  │  ShellManager (REPL)            │     │
│  └─────────────────────────────────┘     │
└──────────────────────────────────────────┘
             ▲▼  HTTP port 8080
┌──────────────────────────────────────────┐
│              AGENT                       │
│  Chạy trên máy target (lab)             │
│                                          │
│  test.py  →  register → poll command    │
│           →  execute  → send result     │
└──────────────────────────────────────────┘
```

### Vì sao dùng kiến trúc pluggable?

- **Transport** (cách truyền dữ liệu) tách khỏi **core logic** — có thể thêm TCP transport mà không sửa code server chính
- **Serializer** (cách encode dữ liệu) tách riêng — có thể đổi từ JSON sang MessagePack hay Protobuf
- **Crypto** tách riêng — có thể nâng cấp algorithm mà không ảnh hưởng phần còn lại

Đây là thiết kế **tốt về nguyên tắc** — dễ mở rộng sau này.

---

## 3. Các Thành Phần Chính

### 3.1. Transport Layer — `src/server/transport/http_transport.py`

**Vai trò:** Chịu trách nhiệm nhận và gửi dữ liệu thô qua mạng.

**Cách hoạt động:**

Flask tạo 3 endpoint:

| Endpoint | Method | Mục đích |
|---|---|---|
| `/connect` | POST | Agent đăng ký lần đầu |
| `/command` | GET | Agent đợi nhận lệnh (long-poll) |
| `/message` | POST | Agent gửi kết quả về |

**Trick quan trọng — Queue đồng bộ:**

```
Agent gọi GET /command
  ↓
Flask thread block tại: send_queue.get(timeout=50s)
  ↓                              ↑ wait...
Operator gõ lệnh                 │
  ↓                              │
Server.send() → send_queue.put() ┘
  ↓
Flask thread nhận được → trả response cho Agent
```

Đây là cách HTTP (vốn stateless) được biến thành **kênh real-time** — khá clever.

---

### 3.2. Core Server — `src/server/core/server.py`

**Vai trò:** Orchestrator — điều phối toàn bộ hệ thống.

Khi agent kết nối:
1. Transport gọi callback `on_client(uuid, addr)`
2. Server tạo `ClientSession` cho agent đó
3. Đọc message đăng ký → xác thực → lưu vào `ClientManager`
4. Gửi ACK về cho agent

---

### 3.3. ClientSession — `src/server/core/client_session.py`

**Vai trò:** Đại diện cho 1 kết nối với 1 agent cụ thể.

Mỗi message gửi đi có dạng:
```json
{
  "type": "command",
  "uuid": "<agent-id>",
  "message_id": "<uuid>-<counter>",
  "timestamp": 1234567890,
  "data": "<lệnh cần thực thi>"
}
```

Sau đó **JSON → AES-256-GCM encrypt → bytes** → gửi qua transport.

---

### 3.4. Crypto — `src/server/crypto/aes_gcm.py`

**Vai trò:** Mã hoá/giải mã mọi message.

**Tại sao dùng AES-GCM thay vì AES-CBC?**
- GCM là **AEAD** — vừa encrypt vừa authenticate (không cần HMAC riêng)
- Chống giả mạo, chống replay attack (nếu implement đúng)

**Tại sao dùng PBKDF2 với 600,000 iterations?**
- Biến password (`SECRET_KEY`) thành encryption key an toàn hơn
- Làm chậm brute-force attack nếu key bị lộ

**AAD (Additional Authenticated Data) là gì?**
```python
aad = {"agent_id": "<uuid>"}
```
Bind message với agent cụ thể — message của agent A không thể dùng cho agent B, ngăn replay attack.

---

### 3.5. Command Registry — `src/server/commands/`

**Cách đăng ký command:**
```python
@register
class MyCommand(Command):
    name = "my.cmd"
    group = "agent"      # → AGENT_COMMANDS["my.cmd"]
    description = "..."

    def execute(self, *args): ...
    def get_help(self) -> str: ...
```

`@register` decorator tự động đăng ký vào đúng dict (`GENERAL`, `HOST`, hoặc `AGENT`) dựa trên `group`.

**Commands hiện có:**

| Nhóm | Commands |
|---|---|
| GENERAL | `help`, `clear`, `exit` |
| HOST | `client.show`, `client.select`, `client.drop`, `client.remove` |
| AGENT | `shell <cmd>`, `agent.upload <local> <remote>` |

---

### 3.6. Agent — `src/agent/test.py`

**Vai trò:** Implant chạy trên máy target.

**Vòng lặp:**
```
Khởi động
  │
  ▼
POST /connect  → gửi thông tin hệ thống (hostname, username, OS, arch)
  │
  ▼
Nhận ACK
  │
  ▼ ←─────────────────────────────────┐
GET /command (đợi tối đa 60 giây)     │
  │                                    │
  ├─ Timeout → GET lại                 │
  │                                    │
  └─ Nhận lệnh → thực thi → POST /message → kết quả ─┘
                                       │
                    Lỗi kết nối → đợi 3s → kết nối lại
```

> ⚠️ **Điểm quan trọng:** Agent hiện tại là **demo stub** — `whoami`, `hostname`, `pwd` được implement bằng Python stdlib, **không dùng `subprocess`** để chạy lệnh shell thực. Đây là giới hạn lớn nhất.

---

## 4. Luồng Dữ Liệu

### Gửi lệnh từ Operator đến Agent

```
Operator gõ: shell whoami
  │
  ▼ (ShellManager.handle_command)
RemoteShellCommand.execute("whoami")
  │
  ▼ (với mỗi agent đang chọn)
ClientSession.send_request(COMMAND, "whoami")
  │
  ├─ Tạo envelope JSON: {type, uuid, message_id, timestamp, data}
  ├─ JSONSerializer.encode() → bytes
  ├─ AES-GCM encrypt → ciphertext bytes
  │
  ▼
HTTPTransport.send(uuid, ciphertext)
  │
  ▼
__send_queues[uuid].put(ciphertext)
  │
  ▼ (Agent đang chờ tại GET /command)
Flask trả response cho Agent
  │
  ▼
Agent: decrypt → parse → run_command("whoami")
       → POST /message với kết quả
  │
  ▼
Server nhận /message → decrypt → print kết quả
```

---

## 5. Đánh Giá Hiện Tại

### 5.1. Điểm Mạnh ✅

| Điểm mạnh | Chi tiết |
|---|---|
| **Kiến trúc clean** | Tách biệt rõ transport, serializer, crypto, command |
| **Mã hoá tốt** | AES-256-GCM với PBKDF2 là lựa chọn đúng đắn |
| **Multi-client** | Hỗ trợ nhiều agent đồng thời, thread-safe |
| **Extensible** | Thêm transport/command rất dễ nhờ ABCs và decorators |
| **UI tốt** | Rich library làm terminal output dễ đọc |
| **Code style** | Nhất quán, dễ đọc, đặt tên rõ ràng |
| **File upload** | Atomic write (tmp → rename) — tốt |
| **Agent reconnect** | Tự động kết nối lại khi mất kết nối |

### 5.2. Trạng Thái Tổng Thể

```
Nền tảng kiến trúc:     ████████░░  80%  (tốt, cần hoàn thiện)
Transport HTTP:          █████████░  90%  (gần đầy đủ)
Mã hoá:                 ████████░░  80%  (tốt, thiếu TLS)
Command system:          ███████░░░  70%  (cần thêm commands)
Agent functionality:     ████░░░░░░  40%  (demo stub, cần real exec)
Security hardening:      ████░░░░░░  40%  (SECRET_KEY hardcoded, no auth)
Persistence/logging:     ░░░░░░░░░░   0%  (không có)
```

**Tóm tắt:** Project có **nền tảng kiến trúc rất tốt** cho giai đoạn đầu. Code sạch, tổ chức hợp lý. Tuy nhiên agent còn là demo, thiếu các tính năng thiết yếu cho một C2 framework thực sự.

---

## 6. Điểm Cần Cải Thiện

### 🔴 Critical — Phải sửa trước

#### 6.1. Agent chưa có real shell execution

**Vấn đề:** `run_demo_command()` trong `test.py` dùng stub thay vì `subprocess`:
```python
# Hiện tại (demo)
if command == "whoami":
    return getpass.getuser()  # chỉ trả username, không phải shell thực

# Cần thành
import subprocess
result = subprocess.run(command, shell=True, capture_output=True, text=True)
return result.stdout or result.stderr
```

**Ảnh hưởng:** Mọi lệnh shell thực đều không chạy được — đây là tính năng cốt lõi của C2.

---

#### 6.2. SECRET_KEY hardcoded

**Vấn đề:**
```python
# config.py
SECRET_KEY = "DORAEMONDORAEMONDORAEMONDORAEMON"  # ← hardcoded
```

**Vấn đề cụ thể:**
- Key bị commit vào git history → lộ cho bất kỳ ai có repo
- Mọi instance dùng cùng key → một agent bị compromise → tất cả bị compromise
- Key yếu (readable ASCII, không đủ entropy)

**Cần làm:**
```python
# Sinh key ngẫu nhiên khi khởi động, hoặc đọc từ env
import os
import secrets
SECRET_KEY = os.environ.get("NOX_SECRET_KEY") or secrets.token_bytes(32)
```

---

#### 6.3. Không có authentication

**Vấn đề:** Bất kỳ HTTP request nào tới server với `X-UUID` hợp lệ đều được chấp nhận. Không có cơ chế xác thực agent là thật.

**Nguy cơ:** Kẻ tấn công biết port 8080 có thể gửi request giả mạo, gây MITM hoặc spam.

---

### 🟡 High Priority — Nên làm sớm

#### 6.4. Không có TLS/HTTPS

**Vấn đề:** Toàn bộ traffic đi qua plain HTTP. Dù message được AES-GCM encrypt ở tầng application, không có transport-layer security:
- Header `X-UUID` đi plaintext → observer biết agent ID
- Metadata (timing, size) bị lộ
- Không có certificate pinning

**Cần làm:** Bật HTTPS trong Flask/Werkzeug hoặc dùng reverse proxy (nginx) với TLS.

---

#### 6.5. Không có file download (agent → server)

**Vấn đề:** Hiện chỉ có upload (server → agent). Không có command để lấy file từ agent về.

**Cần thêm:**
- Command `agent.download <remote_path>` 
- Agent stream file data qua POST /message
- Server ghi ra local file

---

#### 6.6. Message có thể bị replay

**Vấn đề:** Server không track message IDs đã nhận. Dù mỗi message có `message_id` và `timestamp`, server không kiểm tra:
- `timestamp` còn "tươi" không (trong vòng N giây)
- `message_id` đã từng nhận chưa

**Nguy cơ:** Attacker capture một encrypted message có thể replay lại → agent nhận lệnh 2 lần.

---

#### 6.7. Lỗi khi agent gọi `/message` nhưng server chưa `get()` queue

**Vấn đề tinh tế:** Trong `HTTPTransport`:
```python
@app.route('/message', methods=['POST'])
def message():
    ...
    response_data = self.__wait_response(uuid, timeout=0.1)  # chỉ 0.1s!
```

Agent gửi kết quả → server cần đọc từ `recv_queue` để process → nhưng nếu server thread chưa kịp gọi `receive()` thì Flask cũng không block đủ lâu để biết có response hay không. Đây là **asymmetry** giữa `/connect` (timeout 50s) và `/message` (timeout 0.1s) có thể gây lost response trong edge cases.

---

### 🟢 Nice to Have — Cải thiện sau

#### 6.8. Không có persistent storage

**Vấn đề:** Mọi state (danh sách agents, lịch sử lệnh) mất khi server restart.

**Cần:** SQLite hoặc JSON file để lưu:
- Danh sách agents đã từng kết nối
- Lịch sử commands đã gửi
- Kết quả đã nhận

---

#### 6.9. Không có logging

**Vấn đề:** Không có log ra file. Mọi output chỉ hiện trên terminal.

**Cần:** Python `logging` module ghi ra file:
```python
logging.basicConfig(
    filename="nox.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
```

---

#### 6.10. Agent dùng `sys.path.insert` để import server crypto

**Vấn đề:**
```python
# test.py (agent)
sys.path.insert(0, str(SERVER_SRC))   # ← hack để dùng server's crypto module
from crypto.aes_gcm import ...
```

**Vấn đề:** Agent phụ thuộc cứng vào cấu trúc thư mục của server. Nếu agent được deploy trên máy thật, không thể có server source ở đó.

**Cần:** Copy logic crypto vào agent như một module độc lập, hoặc dùng shared package.

---

#### 6.11. `PORT` và `BUFFER_SIZE` trong config không dùng

```python
# config.py — các giá trị này không được dùng ở đâu
PORT = 4926          # placeholder TCP port
BUFFER_SIZE = 4926   # chưa dùng
TIMEOUT = 5          # chưa dùng
MAX_WAITING_CLIENT = 10  # chưa dùng
MAX_RETRIES = 5          # chưa dùng (agent tự implement retry loop)
```

Nên dùng hoặc remove để tránh nhầm lẫn.

---

#### 6.12. Không có input validation phía server

**Vấn đề:** Server tin tất cả data từ agent sau khi decrypt. Nếu có agent giả (biết key), có thể inject malformed data làm crash server.

---

## 7. Hướng Phát Triển Tối Ưu

### Phase 1 — Hoàn thiện core (ưu tiên cao, ~2-3 tuần)

**Mục tiêu:** Làm cho project có thể demo đầy đủ tính năng cơ bản của một C2.

#### 1.1. Real shell execution cho agent

```python
# src/agent/executor.py (file mới)
import subprocess

def run_shell(command: str) -> str:
    """Thực thi command trong shell hệ thống."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,           # tránh lệnh hang vô hạn
            cwd=os.getcwd(),
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "[error] Command timed out"
    except Exception as e:
        return f"[error] {e}"
```

Đây là tính năng thiết yếu, phải làm trước nhất.

---

#### 1.2. File download (agent → server)

Thêm command `agent.download <remote_path>`:

```
Server gửi: {command: "agent.download", file_path: "/etc/passwd"}
Agent: đọc file → base64 encode → gửi qua POST /message
Server: nhận → decode → ghi file local
```

Cần xử lý file lớn: chia chunk nếu file > một size nhất định.

---

#### 1.3. Tách crypto ra khỏi server dependency

Tạo `src/shared/crypto/` — package chung cho cả server và agent, xoá `sys.path.insert` hack.

```
NoxC2/
├── src/
│   ├── shared/
│   │   ├── crypto/
│   │   │   └── aes_gcm.py    ← copy từ server, không có config import
│   │   └── protocol.py       ← MessageType constants
│   ├── server/
│   └── agent/
```

---

#### 1.4. Sửa SECRET_KEY — dùng env variable hoặc config file

```python
# config.py
import os
import secrets

_key = os.environ.get("NOX_SECRET_KEY")
if _key:
    SECRET_KEY = _key.encode() if isinstance(_key, str) else _key
else:
    # Sinh key mới và in ra để user copy vào agent
    SECRET_KEY = secrets.token_bytes(32)
    import warnings
    warnings.warn("No NOX_SECRET_KEY set — using random key (won't survive restart)")
```

---

### Phase 2 — Security hardening (~1-2 tuần)

**Mục tiêu:** Nâng cấp bảo mật lên mức phù hợp hơn cho tool nghiên cứu.

#### 2.1. HTTPS với self-signed certificate

```python
# http_transport.py
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')
self.__server = make_server(
    self.__host, self.__port, self.__app,
    ssl_context=ssl_context,
    threaded=True,
)
```

Kèm certificate pinning ở agent.

---

#### 2.2. Agent authentication

Thêm cơ chế xác thực agent khi đăng ký:

**Option A — Pre-shared token:**
```python
# Agent gửi thêm field trong register message
"auth_token": hmac_sha256(SECRET_KEY, agent_id + timestamp)
```

**Option B — Challenge-response:**
Server gửi random challenge → Agent phải sign bằng HMAC → Server verify.

---

#### 2.3. Replay attack prevention

```python
# server/core/server.py
_seen_message_ids = set()   # hoặc TTL-cache
_MAX_AGE_SECONDS = 60

def _check_message(msg: dict):
    ts = msg.get("timestamp", 0)
    if abs(time.time() - ts) > _MAX_AGE_SECONDS:
        raise ValueError("Message too old — possible replay")
    
    mid = msg.get("message_id")
    if mid in _seen_message_ids:
        raise ValueError("Duplicate message_id — replay detected")
    _seen_message_ids.add(mid)
```

---

### Phase 3 — Tính năng nâng cao (~2-4 tuần)

**Mục tiêu:** Mở rộng khả năng của C2 lên gần với các framework thực tế.

#### 3.1. TCP transport

Implement `TCPTransport(BaseTransport)` — dùng `socket` + `threading`. Có thể giao tiếp realtime hơn HTTP, không cần long-polling.

Vì đã có abstraction `BaseTransport`, chỉ cần implement interface đó và swap trong `main.py`:
```python
Server(TCPTransport(), JSONSerializer()).start()
```

---

#### 3.2. Persistent storage — SQLite

```python
# src/server/storage/db.py
import sqlite3

# Tables:
# agents(uuid, hostname, username, os, arch, first_seen, last_seen)
# commands(id, agent_uuid, command, timestamp, status)
# results(id, command_id, output, timestamp)
```

Khi server restart, vẫn biết agents đã từng kết nối.

---

#### 3.3. Thêm commands C2 cơ bản

| Command | Mô tả |
|---|---|
| `agent.ps` | Liệt kê processes (`psutil`) |
| `agent.kill <pid>` | Kill process |
| `agent.screenshot` | Chụp màn hình (PIL/Pillow) |
| `agent.download <path>` | Tải file từ agent về server |
| `agent.ls <dir>` | Liệt kê thư mục |
| `agent.cd <dir>` | Đổi working directory |

---

#### 3.4. Agent builder / generator

Thay vì một file `test.py` cứng, tạo script generate agent với config được bake in:

```python
# src/tools/build_agent.py
def build_agent(server_url: str, secret_key: bytes, output_path: str):
    """Tạo agent file với config đã embed sẵn."""
    ...
```

---

#### 3.5. Logging system

```python
# src/server/logging_setup.py
import logging
from rich.logging import RichHandler

def setup_logging(log_file="nox.log"):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[
            RichHandler(),                        # terminal (rich format)
            logging.FileHandler(log_file),         # file log
        ]
    )
```

---

### Lộ Trình Tóm Tắt

```
Tuần 1-2:  [Phase 1] Real shell exec + File download + Shared crypto package
Tuần 3:    [Phase 1] Sửa SECRET_KEY + Fix /message timeout issue  
Tuần 4-5:  [Phase 2] HTTPS + Agent auth + Replay prevention
Tuần 6-9:  [Phase 3] TCP transport + SQLite + New commands
Tuần 10+:  [Phase 3] Agent builder + Logging + UI improvements
```

### Priority Matrix

```
                IMPACT
                Cao │ Real shell exec    │ HTTPS + Auth
                    │ File download      │ SQLite storage
                    │                   │
                ────┼───────────────────┼──────────────
                    │ Fix SECRET_KEY     │ TCP Transport
                Thấp│ Shared crypto pkg  │ Agent builder
                    └───────────────────┴──────────────
                        Dễ làm          Khó làm
                              EFFORT
```

**Làm trước:** Góc trên trái (impact cao, dễ) → `Real shell exec` + `File download`.

---

## Kết Luận

NoxC2 có **nền tảng kiến trúc tốt**, code clean, tổ chức hợp lý — xứng đáng với mục tiêu học thuật. Phase hiện tại giống như "skeleton" chức năng — đã có đầy đủ xương sườn, cần "đắp thịt" vào.

**Điều cần làm ngay nhất:** Implement real shell execution trong agent (`subprocess`). Không có điều này, project chỉ là demo protocol — không demo được khả năng điều khiển thực sự.

**Điều quan trọng thứ hai:** Tách crypto ra khỏi server dependency để agent có thể deploy độc lập.

Sau hai điều đó, project sẽ thực sự "chạy được" như một C2 framework nhỏ hoàn chỉnh.

---

*Được tạo: 2026-10-01 | NoxC2 v0.1.0*
