from .cargaArchivo import load_excel_file, find_last_uploaded_file
from .uvr import obtener_codigos_faltantes_uvr, asignar_uvr
from .especialidades import profesionales_con_multiples_especialidades, unificar_especialidades
from .liquidacion import liquidar_dataframe, generar_resumen_por_profesional
from .utils import guardar_df_como_excel
import os

def procesar_archivo(file_path):
    """
    Carga un archivo nuevo desde disco.
    """
    return load_excel_file(file_path)

def intentar_cargar_ultimo_archivo():
    """
    Carga el último archivo subido en la carpeta /uploads.
    """
    ruta = find_last_uploaded_file()
    if ruta:
        print(f"🧠 Restaurando desde: {ruta}")
        return load_excel_file(ruta), os.path.basename(ruta)
    return None, None

def guardar_estado(df, nombre_archivo):
    """
    Guarda el DataFrame modificado en disco.
    """
    guardar_df_como_excel(df, nombre_archivo)

def procesar_uvr_manual(df, codigos, valor_uvr):
    """
    Aplica UVR manual a códigos seleccionados.
    """
    return asignar_uvr(df, codigos, valor_uvr)


def detectar_codigos_pendientes(df):
    """
    Retorna lista de códigos sin UVR.
    """
    return obtener_codigos_faltantes_uvr(df)


def aplicar_unificacion(df, decisiones):
    """
    Cambia las especialidades según las decisiones del usuario.
    """
    return unificar_especialidades(df, decisiones)


def ejecutar_liquidacion(df, flags):
    """
    Ejecuta la lógica de liquidación con los flags correspondientes.
    """
    return liquidar_dataframe(df, **flags)


def obtener_resumen(df):
    """
    Resume el total liquidado por profesional.
    """
    return generar_resumen_por_profesional(df)


def filtrar_por_profesional(df, profesional, especialidad=None):
    """
    Retorna solo las filas asociadas al profesional (y especialidad si aplica).
    """
    df_filtrado = df[df['Especialista'] == profesional]
    if especialidad:
        df_filtrado = df_filtrado[df_filtrado['Especialidad'] == especialidad]
    return df_filtrado
