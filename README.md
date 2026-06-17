# Claw-a-thon 2026 — AI Travel Booking Agent

1. Vấn đề đội giải quyết
Hiện nay, việc lên kế hoạch cho một chuyến du lịch thường mất rất nhiều thời gian và công sức. Người dùng phải liên tục chuyển đổi qua lại giữa hàng chục ứng dụng và trang web khác nhau để tìm kiếm, so sánh giá cả và đặt các dịch vụ riêng lẻ. Sự phân mảnh này dẫn đến tình trạng quá tải thông tin, khiến việc "săn" được những mức giá tốt nhất trở nên khó khăn, phức tạp và dễ gây nản lòng trước khi chuyến đi thực sự bắt đầu.

2. Người dùng mục tiêu
Khách hàng mục tiêu bao gồm giới trẻ bận rộn, dân văn phòng, hoặc các gia đình muốn tổ chức những chuyến đi tự túc. Đây là những người cần một giải pháp đặt chỗ tiện lợi, chính xác, không muốn tốn hàng giờ đồng hồ để tự mình nghiên cứu lịch trình hay đối chiếu giá cả.

3. Cách AI Agent giải quyết vấn đề
Chúng tôi phát triển một Trợ lý đặt chỗ du lịch AI bằng tiếng Việt, đóng vai trò như một "em gái du lịch" tận tâm và thông minh. Thay vì phải tự tìm kiếm trên nhiều nền tảng, người dùng chỉ cần tương tác bằng ngôn ngữ tự nhiên qua giao diện chat. Ngay lập tức, AI Agent sẽ hiểu ngữ cảnh, tự động quét và tổng hợp dữ liệu từ 5 loại hình dịch vụ cốt lõi: chuyến bay, xe khách, tàu hỏa, khách sạn và vé tham quan. Trợ lý sẽ phân tích chéo các nguồn, đề xuất những lựa chọn phù hợp nhất với nhu cầu và hỗ trợ hoàn tất đặt chỗ ngay tại một nơi duy nhất.

4. Giá trị mang lại
Giải pháp này mang đến một trải nghiệm du lịch "nhanh - gọn - lẹ" và hoàn toàn liền mạch. Người dùng tiết kiệm được hàng giờ đồng hồ tìm kiếm và giảm bớt căng thẳng khi lên kế hoạch. Đồng thời, nhờ khả năng tối ưu hóa của AI, khách hàng có thể dễ dàng chốt được các "deal" tiết kiệm chi phí nhất. Sản phẩm biến một quy trình đặt vé khô khan, phức tạp trở nên nhẹ nhàng, cá nhân hóa và thân thiện như đang trò chuyện với một người bạn thực sự thấu hiểu sở thích xê dịch của mình.

## Yêu cầu

- Python 3.11+
- Tài khoản GreenNode (hoặc bất kỳ API tương thích OpenAI)
- Model: `minimax/minimax-m2.5` (mặc định), ưu tiên sử dụng `Gemini 3.5 Flash` hoặc `Claude Sonet 4.6` nếu BTC có thể hỗ trợ

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
├── SYSTEM_PROMPT.md        # System prompt của agent Vivi
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

- **Chat tiếng Việt** với agent Vivi
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
| GreenNode | `https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1` | `minimax-m2.5` |
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
