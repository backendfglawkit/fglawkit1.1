from flask import Blueprint,render_template,abort,Flask, request, redirect, url_for, flash
from flask_login import login_required, current_user
from fg_lawkit import db
from flask_mail import Mail, Message
from fg_lawkit import app

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
    msg = Message(
        subject= 'Welcome To FG lawKit',
        recipients = ['backendfglawkit@gmail.com'],
        sender = 'mailtrap@fglawkit.com',
    )
    msg.html = "<h4>Thanks For Registering in FG lawKit<h4><br><p> Please Wait for further Instruction!!</p>"
    mail.send(msg)
    return "Message sent!"

