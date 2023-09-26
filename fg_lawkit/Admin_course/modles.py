from fg_lawkit import db



def push_data_to_content(course_code, element_name, data_to_push_link,data_to_push_nolink):
    filter = {'course_code': course_code}
    filter1 = 'content.' + element_name  
    db.course.update_one(filter, {"$push": {filter1: data_to_push_link}})
    db.course_home.update_one(filter, {"$push": {filter1: data_to_push_nolink}})




def push_module(name,code,db):
    filter={'course_code':code}
    content=db.course.find_one(filter)['content']
    content[name]=[]
    db.course_home.update_one(filter,{"$set":{'content':content}})
    db.course.update_one(filter,{"$set":{'content':content}})


def pull_data_from_content(course_code, element_name, title_to_pull, description_to_pull):
    filter = {'course_code': course_code}
    filter1 = 'content.' + element_name

    # Find the document matching the course_code
    course_doc = db.course.find_one(filter)

    if course_doc:
        # Get the 'content.element_name' array
        content_array = course_doc['content'].get(element_name, [])

        # Create a new list excluding the document that matches the title and description
        updated_content_array = [item for item in content_array if item['title'] != title_to_pull or item['description'] != description_to_pull]

        # Update the document with the modified 'content.element_name' array
        db.course.update_one(filter, {"$set": {filter1: updated_content_array}})
        db.course_home.update_one(filter, {"$set": {filter1: updated_content_array}})
    # else:
    #     print(f"Course with course_code '{course_code}' not found.")

