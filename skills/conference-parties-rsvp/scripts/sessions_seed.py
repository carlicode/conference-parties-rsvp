#!/usr/bin/env python3
"""Suma a la lista de fiestas las sesiones de la comunidad de una conferencia.

Uso:
    python3 sessions_seed.py references/sesiones/reinvent2026.json perfil.json tracker/

Escribe en tracker/ un JSON por cada horario de cada sesión y
tracker/batches_sesiones.json con los lotes para ArtifactData (action "batch",
colección "eventos"). Todos los horarios que caen en los días de la persona,
repeticiones incluidas, quedan "por-reservar" como referencia: la persona no
tiene que elegir uno. Los que caen fuera de sus días quedan "descartado".
Cada horario lleva en la nota el código para buscarlo, sus repeticiones y el
aviso de llegar con tiempo para el acceso walk-in (`walk_in_note` del archivo).

Las sesiones se reservan en el catálogo oficial, no con un formulario: Claude
no las llena en el Paso 6.
"""
import json
import os
import sys
from datetime import datetime, timedelta

BATCH = 50


def short_day(dt: datetime) -> str:
    # Mismo formato que filter_events.py y tracker_seed.py: "Mon Nov 30"
    return f"{dt:%a} {dt:%b} {dt.day}"


def human_time(dt: datetime) -> str:
    # 13:30 -> "1:30PM", 9:00 -> "9AM"
    h = dt.hour % 12 or 12
    mins = f":{dt.minute:02d}" if dt.minute else ""
    return f"{h}{mins}{'AM' if dt.hour < 12 else 'PM'}"


def human_date(dt: datetime) -> str:
    months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{dt.day} {months[dt.month - 1]}, {human_time(dt)}"


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    prefs = json.load(open(sys.argv[2], encoding="utf-8"))
    out_dir = os.path.abspath(sys.argv[3])
    os.makedirs(out_dir, exist_ok=True)
    days = set(prefs.get("days") or [])
    durations = data.get("duration_minutes", {})
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    walk_in = data.get("walk_in_note", "")
    writes, active, outside = [], 0, []
    for s in data["sessions"]:
        slots = sorted(s["occurrences"], key=lambda o: o["starts"])
        starts = [datetime.strptime(o["starts"], "%Y-%m-%dT%H:%M") for o in slots]
        minutes = durations.get(s["format"], 60)
        base = s.get("code") or s["id"]  # los meetups no tienen código de catálogo
        codes = [o.get("code", base) for o in slots]  # COM312-R, COM312-R1...
        for i, (o, dt) in enumerate(zip(slots, starts)):
            others = [f"{codes[j]} el {human_date(d)}" for j, d in enumerate(starts) if j != i]
            in_days = not days or short_day(dt) in days
            status = "por-reservar" if in_days else "descartado"
            note = " ".join(x for x in [
                "" if in_days else "Fuera de tus días.",
                s.get("where_note") or f"Búscala en el catálogo con el código {codes[i]}.",
                f"Se repite: {', '.join(others)}." if others else "",
                walk_in,
            ] if x)
            active += in_days
            end = (datetime.strptime(o["ends"], "%Y-%m-%dT%H:%M") if o.get("ends")
                   else dt + timedelta(minutes=minutes))
            doc_id = f"ses-{codes[i].lower()}"
            doc = {
                "kind": "sesion", "code": codes[i], "track": s.get("track", ""),
                "event": f"{s['code']} · {s['title']}" if s.get("code") else s["title"],
                "sponsor": f"{s['format'].capitalize()} · {s['speakers']}",
                "summary": s.get("summary", ""),
                "day": short_day(dt), "date": dt.strftime("%Y-%m-%d"),
                "time": f"{human_time(dt)}–{human_time(end)}",
                "sort": f"{dt:%Y-%m-%d} {dt.hour * 60 + dt.minute:04d}",
                "starts": dt.strftime("%Y-%m-%dT%H:%M"), "ends": end.strftime("%Y-%m-%dT%H:%M"),
                "location": o["location"], "url": s.get("url", ""), "platform": "sesion",
                "status": status,
                "note": note,
                "entry": "", "updated_at": now,
            }
            path = os.path.join(out_dir, f"{doc_id}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
            writes.append({"op": "set", "collection": "eventos", "doc_id": doc_id, "file_path": path})
        if not any(not days or short_day(dt) in days for dt in starts):
            outside.append(s["code"])

    batches = [writes[i:i + BATCH] for i in range(0, len(writes), BATCH)]
    with open(os.path.join(out_dir, "batches_sesiones.json"), "w", encoding="utf-8") as f:
        json.dump(batches, f, ensure_ascii=False, indent=1)
    print(f"Sesiones: {len(data['sessions'])} | horarios: {len(writes)} ({active} en tus días, repeticiones incluidas)")
    if outside:
        print("Fuera de tus días:", ", ".join(outside))
    print(f"Lotes para ArtifactData: {len(batches)} en {os.path.join(out_dir, 'batches_sesiones.json')}")


if __name__ == "__main__":
    main()
