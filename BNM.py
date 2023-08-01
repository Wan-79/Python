from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
from selenium import webdriver
import csv

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
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    html_table = soup.find(id="dvData2")
    html_rows = html_table.find_all("tr")
    table_text = []
    for row in html_rows:
        temp_list = []
        for cell in row.find_all(['td', 'th']):
            cell_text = cell.get_text(strip=True)
            temp_list.append(cell_text)
        table_text.append(temp_list)
    with open(f'{file_name}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(table_text)
        f.close()

