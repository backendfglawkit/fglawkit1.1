from flask import Blueprint,render_template,redirect,url_for,flash,abort
from flask_login import login_required, current_user
from fg_lawkit import db
from fg_lawkit.Admin_course.forms import add_course,add_module,add_video,add_res
from fg_lawkit.Admin_course.modles import *

Admin_course_blueprint = Blueprint('Admin_course', __name__, template_folder='templates/Admin_course')

@Admin_course_blueprint.before_request
@login_required
def check_is_admin():
    id=current_user.user_id
    x=db.users.find_one(id)
    if not (current_user.is_authenticated  and x['role']=='admin'):
            abort(404)

@Admin_course_blueprint.route('/')
def course_dashboard():
    list_of_course=list(db.course_home.find({}))
    return render_template("course_dashboard.html",list_of_course=list_of_course)

@Admin_course_blueprint.route('/add_course', methods=['GET', 'POST'])
def add_courses():
    form=add_course()
    if form.validate_on_submit():
        course_data = {
                    'course': form.course.data,
                    'course_code': form.course_code.data,
                    'short_dic': form.short_dic.data,
                    'long_dic': form.long_dic.data,
                    'feature': [feature_form.features.data for feature_form in form.feature if feature_form.features.data],
                    'image_link': form.image_link.data,
                    'video_link': form.video_link.data,
                    'price':form.price.data,
                    'validate':form.validate.data,
                    'content':{}
                    }
        flag1=db.course_home.find_one({'course_code': form.course_code.data})
        flag2=db.course.find_one({'course_code': form.course_code.data})

        if not flag1 and not flag2 :
            db.course_home.insert_one(course_data) ## for home page
            db.course.insert_one({'course_code':form.course_code.data,'content':{}}) ## for dashboard page
            flash('Course added successfully', 'success')
            return redirect(url_for('Admin_course.course_dashboard'))
        flash('this course code is already there','warning')
    return render_template('add_course.html',form=form)

@Admin_course_blueprint.route('/delete_course/<value>')
def delete_course(value):
        db.course.delete_one({'course_code':value})
        db.course_home.delete_one({'course_code':value})
        return redirect (url_for('Admin_course.course_dashboard'))

@Admin_course_blueprint.route('/view_inside/<course_code>', methods=['GET', 'POST'])
def view_inside(course_code):
    form_module = add_module()  # Create an instance of your form class
    if form_module.validate_on_submit():
        #make own function to put data
        push_module(form_module.module.data,course_code,db)
        return redirect (url_for('Admin_course.view_inside',course_code=course_code))
    content=db.course.find_one({'course_code': course_code})['content']
    return render_template('view_inside.html', form_module=form_module,content=content,course_code=course_code)

@Admin_course_blueprint.route('/add_videos/<value2>/<value>', methods=['GET', 'POST'])
def add_videos(value,value2):
    form_vid=add_video()
    if form_vid.validate_on_submit():
        data = {
        'type':'video',
        'title': form_vid.title.data,
        'description': form_vid.discription.data,
        'duration': form_vid.duration.data,
        'link': form_vid.video_link.data}
        data_1={
        'type':'video',
        'title': form_vid.title.data,
        'description': form_vid.discription.data,
        'duration': form_vid.duration.data
        }
        push_data_to_content(value,value2,data,data_1)
        return redirect(url_for('Admin_course.view_inside',course_code=value))
    return render_template('add_video.html',form_vid=form_vid)

#value1--sub_name , value2-- module_name,value--> what to change(like title etc)
@Admin_course_blueprint.route('/delete/<value>/<value2>/<value3>/<value4>', methods=['GET', 'POST'])
def delete_details(value,value2,value3,value4):
    pull_data_from_content(value,value2,value3,value4)
    return redirect(url_for('Admin_course.view_inside',course_code=value))


@Admin_course_blueprint.route('/add_res/<value>/<value2>', methods=['GET', 'POST'])
def add_reso(value,value2):
        form=add_res()
        if form.validate_on_submit():
            data={'type':'reso','title':form.title.data,'description':form.title.data[:-3]}
            data_1={'type':'reso','title':form.title.data,'link':form.link.data,'description':form.title.data[:-3]}
            push_data_to_content(value,value2,data_1,data)
            return redirect(url_for('Admin_course.view_inside',course_code=value))
        return render_template('add_res.html',form=form)


@Admin_course_blueprint.route('/delete_module/<value>/<value2>')
def delete_module (value,value2):
    fil='content.'+value2
    db.course.update_one({'course_code':value},{'$unset':{fil:1}})
    db.course_home.update_one({'course_code':value},{'$unset':{fil:1}})
    return redirect(url_for('Admin_course.view_inside',course_code=value))