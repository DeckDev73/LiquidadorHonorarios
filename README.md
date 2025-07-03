# LiquidadorHonorarios  
## 🚀 Funcionalidades principales

- Carga de archivo Excel de servicios.
- Homologación automática de códigos SOAT a CUPS.
- Asignación automática de UVR desde:
  - Excel (`tarifas_iss_completo.xlsx`)
  - PDF (`tarifas-iss-2001.pdf`)
- Ingreso manual de UVR cuando no se encuentra automáticamente (replicado en todos los códigos repetidos).
- Liquidación automática por especialista con reglas específicas para:
  - Anestesiología (con modo diferencial)
  - Ortopedia (general, pediátrica, reconstructiva, mano, pie y socio)
  - Neurocirugía
  - Medicina del dolor
  - Medicina física y rehabilitación
  - Medicina laboral
  - Cirugía maxilofacial
- Selección del profesional a liquidar con métricas por valor total y porcentaje.
- Exportación individual a CSV.
- Informe general por especialista descargable en resumen.