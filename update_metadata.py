import pandas as pd
import pymongo
from pymongo import MongoClient
import csv
from datetime import datetime
from pymongo import MongoClient, DESCENDING
report_path = "LPPM_new.csv"
client = "mongodb://localhost:27017/"
# Opening the mongo client that is given
client = MongoClient(client)
db = client["com_vtx"]
asset_collection = db["Asset"]
report_df = pd.read_csv(report_path)
def add_bulk_update_status(df):
    unique_vid_list = df['vid'].unique().tolist()
    for vid in unique_vid_list:
        # Filter the DataFrame with the current 'vid'
        filtered_df = df[df['vid'] == vid]
        DB_start_Date = filtered_df['DB Start Date'].unique().tolist()
        DB_end_Date = filtered_df['DB End Date'].unique().tolist()
        # Print the filtered DataFrame
        # print(f"DataFrame for vid: {vid}")
        print("===============================================================")
        print(vid)
        print(DB_start_Date)
        print(DB_end_Date)
        print("===============================================================")
def update_assets_by_asset_id(asset_id, new_data_start_date, new_data_end_date):
    filter_criteria = {"_id": asset_id}
    iso_start_date = datetime.strptime(new_data_start_date, "%Y-%m-%d %H:%M:%S")
    iso_end_date = datetime.strptime(new_data_end_date, "%Y-%m-%d %H:%M:%S")
    update_data = {"$set": {
        "dataStartDate": iso_start_date,
        "dataEndDate": iso_end_date
    }
    }
    result = asset_collection.update_one(filter_criteria, update_data)
    if result.modified_count > 0:
        return True
    else:
        return False
for index, row in report_df.iterrows():
    if row["start_date_observation"] is True or row["end_date_observation"] is True:
        update_assets_by_asset_id(row["assetId"], row["db_start_date"], row["db_end_date"])
