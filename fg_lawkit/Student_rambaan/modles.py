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

import random
import string

def generate_custom_uuid(length):
    characters = string.ascii_letters + string.digits
    custom_uuid = ''.join(random.choice(characters) for _ in range(length))
    return custom_uuid

from fuzzywuzzy import fuzz
def perform_fuzzy_search(query,db):
    query=query.strip()
    search_results = []
    collection=db['rambaan_video']
    # Find documents where at least one tag has a similarity score of 70 or higher
    cursor = collection.find({
        'videos.tags': {
            '$elemMatch': {
                '$in': [tag for tag in collection.distinct('videos.tags') if fuzz.ratio(tag, query) >= 60]
            }
        }
    })

    for document in cursor:
        for video in document['videos']:
            # Check if any tag in the video's tags array matches the query
            if any(fuzz.ratio(tag, query) >= 70 for tag in video.get('tags', [])):
                # Extract and append the relevant part of the video
                relevant_video_info = {
                    'title': video.get('title', ''),
                    'dis': video.get('dis', ''),
                    'rating': video.get('rating', 0),
                    'link': video.get('link', ''),
                    'tags': video.get('tags', [])
                }
                search_results.append(relevant_video_info)

    return search_results

def check_have_rambaan(db,email):
    data=db.users.find_one({'email':email})
    return data['rambaan']['status']
