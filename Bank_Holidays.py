from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time
import datetime
import re
from pymongo import MongoClient
import csv
from datetime import datetime
import json

full_list = []
report_list = []

a = pd.read_excel(r"C:\Users\ewanc\OneDrive\Full holiday sheet.xlsx")
df = pd.DataFrame(a)

my_driver = webdriver.Chrome()

# Get current date and time
current_datetime = datetime.now()

# Extract date and time components
current_date = current_datetime.date()
current_time = current_datetime.time()

formatted_time = current_time.strftime("%H-%M-%S")

# Print the results
print(current_date, formatted_time)

# a function which turns the dataframes given into the correct format and puts them to mongodb
def df_conversion(configuration, df):

    final_list = []
    matches = []
    if configuration['content_type'] == 'Table':
        # Adding the dates found from the website to the matches list
        if pd.isna(configuration["second_column_header_dates"]):
            try:
                df[str(configuration["column_header_dates"])].apply(lambda x: matches.extend(re.findall(configuration["pattern"], x)))
            except:
                df[configuration["column_header_dates"]].apply(lambda x: matches.extend(re.findall(configuration["pattern"], x)))
        else:
            df[str(configuration["second_column_header_dates"])][str(configuration["column_header_dates"])].apply(lambda x: matches.extend(re.findall(configuration["pattern"], x)))
    # Finding the dates differently for the list as there will be some rows that are useless
    if configuration['content_type'] == 'List':
        df[configuration["column_header_dates"]].apply(lambda x: matches.extend(re.findall(configuration["pattern"], x)))

    # Converting the dates into the desired date format
    if configuration["is_year_included"] == False:
        for i in range(len(matches)):
            date_str = matches[i]
            # removing any ordinals if they come after the number
            if configuration['ordinals'] == True:
                date_str = re.sub(r"(st|nd|rd|th)", "", date_str)
            # converting the date into the desired format
            date_str = date_str + " 2023"
            date = datetime.strptime(date_str, configuration["date_format"])
            converted_date = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            matches[i] = converted_date

    if configuration["is_year_included"] == True:
        for i in range(len(matches)):
            date_str = matches[i].strip()
            if configuration['ordinals'] == True:
                date_str = re.sub(r"(st|nd|rd|th)", "", date_str)
            date = datetime.strptime(date_str, configuration["date_format"])
            converted_date = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            matches[i] = converted_date

    # Getting the dates and descriptions into a dicitionary, then appending the dicitonary containing the date and description to one dicitonary that contains all the URLs data that has been scraped
    if pd.isna(configuration["table_header"]):
        holiday_dict = {}
        for i in range(len(matches)):
            temp_dict_1 = {"$date": matches[i]}
            temp_dict_4 = {"description": df[configuration["column_header_description"]][i]}
            temp_dict_2 = {"date": temp_dict_1}
            temp_dict_2.update(temp_dict_4)
            holiday_dict[str(i)] = temp_dict_2

        # Create the main dictionary
        main_dict = {
            # "_id": {"$oid": ""},
            "code": configuration["code"],
            "name": configuration["country"],
            "description": configuration["country"],
            "calendarRule": "",
            "modifiedBy": "",
            "holidayList": holiday_dict
        }

        # Convert the main dictionary to a JSON string
        json_string = json.dumps(main_dict)

        # print(json_string)
    else:
        for i in range(len(matches)):
            holiday_dict = {}
            temp_dict_1 = {"$date": matches[i]}
            temp_dict_4 = {"description" : df[configuration["table_header"]][configuration["column_header_description"]][i]}
            temp_dict_2 = {"date": temp_dict_1}
            temp_dict_2.update(temp_dict_4)
            holiday_dict[str(i)] = temp_dict_2

        main_dict = {
            "code": configuration["code"],
            "name": configuration["country"],
            "description": configuration["country"],
            "calendarRule": "",
            "modifiedBy": "",
            "holidayList": holiday_dict
        }

        # Convert the main dictionary to a JSON string
        json_string = json.dumps(main_dict)

    # print(json_string)

    # Adding the output for each URL to a MongoDB Database
    client = MongoClient("mongodb://localhost:27017/")
    db = client["local"]
    collection = db["Calendars"]
    collection.insert_one(main_dict)

def table(configuration):
    # Removing any whitespace from the Header Dates value being read from excel
    try:
        configuration["column_header_dates"].strip()
    except:
        pass


    my_driver.get(configuration["URL"])
    time.sleep(3)

    # Collect table from website using xpath
    table = my_driver.find_element(By.XPATH, configuration["selector_value"])

    # Reading the table and converting into a dataframe
    table1 = table.get_attribute("outerHTML")
    df1 = pd.read_html(table1)
    df1 = df1[0]
    # Getting rid of rows with more than 2 NA values
    df1.dropna(inplace=True, thresh=2)

    # Resetting the index to make sure the numbers are in the right place after removing NA rows
    df1.reset_index(drop=True, inplace=True)

    df_conversion(configuration, df1)

# Creating a list function to scrape data from websites that use a list
def lst(configuration):
    # create empty lists needed for later
    matches = []
    dates = []
    descriptions = []
    try:
        configuration["column_header_dates"].strip()
    except:
        pass
    my_driver.get(configuration["URL"])
    time.sleep(3)
    # collecting the list container from the site
    element = my_driver.find_element(By.XPATH, configuration['selector_value'])
    # collecting all the dates by their class
    date_elements = element.find_elements(By.CLASS_NAME, configuration["date_class"])
    for date in date_elements:
        dates.append(date.text)
    # checking if the site gives holiday descriptions
    if not pd.isna(configuration["description_class"]):
        # for some sites have to use the xpath to find the descriptions as they have no specific class
        if configuration['xpath_used']:
            for i in range(1, len(dates)):
                descriptions.append(element.find_element(By.XPATH, f'//*[@id="HolidayList"]/div[{i}]/div[2]/ul/li').text)
        # otherwise finding it by their class
        else:
            des_elements = element.find_elements(By.CLASS_NAME, configuration["description_class"])
            for des in des_elements:
                descriptions.append(des.text)
    # if the site doesn't give a description then creating a blank list
    else:
        descriptions = [None] * len(dates)
    # making the separate lists into one dataframe
    df1 = pd.DataFrame(list(zip(dates, descriptions)), columns=['Date', 'Holiday'])
    drop_list = []
    # getting rid of any rows that don't have dates or have too many dates as these will be other elements with the
    # same class name
    for index, row in df1.iterrows():
        useful_row = re.findall(fr"{configuration['pattern']}", row['Date'])
        if len(useful_row) != 1:
            drop_list.append(index)
    df1.drop(drop_list,axis=0,inplace=True)
    # Resetting the index to make sure the numbers are in the right place after removing invalid rows
    df1.reset_index(drop=True, inplace=True)
    df_conversion(configuration, df1)


# Create a report function which runs the functions and gives feedback on each row
def report(configuration):
    report = {}
    report["code"] = configuration["code"]
    report["name"] = configuration["country"]
    report["URL"] = configuration["URL"]
    report["Content Type"] = configuration["content_type"]

    # List to store true or false values
    results = True
    if row["Content Type"] == "Table":
        try:
            table(configuration=config)
        except Exception:
            results = False
    if row["Content Type"] == "List":
        try:
            lst(configuration=config)
        except Exception:
            results = False

    report["Execution status"] = results
    report_list.append(report)


# starting_numb = 0
for index, row in df.iterrows():
    # if index == starting_numb:
    config = {
        "URL": row["URL"],
        "code": row["Code"],
        "country": row["Country"],
        "content_type": row["Content Type"],
        "selector_value": row["Selector Value"],
        "date_format": row["Date Format"],
        "pattern": row["Pattern"],
        "is_year_included": row["Is Year Included"],
        "column_header_dates": row["Column Header for Dates"],
        "second_column_header_dates": row["Second Column Header for Dates"],
        "column_header_description": row["Column Header for Description"],
        "table_header": row["Table Header"],
        "date_class": row["Date Class"],
        "description_class": row["Description Class"],
        "ordinals": row["Ordinals"],
        "xpath_used" : row["Needs Xpath"]
    }

    report(configuration=config)

print(report_list)

# Putting the report into a CSV

field_names = ["code", "name", "URL", "Content Type", "Execution status"]

# Specify the filename for the CSV file
filename = f"{current_date}_{formatted_time}.csv"

# Write the list of dictionaries to a CSV file
with open(filename, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=field_names)

    # Write the header
    writer.writeheader()

    # Write the data rows
    writer.writerows(report_list)



