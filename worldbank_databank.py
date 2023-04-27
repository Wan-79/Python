from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium import webdriver

driver = webdriver.Chrome('Chrome.exe')
driver.maximize_window()
driver.get('https://databank.worldbank.org/indicator/NY.GDP.PCAP.CD/1ff4a498/Popular-Indicators')
time.sleep(1)
# the amount of time given for the data to load before scrolling to the bottom
SCROLL_PAUSE_TIME = 2
done_files = []
headings = ['Countries']
# get the table headers
for head in driver.find_elements(By.CLASS_NAME, 'grid-column-text'):
    headings.append(head.get_attribute("textContent"))

def collect_data(current_writer):
    time.sleep(1)
    # find the element which contains the table
    table = driver.find_element(By.CLASS_NAME, 'dxgvCSD')
    last_height = driver.execute_script("return arguments[0].scrollHeight;", table)

    # scroll to the bottom of the table
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", table)

        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return arguments[0].scrollHeight;", table)
        if new_height == last_height:
            break
        last_height = new_height
        table = driver.find_element(By.CLASS_NAME, 'dxgvCSD')

    time.sleep(1)
    # create the dataframe and put into Excel
    df = pd.read_html(table.get_attribute('outerHTML'))
    # drop any blank columns
    for i in range(0, len(df[0].columns)):
        if df[0][i].isnull().values.all():
            df[0] = df[0].drop(columns=df[0].columns.values[i])
    df[0].to_excel(current_writer, index=False, header=headings)
    current_writer.close()


def get_files(fail_count):
    # find the dropdown and each page it contains
    selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
    all_pages = selector.find_elements(By.TAG_NAME, 'option')
    try:
        for i in range(0, len(all_pages)):
            file_name = all_pages[i].text
            if file_name in done_files:
                pass
            else:
                if fail_count < 4:
                    # open the page and collect the table
                    selector.click()
                    all_pages[i].click()
                    time.sleep(5)
                    selector = driver.find_element(By.ID, 'ctl17_ddl_page_WDI_Series')
                    all_pages = selector.find_elements(By.TAG_NAME, 'option')
                    collect_data(current_writer=pd.ExcelWriter(f"{file_name}.xlsx"))
                    print(file_name)
                    done_files.append(file_name)
                    fail_count = 0
                else:
                    done_files.append(file_name)
                    print(f'{file_name} has been skipped')
                    fail_count = 0
    # if there's an error it will refresh and try again unless it fails 4 times then it skips the page
    except:
        driver.get('https://databank.worldbank.org/indicator/NY.GDP.PCAP.CD/1ff4a498/Popular-Indicators')
        fail_count += 1
        get_files(fail_count)


fails = 0
get_files(fails)




