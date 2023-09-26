from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField

class Search(FlaskForm):
        name=StringField('enter here')
        submit = SubmitField('Search')

