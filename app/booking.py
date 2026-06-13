import json
import os
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"

_data: dict[str, list[dict]] = {}

def _load():
    for vertical in ("flights", "buses", "trains", "hotels", "sightseeing"):
        path = DATA_DIR / f"{vertical}.json"
        with open(path, "r", encoding="utf-8") as f:
            _data[vertical] = json.load(f)

_load()

_VERTICAL_MAP = {
    "flight": "flights",
    "chuyến bay": "flights",
    "bus": "buses",
    "xe khách": "buses",
    "train": "trains",
    "tàu hỏa": "trains",
    "hotel": "hotels",
    "khách sạn": "hotels",
    "sightseeing": "sightseeing",
    "vé tham quan": "sightseeing",
}

_FAQ = [
    {
        "topic": "hành lý",
        "keywords": ["hành lý", "baggage", "xách tay", "ký gửi", "cân nặng"],
        "passage": "Hành lý xách tay: VietJet 7kg, Vietnam Airlines 12kg, Bamboo 10kg. Hành lý ký gửi: VietJet mua thêm từ 180,000₫, Vietnam Airlines 23kg miễn phí, Bamboo 20kg miễn phí. Xe khách và tàu hỏa thường cho phép 15-30kg.",
    },
    {
        "topic": "hủy vé",
        "keywords": ["hủy", "hoàn tiền", "refund", "cancellation", "hủy vé"],
        "passage": "Chính sách hủy vé: VietJet không hoàn vé (ngoại trừ trường hợp đặc biệt). Vietnam Airlines hoàn 60-70% nếu hủy trước 48h. Bamboo Airways hoàn 65-70% nếu hủy trước 48h. Khách sạn thường miễn phí hủy trước 24-48h.",
    },
    {
        "topic": "đổi vé",
        "keywords": ["đổi vé", "thay đổi", "reschedule", "change ticket"],
        "passage": "Đổi vé: Vietnam Airlines cho phép đổi trước 24h với phí 200,000₫. Bamboo Airways đổi 1 lần miễn phí trước 24h. VietJet không cho đổi vé. Tàu hỏa: đổi trước 12-24h với phí 5-10%.",
    },
    {
        "topic": "check-in",
        "keywords": ["check-in", "làm thủ tục", "boarding", "lên máy bay"],
        "passage": "Check-in sân bay: nên đến trước 2h với chuyến nội địa. Online check-in mở từ 24h trước chuyến bay. Cổng boarding đóng trước 30 phút khởi hành.",
    },
    {
        "topic": "chuyển nhượng",
        "keywords": ["chuyển nhượng", "tên", "đổi tên", "transfer", "hành khách"],
        "passage": "Đổi tên hành khách: hầu hết hãng bay nội địa không cho đổi tên. VietJet: chỉ chỉnh sửa lỗi chính tả với phí 300,000₫. Vietnam Airlines: không hỗ trợ đổi tên.",
    },
    {
        "topic": "gợi ý điểm đến",
        "keywords": ["popular", "điểm đến", "đi đâu", "gợi ý", "đề xuất", "destinations"],
        "passage": "Điểm đến phổ biến từ Hà Nội: Đà Nẵng (~1h15m), Phú Quốc (~2h), TP.HCM (~2h), Hội An (qua Đà Nẵng), Nha Trang (~2h). Điểm đến phổ biến từ TP.HCM: Phú Quốc (~1h), Nha Trang (~1h15m), Đà Nẵng (~1h15m), Hà Nội (~2h). Điểm gần Hà Nội: Ninh Bình (~2.5h xe), Hải Phòng (~1.5h xe), Hạ Long (~3h xe).",
    },
]

_SUGGESTIONS = {
    "HAN": [
        {"label": "Đà Nẵng", "value": "Đà Nẵng", "image_key": "danang", "subtitle": "✈️ ~1h15m"},
        {"label": "Phú Quốc", "value": "Phú Quốc", "image_key": "phuquoc", "subtitle": "✈️ ~2h"},
        {"label": "TP.HCM", "value": "TP.HCM", "image_key": "hcmc", "subtitle": "✈️ ~2h"},
        {"label": "Hội An", "value": "Hội An", "image_key": "hoian", "subtitle": "✈️ ~1h15m"},
        {"label": "Nha Trang", "value": "Nha Trang", "image_key": "nhatrang", "subtitle": "✈️ ~1h30m"},
    ],
    "SGN": [
        {"label": "Phú Quốc", "value": "Phú Quốc", "image_key": "phuquoc", "subtitle": "✈️ ~1h"},
        {"label": "Nha Trang", "value": "Nha Trang", "image_key": "nhatrang", "subtitle": "✈️ ~1h15m"},
        {"label": "Đà Nẵng", "value": "Đà Nẵng", "image_key": "danang", "subtitle": "✈️ ~1h15m"},
        {"label": "Hà Nội", "value": "Hà Nội", "image_key": "hanoi", "subtitle": "✈️ ~2h"},
        {"label": "Vĩnh Long", "value": "Vĩnh Long", "image_key": "mekong", "subtitle": "🚌 ~2.5h"},
    ],
    "default": [
        {"label": "Đà Nẵng", "value": "Đà Nẵng", "image_key": "danang", "subtitle": "Điểm đến hot"},
        {"label": "Phú Quốc", "value": "Phú Quốc", "image_key": "phuquoc", "subtitle": "Thiên đường biển"},
        {"label": "Hội An", "value": "Hội An", "image_key": "hoian", "subtitle": "Phố cổ lãng mạn"},
        {"label": "Hạ Long", "value": "Hạ Long", "image_key": "halong", "subtitle": "Kỳ quan thiên nhiên"},
        {"label": "Nha Trang", "value": "Nha Trang", "image_key": "nhatrang", "subtitle": "Biển xanh cát trắng"},
    ],
}


def search_inventory(
    vertical: str,
    origin: str = "",
    destination: str = "",
    date: str = "",
    pax: int = 1,
    max_price: float | None = None,
    filters: dict | None = None,
) -> list[dict]:
    key = _VERTICAL_MAP.get(vertical.lower(), vertical.lower())
    items = _data.get(key, [])

    results = []
    for item in items:
        if key in ("flights", "buses", "trains"):
            orig = (origin or "").upper()
            dest = (destination or "").upper()
            if orig and item.get("origin", "").upper() != orig:
                continue
            if dest and item.get("destination", "").upper() != dest:
                # Also check destination_name for fuzzy matching
                dest_name = item.get("destination_name", "").lower()
                dest_lower = destination.lower()
                if dest_lower not in dest_name and dest not in item.get("destination", "").upper():
                    continue
        elif key == "hotels":
            city = (destination or origin or "").upper()
            if city and item.get("city", "").upper() != city:
                city_name = item.get("city_name", "").lower()
                if city.lower() not in city_name:
                    continue
        elif key == "sightseeing":
            loc = destination or origin or ""
            if loc:
                loc_lower = loc.lower()
                item_loc = item.get("location", "").lower()
                item_attr = item.get("attraction", "").lower()
                if loc_lower not in item_loc and loc_lower not in item_attr:
                    continue

        if max_price is not None and item.get("price", 0) > max_price:
            continue

        results.append(item)

    return results[:5]


def get_sku_detail(sku_id: str) -> dict | None:
    for items in _data.values():
        for item in items:
            if item.get("sku_id") == sku_id:
                return item
    return None


def knowledge_base(query: str) -> list[str]:
    query_lower = query.lower()
    matched = []
    for faq in _FAQ:
        if any(kw in query_lower for kw in faq["keywords"]):
            matched.append(faq["passage"])
    if not matched:
        matched = [_FAQ[0]["passage"]]
    return matched[:2]


def get_suggestions(origin: str = "") -> list[dict]:
    key = (origin or "").upper()
    return _SUGGESTIONS.get(key, _SUGGESTIONS["default"])
