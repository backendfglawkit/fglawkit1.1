from flask import Blueprint,render_template,redirect,url_for,request,flash,abort
from flask_login import login_required, current_user
from fg_lawkit import db
from fg_lawkit.Admin_rambaan.forms import create_rambaan_categories,add_tags,put_video_in_rambaan,change_rambaan_details_num,change_rambaan_details_link,change_rambaan_details_feature,change_rambaan_details_txt
from fg_lawkit.Admin_rambaan.modles import del_rambaan_video

Admin_rambaan_blueprint = Blueprint('Admin_rambaan', __name__, template_folder='templates/Admin_rambaan')

@Admin_rambaan_blueprint.before_request
@login_required
def check_is_admin():
    id=current_user.user_id
    x=db.users.find_one(id)
    if not (current_user.is_authenticated and x['role']=='admin'):
            abort(404)

### view rambaan ###
@Admin_rambaan_blueprint.route('/rambaan')
def rambaan():
        list_of_rambaan=db.rambaan.find()
        return render_template ('rambaans.html',list_of_rambaan=list_of_rambaan)

### add rambaan categories ###
@Admin_rambaan_blueprint.route('/rambaan_categories', methods=['GET', 'POST'])
def rambaan_categories():
        form=create_rambaan_categories()
        form.options.choices = form.list_of_tags_visible(db)
        if form.validate_on_submit():
            feature = [i['features'] for i in form.feature.data if not i['features'] == '']
            data={'rambaan_categories_name':form.rambaan_categories_name.data,
                  'short_dic':form.short_dic.data,
                  'long_dic':form.long_dic.data,
                  'rating':form.rating.data,
                  'image_link':form.image_link.data,
                  'video_link':form.video_link.data,
                  'rambaan_categories_code':form.rambaan_categories_code.data,
                  'feature':feature,
                  'course_include':[],
                  'card_tags':form.options.data, 
                  'watch_hours':0}  
            db.rambaan.insert_one(data)
            db.rambaan_video.insert_one({'rambaan_categories_code':form.rambaan_categories_code.data,'videos':[]})
            return redirect (url_for('Admin_rambaan.rambaan'))
        return render_template('rambaan_create_categories.html',form=form)


### add tags (searching) for rambaan ###
@Admin_rambaan_blueprint.route('/add_rambaan_categories_tags', methods=['GET', 'POST'])
def add_rambaan_categories_tags():
        form=add_tags()
        if form.validate_on_submit():
            new_tags={((form.tags_code.data).lower()):((form.tags.data).lower())}
            update_query = {'$set': {'tags.' + key: value for key, value in new_tags.items()}}
            selected_option = form.options.data
            if selected_option=='for_visible_tag':
                db.other.update_one({'name': 'rambaan_tags_card'}, update_query)
            if selected_option=='for_hidden_tag':
                db.other.update_one({'name': 'rambaan_search_tag'}, update_query)
            return redirect(url_for('Admin_rambaan.add_rambaan_categories_tags'))
        rambaan_categories_tags_vs=(db.other.find_one({'name':'rambaan_tags_card'}))['tags'] 
        rambaan_categories_tags_h=(db.other.find_one({'name':'rambaan_search_tag'}))['tags'] 
        return render_template('add_rambaan_categories_tags.html',form=form,rambaan_categories_tags_vs=rambaan_categories_tags_vs,rambaan_categories_tags_h=rambaan_categories_tags_h)

### delete rambaan tags ### --  may be useless i dont know "hi"-- hidden and "vs"-- visible
@Admin_rambaan_blueprint.route('/add_rambaan_categories_tags/<value>/<value2>/del', methods=['GET', 'POST'])
def del_rambaan_categories_tags(value,value2):
        if value2 =='vs':
            filter = {"name": "rambaan_tags_card"}
            data_to_remove='tags.'+value
            update = {"$unset": {data_to_remove: ""}}
            db.other.update_one(filter, update)
        elif value2 == 'hi':
            filter = {"name": "rambaan_search_tag"}
            data_to_remove='tags.'+value
            update = {"$unset": {data_to_remove: ""}}
            db.other.update_one(filter, update)
        return redirect (url_for('Admin_rambaan.add_rambaan_categories_tags'))

### add video to rambaan categories ###
@Admin_rambaan_blueprint.route('/rambaan/<value>/add_video', methods=['GET', 'POST'])
def add_rambaan_videos(value):
        form=put_video_in_rambaan()
        form.options.choices = form.list_of_tags_hidden(db)
        if form.validate_on_submit():
            data_in_rambaan_videos={
                                    'title':form.title.data,
                                    'dis': form.discription.data,
                                     }
            db.rambaan.update_one({'rambaan_categories_code':value},{'$push':{'course_include':data_in_rambaan_videos}})
            db.rambaan.update_one({'rambaan_categories_code':value},{'$inc':{'watch_hours':form.watch_time.data}})
            data_in_rambaan_videos['rating']=form.rating.data
            data_in_rambaan_videos['link']=form.link.data
            data_in_rambaan_videos['tags']=form.options.data
            db.rambaan_video.update_one({'rambaan_categories_code':value},{'$push':{'videos':data_in_rambaan_videos}})
            return redirect (url_for('Admin_rambaan.rambaan'))
        return render_template('add_videos.html',form=form)

### deleting rambaan video inside categories ###
@Admin_rambaan_blueprint.route('/rambaan/<value>/<index>/del_video', methods=['GET', 'POST'])
def del_rambaan_videos(value,index):
        del_rambaan_video(db,value,index)
        return redirect(url_for('Admin_rambaan.view_rambaan_category',value=value))

### deleting rambaan categories ###
@Admin_rambaan_blueprint.route('/rambaan/<value>/del_rambaan_category', methods=['GET', 'POST'])
def del_rambaan_category(value):
        db.rambaan.delete_one({'rambaan_categories_code':value})
        db.rambaan_video.delete_one({'rambaan_categories_code':value})
        return redirect (url_for('Admin_rambaan.rambaan'))

### for view video inside rambaan ###
@Admin_rambaan_blueprint.route('/rambaan/<value>/view_rambaan_category', methods=['GET', 'POST'])
def view_rambaan_category(value):
        data1=(db.rambaan_video.find_one({'rambaan_categories_code':value})['videos'])
        return render_template('view_rambaan.html',data1=data1)

### changing rambaan categories value ###
@Admin_rambaan_blueprint.route('/rambaan_change/<value>/<value2>', methods=['GET', 'POST'])
def rambaan_change(value,value2):
        if value2 == 'rating':
            form=change_rambaan_details_num()
        elif value2 == 'image_link' or value2 == 'video_link':
            form=change_rambaan_details_link()
        elif value2== 'feature':
            form=change_rambaan_details_feature()
        else :
            form=change_rambaan_details_txt()
        if form.validate_on_submit():
            if not value2=='feature':
                data=form.text.data
            else: 
                data = [i['features'] for i in form.text.data if not i['features'] == '']
            X=db.rambaan.update_one({'rambaan_categories_code':value},{"$set":{value2:data}})
            return redirect (url_for('Admin_rambaan.rambaan'))
        return render_template('rambaan_change.html',form=form)