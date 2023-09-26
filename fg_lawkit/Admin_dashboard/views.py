from flask import Blueprint,render_template,abort
from flask_login import login_required, current_user
from fg_lawkit import db

Admin_dashboard_blueprint = Blueprint('Admin_dashboard', __name__, template_folder='templates/Admin_dashboard')


## checking ###
@Admin_dashboard_blueprint.before_request
@login_required
def check_is_admin():
    id=current_user.user_id
    x=db.users.find_one(id)
    if not (current_user.is_authenticated  and x['role']=='admin'):
            abort(404)

### dashboard ###
@Admin_dashboard_blueprint.route('/dashboard')
def dashboard_admin():
        return render_template('dashboard_admin.html')

@Admin_dashboard_blueprint.route('/analytics')
def analytics():
        return render_template('analytics.html')