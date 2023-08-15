from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_login import current_user
from flask import Flask,session,render_template,request,redirect,jsonify,url_for,render_template_string
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
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'embeddedinsurance@gmail.com'
app.config['MAIL_PASSWORD'] = 'wbqmsgclyhsdygqj'
app.secret_key = 'sahil'
bcrypt = Bcrypt(app)
mail = Mail(app)
cred = credentials.Certificate(r'C:\Users\HP\OneDrive\Desktop\web development\DEEPBLUE\EIM-Embbedded Insurance for mobile phone\insurance-claimer-36ec2-firebase-adminsdk-bwg6f-473f77c3cb.json')
firebase_admin.initialize_app(cred,{
    'projectId':'insurance-claimer-36ec2',
    'storageBucket': 'insurance-claimer-36ec2.appspot.com',
    'databaseURL': 'https://insurance-claimer-36ec2-default-rtdb.firebaseio.com/'
}) 

rf=db.reference('Mobile1') 




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


@app.route('/',methods=["POST","GET"])
def home():
    return render_template('home.html')



@app.route('/sign-up',methods=["POST","GET"])
def signup():
    if request.method=='POST':
        email=request.form.get('email')
        
        name=request.form.get('name')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        address=request.form.get('address')
        type=request.form.get('type')
        policynumber=request.form.get('policynumber')
        phoneno=request.form.get('phoneno')
        company=request.form.get('company')

        


        if password1 == password2:
            
        # Check if user already exists
            user_ref = dab.collection('user').where('email', '==', email).get()
            user_policy = dab.collection('user').where('policynumber', '==',policynumber).get()
            if len(user_ref) > 0:
                error_message = 'User already exists'
                return render_template('register.html', error_message=error_message), 404
            
            if len(user_policy) > 0:
                error_message = 'Policy Number Already exists'
                return render_template('register.html',error_message=error_message),404
            
            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')

            
            new_user_ref = dab.collection('user').document()
            new_user_ref.set({
                'email': email,
                'password': hashed_password,
                'name':name,
                'address':address,
                'type':type,
                'phoneno':phoneno,
                'policynumber':policynumber, 
                'company':company,
                'amount':1440              
            })

            ref = db.reference(type)
            realtime_data = ref.get()
            if realtime_data['Backside'] or realtime_data['Bottomleftcorner'] or realtime_data['Bottomrightcorner'] or realtime_data['Topleftcorner'] or realtime_data['Toprightcorner'] > 11:
                subject = 'Your Phone is broken'
                body = 'Dear ' + new_user_ref.get().to_dict()['name'] +' ,\n\nWe are sorry to hear that your phone is broken. To manage your account with us, please log in to our website at http://127.0.0.1:5000/. Our website is mobile-friendly and can be accessed from any web browser.\n\nThank you for choosing our company for your insurance needs.\n\nBest regards,\n\nCOVERWELL .'
                send_email(email, subject, body)

            return render_template('login.html')

        else:
            error_message = 'Password not matched'
            return render_template('register.html', error_message=error_message), 404


    return render_template('register.html')


@app.route('/login', methods=['POST',"GET"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_ref = dab.collection('user').where('email', '==', email).get()

        if len(user_ref) == 0:
            error_message = 'User not found'
            return render_template('login.html', error_message=error_message), 404

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
            error_message = 'Incorrect Password'
            return render_template('login.html', error_message=error_message), 401

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
        print(email)
        print(password)
        user_obj = User()
        user_obj.id = user_ref[0].id
        if realtime_data['Backside'] or realtime_data['Bottomleftcorner'] or realtime_data['Bottomrightcorner'] or realtime_data['Topleftcorner'] or realtime_data['Toprightcorner'] > 11:
            subject = 'Your Phone is broken'
            body = 'Dear ' + user['name'] + ' ,\n\nWe are sorry to hear that your phone is broken. To manage your account with us, please log in to our website at http://127.0.0.1:5000/. Our website is mobile-friendly and can be accessed from any web browser.\n\nThank you for choosing our company for your insurance needs.\n\nBest regards,\n\nCOVERWELL .'
            send_email(email, subject, body)
        login_user(user_obj)
        return render_template('data.html', users=user, message=message_data, data=data,realtime_data=realtime_data)

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
        phoneno=request.form.get('phoneno')

        if password1 == password2:
            # Check if admin already exists
            admin_ref = dab.collection('admin').where('email', '==', email).get()
            if len(admin_ref) > 0:
                error_message = 'Admin Already exists'
                return render_template('admin-register.html', error_message=error_message), 401

            hashed_password = bcrypt.generate_password_hash(password1).decode('utf-8')

            # Create new admin document
            new_admin_ref = dab.collection('admin').document()
            new_admin_ref.set({
                'email': email,
                'password': hashed_password,
                'name': name,
                'phoneno':phoneno,
            })

            return render_template('admin-login.html')

        else:
            error_message = 'Password not matched'
            return render_template('admin-register.html', error_message=error_message), 409
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
            error_message = 'Company not found'
            return render_template('admin-login.html', error_message=error_message), 401

        admin_data = admin_ref[0].to_dict()

        # Check if password is correct
        if bcrypt.check_password_hash(admin_data['password'], password):
            session['admin_email'] = email
            admin_obj.id = admin_ref[0].id
            login_user(admin_obj)
            return redirect(url_for('admin_dashboard'))
        else:
            error_message = 'Invalid password'
            return render_template('admin-login.html', error_message=error_message), 401

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
        if user_data.get('company') == admin['name']:
            users.append(user_data)
        

    for user in users:
        user_type = user["type"]
        print(user_type)
    
    # Construct the reference path based on the user type
        ref_path = f"/{user_type}"  # replace with the correct path

     # Get the reference to the database node
        ref = db.reference(ref_path)

    # Query the data from Realtime Database
        realtime_data = ref.get()

        print(realtime_data)
    
    yesalert="yes"
    noalert="no"
    

    
    return render_template('admin-dashboard.html', users=users,realtime_data=realtime_data,yes=yesalert,no=noalert,admin=admin)


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
        user = user_ref[0].to_dict()
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
        if realtime_data['Backside'] or realtime_data['Bottomleftcorner'] or realtime_data['Bottomrightcorner'] or realtime_data['Topleftcorner'] or realtime_data['Toprightcorner'] > 11:
                subject = 'Your Phone is broken'
                body = 'Dear ' + user['name'] + ' ,\n\nWe are sorry to hear that your phone is broken. To manage your account with us, please log in to our website at http://127.0.0.1:5000/. Our website is mobile-friendly and can be accessed from any web browser.\n\nThank you for choosing our company for your insurance needs.\n\nBest regards,\n\nCOVERWELL .'
                send_email(email, subject, body)

        if not user_ref:
            return "User not found", 404
        user_doc = user_ref[0].reference
        amount_ref = user_doc.collection('amount').get()
        amount = {}
        if amount_ref:
            amount = amount_ref[0].to_dict()
        return render_template('showdata.html', data=realtime_data,user=user)
    else:
        return "Method Not Allowed", 405





def send_email(recipient, subject, body):
    msg = Message(subject=subject, recipients=[recipient], body=body, sender='embeddedinsurance@gmail.com')
    mail.send(msg)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('home.html')

@app.route('/logout-user')
@login_required
def logoutuser():
    if current_user.is_authenticated:
        logout_user()
    return render_template('home.html')

@app.route('/protected')
@login_required
def protected():
    return {'message': 'This is a protected route'}, 200









if __name__ == "__main__":
    app.run(debug=True)