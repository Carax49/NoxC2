# Hướng Dẫn Sử Dụng Giao Diện Web NoxC2 (Dashboard)

Tài liệu này hướng dẫn chi tiết và dễ hiểu cách sử dụng giao diện Web Dashboard của **NoxC2** để quản lý các Agent, thực thi lệnh từ xa và truyền file.

---

## 1. Khởi Động & Truy Cập

### Bước 1: Khởi động Server NoxC2
Mở terminal trên máy chủ (Server):
```bash
cd src/server
python main.py
```
> Khi Server khởi động, Flask sẽ tự động lắng nghe trên cổng `8080` và phục vụ cả REST API lẫn giao diện Web.

### Bước 2: Truy cập Web Dashboard
Mở trình duyệt bất kỳ (Chrome, Edge, Firefox, Brave...) và truy cập:
👉 **`http://127.0.0.1:8080/`** (hoặc `http://<IP_SERVER>:8080/`)

### Bước 3: Kết nối Agent thử nghiệm (Tuỳ chọn)
Mở một terminal khác và chạy Agent mẫu:
```bash
cd src/agent
python test.py
```
Khi Agent khởi động, nó sẽ tự động kết nối về Server và xuất hiện ngay lập tức trên giao diện web.

---

## 2. Tổng Quan Bố Cục Giao Diện

Giao diện được thiết kế theo phong cách **Dark Terminal** hiện đại, chia thành 4 khu vực chính:

```
┌───────────────────────────────────────────────────────────────┐
│ 1. HEADER: Logo NoxC2 | Số lượng Agent | Trạng thái kết nối   │
├─────────────────┬─────────────────────────────────────────────┤
│ 2. SIDEBAR      │ 3. KHU VỰC CHÍNH (MAIN)                     │
│                 │    ┌──────────────────────────────────────┐ │
│ - Danh sách     │    │ Tab: [Shell] | [Upload] | [Agents]   │ │
│   Agent (Cards) │    ├──────────────────────────────────────┤ │
│ - Chọn nhanh    │    │ Nội dung thao tác tương ứng từng Tab │ │
│   Select/Drop   │    │                                      │ │
├─────────────────┴─────────────────────────────────────────────┤
│ 4. ACTIVITY LOG (NHẬT KÝ THỜI GIAN THỰC): Hiển thị kết quả    │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Hướng Dẫn Chi Tiết Các Chức Năng

### 📌 3.1. Theo Dõi & Chọn Agent (Mục Tiêu)

Để thao tác (chạy lệnh hoặc upload file), bạn **phải chọn ít nhất một Agent**.

#### Cách 1: Thao tác nhanh từ Sidebar (Bên trái)
* **Chọn 1 Agent:** Click trực tiếp vào thẻ (Card) của Agent đó. Khi được chọn, thẻ sẽ sáng viền xanh neon và có dấu tích xanh.
* **Chọn nhiều Agent:** Click lần lượt vào từng thẻ bạn muốn nhắm tới.
* **Bỏ chọn:** Click lại vào thẻ đã chọn để bỏ chọn.
* **Chọn tất cả:** Bấm nút **`Select all`** ở đầu Sidebar.
* **Bỏ chọn tất cả:** Bấm nút **`Drop all`**.
* **Làm mới danh sách:** Bấm biểu tượng xoay **`↻`**.

#### Cách 2: Quản lý chi tiết qua Tab `Agents`
* Chuyển sang tab **Agents** ở menu trên cùng để xem bảng đầy đủ thông tin:
  * **UUID:** Mã định danh duy nhất của Agent.
  * **Hostname / User:** Tên máy và tài khoản người dùng đang chạy Agent.
  * **IP / Port:** Địa chỉ mạng và cổng kết nối.
  * **OS / Arch:** Hệ điều hành và kiến trúc CPU (Windows, Ubuntu, x86_64...).
  * **Last beacon:** Thời gian gửi tín hiệu sống gần nhất (vd: `3s ago`).
* **Xoá / Ngắt kết nối Agent:** Bấm nút **`Remove`** màu đỏ ở dòng tương ứng (lệnh `agent.exit` sẽ được gửi đến Agent và ngắt kết nối hoàn toàn).

---

### 💻 3.2. Thực Thi Lệnh Từ Xa (Tab `Shell`)

Tab **Shell** cho phép bạn gửi lệnh đến các Agent đang được chọn.

1. **Kiểm tra mục tiêu:** Nhìn vào thanh `Target: X agent(s)` để biết bạn đang gửi lệnh cho bao nhiêu máy.
2. **Nhập lệnh:**
   * Gõ lệnh vào ô nhập `$ ...` (ví dụ: `whoami`, `hostname`, `pwd`, `platform`, `echo Hello`).
   * Bấm **Enter** hoặc nút **`Send`**.
3. **Phím tắt nhanh (Quick Buttons):**
   * Bấm vào các nút gợi ý sẵn như `whoami`, `hostname`, `pwd`, `platform` để tự động điền lệnh.
4. **Xem kết quả:** Kết quả trả về từ máy nạn nhân sẽ hiển thị ngay lập tức ở khung **Activity Log** phía dưới cùng (màu tím).

---

### 📤 3.3. Tải File Lên Agent (Tab `Upload`)

Tab **Upload** cho phép bạn gửi file từ máy tính của mình lên máy nạn nhân.

1. **Chọn Agent mục tiêu:** Đảm bảo đã chọn ít nhất 1 Agent ở Sidebar.
2. **Chọn file máy chủ (Local file):**
   * Click vào khung nét đứt **"Click to choose or drag & drop"** để chọn file từ máy bạn.
   * Hoặc kéo thả file trực tiếp vào ô này.
   * Tên file và dung lượng sẽ hiển thị sau khi chọn thành công.
3. **Nhập đường dẫn lưu trên máy Agent (Remote path):**
   * Nhập vị trí bạn muốn lưu file trên máy victim.
   * **Linux/Mac ví dụ:** `/tmp/payload.sh` hoặc `/home/user/test.txt`
   * **Windows ví dụ:** `C:\Users\Admin\AppData\Local\Temp\file.exe` hoặc `C:\test.txt`
4. **Gửi file:** Bấm nút **`Upload to selected agents`**.
5. Quá trình tải lên và trạng thái hoàn thành sẽ được thông báo qua popup (Toast) và ghi log bên dưới.

---

### 📜 3.4. Theo Dõi Nhật Ký Thời Gian Thực (Activity Log)

Khung màu đen ở dưới cùng hiển thị mọi sự kiện xảy ra trên Server theo thời gian thực (nhờ công nghệ SSE - Server-Sent Events):

| Màu sắc / Ký hiệu | Ý nghĩa | Ví dụ |
|---|---|---|
| 🟢 **Xanh lá (Success)** | Agent mới kết nối / Đăng ký thành công | `Agent registered: 192.168.1.42` |
| 🔵 **Xanh Cyan (Command)** | Lệnh vừa được gửi đi từ Web | `$ whoami → 1 agent(s)` |
| 🟣 **Tím (Result)** | Kết quả trả về từ Agent | `[192.168.1.42] administrator` |
| 🟡 **Vàng (Warn)** | Cảnh báo hoặc hành động xoá Agent | `Removed 1 agent(s) from server` |
| 🔴 **Đỏ (Error)** | Lỗi xảy ra | Lỗi cú pháp, mất kết nối... |
| ⚪ **Trắng / Xám (Info)** | Thông tin chung | `Selected 2 agent(s)` |

* **Nút `Clear`:** Bấm nút **Clear** ở góc trên thanh log để xoá sạch màn hình log nếu quá nhiều dòng.

---

## 4. Trạng Thái Kết Nối (Connection Status)

Ở góc trên bên phải thanh Header có đèn tín hiệu kết nối SSE:
* 🟢 **Chấm xanh (Live/Connected):** Web Dashboard đang kết nối trực tiếp với Server, dữ liệu và log được cập nhật realtime tức thì.
* 🔴 **Chấm đỏ (Disconnected):** Bị ngắt kết nối với Server (Server tắt hoặc rớt mạng). Trình duyệt sẽ tự động thử kết nối lại sau mỗi 3 giây.

---

## 5. Các Mẹo Tiện Ích

1. **Giao diện Responsive:** Giao diện tự động co giãn tối ưu khi xem trên điện thoại hoặc chia đôi màn hình.
2. **Đồng bộ song song với CLI:** Bạn có thể vừa gõ lệnh trong màn hình dòng lệnh (Terminal/CLI) của Server vừa mở Web Dashboard, kết quả và trạng thái Agent đều được đồng bộ thời gian thực cho cả hai bên.
3. **Thông báo Toasts:** Mọi thao tác thành công (viền xanh) hay thất bại (viền đỏ) đều có thông báo nổi góc dưới phải màn hình trong 3.5 giây.
