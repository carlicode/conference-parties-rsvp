#!/usr/bin/env python3
"""Lee las preguntas de registro de los eventos de Luma (API pública, sin login).

Uso:
    python3 luma_questions.py events.json luma.json

Para cada link de luma.com guarda: nombre, si pide aprobación, si está lleno,
lista de espera, precio, si pide teléfono y las preguntas personalizadas.
Imprime las preguntas más repetidas: sirven para decidir qué pedir en la página de datos.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter


def fetch(slug: str) -> dict:
    url = "https://api.lu.ma/url?url=" + urllib.parse.quote(slug)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=20))["data"]


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    events = json.load(open(sys.argv[1], encoding="utf-8"))
    urls = sorted({e["url"] for e in events if e.get("platform") == "luma"})
    out, counter = {}, Counter()
    for url in urls:
        slug = urllib.parse.urlparse(url).path.strip("/")
        try:
            d = fetch(slug)
        except Exception as exc:  # links de usuario/calendario o redirecciones
            out[url] = {"error": str(exc)}
            continue
        questions = [{k: q.get(k) for k in ("label", "required", "question_type", "options")}
                     for q in d.get("registration_questions") or []]
        for q in questions:
            counter[(q["question_type"], (q["label"] or "")[:70])] += 1
        out[url] = {
            "name": (d.get("event") or {}).get("name"),
            "sold_out": d.get("sold_out"),
            "waitlist": d.get("waitlist_active"),
            "phone": d.get("phone_number_requirement"),
            "paid": any((t.get("cents") or 0) > 0 for t in d.get("ticket_types") or []),
            "questions": questions,
        }
        time.sleep(0.3)
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(1 for v in out.values() if "error" not in v)
    print(f"Luma: {ok}/{len(urls)} leídos")
    print("Llenos:", [v["name"] for v in out.values() if v.get("sold_out")])
    print("Pagados:", [v["name"] for v in out.values() if v.get("paid")])
    print("Preguntas más comunes:")
    for (qtype, label), n in counter.most_common(25):
        print(f"  {n:>3}  [{qtype}] {label}")


if __name__ == "__main__":
    main()
