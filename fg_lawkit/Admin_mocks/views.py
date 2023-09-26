from flask import Blueprint,render_template,redirect,url_for,abort
from flask_login import login_required, current_user
from fg_lawkit import db

from fg_lawkit.Admin_mocks.forms import subject ,AddImage,AddCourseHome,changeImage,change_rambaan_details_feature,change_Faq, change_rambaan_details_num,change_rambaan_details_txt
from fg_lawkit.Admin_mocks.modles import delete_mock_entry,delete_mock_purchased_element,question_paper

Admin_mocks_blueprint = Blueprint('Admin_mocks', __name__, template_folder='templates/Admin_mocks')

@Admin_mocks_blueprint.before_request
@login_required
def check_is_admin():
    id=current_user.user_id
    x=db.users.find_one(id)
    if not (current_user.is_authenticated  and x['role']=='admin'):
            abort(404)

### view subject of mocks ###
@Admin_mocks_blueprint.route('/')
def mocks():
        d=question_paper(db)
        h = [i for i in db.mock_home.find()]
        return render_template('mock.html',d=d,h=h)


### view subject of mocks ###
@Admin_mocks_blueprint.route('/sub/<value>')
def dashboard_admin_sub(value):
        l = [i for i in db.paper.find({'subject_code': value})]
      
        return render_template('sub.html',l=l,value=value)

### view question and solution ###
@Admin_mocks_blueprint.route('/sub/<value>/<value2>')
def dashboard_admin_sub_paper(value,value2):
        l = [i for i in db.paper.find({'subject_code': value,'paper_code':value2})]
        db_entry=db.ans.find_one({'subject_code':value,'paper_code':value2})
        s=db_entry['Question_paper']
        
        return render_template('test.html',l=l,s=s)

### add question and answere###
@Admin_mocks_blueprint.route('/add', methods=['GET', 'POST'])
def add():
        form = subject()
        if form.validate_on_submit():
            l=[]
            d={}
            for field in form.Question:
                Sr_no=(field.question_no.data)
                Sr_no_str=str(field.question_no.data)
                Question=(field.question.data)
                options={'o1':field.o1.data,'o2':field.o2.data,'o3':field.o3.data,'o4':field.o4.data}
                correct_option=(field.correct_option.data)
                if not Sr_no == None:
                    (d[Sr_no_str]) = correct_option
                if not Sr_no == '' and not Question =='' and not options =='' and not correct_option == '':
                    l.append({'sr_no':Sr_no,'question':Question,'option':options})
            db.ans.insert_one({'subject_name':form.subject_name.data,'subject_code':form.subject_code.data,'paper_code':form.paper_code.data,'Question_paper':d})
            db.paper.insert_one({'subject_name':form.subject_name.data,'subject_code':form.subject_code.data,'paper_code':form.paper_code.data,'paper_name':form.paper_name.data,'paper_duration':str(form.paper_time_duration.data),'Question_paper':l})
            db.avg.insert_one({'paper_code':form.paper_code.data,'sub_agv_marks':0,'No_Of_Std':0})
            
            
            return redirect (url_for('Admin_mocks.mocks'))
        return render_template('add_Question_form.html', form=form)

### add image and change ### --- may be removed
@Admin_mocks_blueprint.route('/add_image', methods=['GET', 'POST'])
def add_image():
        form=AddImage()
        if form.validate_on_submit():
            x=db.image.find_one({'subject_name':form.subject_name.data})
            if not x:
                db.image.insert_one({'subject_name':form.subject_name.data,'image_link':form.image.data})
            else:
                db.image.find_one_and_replace({'subject_name':form.subject_name.data},{'subject_name':form.subject_name.data,'image_link':form.image.data})
            return redirect (url_for('Admin_mocks.mocks'))
        return render_template ('add_image.html',form=form)

### delete subject of mocks ###
@Admin_mocks_blueprint.route('/sub/change/<value>/<value2>')
def dashboard_admin_sub_del(value,value2):

    if value2 == 'del':
        db.paper.delete_many({'subject_code':value})
        db.ans.delete_many({'subject_code':value})
        db.mock_home.delete_one({'subject_code':value})
    elif value2 == 'poke':
        delete_mock_purchased_element(db,value)
    return redirect (url_for('Admin_mocks.mocks'))

### delete paper or poke paper of mocks ###
@Admin_mocks_blueprint.route('/sub/<value>/<value2>/<value3>')
def dashboard_admin_sub_mocks_del(value,value2,value3):

    if value3 == 'del':
        db.paper.delete_one({'paper_code':value2,'subject_code':value})
        db.ans.delete_one({'paper_code':value2,'subject_code':value})
        db.mock_home.update_one({'subject_code':value},{"$pull":{'paper_code':value2}})
        return redirect (url_for('Admin_mocks.dashboard_admin_sub',value=value))
        
    elif value3 == 'poke':
        delete_mock_entry(db,value,value2)
        return redirect (url_for('Admin_mocks.dashboard_admin_sub',value=value))

### add detils of mocks to home page ###
@Admin_mocks_blueprint.route('/add_mock_home', methods=['GET', 'POST'])
def add_mock_home():
    form=AddCourseHome()
    if form.validate_on_submit():
        suggest_course = [i['suggest_course'] for i in form.suggested_course.data if not i['suggest_course'] == '']
        feature = [i['features'] for i in form.feature.data if not i['features'] == '']
        mock_code = [i['mock_code'] for i in form.paper_code.data if not i['mock_code'] == '']
        faq=[]
        for j in form.faq.data:
            d={}
            if not j['faq_question']=='' and not j['faq_answer']=='' :
                d[j['faq_question']]=j['faq_answer']   
                faq.append(d)
        data={'subject_name':form.subject_name.data,
                'subject_code':form.subject_code.data,
                'title':form.title.data,
                'sub_title':form.sub_title.data,
                'dic':form.dic.data,
                'no_of_paper':form.paper.data,
                'no_of_question':form.question.data,
                'price':form.price.data,
                'discount':form.discout.data,
                'suggested_course':suggest_course,
                'faq':faq,
                'feature':feature,
                'paper_code':mock_code,
                'video':form.video.data,
                'image':form.image.data}
        xi=check_same_subject=db.mock_home.find_one({'subject_name':form.subject_name.data,'subject_code':form.subject_code.data})
        if check_same_subject:
            Mes="Already Have Same Subject Delete That First"
            return render_template('message.html',Mes=Mes)
        else:
            db.mock_home.insert_one(data)
            return redirect (url_for('Admin_mocks.mocks'))
    return render_template('add_home_page.html',form=form)

### delete mocks from home page ### 
@Admin_mocks_blueprint.route('/del_mock_home/<value>', methods=['GET', 'POST'])
def del_mock_home(value):
        db.mock_home.delete_one({'subject_name':value})
        return redirect (url_for('Admin_mocks.mocks'))

### change image for mocks ###
@Admin_mocks_blueprint.route('/changeimage/<value>', methods=['GET', 'POST'])
def chaneimage(value):
    form=changeImage()
    if form.validate_on_submit():
        db.image.find_one_and_update({'subject_name':value},{'$set':{'image_link':form.image.data}})
        return redirect (url_for('Admin_mocks.mocks'))
    return render_template('change_image.html',form=form)

### home page individual data edit ###
@Admin_mocks_blueprint.route('/home_pg_indi_value/<value>/<value2>', methods=['GET', 'POST'])
def home_page_data_individual_edit(value,value2):
    query={'subject_code':value}
    if value2 in ['subject_name','title','sub_title','dic']:
        form=change_rambaan_details_txt()
        if form.validate_on_submit():
           update= {value2:form.text.data}
           db.mock_home.update_one(query,{'$set':update})
           return redirect (url_for('Admin_mocks.mocks'))
    elif value2 in ['no_of_paper','no_of_question','price','discount']:
        form=change_rambaan_details_num()
        if form.validate_on_submit():
            update={value2:form.text.data}
            db.mock_home.update_one(query,{'$set':update})
            return redirect (url_for('Admin_mocks.mocks'))
    elif value2 in ['suggested_course','feature','paper_code']:
        form=change_rambaan_details_feature()
        if form.validate_on_submit():
            # ={value2:form.text.data}
            data = [i['features'] for i in form.text.data if not i['features'] == '']
            update={value2:data}
            db.mock_home.update_one(query,{'$set':update})
            return redirect (url_for('Admin_mocks.mocks'))
    elif value2 == 'faq':
        form=change_Faq()
        if form.validate_on_submit():
            faq=[]
            for j in form.faq.data:
                d={}
                if not j['faq_question']=='' and not j['faq_answer']=='' :
                    d[j['faq_question']]=j['faq_answer']
                    faq.append(d)
            update={value2:faq}
             
            db.mock_home.update_one(query,{'$set':update})
            return redirect (url_for('Admin_mocks.mocks'))
                
    return render_template('rambaan_change.html',form=form,value=value,value2=value2)
    
