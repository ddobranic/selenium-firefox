from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from deta import Deta 
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

deta = Deta(os.getenv('DETA_PROJECT_KEY'))
db = deta.Base("vocab")
db_def = deta.Base("vocab-def")
db_err = deta.Base("error")

options = Options()
options.add_argument("--headless")

def main_data():
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000?dataset=english&list=ox5000')
    print(driver.title)
    elements = driver.find_elements(By.CSS_SELECTOR,'.top-g>li')
    # driver.get('https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000')
    # time.sleep(2)
    # ##### select ex5000 #######
    # driver.execute_script("arguments[0].click();",driver.find_element(By.ID, 'wordlistsFilters'))
    # time.sleep(2)
    # select_element = driver.find_element(By.ID, 'filterList')
    # select = Select(select_element)
    # time.sleep(2)
    # select.select_by_value('ox5000')
    # time.sleep(2)
    # driver.execute_script("arguments[0].click();",driver.find_element(By.CSS_SELECTOR, '.wordlistButton_Filter_Submit'))
    # time.sleep(3)
    # check_element = driver.find_element(By.ID,'wordlistsBreadcrumb').text
    # if check_element == 'English Oxford 5000 All':
    #     status = True
    # else:
    #     status = False
    for i, element in enumerate(elements):
        key = str(i).zfill(4)
        word = element.get_attribute('data-hw')
        ox3 = element.get_attribute('data-ox3000')
        ox5 = element.get_attribute('data-ox5000')
        link = element.find_element(By.TAG_NAME,'a').get_attribute('href')
        pos = element.find_element(By.TAG_NAME,'span').text
        try: 
            uk = element.find_element(By.CSS_SELECTOR,'div>.pron-uk').get_attribute('data-src-mp3')
            us = element.find_element(By.CSS_SELECTOR,'div>.pron-us').get_attribute('data-src-mp3')
        except:
            uk = ''
            us = ''
        print(key,'-',word,'-',pos)
        data = {
            'key': key,
            'word': word,
            'ox3': ox3,
            'ox5': ox5,
            'link': link,
            'pos': pos,
            'uk': uk,
            'us': us,
        }
        db.put(data)
    driver.quit()

def each_link():
    driver = webdriver.Firefox(options=options)
    for i in range(435,437):
        key = str(i).zfill(4)
        print(key)
        res = db.get(key)
        # print(res['link'])
        try:
            driver.get(res['link'])
            # print(driver.title)
            elements = driver.find_elements(By.CSS_SELECTOR,'.entry>ol>li.sense')
            arr = []
            for element in elements:
                all_text = element.text
                texts = all_text.split('\n')
                define = texts[0].strip()
                def_only = element.find_element(By.CSS_SELECTOR,'.def')
                def_only = def_only.text
                if not define.__contains__(def_only):
                    define = define + ' ' + def_only
                exs = element.find_elements(By.CSS_SELECTOR,'li>.examples>li')
                ex_arr = []
                for ex in exs:
                    ex_str = ex.text
                    if ex_str!="":
                        ex_arr.append(ex_str)
                data = {
                    'def': define,
                    'ex': ex_arr
                }
                arr.append(data)
            db_def.put({'key':key, 'eng-data': arr})
        except:
            print("error", key)
            db_err.put({'key': key, 'link': res['link']})
    driver.quit()

if __name__ == "__main__":
    start_time = datetime.now()
    print('Time start:', str(start_time))
    # main_data()
    each_link()
    # for i in range(1100,1158):
    #     key = str(i).zfill(4)
    #     db_def.delete(key)
    end_time = datetime.now()
    print('Time end:', str(end_time))
    print('Time difference:', str(end_time - start_time))
