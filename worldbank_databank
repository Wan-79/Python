from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium import webdriver

writer = pd.ExcelWriter("page1.xlsx")
driver = webdriver.Chrome('Chrome.exe')
driver.maximize_window()
driver.get('https://databank.worldbank.org/indicator/NY.GDP.PCAP.CD/1ff4a498/Popular-Indicators')
time.sleep(1)

def collect_data():
    table = driver.find_element(By.CLASS_NAME, 'contentReport')
    df = pd.read_html(table.get_attribute('outerHTML'))
    df[-1].to_excel(writer, index=False, header=['countries', '2000', '2001', '2002', '2003', '2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015', ''])

# selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
# all_pages = selector.find_elements(By.TAG_NAME, 'option')
# print(all_pages)
# for page in all_pages:
#     print(page.text)
#     selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
#     selector.click()
#     page.click()
#     time.sleep(10)
collect_data()
writer.close()
