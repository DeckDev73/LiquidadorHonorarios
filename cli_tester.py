import pandas as pd
from logic import workflow_controller as controller

EXCEL_PATH = "uploads/archivo_prueba.xlsx"

print("=== Liquidador CLI ===")

# Cargar Excel
print("📥 Cargando archivo...")
df = controller.procesar_archivo(EXCEL_PATH)
print(f"✅ Archivo cargado con {len(df)} registros")

# Detectar códigos sin UVR
print("\n🔍 Códigos sin UVR asignada:")
faltantes = controller.detectar_codigos_pendientes(df)
print(faltantes)

# Asignar UVR
if faltantes:
    print("\n✏️ Asignando UVR=1000 a los 3 primeros códigos faltantes...")
    df = controller.procesar_uvr_manual(df, codigos=faltantes[:3], valor_uvr=1000)

# Unificación de especialidades
print("\n🔀 Unificando especialidades (ficticio)...")
decisiones = {"GALLEGO DUQUE JORGE ALEJANDRO ": "ANESTESIOLOGIA"}
df = controller.aplicar_unificacion(df, decisiones)

# Liquidación
print("\n💸 Liquidando datos con flags: socio=True, pie=False, anestesia=False...")
flags = {
    'check_anestesia_diff': False,
    'check_socio': True,
    'check_reconstruc': False,
    'check_pie': False
}
df = controller.ejecutar_liquidacion(df, flags)

# Ver liquidación de un profesional específico
print("\n📌 Filtrando liquidación por: GALLEGO DUQUE JORGE ALEJANDRO ")
preview = controller.filtrar_por_profesional(df, "GALLEGO DUQUE JORGE ALEJANDRO ")
print(preview[['Especialidad', 'Codigo Homologado', 'Valor UVR', 'Valor Liquidado']].head())

# Resumen final
print("\n📈 Resumen por profesional:")
resumen = controller.obtener_resumen(df)
print(resumen)

# Guardar resultado en archivo temporal
df.to_excel("uploads/salida_test.xlsx", index=False)
print("\n📁 Resultado guardado como: uploads/salida_test.xlsx")
