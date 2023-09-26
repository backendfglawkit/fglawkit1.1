### code for terminate user if he login from 3 different device ###
def update_ip(ip, user_id, db):
    query = {'email': user_id}
    update = {"$push": {'ip_address': ip}} 
    user = db.users.find_one(query) 
    if user:
        if ip not in user['ip_address']:
            if len(user['ip_address']) < 3:
                db.users.update_one(query, update)
            else:
                db.terminate_user.insert_one(user)
                db.users.delete_one(query)

