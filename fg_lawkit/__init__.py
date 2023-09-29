from flask import Flask, render_template, redirect, request, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import pymongo
from bson.objectid import ObjectId
from fg_lawkit.forms import RegistrationForm, LoginForm 
from datetime import datetime, timedelta
from secrets import token_hex



from phonepe.sdk.pg.payments.v1.payment_client import PhonePePaymentClient  
from phonepe.sdk.pg.env import Env

app = Flask(__name__)

# config
app.config['SECRET_KEY'] = ']0~.c{sp~bVHL5f?}dsauf8fyusdKhgs74d{uty78617~:+{8-sCuu8797aWe2s_&gKbZhcsdbe0a7O]*&-Q^|y'



#secure cookies 
app.config['SESSION_COOKIE_SECURE'] = True  # Use secure cookies only over HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Set session lifetime
# Define a key for the quiz session data






server='mongodb+srv://backendfglawkit:zKLvU4MLdBCdLW2W@fglawkit.fd1gndm.mongodb.net/?retryWrites=true&w=majority'

client = pymongo.MongoClient(server)
db = client['FG_lawkit_1_phase']#this is for server

# bcrypt
bcrypt = Bcrypt(app)


#login
login_manager = LoginManager(app)



# user_login
class User(UserMixin):
    def __init__(self, user_id):
        self.user_id = user_id

    def get_id(self):
        return str(self.user_id)

    @staticmethod
    def get(user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_id=user_data['_id'])
        return None




@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

## payemnt integartion
merchant_id = "FGLAWKITONLINE"  
salt_key = "656e9833-180a-4923-9bf8-d3e803aad5bf"  
salt_index = 1  
env = Env.PROD # Change to Env.PROD when you go live
# env = Env.UAT # Change to Env.PROD when you go live
should_publish_events = True  
phonepe_client = PhonePePaymentClient(merchant_id, salt_key, salt_index, env, should_publish_events)




## basic route page ##
# home
@app.route('/')
def index():
    return render_template ('main_home.html')
@app.route('/about')
def about():
    return render_template ('about.html')
@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template ('T&C.html')
@app.route('/privacy_policy')
def privacy_policy():
    return render_template ('privacy_policy.html')


@app.route('/refund_policy')
def refund_policy():
    return render_template ('refund_policy.html')

# rambaan
@app.route('/rambaan_home')
def rambaan_home():
    list_of_rambaan=list(db.rambaan.find())
    return render_template ('rambaan.html',list_of_rambaan=list_of_rambaan)

# rambaan details
@app.route('/rambaan_home/<value>')
def rambaan_details(value):
    details=db.rambaan.find_one({'_id':ObjectId(value)})
    
    return render_template ('rambaan_details.html',details=details)



# blogs
# @app.route('/blog')
# def blog():
#    return render_template ('base.html')

#mocks
@app.route('/mock_home')
def mock_home():
    course_data_from_db = db.mock_home.find()
    course_data = [i for i in course_data_from_db]
    if current_user.is_authenticated:
        id=current_user.user_id
        x=db.users.find_one(id)
        if  x['role']=='admin':
            admin=True
            return render_template ('home.html',admin=admin,course_data=course_data)
    img=list(db.image.find())
   
    return render_template('home.html',course_data=course_data,img=img)

#mocks details
@app.route('/mock_home/<value>')
def mocks_detail(value):
    course_data_from_db = db.mock_home.find_one({'subject_code':value})
    if course_data_from_db:
        return render_template ('mocks_detail.html',course_data_from_db=course_data_from_db,value=value)
    return "no mocks found"

#course page
@app.route('/course')
def course():
    data=db.course_home.find()
    if data:
        return render_template('course.html',data=data)
    return render_template('course.html',data='false')


@app.route('/course/<value>')
def course_details(value):
    data=db.course_home.find_one({'course_code':value})
    if data:
        return render_template('course_details.html',data=data)
    else:
        return render_template('course_details.html',data='false')

import random
@app.route('/register', methods=['GET', 'POST'])
def register():
    collection = db['users']
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.users.find_one({'email': form.email.data}):
            flash('Email already exists!','error')
            
        else:
            date=str(datetime.now()+timedelta(days=30))[0:10]
            if form.options.data == 'male':
                chose_from=['https://i.pinimg.com/750x/03/66/48/036648e8dcfd28ce322fbebbe46dc0ef.jpg',
      'https://i.pinimg.com/750x/b9/53/2b/b9532b8495b9e659a9cf68ffcedca9ac.jpg',
      'https://i.pinimg.com/750x/ee/56/e5/ee56e511664b0585d96bd43c8ebf488d.jpg',
      'https://i.pinimg.com/750x/ff/59/d2/ff59d29930851b69c5601185aa795f1f.jpg']
            else:
                chose_from=['https://i.pinimg.com/750x/92/e3/3c/92e33ccbfa95a3a94d71b4e046005160.jpg',
        'https://i.pinimg.com/750x/af/6c/ba/af6cbafc1665a4247a877c23a39c8fb7.jpg',
        'https://i.pinimg.com/750x/be/dd/32/bedd32ebea0d8b8b4a456fc88c0fe556.jpg',
        'https://i.pinimg.com/750x/7c/4c/4d/7c4c4db4d30d6d886e4ddd98acfe4fff.jpg',]
            
            password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            data = {'email': form.email.data,
                    'password': password_hash,
                    'name': form.firstname.data ,
                    'role': 'Student',
                    'token':None,
                    'mock_purchased': [],
                    'mock_expired':[],
                    'rambaan': {
                                    "status": False,
                                    "exp_date": "2021-07-18"
                                },
                    'Course_purchases':[],
                    'notifications':[],
                    'publications':[],
                    'ip_address': [],
                    'dispute':[],
                    'gender':form.options.data,
                    'profile_image':random.choice(chose_from),
                    'date_of_register':date
                    }
            collection.insert_one(data)
            flash('Registration successful! You can now login.', 'success')
            return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data = db.users.find_one({'email': form.email.data})
        if user_data and bcrypt.check_password_hash(user_data['password'], form.password.data):
            user = User(user_data['_id'])
            token = token_hex(16)  # Generate a 32-character random token
            db.users.update_one({'_id': user.user_id}, {'$set': {'token': token}})
            login_user(user)
                    
            if user_data['role'] == 'admin':
                # return "yes"
                return redirect(url_for("Admin_dashboard.analytics"))####--- this would be change
            if user_data['role'] == 'Student':
                response = redirect(url_for("Student_dashboard.Student_dashboard"))###--- this also change
                response.set_cookie('token', token)
                return response
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/logout')
@login_required
def logout():
    db.users.update_one({'_id': current_user.user_id}, {'$set': {'token': None}})
    logout_user()
    response = redirect(url_for('login'))
    response.delete_cookie('token')  # Remove the token cookie
    return response

#admin#

from fg_lawkit.Admin_dashboard.views import Admin_dashboard_blueprint
app.register_blueprint(Admin_dashboard_blueprint, url_prefix='/Admin_dashboard')

# from fg_lawkit.Admin_blog.views import Admin_blog_blueprint
# app.register_blueprint(Admin_blog_blueprint, url_prefix='/Admin_blog')

from fg_lawkit.Admin_course.views import Admin_course_blueprint
app.register_blueprint(Admin_course_blueprint, url_prefix='/Admin_course')

from fg_lawkit.Admin_mocks.views import Admin_mocks_blueprint
app.register_blueprint(Admin_mocks_blueprint, url_prefix='/Admin_mocks')

# from fg_lawkit.Admin_publication.views import Admin_publication_blueprint
# app.register_blueprint(Admin_publication_blueprint, url_prefix='/Admin_publication')

from fg_lawkit.Admin_rambaan.views import Admin_rambaan_blueprint
app.register_blueprint(Admin_rambaan_blueprint, url_prefix='/Admin_rambaan')

from fg_lawkit.Admin_user.views import Admin_user_blueprint
app.register_blueprint(Admin_user_blueprint, url_prefix='/Admin_user')

#student#
from fg_lawkit.Student_dashboard.views import Student_dashboard_blueprint
app.register_blueprint(Student_dashboard_blueprint, url_prefix='/Student_dashboard')

from fg_lawkit.Student_course.views import Student_course_blueprint
app.register_blueprint(Student_course_blueprint, url_prefix='/Student_course')

from fg_lawkit.Student_mocks.views import Student_mocks_blueprint
app.register_blueprint(Student_mocks_blueprint, url_prefix='/Student_mocks')

# from fg_lawkit.Student_publication.views import Student_publication_blueprint
# app.register_blueprint(Student_publication_blueprint, url_prefix='/Student_publication')

from fg_lawkit.Student_rambaan.views import Student_rambaan_blueprint
app.register_blueprint(Student_rambaan_blueprint, url_prefix='/Student_rambaan')



#reset password
from fg_lawkit.Reset_password.views import Reset_password_blueprint
app.register_blueprint(Reset_password_blueprint, url_prefix='/Reset_password')


