from flask import Blueprint,render_template,redirect,url_for,request,session,flash,abort
from flask_login import logout_user, login_required, current_user
from fg_lawkit.Student_rambaan.modles import check_active_rambaan,move_expired_mock
from fg_lawkit.Student_course.modles import check_read,check_get_content,check_have_course,is_expire_course
from datetime import datetime, timedelta
from bson import ObjectId
from fg_lawkit import db,phonepe_client
import uuid  
from phonepe.sdk.pg.payments.models.request_v1.pg_pay_request import PgPayRequest  
from flask_mail import Mail, Message
from fg_lawkit import app, db
mail = Mail(app)

Student_course_blueprint = Blueprint('Student_course',__name__,template_folder='templates/Student_course')

@Student_course_blueprint.before_request
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
            is_expire_course(db,email)
            user_data = db.users.find_one({'_id': ObjectId(current_user.user_id)})
            cookie_token = request.cookies.get('token')
            if user_data and user_data.get('token') != cookie_token:
                logout_user()
                flash('You have been logged out due to multiple logins.', 'error')
                return redirect(url_for('login'))
            
@Student_course_blueprint.context_processor
def inject_user():
    user_name = session.get('name', name)  # Default to 'Guest' if the name is not set
    return {'name':name,'profile_pic':profile_pic}

            
@Student_course_blueprint.route("/course")
def course():
    data=check_read(email,db)

    # funtion that return a purchase course
    return render_template('course_dash.html',data=data)

@Student_course_blueprint.route("/course/<value>")
def course_view(value):
    check=check_get_content(email,db,value)

    if check:
        data=db.course.find_one({'course_code':value})['content']
        # return data
        return render_template('view_course.html',data=data)
        
    else:
        
        abort(404)


@Student_course_blueprint.route("/course/<value>/buy")
def buy_course(value):
    if check_have_course(db,email,value):
        ## function to make payment
        merchant_transaction_id = str(uuid.uuid4())
        session['pay_id']= merchant_transaction_id
        session['Course_purchases']=value
        course_details=db.course_home.find_one({'course_code':value})
        course_amt=course_details['price']
        session['validation_time']=course_details['validate']
        pay_page_request = PgPayRequest.pay_page_pay_request_builder(merchant_transaction_id=merchant_transaction_id,  
                                                            amount=course_amt*100,  
                                                            merchant_user_id=email,  
                                                            callback_url=url_for('Student_course.course'),  
                                                            redirect_url="https://www.fglawkit.com/Student_course//confirm_buy"
                                                            )

        pay_page_response = phonepe_client.pay(pay_page_request)  
        pay_page_url = pay_page_response.data.instrument_response.redirect_info.url
        return redirect(pay_page_url)
    return redirect (url_for('Student_course.course'))


@Student_course_blueprint.route("/confirm_buy")
def confirm_buy():
    if session.get('pay_id'):
        merchant_transaction_id=session.get('pay_id')
        name=session.get('Course_purchases')
        validation_time=session.get('validation_time')
        response_pg_check_status = phonepe_client.check_status(merchant_transaction_id)
        flag=response_pg_check_status.success ###(fail-false,success and pending - true)
        code=response_pg_check_status.code ###(fail-'PAYMENT_ERROR',success -'PAYMENT_SUCCESS' and pending - PAYMENT_PENDING)

        if  flag== True and  code == 'PAYMENT_SUCCESS' :
            exp_day = str((datetime.now() + timedelta(days=validation_time)).strftime('%Y-%m-%d'))
            update_result = db.users.update_one({"email": email},{"$push": {"Course_purchases": {'name':name,'exp_date':exp_day}}})
            msg_body = f"Payment Successful, Your Purchase Course -{name} . Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. if any issue you can mail us at fglawkit@gmail.com. Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')}"
            msg = Message('PAYMENT Successful', sender='backendfglawkit@gmail.com ', recipients=[email])
            msg.body = msg_body
            mail.send(msg)
            session.pop('pay_id')
            session.pop('Course_purchases')
            session.pop('validation_time')
            return redirect (url_for('Student_course.course'))
        elif flag== True and  code == 'PAYMENT_PENDING':
            db.users.update_one({'email':email},{'$push':{'dispute':[code,merchant_transaction_id,'course',name]}})
            db.money_dispute.insert_one({'email':email,'dispute':[code,merchant_transaction_id,'course',name],'date':str(datetime.now())})
            msg_body = f"Payment Pending, Your Try yo Purchase Course -{name} . Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}.Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')} if any issue you can mail us at fglawkit@gmail.com."
            msg = Message('PAYMENT PENDING', sender='backendfglawkit@gmail.com ', recipients=[email])
            msg.body = msg_body
            mail.send(msg)

            session.pop('pay_id')
            session.pop('Course_purchases')
            session.pop('validation_time')
            return redirect (url_for('Student_dashboard.Student_dashboard'))
        else:
            msg_body = f"Payment Fail, Your Try yo Purchase Course -{name} . Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}.Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')} if any issue you can mail us at fglawkit@gmail.com."
            msg = Message('PAYMENT FAIL', sender='backendfglawkit@gmail.com ', recipients=[email])
            msg.body = msg_body
            mail.send(msg)
            session.pop('pay_id')
            session.pop('Course_purchases')
            session.pop('validation_time')
            return redirect (url_for('Student_course.course'))
    return redirect (url_for('Student_course.course'))
