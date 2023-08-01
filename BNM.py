from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time


# opening mongodb and the ETLDefinition collection
driver = webdriver.Chrome()
client = MongoClient("")
db = client["com_vtx"]
collection = db["ETLDefinition"]
data_list = []
# getting the url and the id from each BNM dataset, id being teh filename
for data in collection.find({"supplier": "BNM"}):
    temp_dict = {
        "url": data["collectorSettings"]["url"],
        "file_name": data["_id"]
    }
    data_list.append(temp_dict)

# going through the links and scraping the data and adding it to a csv
for dict in data_list:
    link = dict["url"]
    file_name = dict["file_name"]
    print(file_name)
    driver.get(link)
    time.sleep(2)
    html_table = driver.find_element(By.ID, "dvData2")
    table = pd.read_html(html_table.get_attribute("outerHTML"), index=False)
    table[0].to_csv(file_name)

