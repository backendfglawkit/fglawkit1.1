from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,EmailField,RadioField
from wtforms.validators import DataRequired
from wtforms import  SubmitField


class RegistrationForm(FlaskForm):
    firstname=StringField('Name', validators=[DataRequired()])
    options = RadioField('Gender', choices=['male','female'])
    email=EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()]) 
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email=EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

