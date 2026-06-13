# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Claw-a-thon 2026** — an AI-powered travel booking assistant mini-app. The app guides users through searching, comparing, and selecting travel products (flights, hotels, bus, train), then hands off to checkout.

The core AI behavior is defined in [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md), which serves as the LLM system prompt template. It uses placeholder variables (`{{BrandName}}`, `{{AgentName}}`, `{{verticals}}`) intended to be filled at deploy time.

## System Prompt Design

The agent follows a strict 5-stage conversation flow:

1. **Entry / Intent** — identify vertical and goal
2. **Guided Input** — collect required slots (origin, destination, dates, pax) with at most 2 questions per turn
3. **Search** — call `search_inventory()` only after all required slots are filled
4. **Results** — present 3–5 ranked options as structured JSON
5. **Selection & Handoff** — call `get_sku_detail()`, get explicit confirmation, then emit handoff JSON

## Tool Interface Contract

The three tools the AI must call (never fabricate their results):

```
search_inventory(vertical, origin, destination, date, pax, max_price?, filters?)
  → { sku_id, title, price, currency, time/route, key_attributes, availability_status }[]

get_sku_detail(sku_id)
  → full fare rules, baggage, cancellation, inclusions

knowledge_base(query)
  → policy/FAQ passages (RAG)
```

## Structured Output Shapes

When the agent produces results or a checkout handoff, it must emit a fenced `json` block. The two schemas (from SYSTEM_PROMPT.md):

- **Results** (`"type": "results"`): `message`, `options[]` with `sku_id`, `title`, `price`, `currency`, `subtitle`, `highlights[]`
- **Handoff** (`"type": "handoff"`): `sku_id`, `summary`, `total_price`, `currency`

The app renders these as cards/checkout trigger — always valid JSON, no trailing commas, double quotes only.

## Language

Default language is **Vietnamese**. The agent mirrors the user's language if they switch. English is used only for proper nouns, codes, and technical fields.

## Hard Constraints

- Never invent prices, availability, or schedules — all product facts must come from tool calls
- Never emit a handoff JSON without explicit user confirmation
- Never collect payment card details
- If a tool fails or returns empty, tell the user and offer alternatives — never fabricate
