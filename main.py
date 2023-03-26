from flask import Flask,session,render_template,request,redirect,jsonify,url_for

import pyrebase
import uuid
from werkzeug.utils import secure_filename

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore,storage
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import auth

app = Flask(__name__)

cred = credentials.Certificate(r'C:\Users\HP\OneDrive\Desktop\web development\DEEPBLUE\EIM-Embbedded Insurance for mobile phone\test-f38d8-firebase-adminsdk-ag3ap-b07d097e8e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
user_doc = db.collection('users').where('email', '==', 'kashoo@gmail.com').limit(1).get()

user_data = user_doc[0].to_dict()
user_data['uid']
print(user_data)

user = auth.get_user_by_email('kashoo@gmail.com')
print(user)



def register_user(email, password):
    user = auth.create_user(
        email=email,
        password=password
    )
    return user

def store_user_data(uid, name, email,password):
    db = firestore.client()
    users_ref = db.collection("users")
    user_data = {
        "uid": uid,
        "name": name,
        "email": email,
        'password':password
    }
    users_ref.add(user_data)

@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        user = register_user(email, password)
        store_user_data(user.uid, name, email,password)
        return "Registration successful"
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_doc = db.collection('users').where('email', '==', email).limit(1).get()
        user_data = user_doc[0].to_dict()
        userr=user_data['uid']
        if userr:
            return render_template('index.html')
        if not userr:
            error_message = 'User not found'
            return render_template('login.html')
   
    else:
        return render_template('login.html') """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email)
        print(password)
        try:
            user = auth.get_user_by_email(email)
            auth.verify_password(password, user.password)
            return render_template('index.html', email=email)
        except :
            return "error"

    return render_template('login.html')
@app.route("/data")
def data():
    return "This is the data page."
if __name__ == "__main__":
    app.run(debug=True)