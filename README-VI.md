# BỘ CÔNG CỤ COMMS

[English](README.md)

Công cụ quản lý email và lưu trữ đám mây cho Gmail, Google Drive và OneDrive bằng API chính thức.

Thiết kế cho quy trình làm việc với AI.


## DÀNH CHO NGƯỜI MỚI BẮT ĐẦU

Nếu bạn chưa từng lập trình, hãy làm theo các bước sau.

### Bước 1: Cài Đặt Python

Python là ngôn ngữ lập trình các công cụ này được viết bằng.

- Mac: Mở Terminal (tìm "Terminal" trong Spotlight), sau đó gõ:

      xcode-select --install

  Sau đó cài Python từ https://www.python.org/downloads/

- Windows: Tải Python từ https://www.python.org/downloads/
  Khi cài đặt, CHỌN ô "Add Python to PATH"

Nếu bị kẹt, hỏi ChatGPT: "Làm sao để cài Python trên [Mac/Windows]?"

### Bước 2: Cài Đặt Trình Soạn Thảo Code (Tùy Chọn)

Bạn có thể dùng bất kỳ trình soạn thảo nào, nhưng Visual Studio Code được khuyến dùng.

- Tải từ https://code.visualstudio.com/
- Cài đặt như mọi ứng dụng khác

Nếu bị kẹt, hỏi ChatGPT: "Làm sao để cài Visual Studio Code?"

### Bước 3: Mở Terminal hoặc Command Prompt

- Mac: Tìm "Terminal" trong Spotlight (Cmd + Space)
- Windows: Tìm "Command Prompt" hoặc "PowerShell" trong menu Start

Đây là nơi bạn gõ các lệnh.

### Bước 4: Tải Bộ Công Cụ

Trong Terminal hoặc Command Prompt, gõ:

    git clone https://github.com/dakthi/claude-comms.git
    cd claude-comms

Nếu "git" không tìm thấy:
- Mac: Sẽ hiện thông báo cài đặt. Chọn có.
- Windows: Tải từ https://git-scm.com/downloads

Nếu bị kẹt, hỏi ChatGPT: "Làm sao để clone một git repository?"

### Bước 5: Cài Đặt Các Gói Cần Thiết

Trong Terminal, gõ:

    pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2 requests python-dotenv

Nếu "pip3" không tìm thấy, thử "pip" thay thế.

### Bước 6: Thiết Lập Quyền Truy Cập API

Bước này cần tạo tài khoản và lấy thông tin xác thực. Làm theo phần QUICK START bên dưới.

Nếu bước nào khó hiểu, copy lỗi và hỏi ChatGPT giải thích.


## TỔNG QUAN

Bộ công cụ này cung cấp các script Python cho:

- Gmail: Sắp xếp inbox, gán nhãn, lưu trữ, soạn thư trả lời
- Google Drive: Tổ chức file, chuyển giữa các tài khoản, quản lý thư mục
- OneDrive: Liệt kê file, tìm kiếm, tổ chức


## CẤU TRÚC THƯ MỤC

    comms/
    |-- README.md              Tài liệu chính (tiếng Anh)
    |-- README-VI.md           Tài liệu tiếng Việt
    |-- gmail_tool.py          Công cụ Gmail và Google Drive
    |-- onedrive_tool.py       Công cụ OneDrive
    |-- .gitignore             Loại trừ secrets và dữ liệu cá nhân
    |-- .secrets/              (gitignored) Thông tin xác thực
    |   |-- credentials.json   Google OAuth client
    |   |-- token.json         Google access token
    |   |-- onedrive_token.json
    |   +-- .env               OneDrive client ID
    +-- logs/                  (gitignored) Nhật ký phiên
        +-- CLEANUP-YYYY-MM-DD.md


## CÔNG CỤ GMAIL

### Các Lệnh CLI

    python3 gmail_tool.py inbox 20          Xem inbox
    python3 gmail_tool.py unread            Xem chưa đọc
    python3 gmail_tool.py search "query"    Tìm kiếm
    python3 gmail_tool.py read MSG_ID       Đọc thư
    python3 gmail_tool.py labels            Liệt kê nhãn
    python3 gmail_tool.py unsub "email"     Xóa tất cả từ người gửi
    python3 gmail_tool.py mark-all-read     Đánh dấu tất cả đã đọc

### Các Lệnh Drive

    python3 gmail_tool.py drive             Liệt kê file gần đây
    python3 gmail_tool.py drive-folders     Liệt kê thư mục
    python3 gmail_tool.py drive-search "x"  Tìm kiếm file


## CÔNG CỤ ONEDRIVE

### Các Lệnh CLI

    python3 onedrive_tool.py auth           Xác thực
    python3 onedrive_tool.py me             Hiển thị thông tin người dùng
    python3 onedrive_tool.py ls             Liệt kê root
    python3 onedrive_tool.py ls Documents   Liệt kê thư mục
    python3 onedrive_tool.py folders        Liệt kê tất cả thư mục
    python3 onedrive_tool.py search "tên"   Tìm kiếm file
    python3 onedrive_tool.py mkdir "tên"    Tạo thư mục


## QUY TRÌNH TỔ CHỨC DRIVE

### Bước 1: Kiểm Tra Trạng Thái Hiện Tại

    folders = list_root_folders()
    files_at_root = list_drive_files("'root' in parents", 100)

### Bước 2: Tạo Thư Mục Theo Loại

    _Documents/
    _Spreadsheets/
    _PDFs/
    _Images/
    _Videos/
    _Other/
    _Books/

### Bước 3: Di Chuyển File Rời

    drive.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents='root'
    ).execute()

### Bước 4: Tạo Thư Mục Theo Nội Dung

    Business/
    |-- Dự Án A/
    |-- Dự Án B/
    +-- Khách Hàng/

    Personal/
    |-- Tài Chính/
    |-- Sức Khỏe/
    +-- Du Lịch/


## QUY TRÌNH TỔ CHỨC GMAIL

### Bước 1: Phân Tích Inbox

    python3 gmail_tool.py senders 100

### Bước 2: Tạo Cấu Trúc Nhãn

    Receipts/
    |-- Thực Ăn
    |-- Giao Thông
    |-- Mua Sắm
    +-- Đăng Ký

    Notifications/
    |-- Dev
    |-- Tài Chính
    |-- Mạng Xã Hội
    +-- Khuyến Mãi

    Personal/
    |-- Bạn Bè
    |-- Gia Đình
    +-- Sức Khỏe

    Business/
    |-- Khách Hàng
    |-- Leads
    +-- Quản Trị

### Bước 3: Gán Nhãn và Lưu Trữ Hàng Loạt

    while True:
        count = label_and_archive('from:github.com in:inbox', 'Notifications/Dev', 50)
        if count == 0:
            break


## XỬ LÝ SỰ CỐ

TOKEN HẾT HẠN:

    rm .secrets/token.json
    python3 gmail_tool.py auth

THAY ĐỔI SCOPE:

Nếu bạn thêm API scope mới, xóa token và xác thực lại.

VƯỢT QUÁ GIỚI HẠN:

Nếu gặp userRateLimitExceeded, đợi 60 giây, giảm kích thước batch, hoặc thêm time.sleep(1) giữa các thao tác.


## GHI CHÚ BẢO MẬT

- Không bao giờ commit credentials. Tất cả secrets được gitignored.
- Sử dụng test users. Ứng dụng Google OAuth ở chế độ testing cần test users rõ ràng.
- Kiểm tra trước khi chạy. Luôn xem trước query trước khi thao tác hàng loạt.
- Sao lưu trước. Sử dụng Google Takeout trước khi dọn dẹp lớn.


## CÁC GÓI PHỤ THUỘC

    pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2 requests python-dotenv


## GIẤY PHÉP

MIT License. Sử dụng tự do, sửa đổi tùy ý.
