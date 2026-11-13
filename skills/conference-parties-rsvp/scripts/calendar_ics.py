#!/usr/bin/env python3
"""Arma un archivo .ics con las fiestas de la lista, para importarlo en cualquier calendario.

Uso:
    python3 calendar_ics.py <carpeta> <zona-horaria> fiestas.ics [--pendientes]

<carpeta> tiene un JSON por evento: la que deja `ArtifactData` (action "list",
colección "eventos", con out_dir) o la de tracker_seed.py. <zona-horaria> es la
de la ciudad de la conferencia, ej. America/Los_Angeles para Las Vegas.

Incluye los eventos "enviado" y "aprobado" y las sesiones "reservado". Con
--pendientes suma también "por-aprobar", "lista-espera" y las sesiones
"por-reservar" como tentativos, con "Pendiente:" en el título.
Cada evento lleva un UID fijo: al reimportar, los calendarios que lo respetan
(Apple, Outlook) actualizan en vez de duplicar.
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

CONFIRMED = {"enviado", "aprobado", "reservado"}
TENTATIVE = {"por-aprobar", "lista-espera", "por-reservar"}


def esc(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def fold(line: str) -> str:
    # RFC 5545: líneas de máximo 75 bytes; las siguientes empiezan con un espacio.
    out, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > (75 if not out else 74):
            out.append(cur.decode("utf-8"))
            cur = b""
        cur += b
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out)


def utc(local: str, tz: ZoneInfo) -> str:
    dt = datetime.strptime(local, "%Y-%m-%dT%H:%M").replace(tzinfo=tz)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        sys.exit(__doc__)
    folder, tz, out = args[0], ZoneInfo(args[1]), args[2]
    statuses = CONFIRMED | (TENTATIVE if "--pendientes" in sys.argv else set())

    docs = []
    for path in glob.glob(os.path.join(folder, "**", "*.json"), recursive=True):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or "event" not in d:
            continue  # batches.json u otros archivos
        d.setdefault("id", os.path.splitext(os.path.basename(path))[0])
        docs.append(d)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//conference-parties-rsvp//ES",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    added, no_time = 0, []
    for d in sorted(docs, key=lambda d: d.get("sort", "")):
        if d.get("status") not in statuses:
            continue
        if not d.get("starts") or not d.get("ends"):
            no_time.append(d["event"])
            continue
        tentative = d["status"] in TENTATIVE
        title = ("Pendiente: " if tentative else "") + d["event"]
        desc = "\n".join(x for x in [
            d.get("sponsor") and (d["sponsor"] if d.get("kind") == "sesion" else f"Organiza: {d['sponsor']}"),
            d.get("summary"),
            d.get("entry") and f"Entrada: {d['entry']}",
            d.get("note"),
            d.get("url"),
        ] if x)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{d['id']}@conference-parties-rsvp",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{utc(d['starts'], tz)}",
            f"DTEND:{utc(d['ends'], tz)}",
            f"SUMMARY:{esc(title)}",
            f"LOCATION:{esc(d.get('location', ''))}",
            f"DESCRIPTION:{esc(desc)}",
            f"STATUS:{'TENTATIVE' if tentative else 'CONFIRMED'}",
            f"TRANSP:{'TRANSPARENT' if tentative else 'OPAQUE'}",
        ]
        if d.get("url", "").startswith("http"):
            lines.append(f"URL:{d['url']}")
        lines.append("END:VEVENT")
        added += 1
    lines.append("END:VCALENDAR")

    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(fold(l) for l in lines) + "\r\n")
    print(f"Calendario: {added} eventos en {out}")
    if no_time:
        print(f"Sin hora reconocible ({len(no_time)}), agrégalos a mano:")
        for name in no_time:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
