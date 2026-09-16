#!/usr/bin/env python3
"""
Chequea las paginas de referencia de vencimientos (estudiodelamo.com) y, si
detecta que alguna se modifico desde la ultima verificacion (via su fecha de
"modified" en el HTML) o que ya circula la tabla del anio siguiente, deja un
aviso en data.json para que se revise y cargue a mano. No reescribe las
tablas de fechas solo: son demasiados numeros como para confiar eso a un
scraper sin supervision.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import requests

FUENTES = {
    "monotributo": "https://estudiodelamo.com/vencimiento-monotributo-recategorizacion/",
    "autonomos": "https://estudiodelamo.com/vencimientos-autonomos/",
    "iva": "https://estudiodelamo.com/vencimientos-iva/",
    "ganancias_bienes_personales": "https://estudiodelamo.com/vencimientos-impuesto-ganancias-personas-fisicas-bienes-personales-anticipos/",
    "sicore": "https://estudiodelamo.com/vencimientos-retenciones-sicore/",
}

DATA_PATH = Path(__file__).resolve().parent.parent / "vencimientos" / "data.json"


def obtener_modified(url):
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (RindexBot)"})
    r.raise_for_status()
    m = re.search(r'article:modified_time"\s+content="([^"]+)"', r.text)
    if not m:
        m = re.search(r'article:modified_time[^\d]+(\d{4}-\d{2}-\d{2})', r.text)
    fecha_mod = m.group(1)[:10] if m else None

    # Señal extra: ¿ya aparece el año siguiente en el texto de la tabla?
    anio_actual = date.today().year
    tiene_anio_siguiente = str(anio_actual + 1) in r.text

    return fecha_mod, tiene_anio_siguiente


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    meta = data.setdefault("_meta", {})
    modified_conocidos = meta.setdefault("modified_conocidos", {})

    cambios = []
    for nombre, url in FUENTES.items():
        try:
            fecha_mod, tiene_anio_siguiente = obtener_modified(url)
        except Exception as e:
            print(f"[{nombre}] no se pudo chequear ({e}), se omite esta vez.")
            continue

        anterior = modified_conocidos.get(nombre)
        if fecha_mod and fecha_mod != anterior:
            cambios.append({
                "pagina": nombre,
                "url": url,
                "modified_anterior": anterior,
                "modified_nuevo": fecha_mod,
                "tiene_anio_siguiente": tiene_anio_siguiente,
            })
            modified_conocidos[nombre] = fecha_mod
        elif tiene_anio_siguiente and not meta.get("aviso_anio_siguiente"):
            cambios.append({
                "pagina": nombre,
                "url": url,
                "modified_anterior": anterior,
                "modified_nuevo": fecha_mod,
                "tiene_anio_siguiente": True,
            })

    if not cambios:
        print("Sin cambios detectados en ninguna fuente.")
        meta["ultimo_chequeo_automatico"] = date.today().isoformat()
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sys.exit(0)

    print(f"Se detectaron {len(cambios)} cambio(s) en las fuentes:")
    for c in cambios:
        print(f"  - {c['pagina']}: modified {c['modified_anterior']} -> {c['modified_nuevo']}"
              f"{' (¡aparece el año siguiente!)' if c['tiene_anio_siguiente'] else ''}")

    meta["pendiente_revision"] = {
        "detectado": date.today().isoformat(),
        "cambios": cambios,
        "nota": "Una o más páginas de referencia cambiaron. Revisar y cargar las fechas nuevas a mano en data.json.",
    }
    meta["ultimo_chequeo_automatico"] = date.today().isoformat()
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("data.json actualizado con el aviso de 'pendiente_revision'.")


if __name__ == "__main__":
    main()
