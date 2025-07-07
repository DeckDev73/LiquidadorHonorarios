import pandas as pd
import os

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