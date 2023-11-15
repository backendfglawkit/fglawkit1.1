from flask import Blueprint, render_template, redirect, url_for, flash, session
import random
from flask_mail import Mail, Message
from fg_lawkit.Reset_password.forms import validateform, resetpassword, emailform
from fg_lawkit import bcrypt, app, db
import mailtrap as mt

Reset_password_blueprint = Blueprint('Reset_password', __name__, template_folder='templates/Reset_password')

# Config for mailtrap
app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = 'fb600527ba148033335e46c408ba6971'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@Reset_password_blueprint.route('/emailValidate', methods=['GET', 'POST'])
def email_validate():
    form = emailform()
    if form.validate_on_submit():
        user_email = form.email.data
        
        # Check if the email exists in your user database
        user = db.users.find_one({'email': user_email})
        if user:
            # Generate a secure random token (6-digit OTP)
            random_number = str(random.randint(1000, 9999))

            # Store the OTP in the session (encrypted)
            session['otp'] = bcrypt.generate_password_hash(random_number).decode('utf-8')
            session['email'] = user_email

            # message body
            message = 'Your OTP is: ' + random_number +',Dont share it to anyone!'
            
            
            # old method Send the OTP via email
            # msg = Message('Password Reset OTP', sender='jainnaman4me@gmail.com', recipients=[user_email])
            # msg.body = str(message)
            # mail.send(msg)

            #new method by using api of mailtrap 
            mail = mt.Mail(
                        sender=mt.Address(email="mailtrap@fglawkit.com", name="FG LawKit"),
                        to=[mt.Address(email=user_email)],
                        subject="Reset Password",
                        text=str(message),
                        category="Forgot Password",
                )
            client = mt.MailtrapClient(token="fb600527ba148033335e46c408ba6971")
            client.send(mail)
            
            return redirect(url_for('Reset_password.validate_otp'))
        else:
            flash('Email not found. Please check your email address.')
    
    return render_template('emailvalidate.html', form=form)

@Reset_password_blueprint.route('/validate_otp', methods=['GET', 'POST'])
def validate_otp():
    if 'email' in session and 'otp' in session:
        email = session['email']
        saved_otp = session['otp']
        
        form = validateform()
        if form.validate_on_submit():
            user_input_otp1 = form.number1.data
            user_input_otp2 = form.number2.data
            user_input_otp3 = form.number3.data
            user_input_otp4 = form.number4.data
            user_input_otp=user_input_otp1+user_input_otp2+user_input_otp3+user_input_otp4
            # Verify the OTP
            if bcrypt.check_password_hash(saved_otp, user_input_otp):
                return redirect(url_for('Reset_password.resetpass'))
            else:
                flash('Invalid OTP.')
    else:
        # Handle cases where session data is missing (e.g., user didn't go through the email validation step)
        flash('Invalid access to this page.')
        return redirect(url_for('Reset_password.email_validate'))
    
    return render_template('validate.html', form=form)

@Reset_password_blueprint.route('/reset_pass', methods=['GET', 'POST'])
def resetpass():
    if 'email' in session:
        email = session['email']
        
        form = resetpassword()
        if form.validate_on_submit():
            # Hash the new password
            password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
            # Update the user's password in your user database
            db.users.update_one({"email": email}, {"$set": {"password": password_hash}})
            
            # Clear the session data after a successful password reset
            session.pop('email', None)
            session.pop('otp', None)
            
            flash('Your password has been reset successfully.')
            return redirect(url_for('login'))
    else:
        # Handle cases where session data is missing (e.g., user didn't go through the email validation step)
        flash('Invalid access to this page.')
        return redirect(url_for('Reset_password.email_validate'))
    
    return render_template('resetpass.html', form=form)
