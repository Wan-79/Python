import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome("Chrome.exe")


def process(url, file_name):
    # open url and find the table element
    driver.get(url)
    # finding the table using xpaths, it can be either or
    try:
        table = driver.find_element(By.XPATH, '//*[@id="main"]/div/div/article/section/div/div/div/section/div/div[2]')
    except:
        table = driver.find_element(By.XPATH, '//*[@id="main"]/div/span/article/div/div[2]/section/div/div[2]')
    # finding the countries
    countries = table.find_elements(By.CLASS_NAME, 'country-name')
    # splitting the table into rows
    table = table.text
    table = table.split('\n')
    new_table = []
    # splitting the rows into each column
    for i in range(len(table)):
        country = countries[i].text
        row = table[i]
        row = row.replace(country, '').strip()
        row = row.split()
        row = [country] + row
        new_table.append(row)
    # making the table into a pandas dataframe
    headers = ['Country', 'Most Recent Year', 'Most Recent Value']
    df = pd.DataFrame(new_table, columns=headers)
    # converting the df to a csv file
    df.to_csv(file_name, index=False)


url_list = ['https://data.worldbank.org/indicator/NY.GDP.PCAP.KD.ZG','https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD', 'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG',
'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=XD', 'https://data.worldbank.org/indicator/NY.GDP.MKTP.CD', 'https://data.worldbank.org/indicator/NY.GDP.PCAP.KD']


for url in url_list:
    # getting the file name from the url
    name = url.split('/')[-1]
    name = name.replace('?', '.')
    # calling on the function and passing in the url and the csv name
    process(url, f'{name}.csv')
