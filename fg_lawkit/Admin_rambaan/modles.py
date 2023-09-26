def del_rambaan_video(db,category_code,index_no):
    query = {"rambaan_categories_code": category_code}  # Use the actual query

    # Fetch the document
    document = db.rambaan_video.find_one(query)
    document_1 = db.rambaan.find_one(query)

    # Define the index of the entry you want to delete
    entry_index = (int(index_no)-1)  # Index of the entry you want to delete

    # Remove the entry from the "videos" list
    if document and "videos" in document and 0 <= entry_index < len(document["videos"]):

        if document_1 and "course_include" in document_1 and 0 <= entry_index < len(document_1["course_include"]):


            del document["videos"][entry_index]
            del document_1["course_include"][entry_index]

            db.rambaan_video.update_one(query, {"$set": {"videos": document["videos"]}})
            db.rambaan.update_one(query, {"$set": {"course_include": document_1["course_include"]}})
