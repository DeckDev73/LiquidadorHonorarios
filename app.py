from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
from io import BytesIO
import pandas as pd

from logic.cargaArchivo import load_excel_file
from logic.uvr import obtener_codigos_faltantes_uvr, asignar_uvr
from logic.especialidades import obtener_profesionales_y_especialidades
from logic.liquidacion import liquidar_dataframe, generar_resumen_por_profesional

from logic.utils import guardar_estado_como_pickle, cargar_estado_desde_pickle, limpiar_archivos_anteriores

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
            flash(f"🧠 Estado restaurado automáticamente: estado.pkl")

    df = STATE['df']
    profesionales = obtener_profesionales_y_especialidades(df) if df is not None else {}
    seleccionadas = {k: v[0] for k, v in profesionales.items()}

    return render_template('main.html',
                           archivo_nombre=STATE['archivo_nombre'],
                           codigos_faltantes=obtener_codigos_faltantes_uvr(df) if df is not None else [],
                           profesionales=profesionales,
                           seleccionadas=seleccionadas,
                           resumen=None,
                           df_preview=None)

from logic.utils import guardar_estado_como_pickle, cargar_estado_desde_pickle, limpiar_archivos_anteriores

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['archivo']
    if not file:
        flash("No se seleccionó archivo.")
        return redirect(url_for('index'))

    # 🧹 Eliminar archivos y estado anteriores
    limpiar_archivos_anteriores(app.config['UPLOAD_FOLDER'])

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

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

@app.route('/tabla_especialista', methods=['GET'])
def obtener_tabla_especialista():
    profesional = request.args.get('profesional')
    especialidad = request.args.get('especialidad')

    if not profesional or not especialidad:
        return "<p>❌ Faltan datos para mostrar la tabla.</p>"

    df = STATE['df']
    columnas = ["Codigo Homologado", "Especialidad", "Valor UVR", "Valor Total"]

    df_filtrado = df[(df['Especialista'] == profesional) & (df['Especialidad'] == especialidad)]

    if df_filtrado.empty:
        return "<p>⚠️ No hay datos disponibles para este especialista y especialidad.</p>"

    df_final = df_filtrado[columnas].copy()

    # ✅ Formateo
    df_final['Codigo Homologado'] = df_final['Codigo Homologado'].astype(str).str.extract(r'(\d+)')
    df_final['Valor UVR'] = df_final['Valor UVR'].apply(lambda x: int(x) if pd.notna(x) and float(x).is_integer() else x)
    df_final['Valor Total'] = df_final['Valor Total'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else '')

    data = df_final.to_dict(orient='records')

    return render_template('partials/tabla_detalle.html', columnas=columnas, data=data)





@app.route('/liquidar', methods=['POST'])
def liquidar():
    profesional = request.form.get('profesional')
    flags = {
        'check_anestesia_diff': 'check_anestesia_diff' in request.form,
        'check_socio': 'check_socio' in request.form,
        'check_reconstruc': 'check_reconstruc' in request.form,
        'check_pie': 'check_pie' in request.form
    }

    STATE['df'] = liquidar_dataframe(STATE['df'], **flags)
    guardar_estado_como_pickle(STATE['df'])

    df_preview = STATE['df'][(STATE['df']['Especialista'] == profesional)]
    resumen = generar_resumen_por_profesional(STATE['df'])

    return render_template('main.html',
                           archivo_nombre=STATE['archivo_nombre'],
                           codigos_faltantes=obtener_codigos_faltantes_uvr(STATE['df']),
                           profesionales=obtener_profesionales_y_especialidades(STATE['df']),
                           resumen=resumen,
                           df_preview=df_preview)

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

if __name__ == '__main__':
    app.run(debug=True)
