from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
from io import BytesIO
import pandas as pd
from logic.cargaArchivo import load_excel_file
from logic.uvr import obtener_codigos_faltantes_uvr, asignar_uvr
from logic.especialidades import obtener_profesionales_y_especialidades
from logic.liquidacion import liquidar_dataframe, actualizar_flag_especialista, eliminar_flag_profesional, cargar_flags_por_profesional
from logic.utils import guardar_estado_como_pickle, cargar_estado_desde_pickle, limpiar_archivos_anteriores
from logic.resumen import obtener_resumen_general, guardar_resumen_como_pickle, cargar_resumen_desde_pickle
from types import SimpleNamespace
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

STATE = {
    'df': None,
    'archivo_nombre': None,
    'especialidades_seleccionadas': {},
}


@app.route('/', methods=['GET'])
def index():
    if STATE['df'] is None:
        df = cargar_estado_desde_pickle()
        if df is not None:
            STATE['df'] = df
            STATE['archivo_nombre'] = 'estado.pkl'
            flash("🧠 Estado restaurado automáticamente: estado.pkl")

    df = STATE['df']
    profesionales = obtener_profesionales_y_especialidades(df) if df is not None else {}
    seleccionadas = {k: v[0] for k, v in profesionales.items()}

    primer_profesional = next(iter(profesionales), "")
    flags_dict = cargar_flags_por_profesional()
    flag_activo = flags_dict.get(primer_profesional, None)

    flags_estado = {
        'check_anestesia_diff': flag_activo == 'check_anestesia_diff',
        'check_socio': flag_activo == 'check_socio',
        'check_reconstruc': flag_activo == 'check_reconstruc',
        'check_pie': flag_activo == 'check_pie'
    }

    return render_template(
        'main.html',
        archivo_nombre=STATE['archivo_nombre'],
        codigos_faltantes=obtener_codigos_faltantes_uvr(df) if df is not None else [],
        profesionales=profesionales,
        seleccionadas=seleccionadas,
        resumen=None,
        df_preview=None,
        flags=SimpleNamespace(**flags_estado)
    )

@app.route('/get_flag', methods=['GET'])
def get_flag():
    profesional = request.args.get('profesional')
    flags_dict = cargar_flags_por_profesional()
    flag_activo = flags_dict.get(profesional, "")

    return jsonify({
        'check_anestesia_diff': flag_activo == 'check_anestesia_diff',
        'check_socio': flag_activo == 'check_socio',
        'check_reconstruc': flag_activo == 'check_reconstruc',
        'check_pie': flag_activo == 'check_pie'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['archivo']
    if not file:
        flash("No se seleccionó archivo.")
        return redirect(url_for('index'))

    limpiar_archivos_anteriores(app.config['UPLOAD_FOLDER'])

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    flash("✅ Archivo cargado correctamente y anteriores eliminados.")
    try:
        df = load_excel_file(path)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

    STATE['df'] = df
    STATE['archivo_nombre'] = filename
    guardar_estado_como_pickle(df)

    flash("✅ Archivo cargado correctamente y anteriores eliminados.")
    return redirect(url_for('index'))

@app.route('/eliminar_repetidos', methods=['POST'])
def eliminar_repetidos():
    df = STATE.get('df')

    if df is None:
        flash("⚠️ No hay datos cargados para limpiar.")
        return redirect(url_for('index'))

    original_shape = df.shape

    # Eliminar filas duplicadas
    df = df.drop_duplicates()

    # Eliminar columnas duplicadas (columnas con los mismos valores en todas las filas)
    df = df.loc[:, ~df.T.duplicated()]

    nueva_shape = df.shape

    STATE['df'] = df
    guardar_estado_como_pickle(df)

    flash(f"🧹 Eliminados duplicados. Dimensiones pasaron de {original_shape} a {nueva_shape}.")
    return redirect(url_for('index'))



@app.route('/asignar_uvr', methods=['POST'])
def asignar_uvr_route():
    codigos = request.form.getlist('codigos[]') or []
    valor_uvr = request.form.get('valor_uvr')

    if not codigos:
        flash("❌ Debes seleccionar al menos un código.")
        return redirect(url_for('index'))

    try:
        valor_uvr = int(valor_uvr)
    except (ValueError, TypeError):
        flash("❌ Valor UVR inválido.")
        return redirect(url_for('index'))

    STATE['df'] = asignar_uvr(STATE['df'], codigos, valor_uvr)
    guardar_estado_como_pickle(STATE['df'])
    flash(f"✅ UVR {valor_uvr} asignada a {len(codigos)} código(s).")
    return redirect(url_for('index'))

@app.route('/uvr_faltantes', methods=['GET'])
def uvr_faltantes():
    df = STATE.get('df')
    codigos = obtener_codigos_faltantes_uvr(df) if df is not None else []
    return render_template('partials/uvr.html', codigos_faltantes=codigos)


@app.route('/guardar_flags_liquidacion', methods=['POST'])
def guardar_flags_liquidacion():
    profesional = request.form.get('profesional')
    flags = ['check_anestesia_diff', 'check_socio', 'check_reconstruc', 'check_pie']
    seleccionados = [f for f in flags if f in request.form]

    if not profesional:
        flash("❌ Falta el nombre del profesional.")
        return redirect(url_for('index'))

    if len(seleccionados) == 0:
        eliminar_flag_profesional(profesional)
        flash(f"⚠️ Sin flag activo. Se aplicará liquidación base para {profesional}.")
    elif len(seleccionados) == 1:
        actualizar_flag_especialista(profesional, seleccionados[0])
        flash(f"✅ Flag '{seleccionados[0]}' asignado a {profesional}")
    else:
        flash("❌ Solo se permite un flag por especialista.")
    return redirect(url_for('index'))



@app.route('/tabla_especialista', methods=['GET'])
def obtener_tabla_especialista():
    profesional = request.args.get('profesional')
    especialidad = request.args.get('especialidad')

    if not profesional or not especialidad:
        return "<p>❌ Faltan datos para mostrar la tabla.</p>"

    df = STATE['df']
    if df is None:
        return "<p>⚠️ No hay datos disponibles.</p>"

    # ✅ Ya no necesitamos pasar flags
    df_liquidado = liquidar_dataframe(df)

    df_filtrado = df_liquidado[
        (df_liquidado['Especialista'] == profesional) &
        (df_liquidado['Especialidad'] == especialidad)
    ]

    if df_filtrado.empty:
        return "<p>⚠️ No hay datos disponibles para este especialista y especialidad.</p>"

    columnas = ["Codigo Homologado", "Especialidad", "Valor UVR", "Valor Liquidado"]
    df_final = df_filtrado[columnas].copy()
    df_final['Codigo Homologado'] = df_final['Codigo Homologado'].astype(str).str.extract(r'(\d+)')
    df_final['Valor UVR'] = df_final['Valor UVR'].apply(lambda x: int(x) if pd.notna(x) and float(x).is_integer() else x)
    df_final['Valor Liquidado'] = df_final['Valor Liquidado'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else '')

    data = df_final.to_dict(orient='records')
    return render_template('partials/tabla_detalle.html', columnas=columnas, data=data)

@app.route('/total_liquidado', methods=['GET'])
def obtener_total_liquidado():
    profesional = request.args.get('profesional')
    especialidad = request.args.get('especialidad')

    if not profesional or not especialidad:
        return {"error": "Faltan parámetros"}, 400

    df = STATE.get('df')
    if df is None:
        return {"error": "No hay datos cargados"}, 404

    # ✅ Sin flags desde request
    df_liquidado = liquidar_dataframe(df)

    df_filtrado = df_liquidado[
        (df_liquidado['Especialista'] == profesional) &
        (df_liquidado['Especialidad'] == especialidad)
    ]

    total = df_filtrado['Valor Liquidado'].sum()
    return {"total_liquidado": total}


# ✅ RUTAS PARA RESUMEN GENERAL (componente)
@app.route('/resumen_data', methods=['GET'])
def resumen_data():
    """Endpoint para obtener datos del resumen como JSON"""
    df = STATE.get('df')
    
    if df is None:
        return jsonify({"error": "No hay datos cargados"}), 404
    
    resumen = obtener_resumen_general(df)
    
    # Guardar en pickle para uso posterior
    guardar_resumen_como_pickle(resumen)
    
    return jsonify(resumen)


@app.route('/descargar', methods=['GET'])
def descargar():
    df = STATE['df']
    if df is None:
        flash("No hay datos para exportar.")
        return redirect(url_for('index'))

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="liquidacion.xlsx")
@app.route('/porcentaje_liquidado', methods=['GET'])
def obtener_porcentaje_liquidado():
    profesional = request.args.get('profesional')
    especialidad = request.args.get('especialidad')

    if not profesional or not especialidad:
        return {"error": "Faltan parámetros"}, 400

    df = STATE.get('df')
    if df is None:
        return {"error": "No hay datos cargados"}, 404

    df_liquidado = liquidar_dataframe(df)

    df_filtrado = df_liquidado[
        (df_liquidado['Especialista'] == profesional) &
        (df_liquidado['Especialidad'] == especialidad)
    ]

    total_filas = len(df_filtrado)
    if total_filas == 0:
        return {"porcentaje_liquidado": 0}

    filas_liquidadas = (df_filtrado['Valor Liquidado'] > 0).sum()
    porcentaje = round((filas_liquidadas / total_filas) * 100)

    return {"porcentaje_liquidado": porcentaje}

if __name__ == '__main__':
    app.run(debug=True)
