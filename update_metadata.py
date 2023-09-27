import pandas as pd
import pymongo
from pymongo import MongoClient
import csv
from datetime import datetime
from pymongo import MongoClient, DESCENDING
import json, re
from bson import json_util


with open("test_LPPM.json", 'r') as f:
    data = json.load(f)
report_path = "LPPM_new.csv"
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
    iso_start_date = datetime.strptime(new_data_start_date, "%Y-%m-%d %H:%M:%S").isoformat()
    iso_end_date = datetime.strptime(new_data_end_date, "%Y-%m-%d %H:%M:%S").isoformat()
    update_data_start = {"$set": {
        "dataStartDate": iso_start_date
    }
    }
    update_data_end = {"$set": {
        "dataEndDate": iso_end_date
    }
    }
    for j in data:
        if iso_start_date != j["dataStartDate"]:
            j["dataStartDate"] = update_data_start
        if iso_end_date != j["dataEndDate"]:
            j["dataEndDate"] = update_data_end
        data[data.index(j)] = j
    with open("test_LPPM.json", 'w') as file:
        json.dump(data, file, indent=4)
        
for index, row in report_df.iterrows():
    if row["start_date_observation"] is False or row["end_date_observation"] is False:
        update_assets_by_asset_id(row["assetId"], row["db_start_date"], row["db_end_date"])
