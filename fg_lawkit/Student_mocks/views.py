from flask import Blueprint,render_template,redirect,url_for,request,session,flash
from flask_login import logout_user, login_required, current_user
from fg_lawkit import db,phonepe_client
from fg_lawkit.Student_mocks.modles import compare_dicts,subject_data,check_sub,check_sub_check_mock,update_mock_entry,move_expired_mock,remove_and_archive_mock,Update_MarksAgv,check_active_rambaan,update_mock_array,get_avg,get_img,get_number_of_question,get_name,check_attempt_left
from datetime import datetime, timedelta
from fg_lawkit.Student_mocks.forms import  Confirmi
from bson import ObjectId
import uuid  
from phonepe.sdk.pg.payments.models.request_v1.pg_pay_request import PgPayRequest  
from flask_mail import Mail, Message
from fg_lawkit import app, db
mail = Mail(app)


Student_mocks_blueprint = Blueprint('Student_mocks',__name__,template_folder='templates/Student_mocks',static_folder='Student_dashboard/static')

STATES = {
    'NOT_STARTED': 'not_started',
    'CONFIRMED_STARTS': 'confirmed_start',
    'IN_QUIZ': 'in_quiz',
    'COMPLETED_QUIZ': 'completed_quiz'
}


@Student_mocks_blueprint.before_request
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
    profile_pic=x['profile_image']
    name=x['name']

    
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
                
@Student_mocks_blueprint.context_processor
def inject_user():
    user_name = session.get('name', name)  # Default to 'Guest' if the name is not set
    return {'name':name,'profile_pic':profile_pic}

@Student_mocks_blueprint.route('/Student_admin', methods=['GET', 'POST'])
def Student_admin():
    if session.get('quiz_state'):
        if session.get('quiz_state') == STATES['COMPLETED_QUIZ']:     
                session.pop('quiz_state')
                session.pop('value')
                session.pop('value2')
    if current_user.is_authenticated and x['role']=='Student'  :
        
        pur_course=x['mock_purchased'] ##list of purchased course
        avg=get_avg(db,pur_course)
        img=get_img(db,pur_course)
        m_name=get_name(db,pur_course)   
        
        exp_course=x['mock_expired']
        
        for i in pur_course:
            y=remove_and_archive_mock(x['email'],i['subject_code'],db)
        return render_template('dashboard_Student.html',pur_course=pur_course,exp_course=exp_course,avg=avg,img=img,m_name=m_name)
    return 'invalid'
    
### clear expired course ###

@Student_mocks_blueprint.route('/Student_admin_clear', methods=['GET', 'POST'])
def Student_admin_clear():
        db.users.update_one({'email':x['email']},{"$set":{'mock_expired':[]}})
        return redirect (url_for('Student_mocks.Student_admin'))
    
#### mocks ###########

## to view mocks inside paper ##
@Student_mocks_blueprint.route('/Student_admin/<value>')
def Student_admin_sub(value):
    if check_sub(x,db,value):
            is_admin_delete=db.paper.find_one({'subject_code':value})
            if not is_admin_delete: 
                return "admin delete this course"
            UPCD,MCTMT,asd=subject_data(x['email'],value,db)
            session['quiz_state'] = STATES['NOT_STARTED']     
            number_of_question=get_number_of_question(db,value)
            m_name=get_name(db,value)   
            return render_template('subject.html',UPCD=UPCD,MCTMT=MCTMT,valuei=value,asd=asd,number_of_question=number_of_question,m_name=m_name)
    return redirect(url_for('Student_mocks.Student_admin'))


## confirm start
@Student_mocks_blueprint.route('/Student_admin/<value>/<value2>/confirm_start', methods=['GET', 'POST'])
def confirm_start(value,value2):
    if session.get('quiz_state') != STATES['NOT_STARTED']:
        update_mock_array(db,x['email'],value,value2)

        return redirect(url_for('Student_mocks.Student_admin'))
    else:
        #check the limit is done all 3 then go to back route
        if check_attempt_left(db,email,value,value2):
            if check_sub(x,db,value):
                form=Confirmi()
                if form.validate_on_submit():
                    session['quiz_state'] = STATES['CONFIRMED_STARTS']
                    return redirect(url_for('Student_mocks.Student_admin_sub_mock',value=value,value2=value2))
                return render_template ('confirm_start.html',form=form)
            return 'invalid'
        return redirect(url_for('Student_mocks.Student_admin_sub',value=value))

## start paper ##
@Student_mocks_blueprint.route('/Student_admin/<value>/<value2>', methods=['GET', 'POST'])

def Student_admin_sub_mock(value,value2):
        if session.get('quiz_state') != STATES['CONFIRMED_STARTS']:
  
            update_mock_array(db,x['email'],value,value2)
            return redirect(url_for('Student_mocks.Student_admin'))
        else:
            if check_sub_check_mock(x,db,value,value2) :            
                    data=db.paper.find_one({'subject_code':value,'paper_code':value2})
                    l = [i for i in data['Question_paper']]
                    data={}
                    ### fornt end js code for auto submit after some time ###
                    if request.method == 'POST':
                        for i in request.form:
                            if i != 'submitBtn': 
                                data[i] = request.form[i]
                        session['quiz_state'] = STATES['IN_QUIZ']  
                        submitted_ans = {i: int(data[i][-1]) for i in data}
                        ##### session managemnt for answere ###########
                        session['submitted_ans']=submitted_ans
                        session['value']=value
                        session['value2']=value2
                        ################################################
                        return redirect (url_for('Student_mocks.confirm'))
                    return render_template('mocks.html',l=l,value=value)
            return 'invalid'

@Student_mocks_blueprint.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if session.get('quiz_state') != STATES['IN_QUIZ']:

        ## need update ################################################################################

        return redirect(url_for('Student_mocks.Student_admin')) 
    else:

        session['quiz_state'] = STATES['COMPLETED_QUIZ']
        submitted_ans=session.get('submitted_ans',None)
        value=session.get('value')
        value2=session.get('value2')
        correct_ans=db.ans.find_one({'subject_code':value,'paper_code':value2})
        x,y,z=compare_dicts(submitted_ans,correct_ans['Question_paper'])
        marks=(x*4)+(y*(-1))+z*0
        update_mock_entry(email,value,value2,marks,db)
        Update_MarksAgv(marks,value2,db)
        data=db.paper.find_one({'subject_code':value,'paper_code':value2})
        l = [i for i in data['Question_paper']]
        return render_template("check_ans.html",submitted_ans=submitted_ans,correct_ans=correct_ans['Question_paper'],l=l,marks=marks)

        
## to buy mocks ##
@Student_mocks_blueprint.route('/<value>/buy')
def buy_mock(value):
    if  current_user.is_authenticated and x['role']=='Student':
        course_info=db.mock_home.find_one({'subject_code':value})
        d={}
        flag=True
        for i in x['mock_purchased']:
            if i ['subject_code']==value:
                flag=False
                break
        for i in course_info['paper_code']:
            d[i]=[]
        if flag :
            session['mock_name']=value
            merchant_transaction_id = str(uuid.uuid4())
            session['pay_id']=merchant_transaction_id
            pay_page_request = PgPayRequest.pay_page_pay_request_builder(merchant_transaction_id=merchant_transaction_id,  
                                                                amount=int(course_info['price'])*100,  
                                                                merchant_user_id=x['email'],  
                                                                callback_url=url_for('Student_mocks.Student_admin'),  
                                                                redirect_url="https://www.fglawkit.com/Student_mocks/confirm/buy/payment"
                                                                )

            pay_page_response = phonepe_client.pay(pay_page_request)  
            pay_page_url = pay_page_response.data.instrument_response.redirect_info.url

            return redirect(pay_page_url)
            # db.users.find_one_and_update(filter,{"$push":{'mock_purchased':data}})
            # return redirect(url_for("Student_mocks.Student_admin"))
            
    return redirect(url_for('Student_mocks.Student_admin'))

@Student_mocks_blueprint.route('confirm/buy/payment')
def confirm_buy_payment():

    if session.get('pay_id'):
        merchant_transaction_id=session.get('pay_id')
        response_pg_check_status = phonepe_client.check_status(merchant_transaction_id)
        flag=response_pg_check_status.success
        code=response_pg_check_status.code ###(fail-'PAYMENT_ERROR',success -'PAYMENT_SUCCESS' and pending - PAYMENT_PENDING)
        name=session.get('mock_name')

        
        if  flag== True and  code == 'PAYMENT_SUCCESS' :
            d={}
            course_info=db.mock_home.find_one({'subject_code':session['mock_name']})
            for i in course_info['paper_code']:
                d[i]=[]
            filter={'email':x['email']}
            data1={'subject_name':course_info['subject_name'],'subject_code':course_info['subject_code'],'expiry_date':str(datetime.now()+timedelta(days=30))[0:10],'mocks':d}
            db.users.find_one_and_update(filter,{"$push":{'mock_purchased':data1}})
            #message sent
            msg_body = f"Payment Successful, Your Purchase Mcoks -{name} . Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')} and expires no. {str(datetime.now()+timedelta(days=30))[0:10]} if any issue you can mail us at fglawkit@gmail.com."
            msg = Message('PAYMENT_SUCCESS', sender='backendfglawkit@gmail.com ', recipients=[email])
            msg.body = msg_body
            mail.send(msg)
            session.pop('pay_id')
            session.pop('mock_name')
            return redirect(url_for("Student_mocks.Student_admin"))
        elif flag== True and  code == 'PAYMENT_PENDING':
            db.money_dispute.insert_one({'email':email,'dispute':[code,merchant_transaction_id,'mocks',name],'date':str(datetime.now())})
            db.users.update_one({'email':email},{'$push':{'dispute':[code,merchant_transaction_id,'mocks',name]}})
            msg_body = f"Payment Pending, Your Try To Purchase Mcoks -{name} . Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. if any issue you can mail us at fglawkit@gmail.com."
            msg = Message('PAYMENT PENDING', sender='backendfglawkit@gmail.com ', recipients=[email])
            msg.body = msg_body
            mail.send(msg)
            session.pop('pay_id')
            session.pop('mock_name')
            return redirect (url_for('Student_dashboard.Student_dashboard'))
        else:
            msg_body = f"Payment Fail, Your Try To Purchase Mcoks -{name} . Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. if any issue you can mail us at fglawkit@gmail.com."
            msg = Message('PAYMENT FAIL', sender='backendfglawkit@gmail.com ', recipients=[email])
            msg.body = msg_body
            mail.send(msg)
            session.pop('pay_id')
            session.pop('mock_name')
            return redirect(url_for('Student_mocks.Student_admin'))  
    return redirect(url_for('Student_mocks.Student_admin'))  


#### mocks-ends ###########