# -*- coding: utf-8 -*-
import os
import re
import sqlite3

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import g

from werkzeug import secure_filename

CARPETA_SUBIDOS = '/tmp'
EXTENSIONES_DE_IMAGEN = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

BASE_DE_DATOS = '/tmp/inscriptos.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CARPETA_SUBIDOS

# >>> from venti import init_db
# >>> init_db()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(BASE_DE_DATOS)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
        errores['titulo-obra'] = "Ingresar el titulo de la obra."

    if datos['duracion-obra'] == "":
        errores['duracion-obra'] = "Ingresar una duracion correcta."

    if datos['url-obra'] == "":
        errores['url-obra'] = "Ingresar una URL correcta."

    if datos['imagen-obra-1'] == "":
        errores['imagen-obra-1'] = "Seleccionar un archivo de imagen."

    if not es_archivo_permitido(datos['imagen-obra-1']):
        errores['imagen-obra-1'] = "Seleccionar un archivo de imagen."

    if datos['imagen-obra-2'] == "":
        errores['imagen-obra-2'] = "Seleccionar un archivo de imagen."

    if not es_archivo_permitido(datos['imagen-obra-2']):
        errores['imagen-obra-2'] = "Seleccionar un archivo de imagen."

    if len(datos['duracion-obra'].split(":")) != 3:
        errores['duracion-obra'] = "Ingresar una duracion correcta, en el formato especificado."

    if datos['nombre-presentante'] == "":
        errores['nombre-presentante'] = "Ingresar el nombre del presentante."

    if datos['correo-presentante'] == "":
        errores['correo-presentante'] = "Ingresar una direccion de correo electronico valida."

    if not re.match(r"[^@]+@[^@]+\.[^@]+", datos['correo-presentante']):
        errores['correo-presentante'] = "Ingresar una direccion de correo electronico valida."

    if datos['nacionalidad-presentante'] == "":
        errores['nacionalidad-presentante'] = "Ingresar la nacionalidad del presentante."

    if datos['domicilio-presentante'] == "":
        errores['domicilio-presentante'] = "Ingresar el domicilio del presentante."

    if datos['telefono-presentante'] == "":
        errores['telefono-presentante'] = "Ingresar el telefono del presentante."

    if datos['foto-director'] == "":
        errores['foto-director'] = "Seleccionar un archivo de imagen."

    if not es_archivo_permitido(datos['foto-director']):
        errores['foto-director'] = "Seleccionar un archivo de imagen."

    return datos, errores

@app.route('/inscripcion/formulario', methods=['GET', 'POST'])
def formu():
    datos = {}
    errores = {}
    if request.method == 'POST':
        datos, errores = este_formu_vale(request.form, request.files)
        if not errores:

            # guardar archivos

            subdir = os.path.join(app.config['UPLOAD_FOLDER'],
                                  secure_filename(datos['titulo-obra']))

            if not os.path.exists(subdir):
                os.makedirs(subdir)

            filename_1 = secure_filename(datos['imagen-obra-1'])
            request.files['imagen-obra-1'].save(os.path.join(
                    subdir, filename_1))

            filename_1 = os.path.join(subdir, secure_filename(datos['imagen-obra-1']))
            request.files['imagen-obra-1'].save(filename_1)

            filename_2 = os.path.join(subdir, secure_filename(datos['imagen-obra-2']))
            request.files['imagen-obra-2'].save(filename_2)

            filename_3 = os.path.join(subdir, secure_filename(datos['foto-director']))
            request.files['foto-director'].save(filename_3)

            # guardar en la base de datos

            cur = get_db().cursor()
            cur.execute('insert into inscripciones values (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (None,
                         datos['titulo-obra'],
                         datos['duracion-obra'],
                         datos['es-serie-obra'],
                         filename_1,
                         filename_2,
                         datos['url-obra'],
                         datos['nombre-presentante'],
                         datos['correo-presentante'],
                         datos['nacionalidad-presentante'],
                         datos['domicilio-presentante'],
                         datos['telefono-presentante'],
                         filename_3,
                         ))
            get_db().commit()

            return render_template('gracias.html')

    return render_template('formu.html', datos=datos, errores=errores)

@app.route('/admin')
def admin():
    cur = get_db().cursor()
    cur.execute("select * from inscripciones")
    datos = cur.fetchall()
    return render_template('admin.html', datos=datos)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('ups.html'), 404

if __name__ == '__main__':

    # FIXME PROD remove
    app.debug = True

    app.run()
