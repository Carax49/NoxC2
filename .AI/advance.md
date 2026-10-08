# NoxC2 — Định Hướng Phát Triển Nâng Cao (Roadmap & Architectural Advance)

> **Mục đích:** Tài liệu này ghi lại các định hướng kiến trúc, kế hoạch phát triển tính năng nâng cao và các giải pháp kỹ thuật tối ưu cho NoxC2.  
> Mọi thảo luận thiết kế và lộ trình mở rộng cần tham chiếu và cập nhật tại đây.

---

## 1. Định Hướng Bảo Mật Đường Truyền: Chuyển Sang HTTPS / TLS (Khuyến Nghị Hàng Đầu)

### 1.1. Bối cảnh & Đánh giá Kiến Trúc
Trước đây, hệ thống từng cân nhắc giải pháp tự mã hoá tầng ứng dụng (**Custom AES-256-GCM**) bằng thư viện `cryptography`. Tuy nhiên, hướng đi này bộc lộ nhiều điểm hạn chế lớn:
- **Làm mất tính "Zero Dependency" của Agent:** Thư viện `cryptography` sử dụng C-extension (`hazmat`), bắt buộc máy mục tiêu (victim) phải có sẵn trình biên dịch/thư viện C và chạy `pip install cryptography` thì Agent mới hoạt động được.
- **Rủi ro phụ thuộc (Dependency Leak):** Dễ phát sinh lỗi liên kết import giữa Agent và Server (dẫn đến các lệnh `sys.path.insert` hack hoặc phải mang theo cả thư mục server).
- **Phức tạp hoá quản lý Key & Protocol:** Phải tự quản lý Salt, Nonce, KDF iterations (600,000 vòng), AAD, serialization.

### 1.2. Hướng Giải Pháp: Chuẩn Hoá Giao Tiếp Bằng HTTPS / TLS
Thay vì tự phát minh lại mã hoá ở tầng ứng dụng, **chuyển toàn bộ Transport sang HTTPS (TLS)** với các ưu điểm vượt trội:
- **100% Pure Python (Stdlib):** Phía Agent chỉ dùng thư viện chuẩn `urllib.request` và module `ssl` có sẵn của Python, **không cần cài thêm bất kỳ package nào**.
- **Bảo mật tiêu chuẩn công nghiệp:** Toàn bộ payload (Headers, URL path, Body, JSON, File upload/download) đều được mã hoá tự động bằng chuẩn TLS/HTTPS mạnh nhất mà hệ điều hành hỗ trợ.
- **Chống nghe lén & can thiệp dữ liệu:** Wireshark/Firewall chỉ nhìn thấy các luồng TLS mã hoá (Traffic sniffing không đọc được URL path `/command` hay nội dung lệnh).

### 1.3. Kế Hoạch Triển Khai HTTPS

#### Phía Server (`src/server/transport/http_transport.py`)
1. **Tạo chứng chỉ SSL/TLS:**
   - Tự sinh SSL cert/key tự ký (Self-signed certificate) dùng cho môi trường Lab/Nghiên cứu:
     ```bash
     openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
     ```
   - Hỗ trợ nạp đường dẫn `cert_path` và `key_path` từ `config.py`.
2. **Kích hoạt SSL Context trên Werkzeug/Flask:**
   ```python
   import ssl
   from werkzeug.serving import make_server

   # Cấu hình SSL context cho WSGI Server
   ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
   ssl_context.load_cert_chain(certfile=SSL_CERT_PATH, keyfile=SSL_KEY_PATH)

   self.__server = make_server(
       self.__host, 
       self.__port, 
       self.__app, 
       threaded=True, 
       ssl_context=ssl_context
   )
   ```

#### Phía Agent (`src/agent/test.py`)
1. **Chuyển URL sang HTTPS:**
   ```python
   SERVER_URL = "https://127.0.0.1:8080"
   ```
2. **Xử lý SSL Context (Hỗ trợ Self-signed Certs trong Lab):**
   ```python
   import ssl
   from urllib.request import Request, urlopen

   # Trong môi trường lab/test dùng cert tự ký:
   ssl_context = ssl._create_unverified_context()

   # Thực hiện request an toàn qua TLS:
   with urlopen(request, timeout=30, context=ssl_context) as response:
       ...
   ```

---

## 2. Lộ Trình Phát Triển Tính Năng Mới (Feature Roadmap)

### 2.1. Quản Lý Tiến Trình & Hệ Thống (Process & System Inspection)
- **Liệt kê tiến trình (`ps.list`):**
  - Thực thi liệt kê các tiến trình đang chạy trên máy victim (PID, Process Name, Memory, User).
  - Sử dụng lệnh native không cần thư viện ngoài: `tasklist` / `wmic process` (Windows) hoặc `ps aux` (Linux/macOS).
- **Tiêu diệt tiến trình (`ps.kill <pid>`):**
  - Hỗ trợ dừng tiến trình theo PID (`taskkill /PID` trên Windows hoặc `kill -9` trên Unix).
- **Lấy thông tin mạng chi tiết (`sys.net`):**
  - Liệt kê card mạng, IP cục bộ, IP public, bảng định tuyến (Routing table), ARP cache, kết nối đang mở (`netstat`).

---

### 2.2. Cơ Chế Chụp Màn Hình (Screenshot Capture)
- **Mục tiêu:** Thu thập hình ảnh màn hình hiện tại của victim gửi về server.
- **Thách thức:** Thư viện như `Pillow` hoặc `pyautogui` không phải là stdlib.
- **Giải pháp tiếp cận không phụ thuộc:**
  - **Trên Windows:** Dùng `ctypes` tương tác trực tiếp với Windows GDI API (`user32.dll`, `gdi32.dll`) để capture bitmap và xuất ra file ảnh (hoặc PowerShell script one-liner).
  - **Trên Linux:** Tận dụng các công cụ có sẵn như `import`, `scrot`, `xwd` hoặc đọc frame buffer.
  - Đóng gói dữ liệu ảnh dưới dạng Base64 và truyền về tương tự cơ chế `agent.download`.

---

### 2.3. Tối Ưu Hoá Truyền File Lớn (Chunked File Streaming)
- **Vấn đề hiện tại:** `agent.upload` và `agent.download` load toàn bộ file vào RAM rồi mã hoá Base64. File >50MB sẽ tốn nhiều bộ nhớ.
- **Cải tiến:**
  - Chia nhỏ file thành từng chunks (ví dụ: 1MB/chunk).
  - Server và Agent gửi từng chunk kèm mã hash (MD5/SHA256) để kiểm tra tính toàn vẹn.
  - Tự động ghép nối và ghi file dạng stream (`append`).

---

### 2.4. Agent Jitter & Cơ Chế Ẩn Mình (Stealth & Jittering)
- **Beaconing Jitter:**
  - Hiện tại: Interval cố định (polling 50s-60s hoặc reconnect cố định 3s).
  - Nâng cấp: Thêm `jitter_percent` (ví dụ: dao động ±20% - 30% thời gian ngẫu nhiên) để tránh bị hệ thống giám sát mạng (IDS/IPS/SIEM) phát hiện theo chu kỳ thời gian cố định.
- **Cấu hình Sleep động từ Server:**
  - Thêm lệnh `agent.sleep <seconds> [jitter]` để điều chỉnh thời gian nghỉ của implant trực tiếp từ Web Dashboard / CLI.

---

### 2.5. Trình Đóng Gói / Tạo Agent (Agent Builder & Stager)
- **Ý tưởng:** Xây dựng module sinh agent tự động từ Web Dashboard hoặc CLI.
- **Tính năng:**
  - Nhập Server IP, Port, Reconnect delay, Protocol (HTTP/HTTPS).
  - Tự động gộp tất cả handler (`test.py`, `upload_handler.py`, `download_handler.py`) thành **1 file `.py` duy nhất (Single-file standalone agent)**.
  - Tuỳ chọn compile sang file thực thi độc lập (`.exe` trên Windows / binary trên Linux) thông qua `PyInstaller` chạy tại máy chủ Server.

---

### 2.6. Quản Lý Dữ Liệu & Đa Người Dùng (Persistence & Multi-operator)
- **Lưu trữ lịch sử (SQLite Database):**
  - Thay vì lưu trên RAM (Dict/List), lưu danh sách agent, lịch sử lệnh, kết quả trả về, file đã download vào database SQLite `noxc2.db`.
- **Phân quyền Web Dashboard:**
  - Thêm cơ chế xác thực JWT hoặc Session Login cho Web Dashboard.
  - Hỗ trợ nhiều Operator cùng điều khiển C2 một lúc thông qua SSE đồng bộ.

---

## 3. Nguyên Tắc Thiết Kế Cốt Lõi Khi Phát Triển

1. **Nguyên tắc "Zero Dependency" cho Agent:**
   - Phía Agent **bắt buộc 100% dùng Python Standard Library**. Không được thêm bất kỳ thư viện bên ngoài nào (`pip install`) vào code Agent.
2. **Server-Centric Complexity:**
   - Mọi tính năng phức tạp (mã hoá, giao diện, lưu trữ, xử lý nặng) dồn toàn bộ về phía **Server**.
3. **Tính Độc Lập Hoàn Toàn (Complete Decoupling):**
   - Không chia sẻ code/file trực tiếp giữa thư mục `src/server` và `src/agent` qua đường dẫn file cứng (`sys.path`). Giao tiếp chỉ thực hiện qua Network Protocol (HTTP/HTTPS REST & JSON).
4. **Cập nhật tài liệu nghiêm ngặt:**
   - Bất kỳ tính năng mới nào được hoàn thành phải cập nhật vào `.AI/agent.md` theo quy tắc dự án.

---

*Tài liệu được khởi tạo: 2026-10-02 | Dành cho lộ trình phát triển NoxC2*
