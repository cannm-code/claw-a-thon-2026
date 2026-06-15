import json
import re
from pathlib import Path
from openai import OpenAI
from app.config import settings
from app.booking import search_inventory, get_sku_detail, knowledge_base
from app.airports import search_airports, resolve_iata

_system_prompt = (Path(__file__).parent.parent / "SYSTEM_PROMPT.md").read_text(encoding="utf-8")

_client = OpenAI(base_url=settings.minimax_base_url, api_key=settings.minimax_api_key)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_inventory",
            "description": "Tìm kiếm sản phẩm du lịch (vé máy bay, xe khách, tàu hỏa, khách sạn, vé tham quan) theo các tham số đầu vào.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vertical": {
                        "type": "string",
                        "description": "Loại sản phẩm: flight, bus, train, hotel, hoặc sightseeing",
                    },
                    "origin": {
                        "type": "string",
                        "description": "Mã sân bay/thành phố khởi hành (HAN, SGN, DAD, ...) hoặc tên thành phố",
                    },
                    "destination": {
                        "type": "string",
                        "description": "Mã sân bay/thành phố đến hoặc tên thành phố/điểm đến",
                    },
                    "date": {
                        "type": "string",
                        "description": "Ngày đi/nhận phòng định dạng YYYY-MM-DD",
                    },
                    "pax": {
                        "type": "integer",
                        "description": "Số lượng hành khách/khách",
                        "default": 1,
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Giá tối đa (VND)",
                    },
                    "filters": {
                        "type": "object",
                        "description": "Bộ lọc bổ sung như cabin, star_rating, seat_class, ...",
                    },
                },
                "required": ["vertical"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sku_detail",
            "description": "Lấy thông tin chi tiết (quy định hoàn/đổi vé, hành lý, điều khoản) của một sản phẩm theo sku_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku_id": {
                        "type": "string",
                        "description": "Mã SKU của sản phẩm cần xem chi tiết",
                    }
                },
                "required": ["sku_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "airport_lookup",
            "description": "Tra cứu mã IATA và thông tin sân bay từ tên thành phố, tên sân bay hoặc mã IATA. Dùng khi người dùng nhập tên thành phố hoặc địa danh không rõ mã sân bay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Tên thành phố, tên sân bay, hoặc mã IATA cần tra cứu (ví dụ: 'Hà Nội', 'Phú Quốc', 'Singapore', 'HAN')",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "knowledge_base",
            "description": "Tra cứu chính sách, FAQ về hành lý, hoàn/đổi vé, check-in, quy định chung.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Câu hỏi hoặc từ khóa cần tra cứu",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

def _airport_lookup_handler(args: dict):
    query = args.get("query", "")
    results = search_airports(query, limit=5)
    if not results:
        return {"found": False, "message": f"Không tìm thấy sân bay cho '{query}'"}
    return {"found": True, "airports": [
        {"iata": a["iata"], "name": a["name"], "city": a["city"], "country": a["country"]}
        for a in results
    ]}


_TOOL_HANDLERS = {
    "search_inventory": lambda args: search_inventory(**args),
    "get_sku_detail": lambda args: get_sku_detail(**args),
    "knowledge_base": lambda args: knowledge_base(**args),
    "airport_lookup": _airport_lookup_handler,
}


def _execute_tool(name: str, args: dict):
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return handler(args)
    except Exception as e:
        return {"error": str(e)}


def parse_structured_response(text: str) -> tuple[str, dict | None]:
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    pattern = r"```json\s*([\s\S]*?)```"
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text, None

    structured = None
    actions_list = None
    for m in matches:
        try:
            parsed = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
        if parsed.get("type") == "actions":
            actions_list = parsed.get("actions", [])
        else:
            structured = parsed

    clean_text = re.sub(pattern, "", text).strip()

    if structured is None and actions_list is not None:
        return clean_text, {"type": "actions", "actions": actions_list}
    if structured is not None and actions_list is not None:
        structured["actions"] = actions_list
    return clean_text, structured


def run_agent(messages: list[dict]) -> tuple[str, dict | None]:
    full_messages = [{"role": "system", "content": _system_prompt}] + messages

    for _ in range(8):
        response = _client.chat.completions.create(
            model=settings.model_name,
            messages=full_messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            full_messages.append(msg.model_dump(exclude_none=True))
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                result = _execute_tool(tc.function.name, args)
                full_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
        else:
            final_text = msg.content or ""
            return parse_structured_response(final_text)

    return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu. Vui lòng thử lại.", None
