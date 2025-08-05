import pymysql
import functools
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort, send_file
from sqlalchemy.sql import text
from sqlalchemy import MetaData, Table, select, insert, delete
from flask_sqlalchemy import SQLAlchemy
import hashlib
import requests
import os
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__, template_folder="templates")

app.secret_key = os.getenv("FLASK_SECRET_KEY")

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
server = os.getenv("DB_SERVER")
dbname = '/' + os.getenv("DB_NAME")

userpass = f"mysql+pymysql://{username}:{password}@"
app.config['SQLALCHEMY_DATABASE_URI'] = userpass + server + dbname


app.config['SQLALCHEMY_DATABASE_URI'] = userpass + server + dbname

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True
}


db = SQLAlchemy(app)
with app.app_context():
    db.reflect()
    student= db.Table("student", db.metadata, autoload_with=db.engine)
    admin = db.Table("admin", db.metadata, autoload_with=db.engine)
    users = db.Table("users", db.metadata,
autoload_with=db.engine)

#db.init_app(app)


def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for("adminLogin"))
        return func(*args, **kwargs)

    return secure_function

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/scanner")
def scanPage():
    return render_template('scanner.html')

@app.route("/adminLogin", methods=['GET', 'POST'])
def adminLogin():
    return render_template('login.html')


@app.route("/about")
def aboutPage():
    return render_template("about.html")

@app.route("/contact")
def contactPage():
    return render_template("contact.html")
    
@app.route("/check", methods = ['POST'])
def checkLogin():
    
    username = request.form['username']
    password = request.form['password']
    admt = select(admin).where(admin.c.username==username, admin.c.password==password)
    account = db.session.execute(admt).fetchone()
    if account:
        session['loggedin'] = True
        session['password'] = account.password
        session['username'] = account.username
        return render_template('Dashboard.html')
    else:
        msg = "Incorrect login details, try again"
    return render_template('login.html', msg =msg);

@app.route("/addUser", methods = ['POST'])
def addUser():
    username = request.form['username']
    password = request.form['password']
    #password_hash = hashlib.sha256(password.encode()).hexdigest()
    stmt = insert(users).values(
    username=username,
    password=password)

    db.session.execute(stmt)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/delUser", methods= ['POST'])
def delUser():
    username = request.form['username']
    password = request.form['password']
    #password_hash = hashlib.sha256(password.encode()).hexdigest()
    stmt = delete(users).where(users.c.username==username, users.c.password==password)
    db.session.execute(stmt)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/delStudent", methods = ["POST"])
def delStudent():
    matnumber = request.form['matnumber']
    stmt = delete(student).where(student.c.MatNumber==matnumber)
    db.session.execute(stmt)
    db.session.commit()
    return redirect(url_for("dashboard"))
    
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('password', None)
    session.pop('username', None)
    return redirect(url_for('index'))
    
@app.route("/retrieveQR")
def regenerate():
    return render_template("retrieve.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("Dashboard.html")

@app.route("/home")
@login_required
def home():
    all_users = db.session.query(users).all()
    all_students = db.session.query(student).all()
    return render_template("home.html", all_users = all_users, all_students=all_students)

@app.route("/userMgt")
@login_required
def userMgt():
    return render_template("userMgt.html")

@app.route("/studMgt")
@login_required
def studMgt():
    return render_template("studMgt.html")



@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()

    raw_result = data['value']
    result = raw_result.replace('.', '$').replace('/', '&')
    
    return jsonify({"redirect_url": f"/{result}"})
 

@app.route('/<id>')
def getData(id):
    stmt = select(student).where(student.c.MatNumber == id.replace('$', '.').replace('&', '/'))
    got_student = db.session.execute(stmt).first()
    if got_student is None:
        abort(404)
        
    return render_template('student.html', got_student = got_student)


@app.route('/sendQR', methods = ['post', 'get'])
def sendQR():
    matnumber = request.form['matnumber']
    new = matnumber.replace('$', '.').replace('&', '/')
    stmt = select(student).where (student.c.MatNumber == matnumber)
    careless_student = db.session.execute(stmt).first()
    if careless_student is None:
        abort(404)
    try:
        response = requests.get(careless_student.StudQr)
        response.raise_for_status()
    except Exception as e:
        return f"Failed to fetch QR image: {e}", 500
    return send_file(BytesIO(response.content),
                     mimetype='image/png',
                     as_attachment = True,
                     download_name = f'{new}_qr.png'
                     )
    
    


if __name__ == '__main__':
    app.run(debug = True)