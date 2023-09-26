### poke mocks
def delete_mock_entry(db, subject_code, mock_code):

    collection = db['users']  # Replace with your collection name

    # Define the query to find the document based on subject_code
    query = {"mock_purchased.subject_code": subject_code}

    # Define the update operation to remove the specified mock_code
    update_operation = {
        "$unset": {
            f"mock_purchased.$.mocks.{mock_code}": 1
        }
    }

    # Update the document to remove the specified mock_code
    result = collection.update_many(query, update_operation)

    # Check if any document was modified
    

### poke subject ###
def delete_mock_purchased_element(db, subject_code):
    collection = db['users']
    
    filter = {
        "mock_purchased.subject_code": subject_code
    }

    # Define the update operation to remove the element from the mock_purchased array
    update = {
        "$pull": {
            "mock_purchased": {
                "subject_code": subject_code
            }
        }
    }

    # Use the update_one method to update the document
    result = collection.update_one(filter, update)

    # Check if the update was successful
    

def question_paper(db):
    x=db.paper.find()
    d={}
    for i in x:
        subject_code=i['subject_code']
        subject_name=i['subject_name']
        if subject_code in d:
            n=d[subject_code]['no_of_paper']
            n=n+1
            d[subject_code]['no_of_paper']=n
        else:
           
            d[subject_code]={'subject_name':subject_name,'no_of_paper':1}
    return d