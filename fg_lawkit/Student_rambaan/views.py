
from flask import Blueprint,render_template,redirect,url_for,request,session,flash
from flask_login import logout_user, login_required, current_user
from fg_lawkit import db,phonepe_client
from fg_lawkit.Student_rambaan.modles import check_active_rambaan,move_expired_mock,perform_fuzzy_search,check_have_rambaan,generate_custom_uuid
from datetime import datetime, timedelta
from fg_lawkit.Student_rambaan.forms import Search
from bson import ObjectId
import uuid  
from phonepe.sdk.pg.payments.v1.models.request.pg_pay_request import PgPayRequest

from flask_mail import Mail, Message
from fg_lawkit import  app, db


# Config for mailtrap
app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = 'fb600527ba148033335e46c408ba6971'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


Student_rambaan_blueprint = Blueprint('Student_rambaan',__name__,template_folder='templates/Student_rambaan')


@Student_rambaan_blueprint.before_request
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
            
@Student_rambaan_blueprint.context_processor
def inject_user():
    user_name = session.get('name', name)  # Default to 'Guest' if the name is not set
  

    return {'name':name,'profile_pic':profile_pic}
            

@Student_rambaan_blueprint.route('/rambaan', methods=['GET', 'POST'])

def rambaan():
        if x['rambaan']['status']:
            form=Search()
            data1=[i for i in db.rambaan.find()]
            filter_tags=db.other.find_one({'name':'rambaan_tags_card'})['tags']
            if form.validate_on_submit():
                value=form.name.data
                return redirect (url_for('Student_rambaan.rambaan_search',value=value))
            return render_template('std_rambaan.html',data1=data1,filter_tags=filter_tags,form=form)
        return render_template('buy_rambaan_in_dash.html')


@Student_rambaan_blueprint.route('/rambaan/search/<value>')
def rambaan_search(value):
    if x['rambaan']['status']:
        query=value
        search_results = perform_fuzzy_search(query,db)
        session['search']=search_results
        return render_template('rambaan_video_search.html',tag=search_results,query=query)
    return render_template('buy_rambaan_in_dash.html')



@Student_rambaan_blueprint.route('/rambaan/<value>')
def rambaan_view(value):
        if x['rambaan']['status']:
            # data1=[i for i in db.rambaan_video.find_one({'rambaan_categories_code':value})]
            data1=db.rambaan_video.find_one({'rambaan_categories_code':value})
            return render_template('std_rambaan_video.html',data1=data1)
        return render_template('buy_rambaan_in_dash.html')


@Student_rambaan_blueprint.route('/rambaan/<value>/filter', methods=['GET', 'POST'])
def rambaan_filter(value):
    if x['rambaan']['status']:
        form=Search()
        filter_tags=db.other.find_one({'name':'rambaan_tags_card'})['tags']
        data1=db.rambaan.find({"card_tags": value})
        if form.validate_on_submit():
                value=form.name.data
                return redirect (url_for('Student_rambaan.rambaan_search',value=value))
        return render_template('std_rambaan.html',data1=data1,filter_tags=filter_tags,form=form)
    return render_template('buy_rambaan_in_dash.html')
 
import random

@Student_rambaan_blueprint.route('/rambaan/search/play_single_rambaan_video/<value>')
def play_single_rambaan_video(value):
    if x['rambaan']['status']:
        data=(session['search'])[int(value)-1]
        # data1=[i for i in db.rambaan.find()]
        data1 = (db.rambaan.find()[:3] if db.rambaan.count_documents({}) >= 3 else list(db.rambaan.find()))
        result = random.sample(list(db.rambaan.find()), min(3, db.rambaan.count_documents({})))
        return render_template('play_single_rambaan_video.html',data=data,data1=result)
    return render_template('buy_rambaan_in_dash.html')


@Student_rambaan_blueprint.route('/rambaan/buy')
def proced_to_buy():
      
        if not check_have_rambaan(db,email):
            merchant_transaction_id = str(uuid.uuid4())[:-2]
            session['pay_id']= merchant_transaction_id
            
            
            pay_page_request = PgPayRequest.pay_page_pay_request_builder(merchant_transaction_id=merchant_transaction_id,  
                                                                amount=300,  
                                                                merchant_user_id=email,  
                                                                callback_url=url_for('Student_rambaan.rambaan'),  
                                                                redirect_url="https://www.fglawkit.com/Student_rambaan//rambaan/buy/confirm"
                                                                )

            pay_page_response = phonepe_client.pay(pay_page_request)  
            pay_page_url = pay_page_response.data.instrument_response.redirect_info.url
            
            return redirect(pay_page_url)
        return redirect (url_for('Student_rambaan.rambaan'))
import mailtrap as mt

@Student_rambaan_blueprint.route('/rambaan/buy/confirm')
def confirm_buy():
    if session.get('pay_id'):
        merchant_transaction_id=session.get('pay_id')
        response_pg_check_status = phonepe_client.check_status(merchant_transaction_id)
        flag=response_pg_check_status.success
        code=response_pg_check_status.code ###(fail-'PAYMENT_ERROR',success -'PAYMENT_SUCCESS' and pending - PAYMENT_PENDING)
      
        
       
        if  flag== True and  code == 'PAYMENT_SUCCESS' :
            exp_day = str((datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'))
            update_result = db.users.update_one({"email": email},{"$set": {"rambaan": {'status':True,'exp_date':exp_day}}})
            session.pop('pay_id')
            msg_body = f"Payment Successful, Your Purchase Rambaan. Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')} and expires no. {exp_day} if any issue you can mail us at fglawkit@gmail.com."

            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email=email)],
                        subject="Thanks For Purchasing Rambaan",
                        text=str(msg_body),
                        category="RamBaan Purchase",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)

            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email='parth@fglawkit.com')],
                        subject="rambaan purchase(2)",
                        text=str(msg_body),
                        category="RamBaan Purchase",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)
            
            
            return redirect (url_for('Student_rambaan.rambaan'))
        elif flag== True and  code == 'PAYMENT_PENDING':
            msg_body = f"Payment Pending. Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')}. Your issue is solving as soon as possible. Feel free to mail us at fglawkit@gmail.com."
            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email=email)],
                        subject="Payment Pendind, Contact Us",
                        text=str(msg_body),
                        category="Payment Pendind",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)

            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email='parth@fglawkit.com')],
                        subject="Payment Pendind",
                        text=str(msg_body),
                        category="Payment Pendind(2)",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)
            
            db.money_dispute.insert_one({'email':email,'dispute':[code,merchant_transaction_id,'rambaan','Fg_rambaan'],'date':str(datetime.now())})
            db.users.update_one({'email':email},{'$push':{'dispute':[code,merchant_transaction_id,'rambaan','Fg_rambaan']}})
            if session.get('pay_id'):
                session.pop('pay_id')
            return redirect (url_for('Student_rambaan.rambaan'))
        else:
            session.pop('pay_id')

            msg_body = f"PAYMENT Fail. Your Transaction Id - {merchant_transaction_id}. Purchase by an Id {email}. Purchase Date will Be {datetime.now().strftime('%Y-%m-%d')}. Payment Fail"
            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email=email)],
                        subject="Reset Password",
                        text=str(msg_body),
                        category="RamBaan Purchase",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)

            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email='parth@fglawkit.com')],
                        subject="Reset Password",
                        text=str(msg_body),
                        category="RamBaan Purchase",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)
            return redirect (url_for('Student_rambaan.rambaan'))
    return redirect (url_for('Student_rambaan.rambaan'))
        
    
