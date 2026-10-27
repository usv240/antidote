"""Telegram front door: send a photo of the bottle (or type the product name), get the bedside card back in the chat.

The handler is a pure function over a Telegram update so it can be tested without the network. The webhook route in
main.py verifies Telegram's secret header, then calls handle_update with real I/O.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

MAX_SENTENCES = 4


def format_card(res: Any, npic: str) -> str:
    """Plain text, stop cards first. Clinical sentences are the guideline's own words with their page."""
    lines: list[str] = ["Decision support for trained clinicians. Airway, breathing, circulation first.", ""]
    chosen = res.chosen
    if chosen:
        who = f", WHO class {chosen.who_class}" if chosen.who_class else ""
        lines.append(f"{chosen.active_ingredient} ({res.group['name'] if res.group else chosen.group}{who})")
    else:
        lines.append("Product not identified.")
    for s in res.stops:
        lines += ["", f"STOP: {s['message']}"]
    card = res.card
    if card and not res.guarded:
        for title, sec in (("What to expect", card.expect), ("Management", card.manage), ("Cautions", card.cautions)):
            quotes = [s for s in sec if s.kind == "quote" and s.cite][:MAX_SENTENCES]
            if quotes:
                lines += ["", title + ":"]
                lines += [f'- "{s.text}" ({s.cite.doc}, page {s.cite.page})' for s in quotes]
    lines += ["", f"Poison centre: {npic}"]
    return "\n".join(lines)


def handle_update(
    update: dict[str, Any],
    *,
    analyze: Callable[[dict[str, Any]], Any],
    read_photo: Callable[[str], dict[str, Any]],
    send: Callable[[int, str], None],
    npic: str,
) -> str:
    """Returns what it did, for logs and tests."""
    msg = update.get("message") or update.get("edited_message") or {}
    chat = (msg.get("chat") or {}).get("id")
    if chat is None:
        return "ignored: no chat"
    text = (msg.get("text") or msg.get("caption") or "").strip()
    if text.startswith(("/start", "/help")):
        send(chat, "Send a clear photo of the pesticide label, or type the product name or chemical printed on it. "
                   "You will get the chemical, its hazard class and guidance quoted from the national poison-management module, "
                   "or a stop card when there is no antidote. Decision support for trained clinicians.")
        return "help"
    if msg.get("photo"):
        file_id = msg["photo"][-1]["file_id"]  # largest size
        send(chat, "Reading the label...")
        fields = read_photo(file_id)
        if not fields:
            send(chat, "I could not read that label. Try a closer, flatter photo of the front, or type the chemical name.")
            return "photo unreadable"
        if text:
            fields.setdefault("visible_text", []).append(text)
        res = analyze(fields)
        send(chat, format_card(res, npic))
        return "photo card"
    if text:
        res = analyze({"product_name": text, "active_ingredients": [{"name": text}], "visible_text": [text]})
        send(chat, format_card(res, npic))
        return "text card"
    return "ignored: no content"
