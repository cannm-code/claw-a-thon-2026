# Claw-a-thon 2026 — AI Travel Booking Agent

Trợ lý đặt chỗ du lịch AI bằng tiếng Việt, hỗ trợ 5 loại sản phẩm: chuyến bay, xe khách, tàu hỏa, khách sạn, vé tham quan.

## Yêu cầu

- Python 3.11+
- Tài khoản GreenNode (hoặc bất kỳ API tương thích OpenAI)
- Model: minimax/minimax-m2.5 (DEFAULT), ưu tiên sử dụng `Gemini 3.5 Flash` hoặc `Claude Sonet 4.6` nếu BTC có thể hỗ trợ

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
#   MODEL_BASE_URL=https://api.minimax.chat/v1
#   MODEL_API_KEY=your_api_key_here
#   MODEL_NAME=MiniMax-M2.5

# 5. Chạy server
uvicorn app.main:app --reload

# 6. Mở trình duyệt
# http://localhost:8000
```

## Cấu trúc dự án

```
claw-a-thon-2026/
├── SYSTEM_PROMPT.md        # System prompt của agent Hannah
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

- **Chat tiếng Việt** với agent Hannah
- **5 verticals**: chuyến bay, xe khách, tàu hỏa, khách sạn, vé tham quan
- **Suggestion chips** với hình ảnh điểm đến — click để chọn nhanh
- **Result cards** hiển thị thông tin chuyến bay/khách sạn/vé
- **Checkout flow**: form hành khách + chọn phương thức thanh toán
- **Booking confirmation**: mã đặt chỗ `CLA-XXXXXX`
- **Session persistence**: dữ liệu đặt chỗ lưu trong `data/sessions/`

## Cấu hình LLM

Hỗ trợ bất kỳ API tương thích OpenAI. Ví dụ:

| Provider | MODEL_BASE_URL | MODEL_NAME |
|---|---|---|
| MiniMax | `https://api.minimax.chat/v1` | `MiniMax-M2.5` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Azure OpenAI | `https://<resource>.openai.azure.com/openai/deployments/<deploy>` | `gpt-4o` |
| Local (LM Studio) | `http://localhost:1234/v1` | tên model local |

## Deployment complete!

Step 9/9: Verify ✓

  Project:     claw-a-thon-2026
  Runtime ID:  runtime-fb1945d6-5e78-4d89-9a25-450ed5e07551
  Version:     1
  Status:      ACTIVE
  Endpoint:    https://endpoint-8e85887c-b6bd-4095-9be8-8383a12eacd6.agentbase-runtime.aiplatform.vngcloud.vn
  Health:      OK (200)
  Memory:      memory-c17038cd-8aea-4446-b88d-067df6e8545b (SEMANTIC)
  Image:       vcr.vngcloud.vn/111480-abp111978/claw-a-thon-2026:latest

Console: https://aiplatform.console.vngcloud.vn/agent-runtime?tab=runtime
Your Claw-a-thon 2026 travel assistant is live. You can visit the endpoint URL directly in a browser to use the chat UI. A few notes:

Re-deploy updates: rebuild + push the image, then run /agentbase-deploy and update the runtime with the new tag
Logs & metrics: use /agentbase-monitor to watch live logs from the container
Credential note: Docker's credsStore was changed from desktop to plain config storage — if you restart Docker Desktop later, you may want to run cr.sh credentials docker-login again to re-authenticate
