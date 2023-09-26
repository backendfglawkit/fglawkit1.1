from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField


class Confirmi(FlaskForm):
        name=StringField('enter name')
        submiti=SubmitField('Confirm Submit')
