import pandas as pd

def obtener_codigos_faltantes_uvr(df: pd.DataFrame) -> list:
    mask = (df['Valor UVR'].isna()) | (df['Valor UVR'].astype(float) == 0)
    return df.loc[mask, 'Codigo Homologado'].dropna().unique().tolist()

def asignar_uvr(df: pd.DataFrame, codigos: list, valor_uvr: float) -> pd.DataFrame:
    df_actualizado = df.copy()
    df_actualizado.loc[df_actualizado['Codigo Homologado'].isin(codigos), 'Valor UVR'] = valor_uvr
    return df_actualizado
