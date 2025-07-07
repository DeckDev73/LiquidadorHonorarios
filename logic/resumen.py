#resumen.py
import pandas as pd
from logic.liquidacion import liquidar_dataframe

def obtener_resumen_general(df: pd.DataFrame) -> dict:
    """
    Obtiene un resumen general de la liquidación por especialista.
    
    Returns:
        dict: Con 'especialistas' (lista de dict) y 'totales' (dict)
    """
    if df is None or df.empty:
        return {
            'especialistas': [],
            'totales': {
                'total_liquidado': 0,
                'porcentaje_promedio': 0,
                'total_especialistas': 0
            }
        }
    
    # Liquidar el DataFrame completo
    df_liquidado = liquidar_dataframe(df)
    
    # Agrupar por especialista
    resumen_especialistas = []
    total_general = 0
    suma_porcentajes = 0
    
    especialistas_unicos = df_liquidado['Especialista'].unique()
    
    for especialista in especialistas_unicos:
        df_especialista = df_liquidado[df_liquidado['Especialista'] == especialista]
        
        # Calcular total liquidado
        total_liquidado = df_especialista['Valor Liquidado'].sum()
        
        # Calcular porcentaje liquidado
        total_filas = len(df_especialista)
        filas_liquidadas = (df_especialista['Valor Liquidado'] > 0).sum()
        porcentaje_liquidado = round((filas_liquidadas / total_filas) * 100) if total_filas > 0 else 0
        
        resumen_especialistas.append({
            'especialista': especialista,
            'porcentaje_liquidado': porcentaje_liquidado,
            'total_liquidado': total_liquidado,
            'total_liquidado_formateado': f"${total_liquidado:,.0f}" if total_liquidado > 0 else "$0"
        })
        
        total_general += total_liquidado
        suma_porcentajes += porcentaje_liquidado
    
    # Calcular totales generales
    num_especialistas = len(especialistas_unicos)
    porcentaje_promedio = round(suma_porcentajes / num_especialistas) if num_especialistas > 0 else 0
    
    # Ordenar por total liquidado (descendente)
    resumen_especialistas.sort(key=lambda x: x['total_liquidado'], reverse=True)
    
    return {
        'especialistas': resumen_especialistas,
        'totales': {
            'total_liquidado': total_general,
            'total_liquidado_formateado': f"${total_general:,.0f}",
            'porcentaje_promedio': porcentaje_promedio,
            'total_especialistas': num_especialistas
        }
    }

def obtener_resumen_json(df: pd.DataFrame) -> dict:
    """
    Obtiene los totales generales en formato JSON para endpoints.
    """
    resumen = obtener_resumen_general(df)
    return resumen['totales']