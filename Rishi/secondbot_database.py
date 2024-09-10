import pymongo, os 
from biisal.vars import Var
  
  
dbclient = pymongo.MongoClient(Var.DB_URI) 
database = dbclient[Var.DB_NAME] 
  
  
user_data = database['users'] 
  
  
  
async def present_user(user_id : int): 
    found = user_data.find_one({'_id': user_id}) 
    return bool(found) 
  
async def add_user(user_id: int): 
    user_data.insert_one({'_id': user_id}) 
    return 
  
async def full_userbase(): 
    user_docs = user_data.find() 
    user_ids = [] 
    for doc in user_docs: 
        user_ids.append(doc['_id']) 
  
    return user_ids 
 
async def del_user(user_id: int): 
    user_data.delete_one({'_id': user_id}) 
    return
