import pymongo
from pymongo import MongoClient
import csv
from datetime import datetime
from pymongo import MongoClient, DESCENDING



def to_csv(supplier, client):
    # Opening the mongo client that is given 
    client = MongoClient(client)
    db = client["com_vtx"]
    collection = db["Asset"]
    # Creating an empty list to contain the dictionaries and vids
    final_data = []
    vids = []
    # Going through each set of data of the given supplier
    for data in collection.find({"supplier": supplier}):
        # Creating a temporary dictionary containing all the values that are wanted
        temp_dict = {
             "vid": data["vid"],
             "Supplier": data["supplier"],
             "Start Date": data["dataStartDate"],
             "End Date": data["dataEndDate"],

         }
        # creating a list of the vids
        vids.append(data["vid"])
        # Adding the dictionary to a list
        final_data.append(temp_dict)
    return vids, final_data, client



def dates_from_db(vid_lst, current_data, supplier, client):
    # Opening the database using the supplier name
    db = client[f"ven_{supplier.lower()}"]
    # Going through each group of data
    for i in range(len(vid_lst)):
        vid = vid_lst[i]
        # Splitting the vid so the first part can be used to find the correct collection
        parts = vid.split('|')
        collection = db[parts[0]]
        # Finding all the datasets that match the vid needed and finding the first and last dates
        first_object = collection.find_one({'source': vid}, sort=[('date', 1)])
        last_object = collection.find_one({'source': vid}, sort=[('date', -1)])
        # Putting the first and the last dates into the dictionaries and changing the date format so it's readable
        current_data[i]["DB Start Date"] = datetime.utcfromtimestamp(first_object['date']/1000).strftime('%Y-%m-%d %H:%M:%S')
        current_data[i]["DB End Date"] = datetime.utcfromtimestamp(last_object['date']/1000).strftime('%Y-%m-%d %H:%M:%S')
    return current_data

# List of the suppliers you want data from
suppliers = ['LPPM']
for sup in suppliers:
    vids, data, client = to_csv(sup, 'mongodb://ewan_cowan:ewan.cowan%2423@devcluster-shard-00-00.5kaf3.mongodb.net:27017,devcluster-shard-00-01.5kaf3.mongodb.net:27017,devcluster-shard-00-02.5kaf3.mongodb.net:27017/admin?ssl=true&retryWrites=true&replicaSet=atlas-kvwyjk-shard-0&readPreference=primary&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1')
    final_data = dates_from_db(vids, data, sup, client)

    # Creating a csv file with the supplier as the name
    my_file = open(f'{sup}.csv', 'w')
    writer = csv.writer(my_file)
    # Making the first row of headers
    writer.writerow(["vid", "Supplier", "Asset Start Date", "Asset End Date", "DB Start Date", "DB End Date"])
    # Writing each dictionary into each row
    for d in final_data:
        writer.writerow(d.values())
    my_file.close()
