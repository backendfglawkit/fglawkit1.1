from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField, Form,FieldList,FormField,TimeField,URLField
from wtforms.validators import DataRequired,Optional,NumberRange
from wtforms import  SubmitField, validators




class faqform(Form):
        faq_question=StringField('question',validators=[Optional ()])
        faq_answer=StringField('answer',validators=[Optional()])
        
class sucoform(Form):
        suggest_course=StringField('suggest_course',validators=[Optional()])
                
class featureform(Form):
        features=StringField('feature',validators=[Optional()])
        
class mock(Form):
        mock_code=StringField('Enter Mock Code',validators=[Optional(),validators.Regexp(r'^\S+$', message="Field must not contain whitespace")])        

class addMocks(Form):
        question_no=IntegerField('Question Number', validators=[Optional()])
        question=StringField('Question', validators=[Optional()])
        o1=StringField('Option 1', validators=[Optional()])
        o2=StringField('Option 2', validators=[Optional()])
        o3=StringField('Option 3', validators=[Optional()])
        o4=StringField('Option 4', validators=[Optional()])
        correct_option=IntegerField('Correct Option', validators=[Optional(),NumberRange(min=1, max=4)])

class subject(FlaskForm):
        subject_name = StringField('Subject Name', validators=[DataRequired()])
        subject_code = StringField('Subject Code', validators=[DataRequired(),validators.Regexp(r'^\S+$', message="Field must not contain whitespace")])
        paper_code= StringField('Paper Unique Number', validators=[DataRequired(),validators.Regexp(r'^\S+$', message="Field must not contain whitespace")])
        paper_name=StringField("enter Text to display", validators=[DataRequired()])
        paper_time_duration=TimeField('Time Duration',validators=[DataRequired()])
        Question = FieldList(FormField(addMocks), min_entries=150, max_entries=151)


class AddImage(FlaskForm):
        image=URLField('image_link', validators=[Optional()])
        subject_name=StringField('subject name', validators=[Optional()])
        submit=SubmitField('Add')

class AddCourseHome(FlaskForm):
        subject_name= StringField('subject_name',validators=[DataRequired()])
        subject_code= StringField('subject_code',validators=[DataRequired(),validators.Regexp(r'^\S+$', message="Field must not contain whitespace")])
        title= StringField('title',validators=[DataRequired()])
        sub_title= StringField('sub-title',validators=[DataRequired()])
        dic= StringField('dic',validators=[DataRequired()])
        paper= IntegerField('no of paper',validators=[DataRequired()])
        question= IntegerField('no of question',validators=[DataRequired()])
        price= IntegerField('price',validators=[DataRequired()])
        discout= IntegerField('discout',validators=[DataRequired()])
        video= URLField('video_link',validators=[DataRequired()])    
        image= URLField('image_link',validators=[DataRequired()])    
        paper_code=FieldList(FormField(mock),min_entries=5)
        feature=FieldList(FormField(featureform),min_entries=5)
        faq = FieldList(FormField(faqform),min_entries=5)
        suggested_course=FieldList(FormField(sucoform),min_entries=5)
        submit=SubmitField('Add')

        
class changeImage(FlaskForm):
        image=URLField('image_link', validators=[DataRequired()])
        submit=SubmitField('Change')



class change_rambaan_details_txt(FlaskForm):
        
        text=StringField('Text', validators=[DataRequired()])
        submit=SubmitField('Change')

class change_rambaan_details_num(FlaskForm):
        
        text=IntegerField('number', validators=[DataRequired()])
        submit=SubmitField('Change')

class change_rambaan_details_link(FlaskForm):
        
        text=URLField('url', validators=[DataRequired()])
        submit=SubmitField('Change')

class change_rambaan_details_feature(FlaskForm):
       
        text=FieldList(FormField(featureform),min_entries=5)
        submit=SubmitField('Change')

class change_Faq (FlaskForm):
        faq = FieldList(FormField(faqform),min_entries=5)
        submit=SubmitField('Change')
