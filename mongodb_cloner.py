import pymongo
from pymongo import MongoClient

def db_cloner(connection, sup):
    # creating the local client, databases and collections
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    my_com_db = myclient["com_vtx"]
    my_ven_db = myclient[f"ven_{sup.lower()}"]
    my_etl_col = my_com_db["ETLDefinitions"]
    my_asset_col = my_com_db["Asset"]

    # opening the dev client, databases and collections needed to be cloned
    client = MongoClient(connection)
    com_db = client["com_vtx"]
    ven_db = client[f"ven_{sup.lower()}"]
    collection_etl = com_db["ETLDefinition"]
    collection_asset = com_db["Asset"]
    # creating lists of the data for the specific supplier data is wanted for
    etl_defs = [x for x in collection_etl.find({"supplier": sup})]
    sup_assets = [i for i in collection_asset.find({"supplier": sup})]
    col_names = ven_db.list_collection_names()
    # cloning all collections from the ven_supplier database to the local client
    for name in col_names:
        temp_collection = ven_db[name]
        new_col = my_ven_db[name]
        temp_list = [c for c in temp_collection.find({})]
        new_col.insert_many(temp_list)
    # inserting the lists into the local collections
    my_etl_col.insert_many(etl_defs)
    my_asset_col.insert_many(sup_assets)


supplier = "EURIBOR"
connect = "mongodb://ewan_cowan:ewan.cowan%2423@devcluster-shard-00-00.5kaf3.mongodb.net:27017,devcluster-shard-00-01.5kaf3.mongodb.net:27017,devcluster-shard-00-02.5kaf3.mongodb.net:27017/admin?ssl=true&retryWrites=true&replicaSet=atlas-kvwyjk-shard-0&readPreference=primary&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1"
db_cloner(connect, supplier)
