import pandas as pd

# 🔧 Constantes generales
VALOR_UVR = 1270
VALOR_UVR_ISS_ANESTESIA = 960

# 🧑‍⚕️ Listas de especialistas con reglas especiales
ANESTESIOLOGOS_CON_INCREMENTO = [
    "SINISTERRA MEJIA ERNEY MAURICIO ",
    "GALLEGO DUQUE JORGE ALEJANDRO ",
    "SEPULVEDA LONDOÑO GERMAN ",
    "MARULANDA SANCHEZ JORGE MARIO ",
    "ESPAÑA SAAVEDRA JULIAN CAMILO ",
    "TORRENTE FERNANDEZ JUAN CARLOS ",
    "GARCIA FREITAG MARIA ANGELICA ",
]

ORTOPEDISTAS_CON_INCREMENTO = [
    "CARDONA ESCOBAR FELIPE ",
    "ARTEAGA FERREIRA CAMILO ANDRES ",
    "CUELLO DIAZ MARLA KARIN ",
]

# ✅ Extraer flags desde request.args
def extraer_flags_desde_request(args) -> dict:
    return {
        'check_anestesia_diff': args.get('check_anestesia_diff', 'false').lower() == 'true',
        'check_socio': args.get('check_socio', 'false').lower() == 'true',
        'check_reconstruc': args.get('check_reconstruc', 'false').lower() == 'true',
        'check_pie': args.get('check_pie', 'false').lower() == 'true',
    }

# 💰 Lógica de liquidación fila por fila
def liquidar_fila(row, check_anestesia_diff=False, check_socio=False, check_reconstruc=False, check_pie=False):
    esp = str(row.get("Especialidad", "")).upper()
    especialista = str(row.get("Especialista", "")).upper()
    tipo = str(row.get("Tipo Procedimiento", "")).upper()
    plan = str(row.get("Plan Beneficios", "")).upper()
    via = str(row.get("Cantidad o Via", ""))
    uvr = float(row.get("Valor UVR", 0))
    valor = float(row.get("Valor Total", 0))

    if "ANESTESIOLOGIA" in esp:
        base = uvr * VALOR_UVR_ISS_ANESTESIA
        if especialista == "GARCIA FREITAG MARIA ANGELICA ":
            base *= 0.6
        elif especialista in ANESTESIOLOGOS_CON_INCREMENTO:
            base *= 1.3
        if "Multiple - Igual Via Igual Especialista" in via:
            return base * 0.6
        elif "Multiple - Diferente Via Igual Especialista" in via:
            return base * 0.75
        return base

    if "MAXILOFACIAL" in esp:
        if "INTERCONSULTA" in tipo: return 35000
        elif "CONSULTA" in tipo: return 29000
        return valor * 0.7

    if "FISIATRIA" in esp:
        if "PRIMERA" in tipo: return 59000
        elif "CONTROL" in tipo: return 51000
        elif "ARL" in tipo and "JUNTA" in tipo: return 73000
        elif "JUNTA" in tipo: return 70000
        elif "TOXINA" in tipo: return 155000
        elif "INFILTRACION" in tipo: return 76000
        elif "NO QUIR" in tipo: return valor * 0.7

    if "DOLOR" in esp:
        if "INTERCONSULTA" in tipo: return 58400
        elif "MIOFASCIAL" in tipo: return 64500
        elif "PAQUETE" in tipo: return 350000
        return valor * 0.7

    if "LABORAL" in esp:
        if "JUNTA" in tipo: return valor * 0.8
        return valor * 0.85

    if "NEUROCIRU" in esp:
        return valor * 0.7 if "SOAT" in plan else valor * 0.8

    if "PEDIATRICA" in esp:
        if "EPS" in plan: return 70000
        elif "SOAT" in plan or "POLIZA" in plan: return valor * 0.7
        elif "YESO" in tipo: return 260000
        elif "MALFORMACION" in tipo: return 980000

    if check_reconstruc:
        if "RECONSTRUCTIVA" in tipo: return 2700000 if "EPS" in plan else 3000000
        base = uvr * VALOR_UVR
        return base + base * 0.2

    if check_pie:
        if "CONSULTA" in tipo: return 30000
        elif "JUNTA" in tipo or "ESPECIAL" in tipo: return valor * 0.7
        elif "QUIR" in tipo or "PROCED QX" in tipo or "PROCEDIMIENTOS QUIRURGICOS" in tipo:
            base = uvr * VALOR_UVR
            return base + base * 0.3

    if "MANO" in esp:
        if "CUELLO DIAZ MARLA KARIN " in especialista:
            return (uvr * VALOR_UVR) * 1.3
        if "CONSULTA" in tipo: return 30000
        elif "JUNTA" in tipo or "ESPECIAL" in tipo: return valor * 0.7
        elif "QUIR" in tipo or "PROCED QX" in tipo or "PROCEDIMIENTOS QUIRURGICOS" in tipo:
            return (uvr * VALOR_UVR) + (uvr * VALOR_UVR) * 0.3

    if "ORTOPEDIA" in esp:
        if especialista.strip().upper() in [o.strip().upper() for o in ORTOPEDISTAS_CON_INCREMENTO]:
            return (uvr * VALOR_UVR) * 1.3
        if check_socio:
            return valor * 0.85 if "SOAT" not in plan else valor * 0.7
        if "CONSULTA" in tipo: return 27000
        elif "QUIR" in tipo or "PROCED QX" in tipo or "PROCEDIMIENTOS QUIRURGICOS" in tipo:
            return (uvr * VALOR_UVR) + (uvr * VALOR_UVR) * 0.2
        elif "NO QUIR" in tipo: return valor * 0.7

    return uvr * VALOR_UVR

# 🧾 Aplicar liquidación a todo el DataFrame
def liquidar_dataframe(df: pd.DataFrame, check_anestesia_diff=False, check_socio=False, check_reconstruc=False, check_pie=False) -> pd.DataFrame:
    df = df.copy()
    df['Valor Total'] = pd.to_numeric(df.get('Valor Total', 0), errors='coerce')
    df['Valor Liquidado'] = df.apply(lambda row: liquidar_fila(
        row,
        check_anestesia_diff=check_anestesia_diff,
        check_socio=check_socio,
        check_reconstruc=check_reconstruc,
        check_pie=check_pie
    ), axis=1)
    return df
