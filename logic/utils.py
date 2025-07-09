import pandas as pd
import os
from io import BytesIO
from logic.resumen import obtener_resumen_general
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import numbers

def guardar_estado_como_pickle(df: pd.DataFrame, path='uploads/estado.pkl'):
    df.to_pickle(path)
    print(f"💾 Estado guardado en {path} (pkl)")

def cargar_estado_desde_pickle(path='uploads/estado.pkl') -> pd.DataFrame | None:
    if os.path.exists(path):
        print(f"🧠 Cargando estado desde {path}")
        return pd.read_pickle(path)
    return None

def limpiar_archivos_anteriores(upload_folder='uploads', estado_path='uploads/estado.pkl', flags_estado_path='uploads/flags_estado.pkl'):
    # Elimina todos los archivos en la carpeta de uploads
    for archivo in os.listdir(upload_folder):
        archivo_path = os.path.join(upload_folder, archivo)
        if os.path.isfile(archivo_path):
            os.remove(archivo_path)

    # Elimina estado.pkl si existe
    if os.path.exists(estado_path):
        os.remove(estado_path)
    
    # Elimina flags_estado.pkl si existe
    if os.path.exists(flags_estado_path):
        os.remove(flags_estado_path)

def generar_excel_con_resumen(df):
    """
    Genera un archivo Excel con dos hojas:
    - 'Resumen': resumen por especialista (sin total_liquidado)
    - 'Liquidación': los datos completos del DataFrame original, con columnas clave en formato texto
    """
    output = BytesIO()

    # Obtener resumen completo
    resumen_completo = obtener_resumen_general(df)
    
    # Crear DataFrame de resumen SIN total_liquidado
    resumen_data = []
    for especialista_data in resumen_completo['especialistas']:
        resumen_data.append({
            "Especialista": especialista_data['especialista'],
            "Porcentaje Liquidado": especialista_data['porcentaje_liquidado'],
            "Total Liquidado": especialista_data['total_liquidado_formateado']
        })
    
    df_resumen = pd.DataFrame(resumen_data)

    # Preparar DataFrame de liquidación
    df_copia = df.copy()
    
    # Convertir a entero las columnas que tienen .0
    if 'Codigo Homologado' in df_copia.columns:
        # Usar pd.to_numeric para manejar valores problemáticos
        df_copia['Codigo Homologado'] = pd.to_numeric(df_copia['Codigo Homologado'], errors='coerce').fillna(0).astype(int).astype(str)
    
    if 'Valor UVR' in df_copia.columns:
        # Usar pd.to_numeric para manejar valores problemáticos
        df_copia['Valor UVR'] = pd.to_numeric(df_copia['Valor UVR'], errors='coerce').fillna(0).astype(int).astype(str)

    # Escribir el archivo Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Escribir hoja de resumen
        df_resumen.to_excel(writer, index=False, sheet_name='Resumen')

        # Escribir hoja de liquidación
        df_copia.to_excel(writer, index=False, sheet_name='Liquidación')

        # Establecer la hoja activa como Resumen
        writer.book.active = writer.book['Resumen']

    # Cargar el workbook para aplicar formato texto
    output.seek(0)
    wb = load_workbook(output)
    
    # Aplicar formato texto a las columnas específicas en la hoja 'Liquidación'
    ws_liquidacion = wb['Liquidación']
    
    # Obtener mapeo de columnas
    col_map = {}
    for cell in ws_liquidacion[1]:  # Primera fila (headers)
        if cell.value:
            col_map[cell.value] = cell.column_letter
    
    # Aplicar formato texto a columnas específicas
    for col_name in ['Codigo Homologado', 'Valor UVR']:
        col_letter = col_map.get(col_name)
        if col_letter:
            # Aplicar formato texto a toda la columna
            for row in range(2, ws_liquidacion.max_row + 1):  # Empezar desde fila 2 (después del header)
                cell = ws_liquidacion[f'{col_letter}{row}']
                cell.number_format = numbers.FORMAT_TEXT

    # Guardar los cambios
    output_final = BytesIO()
    wb.save(output_final)
    output_final.seek(0)
    
    return output_final