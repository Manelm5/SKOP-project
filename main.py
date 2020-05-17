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

# This works as a controller in MVC architecture

categorias = ["cooking", "maths", "English", "music", "History"]


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Return a friendly HTTP greeting."""
    return render_template("login.html")

@app.route('/register')
def register():
    """Return a friendly HTTP greeting."""
    return render_template("register.html")


#Falta añadir id de usuario al video y categorizar
@app.route('/upload', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        upload = request.files['upload']
        title = request.form['title']
        category = request.form.get('category')
        m.storage.child(category + "/" + title + ".mp4").put(upload)
        return redirect(url_for('mainpage'))
    return render_template('UploadFile1.html', categorias = categorias)


@app.route('/categoryVideos', methods=['GET', 'POST'])
def categoryVideos():
    category = request.args['cat']
    links = m.storage.child( category + '/test.mp4').get_url(None) #TODO
    return render_template('CategoryVideos.html', l=links, c = category)


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    app.logger.debug('Arranque de la aplicacion')

    """Return a friendly HTTP greeting."""
    return render_template("main_guille.html", categorias=categorias) # Aqui colocar o la nuestra o la tuya Guille, como quieras



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
