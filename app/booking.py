from __future__ import annotations

import hashlib
import json
from pathlib import Path

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

_CITY_IMAGE_KEY = {
    "HAN": "hanoi",
    "SGN": "hcmc",
    "HCM": "hcmc",
    "DAD": "danang",
    "DAN": "danang",
    "PQC": "phuquoc",
    "NHA": "nhatrang",
    "NTR": "nhatrang",
    "HOI": "hoian",
    "HAN_HOI": "hoian",
    "HLG": "halong",
    "MEK": "mekong",
}

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

        entry = dict(item)
        if date:
            if key in ("flights", "buses", "trains"):
                entry["depart_date"] = date
            elif key == "hotels":
                entry["check_in_date"] = date
            elif key == "sightseeing":
                entry["visit_date"] = date
        if "image_key" not in entry or not entry["image_key"]:
            if key == "sightseeing":
                entry["image_key"] = entry.get("location_key", "")
            elif key in ("flights", "buses", "trains"):
                dest_code = entry.get("destination", "").upper()
                entry["image_key"] = _CITY_IMAGE_KEY.get(dest_code, "")
            elif key == "hotels":
                city_code = entry.get("city", "").upper()
                entry["image_key"] = _CITY_IMAGE_KEY.get(city_code, "")
        results.append(entry)

    if not results:
        results = _generate_mock(key, origin, destination, date, pax, max_price)

    return results[:5]


def _seed(origin: str, destination: str, date: str, idx: int) -> int:
    raw = f"{origin}{destination}{date}{idx}"
    return int(hashlib.md5(raw.encode()).hexdigest(), 16)


def _pick(seed: int, choices: list):
    return choices[seed % len(choices)]


def _mock_flights(origin: str, destination: str, date: str, pax: int, max_price: float | None) -> list[dict]:
    origin_name = origin or "Điểm khởi hành"
    dest_name = destination or "Điểm đến"
    templates = [
        {"airline": "Vietnam Airlines", "airline_code": "VN", "cabin": "Phổ thông",
         "base_price": 1_200_000, "baggage_kg": 23,
         "highlights": ["Hành lý 23kg miễn phí", "Bữa ăn trên máy bay", "Đổi vé linh hoạt"],
         "fare_rules": "Đổi trước 24h với phí 200,000₫.", "cancellation": "Hoàn 70% trước 48h."},
        {"airline": "VietJet Air", "airline_code": "VJ", "cabin": "Phổ thông",
         "base_price": 750_000, "baggage_kg": 0,
         "highlights": ["Giá tiết kiệm", "Chọn chỗ ngồi linh hoạt"],
         "fare_rules": "Không đổi, không hoàn.", "cancellation": "Không hoàn vé."},
        {"airline": "Bamboo Airways", "airline_code": "QH", "cabin": "Phổ thông",
         "base_price": 990_000, "baggage_kg": 20,
         "highlights": ["Hành lý 20kg miễn phí", "Đổi vé 1 lần miễn phí"],
         "fare_rules": "Đổi 1 lần miễn phí trước 24h.", "cancellation": "Hoàn 65% trước 48h."},
        {"airline": "Vietnam Airlines", "airline_code": "VN", "cabin": "Thương gia",
         "base_price": 4_500_000, "baggage_kg": 32,
         "highlights": ["Ghế nằm phẳng", "Phòng chờ VIP", "Hành lý 32kg"],
         "fare_rules": "Đổi vé miễn phí.", "cancellation": "Hoàn 80% bất kỳ lúc nào."},
        {"airline": "Vietravel Airlines", "airline_code": "VU", "cabin": "Phổ thông",
         "base_price": 850_000, "baggage_kg": 0,
         "highlights": ["Giá ưu đãi", "Thanh toán linh hoạt"],
         "fare_rules": "Không đổi vé.", "cancellation": "Không hoàn."},
    ]
    depart_times = ["06:00", "08:30", "10:15", "13:00", "15:45", "17:20", "19:00", "21:10"]
    results = []
    for i, tpl in enumerate(templates[:4]):
        s = _seed(origin, destination, date, i)
        price = tpl["base_price"] + (s % 5) * 50_000
        if max_price is not None and price > max_price:
            price = int(max_price * 0.9)
        d_hour, d_min = map(int, _pick(s, depart_times).split(":"))
        duration = 75 + (s % 6) * 10
        a_hour = (d_hour + (d_min + duration) // 60) % 24
        a_min = (d_min + duration) % 60
        fn = f"{tpl['airline_code']} {100 + (s % 800)}"
        results.append({
            "sku_id": f"MOCK-{tpl['airline_code']}-{origin}-{destination}-{i+1:03d}",
            "vertical": "flight",
            "airline": tpl["airline"],
            "airline_code": tpl["airline_code"],
            "flight_number": fn,
            "origin": origin,
            "origin_name": origin_name,
            "destination": destination,
            "destination_name": dest_name,
            "depart_date": date,
            "depart_time": f"{d_hour:02d}:{d_min:02d}",
            "arrive_time": f"{a_hour:02d}:{a_min:02d}",
            "duration_min": duration,
            "price": price,
            "currency": "VND",
            "cabin": tpl["cabin"],
            "availability": True,
            "seats_left": 5 + (s % 30),
            "baggage_kg": tpl["baggage_kg"],
            "highlights": tpl["highlights"],
            "fare_rules": tpl["fare_rules"],
            "cancellation": tpl["cancellation"],
            "baggage": f"Hành lý xách tay: 7kg. Ký gửi: {tpl['baggage_kg']}kg{'miễn phí' if tpl['baggage_kg'] > 0 else ' (mua thêm)'}.",
        })
    return results


def _mock_buses(origin: str, destination: str, date: str, pax: int, max_price: float | None) -> list[dict]:
    dest_name = destination or "Điểm đến"
    operators = ["Hoàng Long", "Phương Trang (FUTA)", "Thành Bưởi", "Kumho Samco", "Mai Linh Express"]
    seat_types = ["Giường nằm 40 chỗ", "Limousine 22 chỗ", "Ghế ngồi 45 chỗ", "Sleeper cao cấp"]
    depart_times = ["06:00", "07:30", "09:00", "12:00", "15:00", "20:00", "22:00"]
    results = []
    for i in range(4):
        s = _seed(origin, destination, date, i)
        price = 150_000 + (s % 10) * 20_000
        if max_price is not None and price > max_price:
            price = int(max_price * 0.9)
        d_time = _pick(s + i, depart_times)
        d_hour, d_min = map(int, d_time.split(":"))
        duration = 180 + (s % 8) * 30
        a_hour = (d_hour + (d_min + duration) // 60) % 24
        a_min = (d_min + duration) % 60
        results.append({
            "sku_id": f"MOCK-BUS-{origin}-{destination}-{i+1:03d}",
            "vertical": "bus",
            "operator": _pick(s, operators),
            "origin": origin,
            "origin_name": origin or "Điểm đi",
            "destination": destination,
            "destination_name": dest_name,
            "depart_date": date,
            "depart_time": d_time,
            "arrive_time": f"{a_hour:02d}:{a_min:02d}",
            "duration_min": duration,
            "price": price,
            "currency": "VND",
            "seat_type": _pick(s + 1, seat_types),
            "availability": True,
            "seats_left": 3 + (s % 20),
            "highlights": ["Xe cao cấp máy lạnh", "Wifi miễn phí", "Đón tại bến chính"],
            "fare_rules": "Đổi vé trước 2h, phí 20,000₫.",
            "cancellation": "Hoàn 80% nếu hủy trước 4h.",
            "baggage": "Hành lý tối đa 20kg/người.",
        })
    return results


def _mock_trains(origin: str, destination: str, date: str, pax: int, max_price: float | None) -> list[dict]:
    dest_name = destination or "Điểm đến"
    classes = [
        {"seat_class": "Ngồi cứng", "base": 150_000},
        {"seat_class": "Ngồi mềm có điều hoà", "base": 280_000},
        {"seat_class": "Nằm cứng (6 chỗ)", "base": 350_000},
        {"seat_class": "Nằm mềm có điều hoà (4 chỗ)", "base": 550_000},
    ]
    trains = ["SE1", "SE3", "SE5", "SE7", "TN1", "SNT1"]
    depart_times = ["06:00", "10:00", "14:30", "19:30", "22:00"]
    results = []
    for i, cls in enumerate(classes):
        s = _seed(origin, destination, date, i)
        price = cls["base"] + (s % 5) * 20_000
        if max_price is not None and price > max_price:
            price = int(max_price * 0.9)
        d_time = _pick(s, depart_times)
        d_hour, d_min = map(int, d_time.split(":"))
        duration = 300 + (s % 10) * 60
        a_hour = (d_hour + (d_min + duration) // 60) % 24
        a_min = (d_min + duration) % 60
        results.append({
            "sku_id": f"MOCK-TRN-{origin}-{destination}-{i+1:03d}",
            "vertical": "train",
            "operator": "Đường sắt Việt Nam",
            "train_number": _pick(s, trains),
            "origin": origin,
            "origin_name": origin or "Điểm đi",
            "destination": destination,
            "destination_name": dest_name,
            "depart_date": date,
            "depart_time": d_time,
            "arrive_time": f"{a_hour:02d}:{a_min:02d}",
            "duration_min": duration,
            "price": price,
            "currency": "VND",
            "seat_class": cls["seat_class"],
            "availability": True,
            "seats_left": 5 + (s % 40),
            "highlights": ["Ngắm phong cảnh đẹp", "Rộng rãi thoải mái", "Điều hoà mát lạnh"],
            "fare_rules": "Đổi vé trước 24h: phí 10%.",
            "cancellation": "Hoàn 75% nếu hủy trước 24h.",
            "baggage": "Hành lý tối đa 30kg/người.",
        })
    return results


def _mock_hotels(city: str, date: str, pax: int, max_price: float | None) -> list[dict]:
    city_name = city or "Điểm đến"
    templates = [
        {"name": f"Grand {city_name} Hotel & Spa", "stars": 5, "base": 3_500_000,
         "amenities": ["Hồ bơi", "Spa", "Gym", "Nhà hàng", "Bar"], "style": "sang trọng"},
        {"name": f"Novotel {city_name} Centre", "stars": 4, "base": 1_800_000,
         "amenities": ["Hồ bơi", "Nhà hàng", "Gym", "Wifi"], "style": "hiện đại"},
        {"name": f"Ibis {city_name}", "stars": 3, "base": 900_000,
         "amenities": ["Nhà hàng", "Wifi", "Lễ tân 24h"], "style": "tiết kiệm"},
        {"name": f"{city_name} Boutique Hotel", "stars": 3, "base": 750_000,
         "amenities": ["Wifi", "Bữa sáng", "Tour hỗ trợ"], "style": "boutique"},
        {"name": f"Mường Thanh Luxury {city_name}", "stars": 4, "base": 1_400_000,
         "amenities": ["Hồ bơi", "Spa", "Nhà hàng VN", "Wifi"], "style": "nội địa cao cấp"},
    ]
    results = []
    for i, tpl in enumerate(templates[:4]):
        s = _seed(city, "", date, i)
        price = tpl["base"] + (s % 8) * 100_000
        if max_price is not None and price > max_price:
            price = int(max_price * 0.9)
        results.append({
            "sku_id": f"MOCK-HTL-{city}-{i+1:03d}",
            "vertical": "hotel",
            "name": tpl["name"],
            "city": city,
            "city_name": city_name,
            "star_rating": tpl["stars"],
            "check_in_date": date,
            "price_per_night": price,
            "currency": "VND",
            "availability": True,
            "rooms_left": 1 + (s % 8),
            "amenities": tpl["amenities"],
            "highlights": [
                f"Khách sạn {tpl['stars']} sao {tpl['style']}",
                f"Trung tâm {city_name}",
                "Dịch vụ chuyên nghiệp",
            ],
            "fare_rules": "Giá theo đêm, chưa gồm thuế & phí dịch vụ.",
            "cancellation": "Miễn phí hủy trước 48h. Sau 48h tính phí 1 đêm.",
            "baggage": "N/A",
        })
    return results


def _mock_sightseeing(location: str, date: str, pax: int, max_price: float | None) -> list[dict]:
    loc_name = location or "Điểm tham quan"
    templates = [
        {"attraction": f"Tour {loc_name} trọn ngày", "base": 450_000,
         "highlights": ["Hướng dẫn viên chuyên nghiệp", "Xe đưa đón", "Bữa trưa included"]},
        {"attraction": f"Vé tham quan {loc_name}", "base": 150_000,
         "highlights": ["Vé ưu tiên vào cổng", "Không chờ đợi", "Bản đồ tham quan"]},
        {"attraction": f"Tour {loc_name} buổi tối", "base": 350_000,
         "highlights": ["Trải nghiệm về đêm", "Ẩm thực địa phương", "Hướng dẫn tiếng Việt"]},
        {"attraction": f"Combo {loc_name} + ẩm thực", "base": 600_000,
         "highlights": ["Tham quan + ăn uống", "Top 5 quán ngon", "Linh hoạt thời gian"]},
    ]
    results = []
    for i, tpl in enumerate(templates):
        s = _seed(location, "", date, i)
        price = tpl["base"] + (s % 5) * 30_000
        if max_price is not None and price > max_price:
            price = int(max_price * 0.9)
        results.append({
            "sku_id": f"MOCK-SIGHT-{location}-{i+1:03d}",
            "vertical": "sightseeing",
            "attraction": tpl["attraction"],
            "location": loc_name,
            "visit_date": date,
            "price": price,
            "currency": "VND",
            "availability": True,
            "slots_left": 5 + (s % 20),
            "highlights": tpl["highlights"],
            "fare_rules": "Vé đã xác nhận, không đổi ngày.",
            "cancellation": "Hoàn 80% nếu hủy trước 24h.",
            "baggage": "N/A",
        })
    return results


def _generate_mock(
    key: str, origin: str, destination: str, date: str, pax: int, max_price: float | None
) -> list[dict]:
    if key == "flights":
        return _mock_flights(origin, destination, date, pax, max_price)
    if key == "buses":
        return _mock_buses(origin, destination, date, pax, max_price)
    if key == "trains":
        return _mock_trains(origin, destination, date, pax, max_price)
    if key == "hotels":
        return _mock_hotels(destination or origin, date, pax, max_price)
    if key == "sightseeing":
        return _mock_sightseeing(destination or origin, date, pax, max_price)
    return []


def get_sku_detail(sku_id: str) -> dict | None:
    for items in _data.values():
        for item in items:
            if item.get("sku_id") == sku_id:
                return item
    # For mock SKUs, re-generate the result set and find by sku_id
    if sku_id.startswith("MOCK-"):
        parts = sku_id.split("-")
        if len(parts) >= 3:
            vertical_tag = parts[1]
            tag_map = {"VN": "flights", "VJ": "flights", "QH": "flights", "VU": "flights",
                       "BUS": "buses", "TRN": "trains", "HTL": "hotels", "SIGHT": "sightseeing"}
            key = tag_map.get(vertical_tag)
            if key:
                origin = parts[2] if len(parts) > 2 else ""
                destination = parts[3] if len(parts) > 3 else ""
                mocks = _generate_mock(key, origin, destination, "", 1, None)
                for m in mocks:
                    if m.get("sku_id") == sku_id:
                        return m
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


# ── Destination lookup helper ─────────────────────────────────────────────────

_DESTINATIONS = [
    {"destination":"Bangkok","country":"TH","iata":"BKK","est_price":2500000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN, ở tối đa 30 ngày","best_months":["11","12","1","2","3"],"vibe_tags":["city","shopping","food"],"flight_time":"2h"},
    {"destination":"Phuket","country":"TH","iata":"HKT","est_price":3200000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN, ở tối đa 30 ngày","best_months":["11","12","1","2"],"vibe_tags":["beach","nature"],"flight_time":"1h30"},
    {"destination":"Singapore","country":"SG","iata":"SIN","est_price":4500000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN, ở tối đa 30 ngày","best_months":["2","3","4","5"],"vibe_tags":["city","shopping","food"],"flight_time":"2h15"},
    {"destination":"Kuala Lumpur","country":"MY","iata":"KUL","est_price":2200000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN, ở tối đa 30 ngày","best_months":["3","4","5","6"],"vibe_tags":["city","food","shopping"],"flight_time":"2h"},
    {"destination":"Bali","country":"ID","iata":"DPS","est_price":4800000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN, ở tối đa 30 ngày","best_months":["5","6","7","8","9"],"vibe_tags":["beach","nature","culture"],"flight_time":"4h"},
    {"destination":"Cebu","country":"PH","iata":"CEB","est_price":4500000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN, ở tối đa 30 ngày","best_months":["3","4","5"],"vibe_tags":["beach","diving"],"flight_time":"3h30"},
    {"destination":"Siem Reap","country":"KH","iata":"REP","est_price":2800000,"visa_status":"visa_conditional","visa_note":"Cần visa on arrival, làm tại cửa khẩu (~$30 USD)","best_months":["11","12","1","2","3"],"vibe_tags":["culture","nature","history"],"flight_time":"1h30"},
    {"destination":"Tokyo","country":"JP","iata":"NRT","est_price":9500000,"visa_status":"visa_required","visa_note":"Cần xin visa Nhật tại Đại sứ quán, mất 5–7 ngày làm việc","best_months":["3","4","10","11"],"vibe_tags":["city","culture","food","nature"],"flight_time":"6h"},
    {"destination":"Seoul","country":"KR","iata":"ICN","est_price":6500000,"visa_status":"visa_free","visa_note":"Miễn visa cho hộ chiếu VN đến 15 ngày (K-ETA cần đăng ký trước)","best_months":["4","5","9","10"],"vibe_tags":["city","food","shopping","culture"],"flight_time":"5h"},
    {"destination":"Đà Nẵng","country":"VN","iata":"DAD","est_price":1200000,"visa_status":"visa_free","visa_note":"Trong nước","best_months":["3","4","5","6","7","8"],"vibe_tags":["beach","city"],"flight_time":"1h20"},
    {"destination":"Nha Trang","country":"VN","iata":"CXR","est_price":950000,"visa_status":"visa_free","visa_note":"Trong nước","best_months":["6","7","8"],"vibe_tags":["beach","diving"],"flight_time":"1h"},
    {"destination":"Phú Quốc","country":"VN","iata":"PQC","est_price":1400000,"visa_status":"visa_free","visa_note":"Trong nước","best_months":["11","12","1","2","3","4"],"vibe_tags":["beach","resort","nature"],"flight_time":"1h10"},
    {"destination":"Quy Nhơn","country":"VN","iata":"UIH","est_price":900000,"visa_status":"visa_free","visa_note":"Trong nước","best_months":["4","5","6","7"],"vibe_tags":["beach","hidden gem"],"flight_time":"1h10"},
    {"destination":"Đà Lạt","country":"VN","iata":"DLI","est_price":850000,"visa_status":"visa_free","visa_note":"Trong nước","best_months":["11","12","1","2","3"],"vibe_tags":["nature","city","honeymoon"],"flight_time":"1h"},
    {"destination":"Hà Nội","country":"VN","iata":"HAN","est_price":1100000,"visa_status":"visa_free","visa_note":"Trong nước","best_months":["10","11","12","3","4"],"vibe_tags":["city","culture","food"],"flight_time":"2h"},
    {"destination":"Jeju","country":"KR","iata":"CJU","est_price":5500000,"visa_status":"visa_free","visa_note":"Miễn visa khi bay thẳng vào đảo Jeju","best_months":["9","10","11","3","4","5"],"vibe_tags":["nature","beach","honeymoon"],"flight_time":"5h"},
]

_VIBE_MAP = {
    "beach": ["beach","diving","resort"],
    "city": ["city","shopping"],
    "nature": ["nature"],
    "food": ["food"],
    "culture": ["culture","history"],
    "honeymoon": ["honeymoon","beach","nature"],
}


def discover_destinations(
    origin: str = "SGN",
    budget_max: float | None = None,
    region: str | None = None,
    vibe: str | None = None,
    month: str | None = None,
    visa_free_only: bool = True,
) -> dict:
    results = []
    for d in _DESTINATIONS:
        if visa_free_only and d["visa_status"] == "visa_required":
            continue
        if budget_max and d["est_price"] > budget_max:
            continue
        if region == "domestic" and d["country"] != "VN":
            continue
        if region not in (None, "any", "domestic") and d["country"] == "VN":
            continue
        if vibe:
            accepted = _VIBE_MAP.get(vibe, [vibe])
            if not any(tag in d["vibe_tags"] for tag in accepted):
                continue
        results.append(d)
    results.sort(key=lambda x: x["est_price"])
    return {"destinations": results[:6]}


def price_calendar(
    origin: str = "SGN",
    destination: str = "",
    month: str | None = None,
) -> dict:
    import calendar as _cal
    dest = destination.upper()
    # Base price from mock flights or estimate
    base = 1_400_000
    for d in _DESTINATIONS:
        if d["iata"] == dest or d["destination"].upper() == dest:
            base = int(d["est_price"] * 0.9)
            break

    # Generate cheapest dates deterministically
    from datetime import date as _date, timedelta as _td
    today = _date.today()
    if month:
        try:
            y, m = map(int, month.split("-"))
            start = _date(y, m, 1)
        except Exception:
            start = today.replace(day=1)
    else:
        # find cheapest month: pick 2 months ahead
        start = (today.replace(day=1))

    cheapest_dates = []
    for offset in range(28):
        d = start + _td(days=offset)
        # Cheaper mid-week (Tue=1, Wed=2)
        dow = d.weekday()
        if dow in (1, 2):
            price = int(base * 0.85)
        elif dow in (4, 5, 6):
            price = int(base * 1.15)
        else:
            price = base
        cheapest_dates.append({"date": d.isoformat(), "price": price})

    cheapest_dates.sort(key=lambda x: x["price"])
    cheapest_month = start.strftime("%Y-%m")

    return {
        "cheapest_month": cheapest_month,
        "cheapest_dates": cheapest_dates[:5],
        "weekday_tip": "Bay T3/T4 rẻ hơn cuối tuần ~15–20%",
        "trend": "Giá tăng dần khi vào mùa cao điểm và dịp lễ",
    }


_ISLAND_ONLY = {"PQC", "PHU QUOC", "DPS", "BALI", "CEB", "CEBU", "HKT", "PHUKET"}


def compare_transport(
    origin: str = "SGN",
    destination: str = "",
    date: str = "",
) -> dict:
    dest_upper = destination.upper()
    # Islands / international → air only
    is_island_or_intl = dest_upper in _ISLAND_ONLY or dest_upper in {
        d["iata"] for d in _DESTINATIONS if d["country"] != "VN"
    }

    s = _seed(origin, destination, date, 0)
    air_price = 1_200_000 + (s % 8) * 100_000
    options = [
        {"mode": "air", "sku_id": f"MOCK-VJ-{origin}-{destination}-001",
         "price": air_price, "currency": "VND", "duration": "1h–2h", "note": "bay thẳng"}
    ]
    available_modes = ["air"]

    if not is_island_or_intl:
        train_price = 350_000 + (s % 5) * 30_000
        bus_price = 200_000 + (s % 4) * 25_000
        options += [
            {"mode": "train", "sku_id": f"MOCK-TRN-{origin}-{destination}-001",
             "price": train_price, "currency": "VND", "duration": "7–10h (tàu đêm)",
             "note": "Đi đêm, tiết kiệm 1 đêm khách sạn"},
            {"mode": "bus", "sku_id": f"MOCK-BUS-{origin}-{destination}-001",
             "price": bus_price, "currency": "VND", "duration": "6–8h",
             "note": "Giường nằm cao cấp"},
        ]
        available_modes = ["air", "train", "bus"]

    return {"available_modes": available_modes, "options": options}


def search_accommodation(
    area: str = "",
    check_in: str = "",
    check_out: str = "",
    guests: int = 2,
    budget_max: float | None = None,
    acc_type: str | None = None,
) -> dict:
    area_name = area or "điểm đến"
    templates = [
        {"name": f"Grand {area_name} Hotel", "type": "hotel", "base": 2_500_000,
         "note": "Trung tâm, view đẹp, đầy đủ tiện nghi"},
        {"name": f"Boutique {area_name} Hotel", "type": "hotel", "base": 1_400_000,
         "note": "Gần chợ đêm, phong cách địa phương"},
        {"name": f"Homestay {area_name} Xanh", "type": "homestay", "base": 750_000,
         "note": "Ấm cúng, chủ nhà thân thiện, có bếp"},
        {"name": f"Homestay View Đồi {area_name}", "type": "homestay", "base": 650_000,
         "note": "View đẹp, cách trung tâm ~2km"},
        {"name": f"Hostel {area_name} Social", "type": "hostel", "base": 450_000,
         "note": "Phòng riêng, bếp chung, nhiều khách Tây"},
    ]
    results = []
    for i, tpl in enumerate(templates):
        if acc_type and tpl["type"] != acc_type:
            continue
        s = _seed(area, check_in, "", i)
        price = tpl["base"] + (s % 6) * 50_000
        if budget_max and price > budget_max:
            continue
        results.append({
            "sku_id": f"MOCK-ACC-{area.upper()}-{i+1:02d}",
            "name": tpl["name"],
            "type": tpl["type"],
            "price_per_night": price,
            "currency": "VND",
            "area": area_name,
            "check_in": check_in,
            "check_out": check_out,
            "note": tpl["note"],
        })
    if not results:
        # Return all if nothing matches budget — so agent can apply fallback logic
        for i, tpl in enumerate(templates):
            if acc_type and tpl["type"] != acc_type:
                continue
            s = _seed(area, check_in, "", i)
            results.append({
                "sku_id": f"MOCK-ACC-{area.upper()}-{i+1:02d}",
                "name": tpl["name"],
                "type": tpl["type"],
                "price_per_night": tpl["base"] + (s % 6) * 50_000,
                "currency": "VND",
                "area": area_name,
                "check_in": check_in,
                "check_out": check_out,
                "note": tpl["note"],
            })
    return {"options": results[:5], "min_price": min(r["price_per_night"] for r in results) if results else 0}


def get_suggestions(origin: str = "") -> list[dict]:
    key = (origin or "").upper()
    return _SUGGESTIONS.get(key, _SUGGESTIONS["default"])
