from itertools import product


def generar_tabla_verdad():
    print("P: autorización; Q: peso excedido; R: carga peligrosa.")
    print("S: certificado del conductor; C: certificado especial; T: horario permitido.")
    print("A: acceso estándar; E: inspección; las últimas columnas indican si pasan los requisitos de carga peligrosa.")
    print("P     Q     R     S     C     T     | A     E     Certificado carga   Horario carga")

    combinaciones = list(product((False, True), repeat=6))
    combinaciones.remove((True, False, False, True, True, True))
    combinaciones.insert(0, (True, False, False, True, True, True))

    for P, Q, R, S, C, T in combinaciones:
        A = P and S and not Q
        E = P and (R or Q)
        certificado_carga_valido = not R or C
        horario_carga_valido = not R or T
        valores = (P, Q, R, S, C, T)
        salidas = (A, E, certificado_carga_valido, horario_carga_valido)
        print(" ".join(f"{str(valor):5}" for valor in valores) + "| " + " ".join(f"{str(valor):5}" for valor in salidas))


if __name__ == "__main__":
    generar_tabla_verdad()