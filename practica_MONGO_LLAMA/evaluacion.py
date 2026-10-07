from statistics import mean
from time import perf_counter

from clasificador import ClasificadorHibrido, clasificar_por_reglas


CORREOS_ETIQUETADOS = [
    ("seguridad", "Reporte de accidente con un conductor herido en el patio."),
    ("seguridad", "Incendio detectado en la zona de carga, necesitamos apoyo."),
    ("seguridad", "Choque entre dos camiones; hay una persona herida."),
    ("seguridad", "Informo un robo de mercancía durante la noche."),
    ("seguridad", "Amenaza recibida contra el personal de vigilancia."),
    ("medio_ambiente", "Se produjo un derrame de combustible junto al muelle."),
    ("medio_ambiente", "Posible contaminación del agua por producto químico."),
    ("medio_ambiente", "Derrame químico en el área de almacenamiento."),
    ("medio_ambiente", "Reportamos contaminación y fuga de sustancias."),
    ("medio_ambiente", "Un químico se filtró cerca del drenaje."),
    ("control_acceso", "La placa CAM-101 no permite acceso al recinto."),
    ("control_acceso", "Camión con peso excedido bloqueado en la entrada."),
    ("control_acceso", "Falta certificación vigente para autorizar el acceso."),
    ("control_acceso", "Solicito revisión de acceso para placa ABC-1234."),
    ("control_acceso", "El camión no tiene autorización para ingresar."),
    ("operacional", "Retraso de dos horas en la ruta norte."),
    ("operacional", "Avería mecánica reportada durante el turno."),
    ("operacional", "Falla en el sistema de despacho."),
    ("operacional", "Demora en la entrega por cierre de carretera."),
    ("operacional", "La ruta asignada aparece incorrecta en el manifiesto."),
    ("general", "Adjunto el calendario de reuniones de la próxima semana."),
    ("general", "Favor confirmar recepción del documento administrativo."),
    ("general", "Consulta sobre el horario de atención de oficinas."),
    ("general", "Comparto el acta de la reunión de seguimiento."),
    ("general", "Necesito actualizar los datos de contacto del proveedor."),
    ("seguridad", "URGENTE: incendio y evacuación en el almacén principal."),
    ("medio_ambiente", "Derrame de combustible requiere contención inmediata."),
    ("control_acceso", "Urgente, CAM-208 bloqueado por carga peligrosa."),
    ("operacional", "Urgente, avería deja la unidad fuera de servicio."),
    ("general", "Solicitud de información general sobre el proceso de alta."),
]


def _metricas(etiquetas, predicciones, latencias):
    clases = sorted(set(etiquetas) | {valor for valor in predicciones if valor})
    matriz = {real: {predicha: 0 for predicha in clases} for real in clases}
    aciertos = 0
    respondidos = 0
    for real, predicha in zip(etiquetas, predicciones):
        if predicha:
            respondidos += 1
            matriz[real][predicha] += 1
            aciertos += real == predicha
    return {
        "exactitud": round(aciertos / len(etiquetas), 4) if etiquetas else 0,
        "cobertura": round(respondidos / len(etiquetas), 4) if etiquetas else 0,
        "latencia_media_ms": round(mean(latencias), 2) if latencias else 0,
        "matriz_confusion": matriz,
    }


def evaluar_conjunto(repositorio, modelo="llama3.2", progreso=None, usar_llm=True):
    clasificador = ClasificadorHibrido(repositorio, modelo=modelo, usar_llm=usar_llm)
    etiquetas = [etiqueta for etiqueta, _ in CORREOS_ETIQUETADOS]
    pred_reglas, pred_llm, pred_hibrido = [], [], []
    tiempo_reglas, tiempo_llm, tiempo_hibrido = [], [], []
    detalles = []
    for indice, (etiqueta, correo) in enumerate(CORREOS_ETIQUETADOS, 1):
        inicio = perf_counter()
        por_reglas = clasificar_por_reglas(correo)
        tiempo_reglas.append((perf_counter() - inicio) * 1000)
        resultado = clasificador.clasificar(correo)
        llm = resultado["clasificacion_llm"]
        pred_reglas.append(por_reglas.categoria)
        pred_llm.append(llm["categoria"] if llm else None)
        pred_hibrido.append(resultado["categoria"])
        tiempo_hibrido.append(resultado["latencia_ms"])
        tiempo_llm.append(resultado["latencia_llm_ms"])
        detalles.append({
            "etiqueta": etiqueta,
            "correo": correo,
            "reglas": por_reglas.categoria,
            "llm": llm["categoria"] if llm else "sin_respuesta",
            "hibrido": resultado["categoria"],
            "latencia_ms": resultado["latencia_ms"],
            "latencia_llm_ms": resultado["latencia_llm_ms"],
        })
        if progreso:
            progreso(indice, len(CORREOS_ETIQUETADOS))
    return {
        "muestra": len(CORREOS_ETIQUETADOS),
        "metricas": {
            "reglas": _metricas(etiquetas, pred_reglas, tiempo_reglas),
            "llm": _metricas(etiquetas, pred_llm, [valor for valor in tiempo_llm if valor]),
            "hibrido": _metricas(etiquetas, pred_hibrido, tiempo_hibrido),
        },
        "detalles": detalles,
    }