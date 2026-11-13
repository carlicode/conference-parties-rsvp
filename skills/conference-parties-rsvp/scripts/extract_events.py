#!/usr/bin/env python3
"""Extrae todos los eventos de una página de conferenceparties.com.

Uso:
    python3 extract_events.py https://conferenceparties.com/reinvent2026/ events.json

Escribe una lista JSON con: day, time, sponsor, event, location, url, platform.
Imprime un resumen (cantidad de eventos, links únicos, plataformas).
"""
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter

DAY_RE = re.compile(r"(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\s*[-–]\s*([A-Za-z]+ \d{1,2}, \d{4})")


def text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def platform(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    for key, name in [("luma.com", "luma"), ("lu.ma", "luma"), ("cvent", "cvent"),
                      ("eventbrite", "eventbrite"), ("meetup.com", "meetup"),
                      ("hubs.l", "hubspot"), ("swoogo", "swoogo"), ("goldcast", "goldcast"),
                      ("docs.google.com/forms", "google-forms"), ("forms.cloud.microsoft", "ms-forms"),
                      ("reinvent-planner", "conference-portal")]:
        if key in host or key in url:
            return name
    return "web"


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    url, out = sys.argv[1], sys.argv[2]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

    # Cortamos la página en bloques por día usando los encabezados "Monday - November 30, 2026".
    marks = [(m.start(), f"{m.group(1)} {m.group(2)}") for m in DAY_RE.finditer(page)]
    events = []
    for row in re.finditer(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row.group(1), re.S)
        if len(cells) < 3:
            continue
        links = [l for l in re.findall(r'href="([^"]+)"', cells[2]) if "conferenceparties.com" not in l]
        if not links:
            continue  # fiestas oficiales sin link de registro
        day = ""
        for pos, label in marks:
            if pos < row.start():
                day = label
        link = html.unescape(links[0]).replace("hhttps", "https").split("#")[0]
        events.append({
            "day": day,
            "time": text(cells[0]),
            "sponsor": text(cells[1]),
            "event": re.sub(r"\s*-?\s*Request an Invite\s*-?\s*", " ", text(cells[2])).strip(),
            "location": text(cells[3]) if len(cells) > 3 else "",
            "url": link,
            "platform": platform(link),
        })

    with open(out, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=1)

    unique = {e["url"] for e in events}
    days = list(dict.fromkeys(e["day"] for e in events if e["day"]))
    print(f"Eventos con link: {len(events)} | links únicos: {len(unique)}")
    print("Días:", ", ".join(days))
    print("Plataformas:", dict(Counter(e["platform"] for e in {e['url']: e for e in events}.values())))


if __name__ == "__main__":
    main()
