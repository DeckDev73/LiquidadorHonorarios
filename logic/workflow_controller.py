from .cargaArchivo import load_excel_file, find_last_uploaded_file
from .uvr import obtener_codigos_faltantes_uvr, asignar_uvr
from .utils import guardar_estado_como_pickle, cargar_estado_desde_pickle

def procesar_archivo(file_path):
    return load_excel_file(file_path)

def procesar_uvr_manual(df, codigos, valor_uvr):
    return asignar_uvr(df, codigos, valor_uvr)

def detectar_codigos_pendientes(df):
    return obtener_codigos_faltantes_uvr(df)

def guardar_estado(df, nombre_archivo=None):
    guardar_estado_como_pickle(df)

def intentar_cargar_estado_previo():
    return cargar_estado_desde_pickle(), 'estado.pkl'

def profesionales_con_multiples_especialidades(df):
    resultado = {}
    for prof in df['Especialista'].dropna().unique():
        especialidades = df[df['Especialista'] == prof]['Especialidad'].dropna().unique()
        if len(especialidades) > 1:
            resultado[prof] = especialidades
    return resultado

def aplicar_unificacion(df, decisiones):
    df_actualizado = df.copy()
    for prof, esp in decisiones.items():
        df_actualizado.loc[df_actualizado['Especialista'] == prof, 'Especialidad'] = esp
    return df_actualizado

def ejecutar_liquidacion(df, flags):
    df = df.copy()
    df['Valor Liquidado'] = df['Valor UVR'].astype(float) * 1000  # dummy logic
    return df

def obtener_resumen(df):
    return df.groupby("Especialista")["Valor Liquidado"].sum().reset_index()

def filtrar_por_profesional(df, profesional, especialidad=None):
    df_filtrado = df[df['Especialista'] == profesional]
    if especialidad:
        df_filtrado = df_filtrado[df_filtrado['Especialidad'] == especialidad]
    return df_filtrado
