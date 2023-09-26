def check_read(email,db):
    x=db.users.find_one({'email':email})['Course_purchases']
    data=None
    if x:
        data=[]
        for i in x: 
                y=db.course_home.find_one({'course_code':i['name']})
                data.append(y)
    return data


# it checks that user have access to perticular course
def check_get_content(email,db,course_code):
    flag=True
    data=check_read(email,db)
    for i in data:
        if not i['course_code']==course_code:
            flag=False
            break
    return flag    

def check_have_course(db,email,value):
    data=db.users.find_one({'email':email})
    course_name=data['Course_purchases']
    for i in course_name:
        if i['name']==value:
            return False
    return True
            
from datetime import datetime, timedelta

def is_expire_course(db,email):
    collection=db['users']
    document = collection.find_one({"email": email})
    current_date = datetime.now()
    course_purchases = document.get("Course_purchases", [])
    valid_course_purchases = [purchase for purchase in course_purchases if datetime.strptime(purchase["exp_date"], "%Y-%m-%d") > current_date]
    collection.update_one({"email": email}, {"$set": {"Course_purchases": valid_course_purchases}})