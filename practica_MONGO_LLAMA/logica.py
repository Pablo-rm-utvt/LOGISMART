# P = autorización previa; Q = peso excedido; R = carga peligrosa.
# S = certificación del conductor vigente; C = certificado especial vigente.
# T = horario permitido para carga peligrosa.
# A = P ∧ S ∧ ¬Q; E = P ∧ (R ∨ Q).
# Regla 1: R → C (¬R ∨ C). Regla 2: R → T (¬R ∨ T).

def evaluar_camion(P, Q, R, S, horario_peligroso_permitido=True, certificado_peligrosos=True):
    acceso_estandar = P and S and not Q
    inspeccion_especial = P and (R or Q)
    certificacion_peligrosa_valida = not R or certificado_peligrosos
    horario_peligroso_valido = not R or horario_peligroso_permitido
    requisitos_acceso = acceso_estandar and certificacion_peligrosa_valida and horario_peligroso_valido

    if not requisitos_acceso:
        decision = "ACCESO BLOQUEADO"
    elif inspeccion_especial:
        decision = "INSPECCION ESPECIAL"
    else:
        decision = "ACCESO APROBADO"

    return {
        "autorizacion": P,
        "peso_excedido": Q,
        "carga_peligrosa": R,
        "certificacion": S,
        "certificado_peligrosos": certificado_peligrosos,
        "horario_peligroso_permitido": horario_peligroso_permitido,
        "acceso_estandar": acceso_estandar,
        "inspeccion_especial": inspeccion_especial,
        "certificacion_peligrosa_valida": certificacion_peligrosa_valida,
        "horario_peligroso_valido": horario_peligroso_valido,
        "decision_final": requisitos_acceso and not inspeccion_especial,
        "decision_operativa": decision,
        "explicacion": [
            f"P={P}: autorización previa",
            f"Q={Q}: peso excedido",
            f"R={R}: carga peligrosa",
            f"S={S}: certificado del conductor vigente",
            f"C={certificado_peligrosos}: certificado especial vigente",
            f"T={horario_peligroso_permitido}: horario permitido",
            f"A=P∧S∧¬Q={acceso_estandar}",
            f"E=P∧(R∨Q)={inspeccion_especial}",
            f"R→C (¬R∨C)={certificacion_peligrosa_valida}",
            f"R→T (¬R∨T)={horario_peligroso_valido}",
        ],
    }


if __name__ == "__main__":
    print(evaluar_camion(P=True, Q=False, R=False, S=True))