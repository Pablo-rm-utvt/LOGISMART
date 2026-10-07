# ============================================================
# EVALUACIÓN ÉTICA Y MATRIZ DE RIESGOS
# ============================================================

# Ahora vamos a crear una clase:

# EvaluadorRiesgosIA La clase permitirá registrar:

# módulo, riesgo, categoría, impacto, probabilidad, mitigación

# Por ejemplo:
# Módulo:Cámara de detección de somnolencia
# Riesgo: Sesgo en visión nocturna
# Categoría: Sesgo
# Impacto: Alto
# Probabilidad: Media
# Mitigación: Pruebas con diferentes condiciones de iluminación

# python -m py_compile logismart/riesgos.py para verificar que no exista ningun error 
# e indica que se pudo compilar

import json
import os


class EvaluadorRiesgosIA:
    """
    Clase encargada de registrar y exportar
    los riesgos éticos de un sistema de IA.
    """

    def __init__(self):
        """
        Constructor de la clase.

        self.riesgos almacenará todos los
        riesgos registrados.
        """

        self.riesgos = []

    @staticmethod
    def calcular_puntaje(probabilidad, impacto):
        niveles = {"baja": 1, "medio": 3, "media": 3, "alta": 4, "alto": 4, "critica": 5, "crítica": 5}
        valor_probabilidad = niveles.get(str(probabilidad).lower(), probabilidad)
        valor_impacto = niveles.get(str(impacto).lower(), impacto)
        return int(valor_probabilidad) * int(valor_impacto)

    # ========================================================
    # REGISTRAR RIESGO
    # ========================================================

    def registrar_riesgo(
        self,
        modulo,
        riesgo,
        categoria,
        impacto,
        probabilidad,
        mitigacion
    ):
        """
        Registra un nuevo riesgo dentro del sistema.
        """

        riesgo_nuevo = {
            "modulo": modulo,
            "riesgo": riesgo,
            "categoria": categoria,
            "impacto": impacto,
            "probabilidad": probabilidad,
            "mitigacion": mitigacion,
            "puntaje": self.calcular_puntaje(probabilidad, impacto)
        }

        self.riesgos.append(riesgo_nuevo)

    # ========================================================
    # MOSTRAR RIESGOS
    # ========================================================

    def mostrar_riesgos(self):
        """
        Muestra en pantalla todos los riesgos registrados.
        """

        print("\n========================================")
        print("       MATRIZ DE RIESGOS DE IA")
        print("========================================")

        for numero, riesgo in enumerate(
            self.riesgos,
            start=1
        ):

            print(f"\nRiesgo #{numero}")

            print(
                "Módulo:",
                riesgo["modulo"]
            )

            print(
                "Riesgo:",
                riesgo["riesgo"]
            )

            print(
                "Categoría:",
                riesgo["categoria"]
            )

            print(
                "Impacto:",
                riesgo["impacto"]
            )

            print(
                "Probabilidad:",
                riesgo["probabilidad"]
            )

            print(
                "Mitigación:",
                riesgo["mitigacion"]
            )

    # ========================================================
    # EXPORTAR REPORTE
    # ========================================================

    def exportar_reporte(self, archivo):
        """
        Exporta los riesgos registrados a un archivo JSON.

        Si la carpeta no existe, se crea automáticamente.
        """

        # ----------------------------------------------------
        # Obtener la carpeta donde se guardará el archivo
        # ----------------------------------------------------

        carpeta = os.path.dirname(archivo)

        # ----------------------------------------------------
        # Crear la carpeta si no existe
        # ----------------------------------------------------

        if carpeta:
            os.makedirs(
                carpeta,
                exist_ok=True
            )

        # ----------------------------------------------------
        # Crear estructura del reporte
        # ----------------------------------------------------

        reporte = {
            "total_riesgos": len(self.riesgos),
            "riesgos": self.riesgos
        }

        # ----------------------------------------------------
        # Abrir archivo
        # ----------------------------------------------------

        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            # ------------------------------------------------
            # Convertir Python a JSON
            # ------------------------------------------------

            json.dump(
                reporte,
                f,
                indent=4,
                ensure_ascii=False
            )

        # ----------------------------------------------------
        # Confirmación
        # ----------------------------------------------------

        print(
            f"\nReporte exportado correctamente en: {archivo}"
        )


# ============================================================
# PRUEBA DIRECTA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    evaluador = EvaluadorRiesgosIA()

    # --------------------------------------------------------
    # RIESGO 1
    # --------------------------------------------------------

    evaluador.registrar_riesgo(
        modulo="Cámara de detección",
        riesgo="Sesgo en condiciones nocturnas",
        categoria="Sesgo",
        impacto="Alto",
        probabilidad="Media",
        mitigacion=(
            "Realizar pruebas con diferentes "
            "condiciones de iluminación"
        )
    )

    # --------------------------------------------------------
    # RIESGO 2
    # --------------------------------------------------------

    evaluador.registrar_riesgo(
        modulo="Sistema de vigilancia",
        riesgo="Uso inadecuado de información personal",
        categoria="Privacidad",
        impacto="Alto",
        probabilidad="Media",
        mitigacion=(
            "Aplicar controles de acceso "
            "y políticas de retención"
        )
    )

    # --------------------------------------------------------
    # MOSTRAR
    # --------------------------------------------------------

    evaluador.mostrar_riesgos()

    # --------------------------------------------------------
    # EXPORTAR
    # --------------------------------------------------------

    evaluador.exportar_reporte(
        "reportes/reporte_riesgos.json"
    )