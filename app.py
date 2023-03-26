from flask import Flask,session,render_template,request,redirect
import pyrebase
import uuid
from werkzeug.utils import secure_filename

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore,storage

app=Flask(__name__);

config = {
  "apiKey": "AIzaSyBPlPA4fr0_C5Hp46tbRKG0S-rKXxcW4wY",
  "authDomain": "test-f38d8.firebaseapp.com",
  "projectId": "test-f38d8",
  "storageBucket": "test-f38d8.appspot.com",
  "messagingSenderId": "495554980095",
  "appId": "1:495554980095:web:6720be18811bd0ab7e44ca",
  'databaseURL':'https://test-f38d8-default-rtdb.firebaseio.com/'
}

cred = credentials.Certificate(r'C:\Users\HP\OneDrive\Desktop\web development\DEEPBLUE\EIM-Embbedded Insurance for mobile phone\test-f38d8-firebase-adminsdk-ag3ap-b07d097e8e.json')
firebase_admin.initialize_app(cred,{
     'storageBucket': 'gs://test-f38d8.appspot.com'
})
bucket = storage.bucket()
""" firebase = pyrebase.initialize_app(config)
db=firebase.database()
auth = firebase.auth(); """
db=firestore.client()
""" user_ref = db.collection('users').document('user_id')
user_ref.set({
    'name': 'John Doe',
    'email': 'johndoe@example.com',
    'age': 30
}) """
app.secret_key = 'secret'
""" @app.route('/data',methods=["POST","GET"])
def data():
    
    todo=db.child("names").get()
    to=todo.val()
    return render_template('data.html',t=to.values()) """
@app.route('/', methods=['POST','GET'])
def index():
   
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            
            user = auth.sign_in_with_email_and_password(email, password)
            
            
            session['user'] = email
            return render_template('index.html');
        except:
            return 'Failed to login'
    return render_template('home.html')

""" 
def upload_file():
    file = request.files['file:///C:/Users/HP/Downloads/IRJET_Mental_Health_Chatbot_Psykh.pdf']
    storage_client = storage.Client()
    bucket = storage_client.bucket('test-f38d8')
    filename = secure_filename(file.filename)
    blob = bucket.blob(filename)
    blob.upload_from_string(file.read(), content_type=file.content_type)

    # Make the blob publicly accessible
    blob.make_public()

    # Get the public URL of the file
    url = blob.public_url
    return 'File uploaded successfully. URL: {}'.format(url)

print(upload_file) """

def upload_file_to_storage(file):
    filename = secure_filename(file.filename)
    blob = bucket.blob(filename)
    blob.upload_from_string(
        file.read(),
        content_type=file.content_type
    )
    return filename


def add_user_to_firestore( email, password,file):
    users_id = str(uuid.uuid4())
    filename = upload_file_to_storage(file)
    user_ref = db.collection('users').document(users_id)
    user_ref.set({
       
        'email': email,
        'password':password,
        'file':filename
    })
    return users_id


@app.route('/sign-up',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1 == password2:
            try:
                email = request.form.get('email')
                password = request.form.get('password1')
                file = request.files.get('myfile')
                upload_file_to_storage(file)
                users_id=add_user_to_firestore(email,password,file)
                 
                return render_template('home.html')
            except:
                existing_account = 'This email is already registered'
                
                
    return render_template('register.html')


@app.route('/logout')
def logout():
    
    session.pop('user')
    return redirect('/')

if __name__=='__main__':
    app.run(port=1111)