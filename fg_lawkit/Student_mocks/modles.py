from datetime import datetime

def check_active_rambaan(db,user_id):
    x=db.users.find_one({'email':user_id})
    if x['rambaan']:
        if x['rambaan']['exp_date']:
            exp_date = datetime.strptime((x['rambaan']['exp_date']), "%Y-%m-%d")
            current_date = datetime.strptime((datetime.now()).strftime('%Y-%m-%d'), "%Y-%m-%d")
            if exp_date > current_date:
                
 
                return False # means no expired yet
            else:
                filter_criteria = {"email": x['email']}  # Use the appropriate criteria to identify the document
                update_data = {"$set": {"rambaan": {"status": False,"exp_date": None}}}
                db.users.update_one(filter_criteria, update_data)


                return True # means expired



def move_expired_mock(db,user_id):
    user = db.users.find_one({'email': user_id})
    
    for i, mock in enumerate(user['mock_purchased']):
        exp_date_db = mock['expiry_date']
        exp_date = datetime.strptime(exp_date_db, "%Y-%m-%d")
        current_date = datetime.now()
        
        if exp_date <= current_date:
            # Move the mock to the mock_expired array
            expired_mock = user['mock_purchased'].pop(i)
            db.users.update_one({'_id': user['_id']}, {
                '$push': {'mock_expired': expired_mock},
                '$set': {'mock_purchased': user['mock_purchased']}
            })


def remove_and_archive_mock(email, subject_code, db):

    user = db.users.find_one({"email": email})

    if user and "mock_purchased" in user:

        subject = next(
            (s for s in user["mock_purchased"] if s["subject_code"] == subject_code), None)

        if subject and "mocks" in subject:
            # Check if the subject's mocks have all arrays with length >= 3
            all_mocks_valid = all(
                len(subject["mocks"][mock_key]) >= 3 for mock_key in subject["mocks"])

            if all_mocks_valid:
                # Archive the subject to mock_expired
                user["mock_expired"].append(subject)
                # Remove the subject from the mock_purchased array
                user["mock_purchased"] = [
                    s for s in user["mock_purchased"] if s["subject_code"] != subject_code]

                # Update the user in the database
                db.users.replace_one({"email": email}, user)

    return user

def subject_data(email, value, db):
    x = db.users.find_one({'email': email})
    list_of_apply = {}
    lsit_of_not_apply = {}
    for i in x['mock_purchased']:
        if i['subject_code'] == value:
            data = i
            break
    lsit_of_mocks = list(data['mocks'].keys())
    for i in lsit_of_mocks:

        y = db.paper.find_one({'paper_code': i})
        if is_mock_count_greater_than_three(email, value, i, db):
            list_of_apply[i] = i
        else:
            lsit_of_not_apply[i] = '#'
            
    return data, list_of_apply, lsit_of_not_apply



def is_mock_count_greater_than_three(email, subject_code, mock_name, db):

    # Find the user by email
    user = db.users.find_one({"email": email})
    if not user:

        return False

    # Find the subject by subject_code
    subject = next(
        (s for s in user["mock_purchased"] if s["subject_code"] == subject_code), None)
    if not subject:

        return False

    # Check if the mock_name exists in the subject's mocks
    if mock_name not in subject["mocks"]:

        return False

    # Get the count of the mock array
    mock_count = len(subject["mocks"][mock_name])

    # Check if the count is greater than or equal to 3
    if mock_count >= 3:
        return False
    else:
        return True

    # Close the MongoDB connection


def check_sub(x, db, value):
    x = db.users.find_one({'email': x['email']})
    for i in x['mock_purchased']:
        if value in (i['subject_code']):
            return True

def update_mock_array(db, email, subject_code, mock_code):
    query = {"email": email, "mock_purchased.subject_code": subject_code}
    update_field = f"mock_purchased.$.mocks.{mock_code}"

    # Update the array in the document
    result = db.users.update_one(
        query,
        {"$push": {f"{update_field}": 0}},
    )

def check_sub_check_mock(x, db, value, value2):
    x = db.users.find_one({'email': x['email']})
    for i in x['mock_purchased']:
        if value in (i['subject_code']):
            if value2 in (i['mocks']):
                return True


def compare_dicts(d1, d2):
    same_count = 0
    different_count = 0
    not_in_d1 = -1
    for key, value in d2.items():
        if key in d1:
            if value == d1[key]:
                same_count += 1
            else:
                different_count += 1
        else:
            not_in_d1 += 1
    return same_count, different_count, not_in_d1

def update_mock_entry(email, subject_code, mock_name, new_integer, db):

    # Update the specific mock array
    query = {"email": email, "mock_purchased.subject_code": subject_code}
    update_field = f"mock_purchased.$.mocks.{mock_name}"
    db.users.update_one(query, {"$push": {update_field: new_integer}})



def Update_MarksAgv(user_marks,mock_code,db):
    
    filter_criteria={"paper_code":mock_code}
    y=db.avg.find_one({"paper_code":mock_code})

    sub_agv_marks=y['sub_agv_marks']
    No_Of_Std=y['No_Of_Std']
    new_mean=((sub_agv_marks*No_Of_Std)+user_marks)/(No_Of_Std+1)
    new_No_Of_Std=No_Of_Std+1
    update_data = {
        '$set': {
            'sub_agv_marks': int(new_mean),
            'No_Of_Std': new_No_Of_Std
        }
    }
    db.avg.update_one(filter_criteria, update_data)


def get_avg(db,pur_course):
    avg={}
    for i in pur_course:
        for j in (i['mocks']):
            y=(db.avg.find_one({'paper_code':j}))
            x=y['sub_agv_marks']
            avg[j]=x
    return avg
def get_img(db,pur_course):
    img={}
    for i in pur_course:
            x=db.mock_home.find_one({'subject_code':i['subject_code']})
            img[i['subject_name']]=x['image']
    return img
def get_number_of_question(db,pur_course):
    number={}
    x=db.paper.find ({'subject_code':pur_course})
    for i in x:
        number[i['paper_code']]=len(i['Question_paper'])
    return number
def get_name(db,pur_course):
    name={}
    x=db.paper.find ({'subject_code':pur_course})
    for i in x:
        name[i['paper_code']]=(i['paper_name'])

    return name
def check_attempt_left(db,email,sub_name,mock_name):
    data=db.users.find_one({'email':email})
    flag=True
    for i in data['mock_purchased']:
        if i['subject_code']==sub_name:
       
            if len(i['mocks'][mock_name])>4:
                flag = False 
                return flag
    return flag