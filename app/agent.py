import json
import re
from pathlib import Path
from openai import OpenAI
from app.config import settings
from app.booking import search_inventory, get_sku_detail, knowledge_base, discover_destinations, price_calendar, compare_transport, search_accommodation
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
    {
        "type": "function",
        "function": {
            "name": "discover_destinations",
            "description": "Gợi ý điểm đến phù hợp khi user chưa biết muốn đi đâu. Lọc theo ngân sách, vibe (beach/city/nature/food/culture), tình trạng visa, và khu vực (domestic/any).",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Mã sân bay khởi hành, mặc định SGN"},
                    "budget_max": {"type": "number", "description": "Ngân sách tối đa (VND) cho chặng bay 1 chiều"},
                    "region": {"type": "string", "description": "Khu vực: 'domestic' (nội địa VN), 'any' (tất cả)"},
                    "vibe": {"type": "string", "description": "Kiểu du lịch: beach, city, nature, food, culture, honeymoon"},
                    "month": {"type": "string", "description": "Tháng dự định đi, định dạng YYYY-MM"},
                    "visa_free_only": {"type": "boolean", "description": "Chỉ lấy điểm đến miễn visa, mặc định true"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "price_calendar",
            "description": "Tra lịch giá vé cho một chặng bay để tìm ngày rẻ nhất trong tháng.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Mã sân bay khởi hành"},
                    "destination": {"type": "string", "description": "Mã sân bay hoặc tên thành phố đến"},
                    "month": {"type": "string", "description": "Tháng cần xem, định dạng YYYY-MM. Null = xem tổng thể"},
                },
                "required": ["origin", "destination"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_transport",
            "description": "So sánh các phương tiện di chuyển (máy bay, tàu hỏa, xe khách) cho cùng một chặng và ngày. Chỉ trả phương tiện thực sự hỗ trợ chặng đó.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Điểm khởi hành"},
                    "destination": {"type": "string", "description": "Điểm đến"},
                    "date": {"type": "string", "description": "Ngày đi YYYY-MM-DD"},
                },
                "required": ["origin", "destination", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_accommodation",
            "description": "Tìm kiếm khách sạn, homestay, hostel theo khu vực, ngày nhận/trả phòng, số khách, ngân sách. Trả về options[{sku_id, title, type, price, currency, area, note}] — dùng title và price trực tiếp vào results JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area": {"type": "string", "description": "Tên thành phố / khu vực"},
                    "check_in": {"type": "string", "description": "Ngày nhận phòng YYYY-MM-DD"},
                    "check_out": {"type": "string", "description": "Ngày trả phòng YYYY-MM-DD"},
                    "guests": {"type": "integer", "description": "Số khách", "default": 2},
                    "budget_max": {"type": "number", "description": "Giá tối đa mỗi đêm (VND)"},
                    "acc_type": {"type": "string", "description": "Loại chỗ ở: hotel, homestay, hostel. Null = tất cả"},
                },
                "required": ["area", "check_in", "check_out"],
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
    "discover_destinations": lambda args: discover_destinations(**args),
    "price_calendar": lambda args: price_calendar(**args),
    "compare_transport": lambda args: compare_transport(**args),
    "search_accommodation": lambda args: search_accommodation(**{k if k != "type" else "acc_type": v for k, v in args.items()}),
}


def _execute_tool(name: str, args: dict):
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return handler(args)
    except Exception as e:
        return {"error": str(e)}


def _parse_minimax_xml(text: str) -> tuple[str, dict | None]:
    """Parse MiniMax XML tool-call blocks that appear in message content.

    Handles both:
      <minimax:tool_call><invoke name="TYPE"><parameter name="K">V</parameter>...</invoke></minimax:tool_call>
    and the plain variant without namespace:
      <tool_call><invoke name="TYPE">...</invoke></tool_call>
    """
    xml_pattern = re.compile(
        r"<(?:minimax:)?tool_call>\s*<invoke\s+name=[\"']([^\"']+)[\"']>([\s\S]*?)</invoke>\s*</(?:minimax:)?tool_call>",
        re.IGNORECASE,
    )
    param_pattern = re.compile(r"<parameter\s+name=[\"']([^\"']+)[\"']>([\s\S]*?)</parameter>", re.IGNORECASE)

    structured = None
    actions_list = None

    def _replace(m: re.Match) -> str:
        nonlocal structured, actions_list
        invoke_name = m.group(1).strip()
        params_block = m.group(2)
        params: dict = {}
        for pm in param_pattern.finditer(params_block):
            key, val = pm.group(1).strip(), pm.group(2).strip()
            # Try to cast numeric values
            try:
                params[key] = int(val)
            except ValueError:
                try:
                    params[key] = float(val)
                except ValueError:
                    params[key] = val

        # Map invoke name to structured payload
        if invoke_name == "handoff":
            payload = {"type": "handoff", **params}
            structured = payload
        elif invoke_name in ("results", "suggestions", "inspiration", "price_calendar", "fallback", "experiences"):
            structured = {"type": invoke_name, **params}
        elif invoke_name == "actions":
            actions_list = params.get("actions", [])
        # Remove the raw XML block from the displayed text
        return ""

    clean_text = xml_pattern.sub(_replace, text).strip()

    if structured is not None and actions_list is not None:
        structured["actions"] = actions_list
    if structured is None and actions_list is not None:
        structured = {"type": "actions", "actions": actions_list}

    return clean_text, structured


def parse_structured_response(text: str) -> tuple[str, dict | None]:
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

    # Handle MiniMax XML tool-call format first
    if re.search(r"<(?:minimax:)?tool_call>", text, re.IGNORECASE):
        clean_text, structured = _parse_minimax_xml(text)
        # If there are also JSON blocks in the same message, merge them below
        text = clean_text
        xml_structured = structured
    else:
        xml_structured = None

    pattern = r"```json\s*([\s\S]*?)```"
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text, xml_structured

    structured = xml_structured
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
