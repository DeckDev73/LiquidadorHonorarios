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
