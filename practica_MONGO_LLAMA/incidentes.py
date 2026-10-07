# ============================================================
# CLASIFICADOR DE INCIDENTES
# ============================================================

import json
from datetime import datetime


def prioridad_por_nivel(nivel):
    if nivel >= 8:
        return "CRITICA"
    if nivel >= 5:
        return "ALTA"
    if nivel >= 3:
        return "MEDIA"
    return "BAJA"


def clasificar_incidente(tipo, descripcion, nivel):
    """
    Procesa la información de un incidente
    y devuelve exclusivamente JSON.
    """

    # --------------------------------------------------------
    # Clasificación del incidente
    # --------------------------------------------------------

    prioridad = prioridad_por_nivel(nivel)

    # --------------------------------------------------------
    # Crear información procesada
    # --------------------------------------------------------

    resultado = {
        "incidente": {
            "tipo": tipo,
            "descripcion": descripcion,
            "nivel": nivel,
            "prioridad": prioridad,
            "fecha": datetime.now().isoformat()
        }
    }

    # --------------------------------------------------------
    # Convertir diccionario a JSON
    # --------------------------------------------------------
    # Pero si queremos enviarlo como JSON
    return json.dumps(
        resultado,
        indent=4,
        ensure_ascii=False
    )


def enviar_correo_soporte(destinatario, asunto, mensaje):
    """
    Simulación del envío de correo.

    En un sistema real aquí se utilizaría SMTP
    o una API de correo.
    """

    print("\n========== CORREO DE SOPORTE ==========")

    print("Destinatario:", destinatario)
    print("Asunto:", asunto)
    print("Mensaje:", mensaje)

    print("========================================")


if __name__ == "__main__":

    json_resultado = clasificar_incidente(
        tipo="Acceso",
        descripcion="Camión excede el límite de peso",
        nivel=8
    )

    enviar_correo_soporte(
        destinatario="soporte@logismart.com",
        asunto="Incidente detectado",
        mensaje=json_resultado
    )

    print("\nJSON generado:")
    print(json_resultado)