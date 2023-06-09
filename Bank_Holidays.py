import pandas as pd
import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import time
import datetime
from bson.objectid import ObjectId


driver = webdriver.Chrome('Chrome.exe')
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
a = pd.read_excel(r"C:\Users\ewanc\OneDrive\Documents\Country Holidays 2.xlsx")


def get_actual_table(url, xpath, date_header, desc_header, table_header):
    # opening the link and finding the table
    driver.get(url)
    time.sleep(1)
    table = driver.find_element(By.XPATH, xpath).get_attribute("outerHTML")
    # reading the table into a pandas df
    table = pd.read_html(table)
    table = table[0]
    # Getting the description from the table
    if pd.isna(table_header):
        description = table[desc_header]
    else:
        description = table[table_header][desc_header]
    dates = table[date_header]
    office_list = []
    # creating a similar list with the date and description as each string
    for i in range(len(dates)):
        temp_str = dates[i] + ' ' + description[i]
        office_list.append(temp_str)
    return office_list


def get_UK_table(url, xpath):
    # opening the link and finding the table
    driver.get(url)
    time.sleep(1)
    table = driver.find_element(By.XPATH, xpath)
    # splitting the table every line to give a list
    table = table.text.split('\n')
    return table


def get_list(url, xpath):
    # opening the link and finding the list
    driver.get(url)
    time.sleep(1)
    holiday_list = driver.find_element(By.XPATH, xpath).get_attribute('textContent')
    holiday_list = holiday_list.split(',')
    for i in range(len(holiday_list)):
        holiday_list[i] = holiday_list[i].strip()
    return holiday_list


def convert_data(table, DATE_FORMAT, remove_dow):
    # Using the date format to create a regex pattern that will take the date out of a line
    pattern = [{
        '%': '%d',
        'Pattern': '\d{1,2}'
    },{
        '%': '%b',
        'Pattern': '[a-zA-Z]{3,4}'
    },{
        '%': '%B',
        'Pattern': '[a-zA-Z]{3,9}'
    },{
        '%': '%m',
        'Pattern': '\d{1,2}'
    },{
        '%': '%y',
        'Pattern': '\d{1,2}'
    },{
        '%': '%Y',
        'Pattern': '\d{4}'
    },]
    re_pattern = DATE_FORMAT
    for d in pattern:
        if d['%'] in DATE_FORMAT:
            re_pattern = re_pattern.replace(d['%'], d['Pattern'])
    bank_holidays = []
    # getting rid of any days of week in rows
    for row in list(table):
        if remove_dow:
            for day in days_of_week:
                row = row.replace(day, ' ')
        # Getting rid of any special characters
        special_characters = ['@', '#', '$', '*', '&', '†', ',']
        for i in special_characters:
            row = row.replace(i, "")
        row = row.strip()
        row = row.replace(' ', ' ')
        date_format = DATE_FORMAT
        # creating a dictionary to be used for formatting, and finding the date in the row
        temp_dict = {}
        try:
            row_date_original = re.match(re_pattern, row)
            row_date_original = row_date_original.group()
        except:
            table.remove(row)
            continue
        # adding the current year to a date if it does not already have a year
        if '%y' and '%Y' not in DATE_FORMAT:
            year = datetime.date.today().strftime("%Y")
            row_date = row_date_original + ' ' + str(year)
            date_format = DATE_FORMAT + ' ' + '%Y'
        else:
            row_date = row_date_original

        if '%b' in DATE_FORMAT:
            try:
                full_month = re.search('[a-zA-Z]{4}', row_date).group()
                part_month = full_month.replace(full_month[-1], '')
                row_date = row_date.replace(full_month, part_month)
            except:
                pass

        # converting the date extracted into a date format and adding it to the dictionary
        date = datetime.datetime.strptime(row_date, date_format)
        date = date.strftime("%m/%d/%Y")
        temp_dict['date'] = date
        # getting the description alone in the row by removing the date from the row
        row = row.replace(row_date_original, '')
        special_characters = ['@', '#', '$', '*', '&', '-', '–', '†', ',']
        for i in special_characters:
            row = row.replace(i, "")
        row = row.strip()
        # adding the description to the dictionary
        temp_dict['description'] = row
        # putting the dictionary into a list
        bank_holidays.append(temp_dict)
    print(bank_holidays)
    return bank_holidays


def compare(data, ID):
    # open the holiday data from mongodb and export it
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = my_client["local"]
    mycol = mydb["holidays"]
    # find the current countries holiday data
    mydoc = mycol.find_one({'_id': ObjectId(ID)})
    bank_holiday_dates = []
    # put both of the datees into the same format
    for bank_hol in list(mydoc["holidayList"]):
        mydoc['holidayList'][bank_hol]['date'] = mydoc['holidayList'][bank_hol]['date'].strftime("%m/%d/%Y")
        bank_holiday_dates.append(mydoc["holidayList"][bank_hol]["date"])
    # compare the bank holidays using the dates and add those that aren't already there
    for specific_bank_hol in data:
        if specific_bank_hol["date"] not in bank_holiday_dates:
            mydoc["holidayList"][len(mydoc["holidayList"])] = specific_bank_hol
    return mydoc


for i in range(83, len(a['URL']) -1):
    print((a['URL'][i]))
    # if a['Content Type'][i] == 'UK':
    #     data_list = get_UK_table(a['URL'][i], a['Xpath'][i])
    # elif a['Content Type'][i] == 'List':
    #     data_list = get_list(a['URL'][i], a['Xpath'][i])
    if a['Content Type'][i] == 'Table':
        data_list = get_actual_table(url=a['URL'][i], xpath=a['Xpath'][i], date_header=a['Date header'][i], desc_header=a['Column header'][i], table_header=a['Table header'][i])
    else:
        continue
    holiday_dates = convert_data(data_list, a['Date Format'][i], a['DOW'][i])
    # compare(holiday_dates, a['DatabaseID'][i])

