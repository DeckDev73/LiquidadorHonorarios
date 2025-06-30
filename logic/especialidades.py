import pandas as pd

def obtener_profesionales_y_especialidades(df: pd.DataFrame) -> dict:
    """
    Retorna todos los profesionales junto a todas sus especialidades (aunque sea solo una).
    """
    resultado = {}
    for prof in df['Especialista'].dropna().unique():
        especialidades = df[df['Especialista'] == prof]['Especialidad'].dropna().unique()
        resultado[prof] = list(especialidades)
    return resultado
