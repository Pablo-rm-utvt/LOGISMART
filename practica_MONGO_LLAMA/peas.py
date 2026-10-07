# ============================================================
# PEAS - LOGISMART PYTHON SUITE
# ============================================================

class AgenteLogiSmart:
    """
    Representa el agente inteligente del centro de control.
    """

    def __init__(self):
        # P = Performance
        self.performance = [
            "Controlar acceso",
            "Detectar situaciones de riesgo",
            "Reducir accesos incorrectos",
            "Generar alertas"
        ]

        # E = Environment
        self.environment = [
            "Centro de control",
            "Camiones",
            "Conductores",
            "Zona de inspección"
        ]

        # A = Actuators
        self.actuators = [
            "Barrera de acceso",
            "Alarma",
            "Correo electrónico",
            "Registro del incidente"
        ]

        # S = Sensors
        self.sensors = [
            "Lector de autorización",
            "Báscula",
            "Cámara",
            "Lector de certificación"
        ]

    def mostrar_peas(self):
        print("\n========== MODELO PEAS ==========")

        print("\nP - PERFORMANCE")
        for elemento in self.performance:
            print(" -", elemento)

        print("\nE - ENVIRONMENT")
        for elemento in self.environment:
            print(" -", elemento)

        print("\nA - ACTUATORS")
        for elemento in self.actuators:
            print(" -", elemento)

        print("\nS - SENSORS")
        for elemento in self.sensors:
            print(" -", elemento)