# -*- coding: utf-8 -*-
import os
import re
import sqlite3

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import send_from_directory
from flask import g
from flask.ext.login import LoginManager
from flask.ext.login import UserMixin
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import current_user

from werkzeug import secure_filename

CARPETA_SUBIDOS = os.path.join(os.path.dirname(__file__), 'media')
EXTENSIONES_DE_IMAGEN = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

# FIXME PROD cambiar
URL_SUBIDOS = "http://0.0.0.0:8000/"

BASE_DE_DATOS = os.path.join(os.path.dirname(__file__), 'inscriptos.db')

PRODUCCION = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CARPETA_SUBIDOS

# FIXME PROD cambiar
# >>> import os
# >>> os.urandom(24)
app.secret_key = "unodostres"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "entrar"

class WebFactionMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = '/el-ventilador'
        return self.app(environ, start_response)

# FIXME solo si el deploy no se hace es un root domain
# if PRODUCCION:
#     app.wsgi_app = WebFactionMiddleware(app.wsgi_app)

class Usuario(UserMixin):
    def __init__(self, id_usuario):
        UserMixin.__init__(self)
        self.id = id_usuario

    def get_id(self):
        return self.id

usuario_admin = Usuario(u'admin')

@login_manager.user_loader
def cargar_usuario(id_usuario):
    return usuario_admin

def se_autoriza(formu):
    # FIXME PROD cambiar
    return formu['username'].strip() == 'admin'

@app.route("/admin/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == 'POST':
        if se_autoriza(request.form):
            # login and validate the user...
            login_user(usuario_admin)
            return redirect(request.args.get("next") or url_for("admin"))

    return render_template("entrar.html", usuario=current_user)

@app.route("/admin/salir")
@login_required
def salir():
    logout_user()
    return redirect(url_for('index'))

# FIXME PROD generar
# >>> from ventilador_web import init_db
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
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return redirect(url_for('inscripcion'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'venti'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
        'sinopsis-obra': formu['sinopsis-obra'].strip(),
        'pais-obra': formu['pais-obra'].strip(),
        'es-serie-obra': formu.get('es-serie-obra', None) == 'on',
        'url-obra': formu['url-obra'].strip(),
        'nombre-presentante': formu['nombre-presentante'].strip(),
        'nacionalidad-presentante': formu['nacionalidad-presentante'].strip(),
        'correo-presentante': formu['correo-presentante'].strip(),
        'domicilio-presentante': formu['domicilio-presentante'].strip(),
        'web-presentante': formu['web-presentante'].strip(),
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
        errores['titulo-obra'] = u"Ingresar el título de la obra."

    if datos['duracion-obra'] == "":
        errores['duracion-obra'] = u"Ingresar una duración correcta."

    if datos['sinopsis-obra'] == "":
        errores['sinopsis-obra'] = u"Ingresar la sinopsis de la obra."

    if datos['pais-obra'] == "":
        errores['pais-obra'] = u"Ingresar el país de origen de la obra."

    if len(datos['duracion-obra'].split(":")) != 3:
        errores['duracion-obra'] = u"Ingresar una duración correcta, en el formato especificado."

    if datos['imagen-obra-1'] == "":
        errores['imagen-obra-1'] = u"Seleccionar un archivo de imagen."

    if not es_archivo_permitido(datos['imagen-obra-1']):
        errores['imagen-obra-1'] = u"Seleccionar un archivo de imagen."

    if datos['imagen-obra-2'] == "":
        errores['imagen-obra-2'] = u"Seleccionar un archivo de imagen."

    if not es_archivo_permitido(datos['imagen-obra-2']):
        errores['imagen-obra-2'] = u"Seleccionar un archivo de imagen."

    if datos['nombre-presentante'] == "":
        errores['nombre-presentante'] = u"Ingresar el nombre del presentante."

    if datos['correo-presentante'] == "":
        errores['correo-presentante'] = u"Ingresar una dirección de correo electrónico válida."

    if not re.match(r"[^@]+@[^@]+\.[^@]+", datos['correo-presentante']):
        errores['correo-presentante'] = u"Ingresar una dirección de correo electrónico válida."

    if datos['nacionalidad-presentante'] == "":
        errores['nacionalidad-presentante'] = u"Ingresar la nacionalidad del presentante."

    if datos['domicilio-presentante'] == "":
        errores['domicilio-presentante'] = u"Ingresar el domicilio del presentante."

    if datos['telefono-presentante'] == "":
        errores['telefono-presentante'] = "Ingresar el telefono del presentante."

    if datos['foto-director'] == "":
        errores['foto-director'] = u"Seleccionar un archivo de imagen."

    if not es_archivo_permitido(datos['foto-director']):
        errores['foto-director'] = u"Seleccionar un archivo de imagen."

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

            filename_1 = os.path.join(subdir, secure_filename(datos['imagen-obra-1']))
            request.files['imagen-obra-1'].save(filename_1)

            url_1 = os.path.join(secure_filename(datos['titulo-obra']),
                                 secure_filename(datos['imagen-obra-1']))

            filename_2 = os.path.join(subdir, secure_filename(datos['imagen-obra-2']))
            request.files['imagen-obra-2'].save(filename_2)

            url_2 = os.path.join(secure_filename(datos['titulo-obra']),
                                 secure_filename(datos['imagen-obra-2']))

            filename_3 = os.path.join(subdir, secure_filename(datos['foto-director']))
            request.files['foto-director'].save(filename_3)

            url_3 = os.path.join(secure_filename(datos['titulo-obra']),
                                 secure_filename(datos['foto-director']))

            # guardar en la base de datos

            cur = get_db().cursor()
            cur.execute('insert into inscripciones values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (None,
                         datos['titulo-obra'],
                         datos['duracion-obra'],
                         datos['sinopsis-obra'],
                         datos['pais-obra'],
                         datos['es-serie-obra'],
                         url_1,
                         url_2,
                         datos['url-obra'],
                         datos['nombre-presentante'],
                         datos['nacionalidad-presentante'],
                         datos['correo-presentante'],
                         datos['domicilio-presentante'],
                         datos['web-presentante'],
                         datos['telefono-presentante'],
                         url_3,
                         ))
            get_db().commit()

            return render_template('gracias.html')

    return render_template('formu.html', datos=datos, errores=errores)

@app.route('/admin')
@login_required
def admin():
    cur = get_db().cursor()
    cur.execute("select * from inscripciones")
    datos = cur.fetchall()
    return render_template('admin.html', datos=datos, usuario=current_user,
                           URL_SUBIDOS=URL_SUBIDOS)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('ups.html'), 404

if __name__ == '__main__':

    if not PRODUCCION:
        app.debug = True

    app.run()
