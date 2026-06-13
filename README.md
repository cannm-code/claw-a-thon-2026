# Claw-a-thon 2026 — AI Travel Booking Agent

Trợ lý đặt chỗ du lịch AI bằng tiếng Việt, hỗ trợ 5 loại sản phẩm: chuyến bay, xe khách, tàu hỏa, khách sạn, vé tham quan.

## Yêu cầu

- Python 3.11+
- Tài khoản MiniMax (hoặc bất kỳ API tương thích OpenAI)

## Cài đặt

```bash
# 1. Clone và vào thư mục dự án
cd claw-a-thon-2026

# 2. Tạo môi trường ảo
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Cấu hình API
cp .env.example .env
# Mở .env và điền thông tin:
#   MINIMAX_BASE_URL=https://api.minimax.chat/v1
#   MINIMAX_API_KEY=your_api_key_here
#   MODEL_NAME=MiniMax-M2.5

# 5. Chạy server
uvicorn app.main:app --reload

# 6. Mở trình duyệt
# http://localhost:8000
```

## Cấu trúc dự án

```
claw-a-thon-2026/
├── SYSTEM_PROMPT.md        # System prompt của agent Chloe
├── requirements.txt
├── .env.example
├── app/
│   ├── main.py             # FastAPI app, routes, session
│   ├── agent.py            # Agent loop + tool calling
│   ├── booking.py          # Mock booking APIs
│   ├── config.py           # Cấu hình từ .env
│   ├── data/               # Mock data JSON
│   │   ├── flights.json
│   │   ├── buses.json
│   │   ├── trains.json
│   │   ├── hotels.json
│   │   └── sightseeing.json
│   └── static/             # Frontend
│       ├── index.html
│       ├── app.js
│       └── images/         # SVG destination images
└── data/sessions/          # Session persistence (auto-created)
```

## Tính năng

- **Chat tiếng Việt** với agent Chloe
- **5 verticals**: chuyến bay, xe khách, tàu hỏa, khách sạn, vé tham quan
- **Suggestion chips** với hình ảnh điểm đến — click để chọn nhanh
- **Result cards** hiển thị thông tin chuyến bay/khách sạn/vé
- **Checkout flow**: form hành khách + chọn phương thức thanh toán
- **Booking confirmation**: mã đặt chỗ `CLA-XXXXXX`
- **Session persistence**: dữ liệu đặt chỗ lưu trong `data/sessions/`

## Cấu hình LLM

Hỗ trợ bất kỳ API tương thích OpenAI. Ví dụ:

| Provider | BASE_URL | MODEL_NAME |
|---|---|---|
| MiniMax | `https://api.minimax.chat/v1` | `MiniMax-M2.5` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Azure OpenAI | `https://<resource>.openai.azure.com/openai/deployments/<deploy>` | `gpt-4o` |
| Local (LM Studio) | `http://localhost:1234/v1` | tên model local |
