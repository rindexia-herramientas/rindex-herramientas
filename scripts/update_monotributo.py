#!/usr/bin/env python3
"""
Chequea la tabla oficial de categorias de Monotributo en la pagina de ARCA
y, si encuentra una tabla nueva y coherente (11 categorias, montos crecientes),
actualiza monotributo/data.json. Si no logra parsear con confianza, no toca
el archivo (mejor no actualizar que actualizar mal).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import requests

FUENTE_URL = "https://www.afip.gob.ar/monotributo/categorias.asp"
DATA_PATH = Path(__file__).resolve().parent.parent / "monotributo" / "data.json"
LETRAS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]


def obtener_html():
    r = requests.get(FUENTE_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0 (RindexBot)"})
    r.raise_for_status()
    return r.text


def parsear_montos(html):
    """
    Busca, para cada categoria A-K en orden, los montos en pesos que aparecen
    en su fila (tope de facturacion, cuota, etc). Devuelve None si no encuentra
    un patron limpio con las 11 categorias en orden creciente.
    """
    texto = re.sub(r"<[^>]+>", " ", html)
    texto = re.sub(r"&nbsp;|&#160;", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    filas = []
    for letra in LETRAS:
        # Busca "Categoria A" (o similar) seguido de un bloque de montos en $
        patron = re.compile(
            r"Categor[ií]a\s+" + letra + r"\b(.{0,400}?)(?=Categor[ií]a\s+[A-K]\b|$)",
            re.IGNORECASE | re.DOTALL,
        )
        m = patron.search(texto)
        if not m:
            return None
        bloque = m.group(1)
        montos = re.findall(r"\$\s?([\d\.]+,\d{2})", bloque)
        if len(montos) < 2:
            return None
        valores = [float(v.replace(".", "").replace(",", ".")) for v in montos]
        filas.append(valores)

    # Coherencia minima: el primer monto de cada fila (tope de facturacion)
    # tiene que ser estrictamente creciente de A a K.
    topes = [f[0] for f in filas]
    if topes != sorted(topes) or len(set(topes)) != len(topes):
        return None

    return filas


def buscar_fecha_vigencia(html):
    texto = re.sub(r"<[^>]+>", " ", html)
    m = re.search(r"vigente[s]?\s+desde\s+el?\s+(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", texto, re.IGNORECASE)
    if not m:
        return None
    d, mo, y = m.groups()
    return date(int(y), int(mo), int(d)).isoformat()


def main():
    try:
        html = obtener_html()
    except Exception as e:
        print(f"No se pudo descargar la pagina de ARCA: {e}")
        sys.exit(0)  # no romper el workflow por un fallo de red puntual

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    vigente_actual = data["oficial"]["vigente_desde"]

    nueva_fecha = buscar_fecha_vigencia(html)
    if not nueva_fecha or nueva_fecha == vigente_actual:
        print("Sin cambios: no se detecto una fecha de vigencia nueva en la pagina de ARCA.")
        sys.exit(0)

    print(f"ARCA muestra una fecha de vigencia distinta a la guardada: {nueva_fecha} (guardada: {vigente_actual})")

    filas = parsear_montos(html)
    if not filas:
        print(
            "No se pudo extraer una tabla de 11 categorias coherente de la pagina "
            "(la estructura de la pagina puede haber cambiado). No se modifica data.json. "
            "Revisar manualmente."
        )
        sys.exit(0)

    print("Se detecto una tabla nueva pero el parseo automatico de columnas no es 100% confiable todavia.")
    print("Por seguridad, este script NO sobreescribe los montos solo: deja un aviso para revision manual.")
    # Nota de diseño: preferimos no auto-completar los 11 x N campos (cuota
    # servicios/bienes, SIPA, obra social, superficie, energia, alquiler) sin
    # verificacion humana, porque un error ahi afecta directamente lo que le
    # mostramos a la gente sobre cuanto tiene que pagar. Lo que SI hacemos es
    # dejar constancia de que hay una tabla nueva pendiente de cargar.
    data["oficial"]["pendiente_actualizacion"] = {
        "detectado": date.today().isoformat(),
        "nueva_vigencia_detectada": nueva_fecha,
        "nota": "ARCA publico una tabla nueva. Pendiente de carga manual verificada en data.json.",
    }
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("data.json actualizado con el aviso de 'pendiente_actualizacion'.")


if __name__ == "__main__":
    main()
