from .cargaArchivo import load_excel_file
from .uvr import obtener_codigos_faltantes_uvr, asignar_uvr
from .especialidades import profesionales_con_multiples_especialidades, unificar_especialidades
from .liquidacion import liquidar_dataframe, generar_resumen_por_profesional

def procesar_archivo(file_path):
    return load_excel_file(file_path)

def procesar_uvr_manual(df, codigos, valor_uvr):
    return asignar_uvr(df, codigos, valor_uvr)

def detectar_codigos_pendientes(df):
    return obtener_codigos_faltantes_uvr(df)

def aplicar_unificacion(df, decisiones):
    return unificar_especialidades(df, decisiones)

def ejecutar_liquidacion(df, flags):
    return liquidar_dataframe(df, **flags)

def obtener_resumen(df):
    return generar_resumen_por_profesional(df)

def filtrar_por_profesional(df, profesional, especialidad=None):
    df_filtrado = df[df['Especialista'] == profesional]
    if especialidad:
        df_filtrado = df_filtrado[df_filtrado['Especialidad'] == especialidad]
    return df_filtrado
