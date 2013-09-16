# -*- coding: utf-8 -*-
import os
import re

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from werkzeug import secure_filename

CARPETA_SUBIDOS = '/tmp'
EXTENSIONES_DE_IMAGEN = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CARPETA_SUBIDOS

@app.route('/')
def index():
    return redirect(url_for('inscripcion'))

@app.route('/inscripcion')
def inscripcion():
    return render_template('inscripcion.html')

def es_archivo_permitido(nombre_archivo):
    return '.' in nombre_archivo and \
        nombre_archivo.rsplit('.', 1)[1] in EXTENSIONES_DE_IMAGEN

def este_formu_vale(formu, archivos):

    # limpiar entradas

    datos = {
        'titulo-obra': formu['titulo-obra'].strip(),
        'duracion-obra': formu['duracion-obra'].strip(),
        'es-serie-obra': formu.get('es-serie-obra', None) == 'on',
        'url-obra': formu['url-obra'].strip(),
        'nombre-presentante': formu['nombre-presentante'].strip(),
        'correo-presentante': formu['correo-presentante'].strip(),
        'nacionalidad-presentante': formu['nacionalidad-presentante'].strip(),
        'domicilio-presentante': formu['domicilio-presentante'].strip(),
        'telefono-presentante': formu['telefono-presentante'].strip(),
        }

    imagen_obra_1 = archivos.get('imagen-obra-1', None)
    if imagen_obra_1 is None:
        datos['imagen-obra-1'] = ''
    else:
        datos['imagen-obra-1'] = imagen_obra_1.filename

    imagen_obra_2 = archivos.get('imagen-obra-2', None)
    if imagen_obra_2 is None:
        datos['imagen-obra-2'] = ''
    else:
        datos['imagen-obra-2'] = imagen_obra_2.filename

    foto_director = archivos.get('foto-director', None)
    if foto_director is None:
        datos['foto-director'] = ''
    else:
        datos['foto-director'] = foto_director.filename

    # checkear entradas

    errores = {}

    if datos['titulo-obra'] == "":
        errores['titulo-obra'] = "Ingrese el titulo de la obra."

    if datos['duracion-obra'] == "":
        errores['duracion-obra'] = "Ingrese una duracion correcta."

    if datos['url-obra'] == "":
        errores['url-obra'] = "Ingrese una URL correcta."

    if datos['imagen-obra-1'] == "":
        errores['imagen-obra-1'] = "Seleccione un archivo de imagen."

    if not es_archivo_permitido(datos['imagen-obra-1']):
        errores['imagen-obra-1'] = "Seleccione un archivo de imagen."

    if datos['imagen-obra-2'] == "":
        errores['imagen-obra-2'] = "Seleccione un archivo de imagen."

    if not es_archivo_permitido(datos['imagen-obra-2']):
        errores['imagen-obra-2'] = "Seleccione un archivo de imagen."

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

    if datos['foto-director'] == "":
        errores['foto-director'] = "Seleccione un archivo de imagen."

    if not es_archivo_permitido(datos['foto-director']):
        errores['foto-director'] = "Seleccione un archivo de imagen."

    return datos, errores

@app.route('/inscripcion/formulario', methods=['GET', 'POST'])
def formu():
    datos = {}
    errores = {}
    if request.method == 'POST':
        datos, errores = este_formu_vale(request.form, request.files)
        if not errores:

            # FIXME hacer algo con los datos

            # guardar archivos

            subdir = os.path.join(app.config['UPLOAD_FOLDER'],
                                  secure_filename(datos['titulo-obra']))

            if not os.path.exists(subdir):
                os.makedirs(subdir)

            filename_1 = secure_filename(datos['imagen-obra-1'])
            request.files['imagen-obra-1'].save(os.path.join(
                    subdir, filename_1))

            filename_2 = secure_filename(datos['imagen-obra-2'])
            request.files['imagen-obra-2'].save(os.path.join(
                    subdir, filename_2))

            filename_3 = secure_filename(datos['foto-director'])
            request.files['foto-director'].save(os.path.join(
                    subdir, filename_3))

            return render_template('gracias.html')

    return render_template('formu.html', datos=datos, errores=errores)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('ups.html'), 404

if __name__ == '__main__':

    # FIXME PROD remove
    app.debug = True

    app.run()
