import os
import pandas as pd

REQUIRED_COLUMNS = ['Codigo Homologado', 'CUPS', 'Valor UVR', 'Especialidad', 'Tipo Procedimiento', 'Plan Beneficios']

def load_excel_file(file_path: str, eliminar_repetidos: bool = False) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    if 'Codigo Homologado' not in df.columns:
        raise ValueError("El archivo debe contener la columna 'Codigo Homologado'")
    
    df['Codigo Homologado'] = df['Codigo Homologado'].astype(str).str.strip()

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col == 'Valor UVR' else ''
    
    if eliminar_repetidos:
        df = df.drop_duplicates()  # Elimina filas idénticas
        df = df.loc[:, ~df.T.duplicated()]  # Elimina columnas duplicadas

    return df
