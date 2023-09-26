from flask import Blueprint,render_template,redirect,url_for,abort
from flask_login import login_required, current_user
from fg_lawkit import db
from datetime import datetime, timedelta

Admin_user_blueprint = Blueprint('Admin_user', __name__, template_folder='templates/Admin_user')

@Admin_user_blueprint.before_request
@login_required
def check_is_admin():
    id=current_user.user_id
    x=db.users.find_one(id)
    if not (current_user.is_authenticated  and x['role']=='admin'):
            abort(404)

        
### manage user ####
@Admin_user_blueprint.route('/user', methods=['GET', 'POST'])
def user():
    user=db.users.find()
    terminated_user=db.terminate_user.find()
    return render_template('user.html',user=user,terminated_user=terminated_user)

### give access to user ###    
@Admin_user_blueprint.route('rambaan_access/<value>', methods=['GET', 'POST'])
def rambaan_access(value):
        exp_day = str((datetime.now() + timedelta(days=335)).strftime('%Y-%m-%d'))
        update_result = db.users.update_one({"email": value},{"$set": {"rambaan": {'status':True,'exp_date':exp_day}}})
        return redirect (url_for('Admin_user.user'))

### block unblock user ###
@Admin_user_blueprint.route('/block_unblock/<value>/<value2>', methods=['GET', 'POST'])
def user_block_unblock(value,value2):
        if value2 == 'block':
            data=db.users.find_one_and_delete({'email':value})
            db.terminate_user.insert_one(data)
            return redirect(url_for('Admin_user.user'))
        if value2 == 'unblock':
            data=db.terminate_user.find_one_and_delete({'email':value})
            db.users.insert_one(data)
            return redirect(url_for('Admin_user.user'))
        if value2 == 'delete':
            data=db.terminate_user.delete_one({'email':value})
            return redirect(url_for('Admin_user.user'))