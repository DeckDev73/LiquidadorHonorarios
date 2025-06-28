import pandas as pd

def profesionales_con_multiples_especialidades(df: pd.DataFrame) -> dict:
    """
    Detecta profesionales con más de una especialidad.
    """
    resultado = {}
    for prof in df['Especialista'].dropna().unique():
        especialidades = df[df['Especialista'] == prof]['Especialidad'].dropna().unique()
        if len(especialidades) > 1:
            resultado[prof] = especialidades
    return resultado

def unificar_especialidades(df: pd.DataFrame, decisiones_usuario: dict) -> pd.DataFrame:
    """
    Aplica la especialidad seleccionada por cada profesional.
    """
    df_actualizado = df.copy()
    for prof, especialidad_final in decisiones_usuario.items():
        mask = (df_actualizado['Especialista'] == prof)
        df_actualizado.loc[mask, 'Especialidad'] = especialidad_final
    return df_actualizado

def obtener_tabla_detalle(df: pd.DataFrame, profesional: str, especialidad: str) -> pd.DataFrame:
    """
    Retorna un sub-DataFrame con columnas clave para un especialista + especialidad.
    """
    filtro = (df['Especialista'] == profesional)
    if especialidad:
        filtro &= (df['Especialidad'] == especialidad)

    columnas = ['Especialidad', 'Valor UVR', 'Valor Total']
    return df.loc[filtro, columnas].copy()