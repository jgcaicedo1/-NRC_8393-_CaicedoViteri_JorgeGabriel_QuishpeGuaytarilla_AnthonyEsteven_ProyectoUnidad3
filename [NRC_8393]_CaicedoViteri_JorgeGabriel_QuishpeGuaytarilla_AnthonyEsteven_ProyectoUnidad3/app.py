from __future__ import print_function
from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin
import logging
import os
import oracledb
from waitress import serve
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from flask import render_template, request, redirect, url_for, flash

os.environ["PYTHON_USERNAME"] = "jcaicedo"
os.environ["PYTHON_PASSWORD"] = "Oracle97190"
os.environ["PYTHON_CONNECTSTRING"] = "localhost:1522/DBParvulos"

app = Flask(__name__)
app.secret_key = '123Parvulos'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app)
cors = CORS(app, resources={
            r"/api/*": {"origins": "*", "methods": "POST,DELETE,PUT,GET,OPTIONS"}})


def start_pool():

    pool_min = 4
    pool_max = 4
    pool_inc = 0

    print("Connecting to", os.environ.get("PYTHON_CONNECTSTRING"))

    pool = oracledb.create_pool(
        user=os.environ.get("PYTHON_USERNAME"),
        password=os.environ.get("PYTHON_PASSWORD"),
        dsn=os.environ.get("PYTHON_CONNECTSTRING"),
        min=pool_min,
        max=pool_max,
        increment=pool_inc
    )

    return pool


def create_schema():
    with pool.acquire() as connection:
        with connection.cursor() as cursor:

            try:
                cursor.execute(
                    """
                    select * from "TB_ROL"
                    """
                )
            except oracledb.Error as err:
                error_obj, = err.args
                print(f"Conexión no extiosa: {error_obj.message}")


pool = start_pool()

create_schema()

@app.route('/login')
def index():
    if current_user.is_authenticated:
        return redirect(url_for("/"))
    return render_template('index.html')

#ADMIN
    
@app.route('/', methods=['GET', 'POST'])
def login():

    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            try:
                msg = ''
                if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
                    username = request.form['username']
                    password = request.form['password']
                    cursor.execute(""" SELECT * FROM "TB_USUARIO" WHERE "STR_NOMBRE_USUARIO" = :usuario AND "STR_PASSWORD_USUARIO" = :contra """,usuario=username, contra=password)
                    account = cursor.fetchone()

                    if account:
                        session['loggedin'] = True
                        return redirect(url_for("home"))
                    else:
                        msg = 'Usuario o contraseña incorrecta!'
            except oracledb.Error as err:
                error_obj, = err.args
                print(f"Conexión no extiosa: {error_obj.message}")
    return render_template('index.html', msg=msg)

@app.route('/home/')
def home():
    if 'loggedin' in session:
        return render_template('home.html')   
    return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   return redirect(url_for('login'))

@app.route('/admin/')
def admin():
    id = current_user.get_id()
    return render_template('admin.html')


@app.route("/query")
def query():
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    '''
                    SELECT * FROM  "TB_USUARIO"
                    ''')
                resultado = cursor.fetchall()
            except oracledb.Error as err:
                error_obj, = err.args
                print(f"Conexión no exitosa: {error_obj.message}")
    return render_template('query.html', resultado=resultado)


@login_manager.user_loader
def load_user(user_id):
    return model.usuarios.objects.get(usuario_id=user_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '8080'))