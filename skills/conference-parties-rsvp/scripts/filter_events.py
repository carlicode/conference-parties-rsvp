#!/usr/bin/env python3
"""Filtra los eventos según las preferencias de la persona.

Uso:
    python3 filter_events.py events.json perfil.json targets.json [luma.json]

Lee de perfil.json: days (lista de días, ej. ["Mon Nov 30"]), include_exec,
include_paid. Quita eventos solo para ejecutivos/CTO/CISO si include_exec es false,
eventos pagados si include_paid es false (requiere luma.json) y los que piden
estar registrado en la conferencia oficial si reinvent_registered es "No".
"""
import json
import re
import sys

EXEC = re.compile(r"executive|\bexecs?\b|\bctos?\b|\bcisos?\b|\bcfos?\b|leaders (dinner|lunch|meet)|"
                  r"security leaders|mastermind|partners only|roundtable|private (dinner|lunch)|"
                  r"industry leaders|vip evening", re.I)


def short_day(day: str) -> str:
    # "Monday November 30, 2026" -> "Mon Nov 30"
    parts = day.replace(",", "").split()
    return f"{parts[0][:3]} {parts[1][:3]} {parts[2]}" if len(parts) >= 3 else day


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    events = json.load(open(sys.argv[1], encoding="utf-8"))
    prefs = json.load(open(sys.argv[2], encoding="utf-8"))
    luma = json.load(open(sys.argv[4], encoding="utf-8")) if len(sys.argv) > 4 else {}
    days = set(prefs.get("days") or [])
    keep, dropped = [], []
    for e in events:
        why = None
        if days and e["day"] and short_day(e["day"]) not in days:
            why = "día fuera de su viaje"
        elif not prefs.get("include_exec") and EXEC.search(e["event"]):
            why = "solo ejecutivos"
        elif not prefs.get("include_paid") and luma.get(e["url"], {}).get("paid"):
            why = "pagado"
        elif e["platform"] == "conference-portal" and str(prefs.get("conference_registered", "")).lower().startswith("no"):
            why = "requiere registro oficial en la conferencia"
        (dropped if why else keep).append({**e, "skip_reason": why} if why else e)
    json.dump(keep, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"A registrar: {len(keep)} eventos ({len({e['url'] for e in keep})} links únicos)")
    print(f"Descartados: {len(dropped)}")
    for e in dropped:
        print(f"  - {e['skip_reason']}: {e['event'][:70]}")


if __name__ == "__main__":
    main()
