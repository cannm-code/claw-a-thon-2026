"""Airport lookup: resolve user input (code, city name, alias) → IATA code + info."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

_RAW: list[dict] = json.loads(
    (Path(__file__).parent / "data" / "airports.json").read_text(encoding="utf-8")
)

# index by IATA code (upper)
_BY_IATA: dict[str, dict] = {a["iata"].upper(): a for a in _RAW}

# index by normalised alias → iata
_BY_ALIAS: dict[str, str] = {}

def _norm(s: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()

for airport in _RAW:
    iata = airport["iata"].upper()
    # IATA code itself
    _BY_ALIAS[iata.lower()] = iata
    # city name
    _BY_ALIAS[_norm(airport["city"])] = iata
    # airport name (full and abbreviated — first 3 significant words)
    _BY_ALIAS[_norm(airport["name"])] = iata
    # declared aliases
    for alias in airport.get("aliases", []):
        _BY_ALIAS[_norm(alias)] = iata


def lookup(query: str) -> dict | None:
    """
    Return airport dict (iata, name, city, country) for query, or None.
    Accepts IATA codes, city names, airport names, and declared aliases.
    """
    if not query:
        return None
    key = _norm(query)
    iata = _BY_ALIAS.get(key)
    if iata:
        return _BY_IATA[iata]
    # Try substring: if query fully contained in any alias key
    for alias, iata_code in _BY_ALIAS.items():
        if key in alias or alias in key:
            return _BY_IATA[iata_code]
    return None


def resolve_iata(query: str) -> str:
    """Return IATA code for query, or the original query uppercased if not found."""
    result = lookup(query)
    if result:
        return result["iata"]
    return query.strip().upper()


def search_airports(query: str, limit: int = 5) -> list[dict]:
    """
    Full-text search across code, city, name, and aliases.
    Returns up to `limit` matching airport dicts.
    """
    key = _norm(query)
    seen: set[str] = set()
    results: list[dict] = []

    # Exact or prefix match on IATA code first
    q_upper = query.strip().upper()
    if q_upper in _BY_IATA and q_upper not in seen:
        seen.add(q_upper)
        results.append(_BY_IATA[q_upper])

    # Alias index matches
    for alias, iata_code in _BY_ALIAS.items():
        if iata_code in seen:
            continue
        if key in alias or alias.startswith(key):
            seen.add(iata_code)
            results.append(_BY_IATA[iata_code])
            if len(results) >= limit:
                break

    return results[:limit]
