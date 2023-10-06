import pymongo
from pymongo import MongoClient
from bson import ObjectId

myclient = pymongo.MongoClient("") # mongodb string


connect = "" # mongodb string
dev_client = MongoClient(connect)

collection = dev_client["com_vtx"]["ETLDefinition"]
supplier_list = list(collection.distinct("supplier"))

for sup in supplier_list:
    my_ven_db = myclient[f"ven_{sup.lower()}"]
    for document in my_ven_db.list_collection_names():
        for object in my_ven_db[document].find({}):
            if 1 < len(object["values"]) < 20:
                lst = [object["values"][i]["updatedTime"] for i in range(len(object["values"]))]
                high = lst[0]
                for i in range(1, len(lst)):
                    if lst[i] >= high:
                        high = lst[i]

                newest = object["values"][lst.index(high)]
                object["values"] = newest
                object_id = ObjectId(object['_id'])
                filter_query = {'_id': object_id}
                update_query = {'$set': {'values': [f'{object["values"]}']}}

                my_ven_db[document].update_one(filter_query, update_query)
