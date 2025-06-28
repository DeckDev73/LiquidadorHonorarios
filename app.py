from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
from io import BytesIO
import pandas as pd

from logic import workflow_controller as controller

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
        df, nombre = controller.intentar_cargar_estado_previo()
        if df is not None:
            STATE['df'] = df
            STATE['archivo_nombre'] = nombre
            flash(f"🧠 Estado restaurado automáticamente: {nombre}")

    df = STATE['df']
    profesionales = controller.profesionales_con_multiples_especialidades(df) if df is not None else {}
    seleccionadas = STATE.get('especialidades_seleccionadas', {k: v[0] for k, v in profesionales.items()})

    return render_template('main.html',
                           archivo_nombre=STATE['archivo_nombre'],
                           codigos_faltantes=controller.detectar_codigos_pendientes(df) if df is not None else [],
                           profesionales=profesionales,
                           seleccionadas=seleccionadas,
                           resumen=None,
                           df_preview=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['archivo']
    if not file:
        flash("No se seleccionó archivo.")
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    try:
        df = controller.procesar_archivo(path)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

    STATE['df'] = df
    STATE['archivo_nombre'] = filename
    controller.guardar_estado(df)
    flash("✅ Archivo cargado correctamente.")
    return redirect(url_for('index'))

@app.route('/asignar_uvr', methods=['POST'])
def asignar_uvr():
    codigos = request.form.getlist('codigos[]') or []
    valor_uvr = request.form.get('valor_uvr')

    if not codigos:
        flash("❌ Debes seleccionar al menos un código.")
        return redirect(url_for('index'))

    try:
        valor_uvr = float(valor_uvr)
    except (ValueError, TypeError):
        flash("❌ Valor UVR inválido.")
        return redirect(url_for('index'))

    STATE['df'] = controller.procesar_uvr_manual(STATE['df'], codigos, valor_uvr)
    controller.guardar_estado(STATE['df'])
    flash(f"✅ UVR {valor_uvr} asignada a {len(codigos)} código(s).")
    return redirect(url_for('index'))

@app.route('/unificar_especialidades', methods=['POST'])
def aplicar_unificacion_especialidades():
    decisiones = {k.replace("especialidad_", ""): v for k, v in request.form.items() if k.startswith("especialidad_")}
    STATE['df'] = controller.aplicar_unificacion_especialidades(STATE['df'], decisiones)
    STATE['especialidades_seleccionadas'] = decisiones
    controller.guardar_estado(STATE['df'])
    flash("✅ Especialidades unificadas.")
    return redirect(url_for('index'))

@app.route('/tabla_especialista', methods=['GET'])
def obtener_tabla_especialista():
    profesional = request.args.get('profesional')
    especialidad = request.args.get('especialidad')

    if not profesional or not especialidad:
        return "<p>❌ Faltan datos para mostrar la tabla.</p>"

    df_detalle = controller.obtener_tabla_especialista(STATE['df'], profesional, especialidad)
    return render_template('partials/tabla_detalle.html', df=df_detalle)



@app.route('/liquidar', methods=['POST'])
def liquidar():
    profesional = request.form.get('profesional')
    flags = {
        'check_anestesia_diff': 'check_anestesia_diff' in request.form,
        'check_socio': 'check_socio' in request.form,
        'check_reconstruc': 'check_reconstruc' in request.form,
        'check_pie': 'check_pie' in request.form
    }

    STATE['df'] = controller.ejecutar_liquidacion(STATE['df'], flags)
    controller.guardar_estado(STATE['df'])

    df_preview = controller.filtrar_por_profesional(
        STATE['df'],
        profesional,
        STATE['especialidades_seleccionadas'].get(profesional)
    )

    resumen = controller.obtener_resumen(STATE['df'])

    return render_template('main.html',
                           archivo_nombre=STATE['archivo_nombre'],
                           codigos_faltantes=controller.detectar_codigos_pendientes(STATE['df']),
                           profesionales=list(STATE['df']['Especialista'].dropna().unique()),
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
