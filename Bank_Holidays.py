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
a = pd.read_excel(r"C:\Users\ewanc\OneDrive\Documents\Holiday data sheet.xlsx")

def get_table(url, xpath, DATE_FORMAT, date_description):
    # Using the date format to create a regex pattern that will take the date out of a line
    pattern = [{
        '%': '%d',
        'Pattern': '\d{1,2}'
    },{
        '%': '%b',
        'Pattern': '[a-zA-Z]{3}'
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
    # opening the link and finding the table
    driver.get(url)
    time.sleep(1)
    table = driver.find_element(By.XPATH, xpath)
    # splitting the table every line to give a list
    table = table.text.split('\n')

    # getting rid of useless rows
    for row in list(table):
        if not row[0].isdigit():
            table.remove(row)
        if row.startswith(datetime.date.today().strftime("%Y")):
            table.remove(row)
    # getting rid of any days of week in rows
    for c in range(len(table)):
        date_format = DATE_FORMAT
        row = table[c]
        for day in days_of_week:
            row = row.replace(day, '', 1)

        # creating a dictionary to be used for formatting, and finding the date in the row
        temp_dict = {}
        row_date_original = re.search(re_pattern, row).group()
        # adding the current year to a date if it does not already have a year
        if '%y' and '%Y' not in DATE_FORMAT:
            year = datetime.date.today().strftime("%Y")
            row_date = row_date_original + str(year)
            date_format = DATE_FORMAT + '%Y'
        else:
            row_date = row_date_original
        # converting the date extracted into a date format and adding it to the dictionary
        date = datetime.datetime.strptime(row_date, date_format)
        date = date.strftime("%m/%d/%Y")
        temp_dict['date'] = date
        # getting the description alone in the row by removing the date from the row
        row = row.replace(row_date_original, '')
        # checking if we just have the description left, if not removing anything else that is not the description
        if not date_description:
            for i in row:
                if i.isdigit():
                    row = row.replace(i, '')
        row = row.strip()
        # adding the description to the dictionary
        temp_dict['description'] = row
        # putting the dictionary into a list
        bank_holidays.append(temp_dict)
    print(bank_holidays)


for i in range(0,2):
    get_table(a['URL'][i], a['Xpath'][i], a['Date Format'][i], a['Only date and description'][i])
