import pandas as pd
import os

def guardar_df_como_excel(df: pd.DataFrame, filename: str, folder='uploads'):
    path = os.path.join(folder, filename)
    df.to_excel(path, index=False)
    print(f"💾 Archivo actualizado en disco: {path}")
