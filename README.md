# Duy Care AI Assistant 🩺

Dự án Chatbot Trợ lý Y tế sử dụng ngôn ngữ AI của Google (Gemini), được xây dựng kết hợp với Backend là FastAPI và Frontend Giao diện Web có hiệu ứng trả chữ theo thời gian thực (Real-time Streaming). 

Hệ thống hỗ trợ lưu giữ ngữ cảnh cuộc trò chuyện (Session Tracking) và tích hợp cơ chế nhận dạng lỗi Google Quota thông minh để Tự động chuyển đổi Model (Auto Fallback) giữ mạch liền mạch cho người dùng.

---

## 📁 Cấu trúc Dự án

```text
/
├── frontend/
│   └── index.html             # Giao diện Trang web Chat (HTML/JS/CSS)
├── backend/
│   ├── api.py                 # Core API xử lý kết nối Google GenAI + Mạng
│   ├── demo.py                # File kiểm thử Script ngầm
│   └── requirements.txt       # Danh sách thư viện bắt buộc
└── README.md                  # Hướng dẫn dự án
```

> ⚠️ **Lưu ý Bảo mật:** Trước khi Push Code này lên dạng Public trên Github, hãy chắc chắn bạn đã xóa `API_KEY` cá nhân trong file `backend/api.py` và thay bằng một chuỗi "YOUR_API_KEY_HERE".

---

## 🚀 Hướng dẫn Cài đặt & Chạy trên Local (Máy tính cá nhân)

### Yêu cầu môi trường
* **Python**: Phiên bản 3.10 trở lên (khuyên dùng `3.13.x`).
* Git (Nếu bạn clone từ Github).

### Bước 1: Khởi tạo và Kích hoạt Môi trường Ảo (venv)
Mở Terminal / Command Prompt tại thư mục gốc của dự án. Thực thi các lệnh:

**Dành cho hệ điều hành Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Dành cho hệ điều hành MacOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Sau khi kích hoạt thành công, dấu nhắc lệnh của bạn ở terminal sẽ có chữ `(venv)` ở đầu.

### Bước 2: Cài đặt Thư viện
Bạn di chuyển Terminal vào thư mục backend và tiến hành nạp thư viện:
```powershell
cd backend
pip install -r requirements.txt
```
*(Lệnh này sẽ tự kéo các package cần thiết như: fastapi, uvicorn, pydantic, google-genai).*

### Bước 3: Cấu hình khóa API (API Key)
Hệ thống cần khoá dịch vụ của Google để có bộ não phản hồi tin nhắn.
1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey) để xin 1 chuỗi ký tự API_KEY miễn phí.
2. Mở file `backend/api.py` hoặc `api.py`.
3. Tìm cụm biến `API_KEY` và trỏ giá trị của bạn vào đó:
   ```python
   API_KEY = "AIzaSy..." # Thay thế bằng key của bạn
   ```

### Bước 4: Vận hành Server
Đảm bảo Terminal của bạn đang đứng tại thư mục `backend` và có dấu `(venv)`. Chạy lệnh:

```powershell
python api.py
```
*(Hoặc có thể bật bằng lệnh gốc của máy chủ FastAPI:`uvicorn api:app --reload`)*

### Bước 5: Trải nghiệm Thành quả
* 🌐 **Truy cập Giao diện Chatbot:** Mở trình duyệt và vào [http://127.0.0.1:8000](http://127.0.0.1:8000). Bot đã sẵn sàng nhận tin nhắn!
* 🛠️ **Truy cập API Docs (Swagger):** Mở [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) để xem cấu hình Endpoint nếu bạn muốn tiếp tục lập trình cho App Mobile hay phần mềm khác kết nối vào.
