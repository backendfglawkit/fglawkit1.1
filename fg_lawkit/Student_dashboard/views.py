from flask import Blueprint,render_template,redirect,url_for,request,session,flash
from flask_login import logout_user, login_required, current_user
from fg_lawkit import db
from fg_lawkit.Student_mocks.modles import move_expired_mock,check_active_rambaan
from bson import ObjectId

Student_dashboard_blueprint = Blueprint('Student_dashboard',__name__,template_folder='templates/Student_dashboard',static_folder='static')

@Student_dashboard_blueprint.before_request
@login_required
def enforce_single_session():
    global id 
    global x
    global email
    global name
    global profile_pic
    
    
    id=current_user.user_id
    x=db.users.find_one(id)
    email=x['email']
    name=x['name']
    profile_pic=x['profile_image']
    y=check_active_rambaan(db,x['email'])
    if current_user.is_authenticated and not check_active_rambaan(db,x['email']) and x['role']=='Student':
            move_expired_mock(db,x['email'])
            user_data = db.users.find_one({'_id': ObjectId(current_user.user_id)})
            cookie_token = request.cookies.get('token')
            if user_data and user_data.get('token') != cookie_token:
                logout_user()
                flash('You have been logged out due to multiple logins.', 'error')
                return redirect(url_for('login'))
                # abort(404) it is working

@Student_dashboard_blueprint.context_processor
def inject_user():
    user_name = session.get('name', name)  # Default to 'Guest' if the name is not set
    return {'name':name,'profile_pic':profile_pic,'email':email}

@Student_dashboard_blueprint.route('/Student_dashboard')
def Student_dashboard():
        return render_template('main.html')

@Student_dashboard_blueprint.route('/Student_dashboard_payment_issue')
def payment_issue():
    x=db.users.find_one({'email':email})
    data=x['dispute']
    return render_template('payment_dispute.html',data=data)
        
        


   
   