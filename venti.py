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

def este_formu_vale(bla):
    return True

@app.route('/inscripcion/formulario', methods=['GET', 'POST'])
def formu():
    error = None
    if request.method == 'POST':
        if este_formu_vale(request.form['bla']):
            return render_template('gracias.html')
        else:
            error = "no vale!"

    return render_template('formu.html', error=error)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('ups.html'), 404

if __name__ == '__main__':

    # FIXME PROD remove
    app.debug = True

    app.run()
