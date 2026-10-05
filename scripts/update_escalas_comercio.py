#!/usr/bin/env python3
"""
Busca en ignacioonline.com.ar las planillas oficiales de escalas de Empleados de
Comercio (PDF firmados de FAECYS) y, si aparece un PDF nuevo, extrae los básicos
de cada categoría y mes y actualiza assets/escalas-comercio.json.

Criterio de seguridad (igual que monotributo): si el PDF no se puede leer con
confianza (faltan categorías, montos fuera de rango), NO toca los básicos y deja
un aviso en "pendiente_actualizacion" para revisión manual.
"""
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

import requests

DATA_PATH = Path(__file__).resolve().parent.parent / "assets" / "escalas-comercio.json"
PAGINAS = [
    "https://www.ignacioonline.com.ar/category/empleados-de-comercio/feed/",
    "https://www.ignacioonline.com.ar/empleados-de-comercio-escala-salarial-2026-oficial/",
    "https://www.ignacioonline.com.ar/calculadora-empleados-de-comercio/",
]
UA = {"User-Agent": "Mozilla/5.0 (RindexBot)"}
MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
         "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
# Nombre en el PDF -> nombre en la herramienta
GRUPOS = {
    "administrativo": "Administrativo",
    "auxiliar especializado": "Auxiliar Especializado",
    "cajeros": "Cajero",
    "maestranza": "Maestranza y Servicios",
    "personal auxiliar": "Personal Auxiliar",
    "vendedores": "Vendedor",
}


def n(s):
    return int(s.replace(".", ""))


def buscar_pdfs():
    urls = set()
    for p in PAGINAS:
        try:
            html = requests.get(p, timeout=30, headers=UA).text
        except Exception as e:
            print(f"No se pudo leer {p}: {e}")
            continue
        for u in re.findall(r"https?://[^\"'\s<>]+?\.pdf", html, re.IGNORECASE):
            low = u.lower()
            if "comercio" in low and ("planilla" in low or "escala" in low):
                urls.add(u)
    return sorted(urls)


def texto_pdf(url):
    from pypdf import PdfReader
    r = requests.get(url, timeout=60, headers=UA)
    r.raise_for_status()
    reader = PdfReader(io.BytesIO(r.content))
    return " ".join((pg.extract_text() or "") for pg in reader.pages)


def parsear(texto):
    """Devuelve {"AAAA-MM": {"nr":..., "ext":..., "basicos": {cat: basico}}}."""
    t = re.sub(r"\s+", " ", texto)
    grupos_re = "|".join(GRUPOS)
    cab = re.compile(
        r"Remuneraciones para Empleados de Comercio\s+(" + grupos_re + r")\s+([A-F])\s+(" +
        "|".join(MESES) + r") de (\d{4})", re.IGNORECASE)
    marcas = list(cab.finditer(t))
    out = {}
    for i, m in enumerate(marcas):
        bloque = t[m.end(): marcas[i + 1].start() if i + 1 < len(marcas) else len(t)]
        grupo, letra, mes, anio = m.group(1).lower(), m.group(2).upper(), m.group(3).lower(), m.group(4)
        cat = f"{GRUPOS[grupo]} {letra}"
        clave = f"{anio}-{MESES[mes]:02d}"
        mi = re.search(r"Inicial\s+([\d\.]+)", bloque)
        if not mi:
            continue
        bas_s = mi.group(1)
        # Fila de 1 año: básico, antigüedad, [sumas NR y asignaciones], antig. s/ NR, total
        m1 = re.search(r"\b1\s+" + re.escape(bas_s) + r"\s+((?:[\d\.]+\s+)+?)2\s+" + re.escape(bas_s), bloque)
        if not m1:
            continue
        nums = [n(x) for x in m1.group(1).split()]
        if len(nums) < 3:
            continue
        items, antig_nr = nums[1:-2], nums[-2]
        nr = round(antig_nr * 100 / 1000) * 1000  # 1% de las sumas NR, redondeado a miles
        ext = sum(items) - nr
        if ext < 0:
            ext = 0
        per = out.setdefault(clave, {"nr": nr, "ext": ext, "basicos": {}})
        per["basicos"][cat] = n(bas_s)
    return out


def coherente(nuevos, data):
    cats = set(data["categorias"])
    ultimo = max((k for k, v in data["periodos"].items() if v["estado"] == "oficial"), default=None)
    ref = data["periodos"][ultimo]["basicos"] if ultimo else None
    for k, per in nuevos.items():
        if set(per["basicos"]) != cats:
            faltan = cats - set(per["basicos"])
            return False, f"{k}: faltan categorías {sorted(faltan)}"
        if ref:
            for c, v in per["basicos"].items():
                if not (0.7 * ref[c] <= v <= 1.8 * ref[c]):
                    return False, f"{k}: {c} = {v} fuera de rango respecto de {ref[c]}"
    return True, ""


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    pdfs = [u for u in buscar_pdfs() if u not in data["pdfs_procesados"]]
    if not pdfs:
        print("Sin planillas nuevas.")
        return
    cambios = False
    for url in pdfs:
        print("Planilla nueva:", url)
        try:
            nuevos = parsear(texto_pdf(url))
        except Exception as e:
            print("No se pudo leer el PDF:", e)
            nuevos = {}
        ok, motivo = coherente(nuevos, data) if nuevos else (False, "no se encontraron tablas de categorías")
        if not ok:
            data["pendiente_actualizacion"] = {
                "detectado": date.today().isoformat(), "pdf": url,
                "nota": f"Hay una planilla nueva pero no se pudo cargar sola ({motivo}). Revisar a mano."}
            cambios = True
            print("No coherente:", motivo)
            continue
        for k, per in nuevos.items():
            data["periodos"][k] = {"estado": "oficial", "nr": per["nr"], "ext": per["ext"],
                                   "basicos": per["basicos"], "nota": "Planilla oficial FAECYS: " + url}
        # Los meses proyectados posteriores dejan de ser confiables: se marcan para revisar
        ultimo = max(nuevos)
        for k, v in data["periodos"].items():
            if k > ultimo and v["estado"] == "proyeccion":
                v["nota"] = "Proyección anterior a la última planilla publicada: verificar."
        data["pdfs_procesados"].append(url)
        data["pendiente_actualizacion"] = None
        cambios = True
        print("Cargados:", ", ".join(sorted(nuevos)))
    if cambios:
        data["actualizado"] = date.today().isoformat()
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error inesperado:", e)
        sys.exit(0)
