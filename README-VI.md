# BỘ CÔNG CỤ COMMS

[English](README.md)

Công cụ quản lý email và lưu trữ đám mây cho Gmail, Google Drive và OneDrive.

Thiết kế cho quy trình làm việc với AI.


## DÀNH CHO NGƯỜI MỚI BẮT ĐẦU

80% công việc là cài đặt Claude Code. Sau khi có Claude Code, nó sẽ lo hết mọi thứ.

### Bước 1: Cài Đặt Visual Studio Code

Đây là trình soạn thảo code nơi Claude Code chạy.

- Tải từ https://code.visualstudio.com/
- Cài đặt như mọi ứng dụng khác

Nếu bị kẹt, hỏi ChatGPT: "Làm sao để cài Visual Studio Code trên [Mac/Windows]?"

### Bước 2: Cài Đặt Claude Code Extension

Sau khi VS Code được cài đặt:

1. Mở VS Code
2. Nhấn Cmd+Shift+X (Mac) hoặc Ctrl+Shift+X (Windows) để mở Extensions
3. Tìm "Claude Code"
4. Nhấn Install

Bạn sẽ cần Anthropic API key. Lấy tại https://console.anthropic.com/

Nếu bị kẹt, hỏi ChatGPT: "Làm sao để cài Claude Code trong VS Code?"

### Bước 3: Xong Rồi

Thật đấy. Đó là phần khó. Giờ chỉ cần nói chuyện với Claude Code.

Mở thư mục này trong VS Code, sau đó mở Claude Code và thử:

    "Giúp tôi thiết lập bộ công cụ này"

    "Tôi muốn dọn dẹp Gmail inbox"

    "Cho tôi xem có gì trong Google Drive"

    "Bộ công cụ này làm được gì?"

Claude Code sẽ:
- Cài Python nếu bạn chưa có
- Cài tất cả các gói cần thiết
- Hướng dẫn bạn thiết lập API từng bước
- Xác thực với Gmail, Drive và OneDrive
- Thực sự làm công việc cho bạn

Bạn không cần:
- Nhớ các lệnh
- Hiểu code
- Đọc phần còn lại của tài liệu này
- Tự mình tìm hiểu

Chỉ cần mô tả những gì bạn muốn bằng tiếng Việt hoặc tiếng Anh. Claude Code sẽ hỏi thêm nếu cần và sau đó làm.


### Cách Nói Chuyện Với Claude Code

Hãy nghĩ Claude Code như một trợ lý rất giỏi. Bạn có thể nói tự nhiên:

    "dọn inbox"
    "email nào từ amazon"
    "sắp xếp drive"
    "email chưa đọc"
    "giúp tôi cài đặt"

Nếu có gì không rõ, Claude Code sẽ hỏi. Nếu có lỗi, cứ nói với Claude Code:

    "không được"
    "bị lỗi"
    "thử lại"
    "sao vậy"

Càng dùng nhiều, càng quen.


## BỘ CÔNG CỤ NÀY LÀM GÌ

Sau khi thiết lập, bạn có thể nhờ Claude Code:

- Dọn dẹp Gmail inbox (gán nhãn, lưu trữ, xóa spam)
- Sắp xếp Google Drive (tạo thư mục, di chuyển file)
- Quản lý OneDrive
- Soạn email trả lời
- Tìm kiếm trên tất cả tài khoản

Bạn không cần biết nó hoạt động như thế nào. Chỉ cần hỏi những gì bạn muốn.


---

PHẦN CÒN LẠI CỦA TÀI LIỆU NÀY LÀ THAM KHẢO KỸ THUẬT CHO CLAUDE CODE.
BẠN KHÔNG CẦN ĐỌC.

---


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
