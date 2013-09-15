# -*- coding: utf-8 -*-
import re

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('inscripcion'))

@app.route('/inscripcion')
def inscripcion():
    return render_template('inscripcion.html')

def este_formu_vale(formu):

    # limpiar entradas

    datos = {
        'titulo-obra': formu['titulo-obra'].strip(),
        'duracion-obra': formu['duracion-obra'].strip(),
        'es-serie-obra': formu.get('es-serie-obra', None) == 'on',
        'nombre-presentante': formu['nombre-presentante'].strip(),
        'correo-presentante': formu['correo-presentante'].strip(),
        'nacionalidad-presentante': formu['nacionalidad-presentante'].strip(),
        'domicilio-presentante': formu['domicilio-presentante'].strip(),
        'telefono-presentante': formu['telefono-presentante'].strip(),
        }

    # checkear entradas

    errores = {}

    if datos['titulo-obra'] == "":
        errores['titulo-obra'] = "Ingrese el titulo de la obra."

    if datos['duracion-obra'] == "":
        errores['duracion-obra'] = "Ingrese una duracion correcta."

    if len(datos['duracion-obra'].split(":")) != 3:
        errores['duracion-obra'] = "Ingrese una duracion correcta, en el formato especificado."

    if datos['nombre-presentante'] == "":
        errores['nombre-presentante'] = "Ingrese el nombre del presentante."

    if datos['correo-presentante'] == "":
        errores['correo-presentante'] = "Ingrese una direccion de correo electronico valida."

    if not re.match(r"[^@]+@[^@]+\.[^@]+", datos['correo-presentante']):
        errores['correo-presentante'] = "Ingrese una direccion de correo electronico valida."

    if datos['nacionalidad-presentante'] == "":
        errores['nacionalidad-presentante'] = "Ingrese la nacionalidad del presentante."

    if datos['domicilio-presentante'] == "":
        errores['domicilio-presentante'] = "Ingrese el domicilio del presentante."

    if datos['telefono-presentante'] == "":
        errores['telefono-presentante'] = "Ingrese el telefono del presentante."

    return datos, errores

@app.route('/inscripcion/formulario', methods=['GET', 'POST'])
def formu():
    datos = {}
    errores = {}
    if request.method == 'POST':
        datos, errores = este_formu_vale(request.form)
        if not errores:
            # FIXME hacer algo con los datos
            return render_template('gracias.html')

    return render_template('formu.html', datos=datos, errores=errores)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('ups.html'), 404

if __name__ == '__main__':

    # FIXME PROD remove
    app.debug = True

    app.run()
