from flask import Blueprint,render_template,abort,Flask, request, redirect, url_for, flash
from flask_login import login_required, current_user
from fg_lawkit import db
from flask_mail import Mail, Message
from fg_lawkit import app
import mailtrap as mt

Admin_dashboard_blueprint = Blueprint('Admin_dashboard', __name__, template_folder='templates/Admin_dashboard')

#for testing only
app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = 'fb600527ba148033335e46c408ba6971'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

## checking ###
@Admin_dashboard_blueprint.before_request
@login_required
def check_is_admin():
    id=current_user.user_id
    x=db.users.find_one(id)
    if not (current_user.is_authenticated  and x['role']=='admin'):
            abort(404)

### dashboard ###
@Admin_dashboard_blueprint.route('/dashboard')
def dashboard_admin():
        return render_template('dashboard_admin.html')

@Admin_dashboard_blueprint.route('/analytics')
def analytics():
        return render_template('analytics.html')

@Admin_dashboard_blueprint.route('/send')
def send():
    mail = mt.Mail(
    sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
    to=[mt.Address(email="2003jaindarshan@gmail.com")],
    subject="Reset Password",
    text="Your Otp is 325698 ,Dont share it to anyone ! this is sample testing ",
    category="Forgot Password",
)

    client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
    client.send(mail)
    return "Message sent!"


