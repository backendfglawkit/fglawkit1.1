from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,EmailField
from wtforms.validators import DataRequired



class validateform(FlaskForm):
    number1=StringField('Enter The Number',validators=[DataRequired()])
    number2=StringField('Enter The Number',validators=[DataRequired()])
    number3=StringField('Enter The Number',validators=[DataRequired()])
    number4=StringField('Enter The Number',validators=[DataRequired()])
    submit = SubmitField('Reset')
    
class resetpassword(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()]) 
    submit = SubmitField('Reset')
    
    
class emailform(FlaskForm):
    email=EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Click to proceed')