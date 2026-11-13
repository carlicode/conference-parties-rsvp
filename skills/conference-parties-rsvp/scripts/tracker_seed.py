#!/usr/bin/env python3
"""Prepara la lista de fiestas que muestra assets/fiestas.html.

Uso:
    python3 tracker_seed.py events.json targets.json tracker/

Escribe en tracker/ un JSON por evento y tracker/batches.json con lotes de
hasta 50 escrituras, listos para pasarlos como `writes` a ArtifactData
(action "batch", colección "eventos"). Los eventos de targets.json quedan
"por-llenar" y el resto "descartado".

Correrlo una sola vez por conferencia: ArtifactData no sobrescribe un
documento que ya existe sin su versión, así que una segunda carga no pisa
los estados que Claude ya actualizó.
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta

BATCH = 50
WORD_TIMES = {"breakfast": 480, "morning": 540, "lunch": 720, "afternoon": 840,
              "evening": 1080, "night": 1260}


def key(e: dict) -> tuple:
    return (e["url"], e["event"], e.get("day", ""), e.get("time", ""))


def short_day(day: str) -> str:
    # "Monday November 30, 2026" -> "Mon Nov 30" (mismo formato que filter_events.py)
    parts = day.replace(",", "").split()
    return f"{parts[0][:3]} {parts[1][:3]} {parts[2]}" if len(parts) >= 3 else day


def iso_date(day: str) -> str:
    # "Monday November 30, 2026" -> "2026-11-30"
    try:
        return datetime.strptime(day.split(" ", 1)[1], "%B %d, %Y").date().isoformat()
    except (ValueError, IndexError):
        return ""


def _to_minutes(h: int, mins: int, mer: str) -> int:
    if not mer:
        return h * 60 + mins
    return (h % 12 + (12 if mer.lower().startswith("p") else 0)) * 60 + mins


def time_range(t: str) -> tuple:
    """(inicio, fin) en minutos desde la medianoche del día del evento.

    "6–9PM" -> (1080, 1260); "11–1PM" -> (660, 780); "10PM–2AM" -> (1320, 1560).
    Sin hora reconocible: (9999, 9999). Sin hora de fin: dos horas después del inicio.
    """
    times = re.findall(r"(\d{1,2})(?::(\d{2}))?\s*([AaPp]\.?[Mm])?", t)
    if not times:
        low = t.lower()
        start = next((m for w, m in WORD_TIMES.items() if w in low), 9999)
        return (start, start if start == 9999 else start + 180)
    h, mins, mer = int(times[0][0]), int(times[0][1] or 0), times[0][2]
    end = None
    if len(times) > 1:
        eh, em, emer = int(times[-1][0]), int(times[-1][1] or 0), times[-1][2]
        if not mer:  # "6–9PM": el inicio hereda el AM/PM del final
            mer = emer
            if mer.lower().startswith("p") and h != 12 and h > eh:
                mer = "am"  # "11–1PM" empieza a las 11 AM
        end = _to_minutes(eh, em, emer or mer)
    start = _to_minutes(h, mins, mer)
    if end is None:
        end = start + 120
    elif end <= start:
        end += 1440  # termina pasada la medianoche
    return (start, end)


def local_iso(date: str, minutes: int) -> str:
    """"2026-11-30", 1260 -> "2026-11-30T21:00" (hora local de la ciudad, sin zona)."""
    if not date or minutes >= 9999:
        return ""
    day = datetime.strptime(date, "%Y-%m-%d") + timedelta(minutes=minutes)
    return day.strftime("%Y-%m-%dT%H:%M")


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    events = json.load(open(sys.argv[1], encoding="utf-8"))
    targets = {key(e) for e in json.load(open(sys.argv[2], encoding="utf-8"))}
    out_dir = os.path.abspath(sys.argv[3])
    os.makedirs(out_dir, exist_ok=True)

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    writes, seen = [], set()
    for e in events:
        doc_id = hashlib.sha1("|".join(key(e)).encode()).hexdigest()[:12]
        if doc_id in seen:  # la misma fila repetida en la página
            continue
        seen.add(doc_id)
        date = iso_date(e.get("day", ""))
        start, end = time_range(e.get("time", ""))
        pending = key(e) in targets
        doc = {
            "event": e["event"], "sponsor": e.get("sponsor", ""),
            "day": short_day(e.get("day", "")), "date": date, "time": e.get("time", ""),
            "sort": f"{date or '9999-99-99'} {start:04d}",
            "starts": local_iso(date, start), "ends": local_iso(date, end),
            "location": e.get("location", ""), "url": e["url"], "platform": e.get("platform", ""),
            "status": "por-llenar" if pending else "descartado",
            "note": "" if pending else "Fuera de tus días o preferencias",
            "entry": "", "updated_at": now,
        }
        path = os.path.join(out_dir, f"{doc_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        writes.append({"op": "set", "collection": "eventos", "doc_id": doc_id, "file_path": path})

    batches = [writes[i:i + BATCH] for i in range(0, len(writes), BATCH)]
    with open(os.path.join(out_dir, "batches.json"), "w", encoding="utf-8") as f:
        json.dump(batches, f, ensure_ascii=False, indent=1)
    pending = sum(1 for w in writes if json.load(open(w["file_path"], encoding="utf-8"))["status"] == "por-llenar")
    print(f"Lista: {len(writes)} eventos ({pending} por llenar, {len(writes) - pending} descartados)")
    print(f"Lotes para ArtifactData: {len(batches)} en {os.path.join(out_dir, 'batches.json')}")


if __name__ == "__main__":
    main()
