#!/usr/bin/env python3
"""Suma a la lista de fiestas las sesiones de la comunidad de una conferencia.

Uso:
    python3 sessions_seed.py references/sesiones/reinvent2026.json perfil.json tracker/

Escribe en tracker/ un JSON por cada horario de cada sesión y
tracker/batches_sesiones.json con los lotes para ArtifactData (action "batch",
colección "eventos"). De cada sesión, el primer horario que cae en los días de
la persona queda "por-reservar". Las repeticiones y los horarios fuera de sus
días quedan "descartado", con una nota para cambiarlos si le cuadran mejor.

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

    writes, booked, outside = [], 0, []
    for s in data["sessions"]:
        slots = sorted(s["occurrences"], key=lambda o: o["starts"])
        starts = [datetime.strptime(o["starts"], "%Y-%m-%dT%H:%M") for o in slots]
        chosen = next((i for i, dt in enumerate(starts) if not days or short_day(dt) in days), None)
        minutes = durations.get(s["format"], 60)
        codes = [o.get("code", s["code"]) for o in slots]  # COM312-R, COM312-R1...
        for i, (o, dt) in enumerate(zip(slots, starts)):
            others = [f"{codes[j]} el {human_date(d)}" for j, d in enumerate(starts) if j != i]
            if i == chosen:
                status = "por-reservar"
                note = f"Se repite: {', '.join(others)}." if others else ""
            elif chosen is not None:
                status = "descartado"
                note = f"Repetición: elegimos {codes[chosen]} el {human_date(starts[chosen])}. Si esta te cuadra mejor, cambia los dos estados."
            else:
                status = "descartado"
                note = "Fuera de tus días."
            end = dt + timedelta(minutes=minutes)
            doc_id = f"ses-{codes[i].lower()}"
            doc = {
                "kind": "sesion", "code": codes[i], "track": s.get("track", ""),
                "event": f"{s['code']} · {s['title']}",
                "sponsor": f"{s['format'].capitalize()} · {s['speakers']}",
                "summary": s.get("summary", ""),
                "day": short_day(dt), "date": dt.strftime("%Y-%m-%d"),
                "time": f"{human_time(dt)}–{human_time(end)}",
                "sort": f"{dt:%Y-%m-%d} {dt.hour * 60 + dt.minute:04d}",
                "starts": dt.strftime("%Y-%m-%dT%H:%M"), "ends": end.strftime("%Y-%m-%dT%H:%M"),
                "location": o["location"], "url": s.get("url", ""), "platform": "sesion",
                "status": status,
                "note": " ".join(x for x in [note, f"Búscala en el catálogo con el código {codes[i]}."] if x),
                "entry": "", "updated_at": now,
            }
            path = os.path.join(out_dir, f"{doc_id}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
            writes.append({"op": "set", "collection": "eventos", "doc_id": doc_id, "file_path": path})
        if chosen is None:
            outside.append(s["code"])
        else:
            booked += 1

    batches = [writes[i:i + BATCH] for i in range(0, len(writes), BATCH)]
    with open(os.path.join(out_dir, "batches_sesiones.json"), "w", encoding="utf-8") as f:
        json.dump(batches, f, ensure_ascii=False, indent=1)
    print(f"Sesiones: {len(data['sessions'])} ({booked} por reservar, {len(writes)} horarios en total)")
    if outside:
        print("Fuera de tus días:", ", ".join(outside))
    print(f"Lotes para ArtifactData: {len(batches)} en {os.path.join(out_dir, 'batches_sesiones.json')}")


if __name__ == "__main__":
    main()
