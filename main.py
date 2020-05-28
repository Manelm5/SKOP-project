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
import generateVideoSubtitles as subs
import base64
import requests
import os

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

# clave privada de cifrado de cookies
app.secret_key = "1234"

# This works as a controller in MVC architecture


class Category:
    def __init__(self, name, image):
        self.name = name
        self.image = image

categorias = ["Cooking", "Maths", "Sport", "Music", "History"]

categorias = [Category("Cooking","../static/img/cocina.jpg"), Category("Maths","../static/img/maths.jpg"),
              Category("Sport","../static/img/gym.jpg"), Category("Music","../static/img/musica.jpg"),
              Category("History","../static/img/history.png")]


@app.before_request
def session_management():
    session.permanent = True


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session["userId"] = m.login_user(email, password)
        session["email"] = request.form['email']
        return render_template("main_guille.html", categorias=categorias, user=session["userId"], email=session["email"])
    return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    m.logout_user()
    return render_template("main_guille.html", categorias=categorias)


# Falta añadir id de usuario al video y categorizar
@app.route('/upload', methods=['GET', 'POST'])
def uploadFile():
    copyIndex = 0
    if request.method == 'POST':
        upload = request.files['upload']
        category = request.form.get('category')
        title = request.form['title']

        if isRepeatedName(title):
            while isRepeatedName(title + str(copyIndex)):
                copyIndex = int(copyIndex) + 1

            title = title + " (" + str(copyIndex) + ")"

        path = category + "/" + title + ".mp4"
        m.storage.child(path).put(upload)
        link = str(m.storage.child(category + "/" + title + ".mp4").get_url(None))

        captions = subs.generateSubtitles(link, path, title)

        data = {
            u'userId': session["userId"],
            u'link': link,
            u'subsBase64': captions,
            u'title': title,
            u'category': category
        }

        m.db.collection(u'videos').document().set(data)
        return redirect(url_for('mainpage'))

    return render_template('UploadFile1.html', categorias=categorias)


@app.route('/categoryVideos', methods=['GET', 'POST'])
def categoryVideos():
    category = request.args['cat']
    category_videos = m.get_videos_by_category(category)
    link = category_videos
    return render_template('CategoryVideos.html', l=link, c=category)

@app.route('/myVideos', methods=['GET', 'POST'])
def myVideos():
    userId = session["userId"]
    userVideos = m.get_videos_by_userId(userId)


    if request.method == 'POST':
        link = request.form['deleteVideo']
        m.deleteVideoFromUrl(link)
        print("done")
        return redirect(url_for('myVideos'))

    return render_template('myVideos.html', l=userVideos)


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


def isRepeatedName(name):
    a = m.storage.child('').list_files()
    names = list()
    for b in a:
        names.append(b.name.split('/')[1].split('.')[0])

    if (name in names):
        return True
    else:
        return False


if __name__ == '__main__':
    app.logger.debug('Arranque de la aplicacion')
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    #subs.generateSubtitles("cooking/test.mp4")
    app.run(host='127.0.0.1', port=8080, debug=True)

# [END gae_python37_app]
