from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField, Form,FieldList,FormField,URLField,RadioField
from wtforms.validators import DataRequired,Optional,NumberRange
from wtforms import SelectMultipleField, SubmitField, widgets,validators


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class featureform(Form):
        features=StringField('feature',validators=[Optional()])
        
class create_rambaan_categories(FlaskForm):
        rambaan_categories_name=StringField('name', validators=[DataRequired()])
        short_dic=StringField('short discription', validators=[DataRequired()])
        long_dic=StringField('long discription', validators=[DataRequired()])
        rating=IntegerField('rating', validators=[Optional(),NumberRange(min=1, max=5)])
        # watch_hrs=IntegerField('Enter the watch hrs', validators=[DataRequired()])
        feature=FieldList(FormField(featureform),min_entries=5)
        image_link=URLField('image link', validators=[DataRequired()])
        video_link=URLField('video link', validators=[DataRequired()])

        
        # options = MultiCheckboxField('Card_Tags:',choices=list_of_tags_visible(db))
        @staticmethod
        def list_of_tags_visible(db):
                reading_from_db=db.other.find_one({'name':'rambaan_tags_card'})
                l = []
                for key, value in reading_from_db['tags'].items():
                        l.append((key, value))
                
                return l
        options = MultiCheckboxField('Card_Tags:', choices=[])
        
        rambaan_categories_code=StringField('unique code', validators=[DataRequired(),validators.Regexp(r'^\S+$', message="Field must not contain whitespace")])
        submit=SubmitField('add')

class add_tags(FlaskForm):
        options = RadioField('Select an option', choices=[('for_visible_tag', 'For Visible Tag'), ('for_hidden_tag', 'For Hidden Tag')], validators=[DataRequired()])
        tags=StringField('Tags', validators=[DataRequired()])
        tags_code=StringField('Tags code', validators=[DataRequired()])
        submit=SubmitField('add')


class put_video_in_rambaan(FlaskForm):
        title=StringField('title', validators=[DataRequired()])
        discription=StringField('discription', validators=[DataRequired()])
        rating=IntegerField('rating', validators=[Optional(),NumberRange(min=1, max=5)])
        link=URLField('video link', validators=[DataRequired()])
        watch_time=IntegerField('watch time in miniute')
        @staticmethod
        def list_of_tags_hidden(db):
                reading_from_db = db.other.find_one({'name': 'rambaan_search_tag'})
                l = []
                for key, value in reading_from_db['tags'].items():
                        l.append((key, value))
                return l

        options = MultiCheckboxField('Card_Tags:', choices=[])
        
        submit=SubmitField('add')


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