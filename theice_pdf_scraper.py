from datetime import datetime
import time
import pandas as pd
import tabula
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium import webdriver
import pickle
from selenium.webdriver.common.keys import Keys
import os
import glob


def pdf(file):
    # getting the date and time the program is run at
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    formatted_time = current_time.strftime("%H-%M-%S")
    print(current_date, current_time)
    filename = f'{current_date}_{formatted_time}.csv'
    with open(fr"{file}", 'rb') as file:
        file_contents = file.read()
        pdf_file = BytesIO(file_contents)
    # reading the tables from the pdf file
    tables = tabula.read_pdf(pdf_file, pages='all', lattice=False, pandas_options={'header': None})
    table = pd.concat(tables)
    table = table.reset_index(drop=True)
    # creating the headers for the table
    table.columns = ['COMMODITY NAME', 'CONTRACT MONTH', 'OPEN', 'HIGH', 'LOW', 'CLOSE',
                     'SETTLE PRICE', 'SETTLE CHANGE', 'TOTAL VOLUME', 'OI', 'CHANGE', 'EFP', 'EFS',
                     'BLOCK VOLUME', 'SPREAD VOLUME']

    # only keeping the rows that has the first column of tfm
    for index, row in table.iterrows():
        if row[0] != 'TFM':
            table = table.drop(index)
    table.to_csv(filename, index=False)
    print(table)


def get_download():
    driver = webdriver.Chrome()
    ## Tried to use cookies to get past captcha
    # driver.get('https://www.theice.com/marketdata/reports/159')
    # cookies = pickle.load(open("cookies.pkl", "rb"))
    # for cookie in cookies:
    #     driver.add_cookie(cookie)
    # time.sleep(2)
    
    driver.get('https://www.theice.com/marketdata/reports/159')
    time.sleep(1)
    # driver.find_element(By.XPATH, '/html/body/dialog/div[2]/button').click()
    time.sleep(15)
    # searching for tfm
    driver.find_element(By.XPATH, '//*[@id="form_selectedContract_chosen"]').click()
    search = driver.find_element(By.XPATH, '//*[@id="form_selectedContract_chosen"]/div/div/input')
    search.send_keys('TFM-Dutch TTF Natural Gas Futures')
    search.send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, '//*[@id="report-content"]/form/input[5]').click()
    time.sleep(3)
    # clicking the download object
    driver.find_element(By.XPATH, '//*[@id="report-content"]/div[2]/div/table/tbody/tr[1]/td[2]/form/input[8]').click()
    time.sleep(2)
    # finding the path for the download
    download_dir = os.path.expanduser("~/Downloads")
    files = glob.glob(os.path.join(download_dir, "*"))
    newest_file = max(files, key=os.path.getctime)
    return newest_file


file_path = get_download()
pdf(file_path)


