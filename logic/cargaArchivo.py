import os
import pandas as pd

REQUIRED_COLUMNS = ['Codigo Homologado', 'CUPS', 'Valor UVR', 'Especialidad', 'Tipo Procedimiento', 'Plan Beneficios']

def load_excel_file(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    if 'Codigo Homologado' not in df.columns:
        raise ValueError("El archivo debe contener la columna 'Codigo Homologado'")
    df['Codigo Homologado'] = df['Codigo Homologado'].astype(str).str.strip()
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col == 'Valor UVR' else ''
    return df

def find_last_uploaded_file(upload_dir='uploads') -> str | None:
    """
    Busca el archivo Excel más recientemente modificado en la carpeta de uploads.
    """
    if not os.path.exists(upload_dir):
        return None

    excel_files = [
        os.path.join(upload_dir, f)
        for f in os.listdir(upload_dir)
        if f.lower().endswith('.xlsx')
    ]

    if not excel_files:
        return None

    # Ordenar por fecha de modificación descendente
    latest_file = max(excel_files, key=os.path.getmtime)
    return latest_file
