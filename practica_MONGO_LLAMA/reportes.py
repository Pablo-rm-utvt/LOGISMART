import csv
import json
from pathlib import Path


def exportar(documentos, archivo, formato):
    ruta = Path(archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos = list(documentos)
    formato = formato.lower()
    if formato == "json":
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    elif formato == "csv":
        campos = sorted({clave for documento in datos for clave in documento})
        with ruta.open("w", encoding="utf-8-sig", newline="") as salida:
            escritor = csv.DictWriter(salida, fieldnames=campos, extrasaction="ignore")
            escritor.writeheader()
            for documento in datos:
                fila = {
                    clave: json.dumps(valor, ensure_ascii=False, default=str)
                    if isinstance(valor, (dict, list)) else valor
                    for clave, valor in documento.items()
                }
                escritor.writerow(fila)
    elif formato == "pdf":
        _escribir_pdf(ruta, datos)
    else:
        raise ValueError("Formato no soportado. Usa PDF, CSV o JSON.")
    return ruta


def _escribir_pdf(ruta, documentos):
    lineas = ["LogiSmart - Reporte", ""]
    for numero, documento in enumerate(documentos, 1):
        lineas.append(f"Registro {numero}")
        for clave, valor in documento.items():
            if clave == "_id":
                continue
            texto = f"{clave}: {json.dumps(valor, ensure_ascii=False, default=str)}"
            lineas.extend(texto[indice:indice + 90] for indice in range(0, len(texto), 90))
        lineas.append("")
    paginas = [lineas[inicio:inicio + 55] for inicio in range(0, len(lineas), 55)] or [[]]

    def pdf_texto(texto):
        valor = texto.encode("cp1252", errors="replace")
        return b"(" + valor.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"

    objetos = [b"<< /Type /Catalog /Pages 2 0 R >>"]
    ids_paginas = [4 + pagina * 2 for pagina in range(len(paginas))]
    hijos = " ".join(f"{identificador} 0 R" for identificador in ids_paginas)
    objetos.append(f"<< /Type /Pages /Kids [{hijos}] /Count {len(paginas)} >>".encode("ascii"))
    objetos.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    for indice, lineas_pagina in enumerate(paginas):
        contenido = b"BT /F1 9 Tf 42 800 Td 12 TL\n"
        for linea in lineas_pagina:
            contenido += pdf_texto(linea) + b" Tj T*\n"
        contenido += b"ET"
        id_pagina = 4 + indice * 2
        id_contenido = id_pagina + 1
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {id_contenido} 0 R >>".encode("ascii")
        )
        objetos.append(
            b"<< /Length " + str(len(contenido)).encode("ascii") + b" >>\nstream\n"
            + contenido + b"\nendstream"
        )
    salida = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for numero, objeto in enumerate(objetos, 1):
        offsets.append(len(salida))
        salida.extend(f"{numero} 0 obj\n".encode("ascii") + objeto + b"\nendobj\n")
    inicio_xref = len(salida)
    salida.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        salida.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    salida.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF".encode("ascii")
    )
    ruta.write_bytes(salida)