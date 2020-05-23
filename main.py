# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import *
import models as m

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

# clave privada de cifrado de cookies
app.secret_key = "1234"

# This works as a controller in MVC architecture

categorias = ["cooking", "maths", "English", "music", "History"]


@app.before_request
def session_management():
    session.permanent = True


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        m.login_user(email, password)
        return render_template("main_guille.html", categorias=categorias)
    return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    m.logout_user()
    return render_template("main_guille.html", categorias=categorias)


# Falta añadir id de usuario al video y categorizar
@app.route('/upload', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        upload = request.files['upload']
        title = request.form['title']
        category = request.form.get('category')
        m.storage.child(category + "/" + title + ".mp4").put(upload)
        return redirect(url_for('mainpage'))
    return render_template('UploadFile1.html', categorias=categorias)


@app.route('/categoryVideos', methods=['GET', 'POST'])
def categoryVideos():
    category = request.args['cat']
    links = m.storage.child(category + '/test.mp4').get_url(None)  # TODO
    return render_template('CategoryVideos.html', l=links, c=category)


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    """Return a friendly HTTP greeting."""
    return render_template("main_guille.html",
                           categorias=categorias)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        response = m.registerUser(email, password, firstname, lastname)
        # La idea es que response[1] se le pase al html para que salga un alert con JavaScript diciendo el resultado.
        if response[0] is True:
            app.logger.debug('Registro completado correctamente del usuario ' + email)
            flash(response[1])
            return render_template("login.html", response=None)
        else:
            app.logger.debug('Error en el registro: ' + str(response[1]))
            flash(response[1])

    return render_template("register.html", response=None)


if __name__ == '__main__':
    app.logger.debug('Arranque de la aplicacion')
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
