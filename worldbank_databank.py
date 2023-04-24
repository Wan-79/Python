from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium import webdriver

driver = webdriver.Chrome('Chrome.exe')
driver.maximize_window()
driver.get('https://databank.worldbank.org/indicator/NY.GDP.PCAP.CD/1ff4a498/Popular-Indicators')
time.sleep(1)
SCROLL_PAUSE_TIME = 1


def collect_data(current_writer):
    time.sleep(1)
    table = driver.find_element(By.CLASS_NAME, 'dxgvCSD')
    last_height = driver.execute_script("return arguments[0].scrollHeight;", table)

    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", table)

        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return arguments[0].scrollHeight;", table)
        if new_height == last_height:
            break
        last_height = new_height
        table = driver.find_element(By.CLASS_NAME, 'dxgvCSD')
    time.sleep(1)
    table = driver.find_element(By.CLASS_NAME, 'dxgvCSD')
    df = pd.read_html(table.get_attribute('outerHTML'))
    df[0].to_excel(current_writer, index=False, header=['Countries', '2000', '2001', '2002', '2003', '2004','2005','2006', '2007', '2008','2009','2010','2011','2012','2013','2014','2015', ''])
    current_writer.close()


selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
all_pages = selector.find_elements(By.TAG_NAME, 'option')

for i in range(0, len(all_pages)):
    selector.click()
    all_pages[i].click()
    time.sleep(5)
    selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
    all_pages = selector.find_elements(By.TAG_NAME, 'option')
    collect_data(current_writer=pd.ExcelWriter(f"{all_pages[i].text}.xlsx"))
    print(all_pages[i].text)
    selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
    all_pages = selector.find_elements(By.TAG_NAME, 'option')

