import pandas as pd
import pickle
import os

# 🔧 Constantes generales
VALOR_UVR = 1270
VALOR_UVR_ISS_ANESTESIA = 960
FLAGS_PATH = os.path.join("uploads", "flags_estado.pkl")

# Listas de especialistas con reglas especiales
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

# 📥 Función para cargar flags desde pkl
def cargar_flags_por_profesional():
    if os.path.exists(FLAGS_PATH):
        with open(FLAGS_PATH, 'rb') as f:
            return pickle.load(f)
    return {}

# 📤 Función para guardar flags (por si necesitas en otros scripts)
def guardar_flags_por_profesional(flags_dict: dict):
    # 👇 Asegurar que la carpeta "uploads" exista
    os.makedirs(os.path.dirname(FLAGS_PATH), exist_ok=True)

    with open(FLAGS_PATH, 'wb') as f:
        pickle.dump(flags_dict, f)

# ✅ Guardar un único flag por especialista
def actualizar_flag_especialista(nombre_profesional: str, flag_activado: str):
    flags_dict = cargar_flags_por_profesional()
    flags_dict[nombre_profesional.strip()] = flag_activado  # Aseguramos consistencia
    guardar_flags_por_profesional(flags_dict)

def eliminar_flag_profesional(nombre_profesional: str):
    flags_dict = cargar_flags_por_profesional()
    nombre_profesional = nombre_profesional.strip()
    if nombre_profesional in flags_dict:
        del flags_dict[nombre_profesional]
        guardar_flags_por_profesional(flags_dict)


# 🔧 Lógica de liquidación
def liquidar_fila(row, flag=None):
    esp = str(row.get("Especialidad", "")).upper()
    especialista = str(row.get("Especialista", "")).strip()
    tipo = str(row.get("Tipo Procedimiento", "")).upper()
    plan = str(row.get("Plan Beneficios", "")).upper()
    via = str(row.get("Cantidad o Via", ""))
    uvr = float(row.get("Valor UVR", 0))
    valor = float(row.get("Valor Total", 0))

    if "ANESTESIOLOGIA" in esp:
        base = uvr * VALOR_UVR_ISS_ANESTESIA
        
        if especialista.upper() in [a.strip().upper() for a in ANESTESIOLOGOS_CON_INCREMENTO]:
            base *= 1.3
        if "Multiple - Igual Via Igual Especialista" in via:
            return base * 0.6
        elif "Multiple - Diferente Via Igual Especialista" in via:
            return base * 0.75
        return base

    # FLAG: Cirujano reconstructivo
    if flag == "check_reconstruc":
        if "RECONSTRUCTIVA" in tipo:
            return 2700000 if "EPS" in plan else 3000000
        base = uvr * VALOR_UVR
        return base + base * 0.2

    # FLAG: Cirujano de pie y tobillo
    if flag == "check_pie":
        if "CONSULTA" in tipo:
            return 30000
        elif "JUNTA" in tipo or "ESPECIAL" in tipo:
            return valor * 0.7
        elif "QUIR" in tipo or "PROCED QX" in tipo or "PROCEDIMIENTOS QUIRURGICOS" in tipo:
            base = uvr * VALOR_UVR
            return base + base * 0.3

    # FLAG: Socio ortopedista
    if flag == "check_socio" and "ORTOPEDIA" in esp:
        if "SOAT" in plan:
            return valor * 0.7
        return valor * 0.85

    # Otras reglas especiales por especialidad
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

    if "MANO" in esp:
        if especialista.upper() == "CUELLO DIAZ MARLA KARIN ":
            return (uvr * VALOR_UVR) * 1.3
        if "CONSULTA" in tipo: return 30000
        elif "JUNTA" in tipo or "ESPECIAL" in tipo: return valor * 0.7
        elif "QUIR" in tipo or "PROCED QX" in tipo or "PROCEDIMIENTOS QUIRURGICOS" in tipo:
            return (uvr * VALOR_UVR) + (uvr * VALOR_UVR) * 0.3

    if "ORTOPEDIA" in esp:
        if especialista.upper() in [o.strip().upper() for o in ORTOPEDISTAS_CON_INCREMENTO]:
            return (uvr * VALOR_UVR) * 1.3
        if "CONSULTA" in tipo:
            return 27000
        elif "QUIR" in tipo or "PROCED QX" in tipo or "PROCEDIMIENTOS QUIRURGICOS" in tipo:
            return (uvr * VALOR_UVR) + (uvr * VALOR_UVR) * 0.2
        elif "NO QUIR" in tipo:
            return valor * 0.7

    return uvr * VALOR_UVR


# 🧾 Aplicar liquidación a todo el DataFrame usando flags por especialista
def liquidar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Valor Total'] = pd.to_numeric(df.get('Valor Total', 0), errors='coerce')
    flags_dict = cargar_flags_por_profesional()

    def aplicar_liquidacion(row):
        especialista = str(row.get("Especialista", "")).strip()
        flag = flags_dict.get(especialista)
        return liquidar_fila(row, flag=flag)

    df['Valor Liquidado'] = df.apply(aplicar_liquidacion, axis=1)
    return df
