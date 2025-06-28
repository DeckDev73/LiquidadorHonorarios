from .cargaArchivo import load_excel_file
from .uvr import obtener_codigos_faltantes_uvr, asignar_uvr
from .especialidades import profesionales_con_multiples_especialidades, unificar_especialidades, obtener_tabla_detalle
from .liquidacion import liquidar_dataframe, generar_resumen_por_profesional
from .utils import guardar_estado_como_pickle, cargar_estado_desde_pickle

# ----------------------------
# 📥 ARCHIVO INICIAL
# ----------------------------
def procesar_archivo(file_path):
    return load_excel_file(file_path)

def intentar_cargar_estado_previo():
    df = cargar_estado_desde_pickle()
    return df, 'estado.pkl' if df is not None else (None, None)

# ----------------------------
# 🔁 GUARDAR ESTADO
# ----------------------------
def guardar_estado(df, nombre_archivo=None):
    guardar_estado_como_pickle(df)

# ----------------------------
# 📌 UVR
# ----------------------------
def detectar_codigos_pendientes(df):
    return obtener_codigos_faltantes_uvr(df)

def procesar_uvr_manual(df, codigos, valor_uvr):
    return asignar_uvr(df, codigos, valor_uvr)

# ----------------------------
# 🧠 ESPECIALIDADES
# ----------------------------
def traer_profesionales_multiples_especialidades(df):
    return profesionales_con_multiples_especialidades(df)

def aplicar_unificacion_especialidades(df, decisiones_usuario):
    return unificar_especialidades(df, decisiones_usuario)

def obtener_tabla_especialista(df, profesional, especialidad):
    return obtener_tabla_detalle(df, profesional, especialidad)

# ----------------------------
# 💸 LIQUIDACIÓN
# ----------------------------
def ejecutar_liquidacion(df, flags):
    return liquidar_dataframe(df, **flags)

def obtener_resumen(df):
    return generar_resumen_por_profesional(df)

def filtrar_por_profesional(df, profesional, especialidad=None):
    df_filtrado = df[df['Especialista'] == profesional]
    if especialidad:
        df_filtrado = df_filtrado[df_filtrado['Especialidad'] == especialidad]
    return df_filtrado
