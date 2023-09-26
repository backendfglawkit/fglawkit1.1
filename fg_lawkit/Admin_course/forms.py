from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form,FieldList,FormField,URLField,IntegerField,TextAreaField
from wtforms.validators import DataRequired,Optional
from wtforms import  SubmitField, validators

class featureform(Form):
        features=StringField('feature',validators=[Optional()])

class add_course(FlaskForm):
    course=StringField('Course Name', validators=[DataRequired()])
    validate=IntegerField('Enter the Number of days')
    course_code=StringField('unique code', validators=[DataRequired(),validators.Regexp(r'^\S+$', message="Field must not contain whitespace")])
    short_dic=TextAreaField('short discription', validators=[DataRequired()])
    long_dic=TextAreaField('long discription', validators=[DataRequired()])
    feature=FieldList(FormField(featureform),min_entries=5)
    image_link=URLField('image link', validators=[DataRequired()])
    video_link=URLField('video link', validators=[DataRequired()])
    price=IntegerField("enter the price",validators=[DataRequired()])
    submit=SubmitField('Add Module', validators=[DataRequired()])
    

class add_module(FlaskForm):
    module=StringField('Name', validators=[DataRequired()])
    submit=SubmitField('Add Module', validators=[DataRequired()])

class add_video(FlaskForm):
    title=StringField('Title', validators=[DataRequired()])
    discription=TextAreaField('Dics', validators=[DataRequired()])
    duration=IntegerField('Enter The Duration',validators=[DataRequired()])
    video_link=URLField('Video Link',validators=[DataRequired()])
    submit=SubmitField('Add Module', validators=[DataRequired()])

class add_res(FlaskForm):
    title=StringField('title', validators=[DataRequired()])
    link=URLField('add a link of google docs', validators=[DataRequired()])    
    submit=SubmitField('Add Reso', validators=[DataRequired()])


class change_txt(FlaskForm):
        
        text=StringField('Text', validators=[DataRequired()])
        submit=SubmitField('Change')

class change_num(FlaskForm):
        
        text=IntegerField('number', validators=[DataRequired()])
        submit=SubmitField('Change')

class change_link(FlaskForm):
        
        text=URLField('url', validators=[DataRequired()])
        submit=SubmitField('Change')