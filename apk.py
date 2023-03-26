from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_login import current_user
from flask import Flask,session,render_template,request,redirect,jsonify,url_for
from google.cloud import firestore
from flask import request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore,storage
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import auth
from firebase_admin import db
from flask_admin import Admin,expose
from flask_admin.contrib.pymongo import ModelView
from flask_admin import AdminIndexView
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.secret_key = 'sahil'
bcrypt = Bcrypt(app)

cred = credentials.Certificate(r'C:\Users\HP\OneDrive\Desktop\web development\DEEPBLUE\EIM-Embbedded Insurance for mobile phone\test-f38d8-firebase-adminsdk-ag3ap-0f571452d9.json')
firebase_admin.initialize_app(cred,{
    'projectId':'test-f38d8',
    'storageBucket': 'test-f38d8.appspot.com',
    'databaseURL': 'https://test-f38d8-default-rtdb.firebaseio.com/'
})


dab = firestore.client()
firebase_storage = storage.bucket()



login_manager = LoginManager(app)
login_manager.init_app(app)


class User(UserMixin):
    pass

class Admin(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    user_ref = dab.collection('user').document(user_id).get()
    if not user_ref.exists:
        admin_ref = dab.collection('admin').document(user_id).get()
        if admin_ref.exists:
            admin = Admin()
            admin.id = admin_ref.id
            return admin
        return None

    user = User()
    user.id = user_ref.id
    return user
""" 
@login_manager.user_loader
def load_user(user_id):
    user_ref = dab.collection('user').document(user_id).get()
    if not user_ref.exists:
        return None

    user = User()
    user.id = user_ref.id
    return user

    

@login_manager.user_loader
def load_user(user_id):
    admin_ref = dab.collection('admin').document(user_id).get()
    if admin_ref.exists:
        admin = Admin()
        admin.id = admin_ref.id
        return admin
    return None """

@app.route('/',methods=["POST","GET"])
def home():
    return redirect(url_for('login'))



@app.route('/sign-up',methods=["POST","GET"])
def signup():
    if request.method=='POST':
        email=request.form.get('email')
        
        name=request.form.get('name')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        file = request.files['file']


        if password1 == password2:
            
        # Check if user already exists
            user_ref = dab.collection('user').where('email', '==', email).get()
            if len(user_ref) > 0:
                return {'message': 'User already exists'}, 409

            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')

            filename = f'user_{request.form["name"]}_{file.filename}'
            blob = firebase_storage.blob(filename)
            blob.upload_from_file(file)

             # Get the download URL of the uploaded file
            download_url = blob.public_url
            # Create new user document
            new_user_ref = dab.collection('user').document()
            new_user_ref.set({
                'email': email,
                'password': hashed_password,
                'name':name,
                'file':download_url,
                
            })
            return render_template('login.html')

        else:
            return {'message':'Password not matched'},409


    return render_template('register.html')


@app.route('/login', methods=['POST',"GET"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_ref = dab.collection('user').where('email', '==', email).get()

        if len(user_ref) == 0:
            return {'message': 'User not found'}, 404

        user = user_ref[0].to_dict()
        user_doc = user_ref[0].reference
        message_id = user_doc.id
        message_ref = user_doc.collection('message').get()
        data_ref = user_doc.collection('data').get()
        data = {}
        message_data = {}

        if len(data_ref) > 0:
            data = data_ref[0].to_dict()
            print(data)

        if len(message_ref) > 0:
            message_data = message_ref[0].to_dict()
            print(message_data)

        if not bcrypt.check_password_hash(user['password'], password):
            return {'message': 'Incorrect password'}, 401

        print(email)
        print(password)
        user_obj = User()
        user_obj.id = user_ref[0].id

        login_user(user_obj)
        return render_template('data.html', users=user, message=message_data, data=data)

    return render_template('login.html')


@app.route('/data', methods=['GET','POST'])
@login_required
def data():
    user_ref = dab.collection('user').document(current_user.id)
    user_doc = user_ref[0].reference
    message_id = user_doc.id
    message_ref = user_doc.collection('message').document(message_id)
   
    
    message_data= message_ref.get().to_dict()
    print(message_data)
    user_data = user_ref.get().to_dict()
    
    return render_template('data.html', users=user_data,message=message_data)

    
@app.route('/admin-signup',methods=["GET","POST"])
def adminsignup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
       

        if password1 == password2:
            # Check if admin already exists
            admin_ref = dab.collection('admin').where('email', '==', email).get()
            if len(admin_ref) > 0:
                return {'message': 'Admin already exists'}, 409

            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')

            # Create new admin document
            new_admin_ref = dab.collection('admin').document()
            new_admin_ref.set({
                'email': email,
                'password': hashed_password,
                'name': name,
               
            })

            return render_template('admin-login.html')

        else:
            return {'message': 'Password not matched'}, 409

    return render_template('admin-register.html')

@app.route('/admin-login', methods=["POST","GET"])
def admin_login():
    admin_obj = Admin()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if admin exists
        admin_ref = dab.collection('admin').where('email', '==', email).get()
        if len(admin_ref) == 0:
            return {'message': 'Admin not found'}, 401

        admin_data = admin_ref[0].to_dict()

        # Check if password is correct
        if bcrypt.check_password_hash(admin_data['password'], password):
            session['admin_email'] = email
            admin_obj.id = admin_ref[0].id
            login_user(admin_obj)
            return redirect(url_for('admin_dashboard'))
        else:
            return {'message': 'Invalid password'}, 401

    return render_template('admin-login.html')





@app.route('/send-message', methods=['POST','GET'])
def send_message():
    message = request.json['message']
    email=request.json['email']
    user_ref = dab.collection('user').where('email', '==', email).get()

    user_id=user_ref[0].id
    if len(user_ref) == 1:
        user_doc = user_ref[0].reference
        message_ref = user_doc.collection('message').document()

        message_ref.set({
            'message':message
        }) 
    # Code to send message to user here
    
    return '',204



@app.route('/get-message',methods=["GET","POST"])
def get_message():
    user=current_user
    return redirect(url_for('data'))






@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    admin_ref = dab.collection('admin').document(current_user.id).get()
    
    admin = admin_ref.to_dict()
    # Check if admin is logged in
    if 'admin_email' not in session:
        return redirect('/admin-login')

    # Retrieve all documents from the user collection
    user_ref = dab.collection('user').get()
    users = []
    for user_doc in user_ref:
        user_data = user_doc.to_dict()
        users.append(user_data)

    return render_template('admin-dashboard.html', users=users)


@app.route('/send-data', methods=["POST", "GET"])
@login_required
def send_data():
    email = request.json['email']
    user_ref = dab.collection('user').where('email', '==', email).get()
    user = user_ref[0].to_dict()

    for doc in user_ref:
        # Get the data of the document as a dictionary
        user_data = doc.to_dict()
        print(user_data)

        if len(user_ref) == 1:
            # Get the value of the 'type' field from the user data dictionary
            user_type = user_data.get('type')
            print(user_type)

        ref = db.reference(user_type)

        # Query the data from Realtime Database
        realtime_data = ref.get()
        print(realtime_data)
        merged_data = {}

        for doc in user_ref:
            user_id = doc.id
            merged_data[user_id] = {}
            merged_data[user_id].update(realtime_data.get(user_id, {}))
            merged_data[user_id].update(doc.to_dict())

        user_doc = user_ref[0].reference
        data_ref = user_doc.collection('data').document()

        for user_id in merged_data:
            data_ref.set(realtime_data)


    return jsonify(realtime_data)



@app.route('/showdata', methods=["GET", "POST"])
def showdata():
    if request.method == "POST":
        email = request.form.get('email')
        type = request.form.get('type')
        if not email:
            return "No email provided", 400
        user_ref = dab.collection('user').where('email', '==', email).get()
        for doc in user_ref:
        # Get the data of the document as a dictionary
            user_data = doc.to_dict()
        if len(user_ref) == 1:
            # Get the value of the 'type' field from the user data dictionary
            user_type = user_data.get('type')
            print(user_type)

        ref = db.reference(user_type)

        # Query the data from Realtime Database
        realtime_data = ref.get()
        print(realtime_data)
        if not user_ref:
            return "User not found", 404
        user_doc = user_ref[0].reference
        data_ref = user_doc.collection('data').get()
        data = {}
        if data_ref:
            data = data_ref[0].to_dict()
        return render_template('showdata.html', data=realtime_data)
    else:
        return "Method Not Allowed", 405



""" @app.route('/show')

def show():
    dbe = firestore.client()
    user_type = dbe.collection('user').get('type')
    # Get a reference to the Realtime Database
    ref = db.reference(user_type)

# Query the data from Realtime Database
    realtime_data = ref.get()

# Get a reference to the Firestore database
    

# Query the data from Firestore
    firestore_data = dbe.collection('user').get()
    
# Merge the data from both sources
    merged_data = {}
    for doc in firestore_data:
        user_id = doc.id
        merged_data[user_id] = {}
        merged_data[user_id].update(realtime_data.get(user_id, {}))
        merged_data[user_id].update(doc.to_dict())

    user_ref = dab.collection('user').get()
    user_doc = user_ref[0].reference
    data_ref = user_doc.collection('data').document()

    

# Store the merged data in Firestore
    for user_id in merged_data:
        data_ref.set(
        realtime_data
    )

# Return a success message
    return 'Data merged and stored in Firestore'
    

# Define a route for merging data from both databases
@app.route('/merge-data')
def merge_data():
    # Retrieve data from Realtime Database
    

    realtime_ref = db.reference('Mobile1')
    realtime_data = realtime_ref.get()
    print(realtime_data)
    # Retrieve data from Firestore
    firestore_ref = firestore.client().collection('user')
    firestore_data = {doc.id: doc.to_dict() for doc in firestore_ref.stream()}

    # Merge the data
    merged_data = {}
    for user_id in realtime_data:
        merged_data[user_id] = {}
        merged_data[user_id].update(dict(realtime_data[user_id]))
        merged_data[user_id].update(firestore_data.get(user_id, {}))

    # Return the merged data as a JSON response
    return jsonify(merged_data)

 """



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('admin-login.html')

@app.route('/logout-user')
@login_required
def logoutuser():
    if current_user.is_authenticated:
        logout_user()
    return render_template('login.html')

@app.route('/protected')
@login_required
def protected():
    return {'message': 'This is a protected route'}, 200









if __name__ == "__main__":
    app.run(debug=True)