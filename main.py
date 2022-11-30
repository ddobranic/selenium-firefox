from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from deta import Deta 
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

deta = Deta(os.getenv('DETA_PROJECT_KEY'))
db = deta.Base("vocab")
db_def = deta.Base("vocab-def")


def app():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    for i in range(0,5948):
        key = str(i).zfill(4)
        print(key)
        res = db.get(key)
        # print(res['link'])
        try:
            driver.get(res['link'])
            print(driver.title)
            elements = driver.find_elements(By.CSS_SELECTOR,'li.sense')
            arr = []
            for element in elements:
                all_text = element.text
                texts = all_text.split('\n')
                define = texts[0].strip()
                exs = element.find_elements(By.CSS_SELECTOR,'li>.examples>li')
                ex_arr = []
                for ex in exs:
                    ex_str = ex.text
                    ex_arr.append(ex_str)
                data = {
                    'def': define,
                    'ex': ex_arr
                }
                arr.append(data)
            db_def.put({'key':key, 'eng-data': arr})
        except:
            print('error with key', key)
            with open('error.txt', 'a') as f:
                f.write(key+'\n')
    driver.quit()

if __name__ == "__main__":
    start_time = datetime.now()
    print('Time start:', str(start_time))
    app()
    # for i in range(0,20):
    #     key = str(i).zfill(4)
    #     db_def.delete(key)
    end_time = datetime.now()
    print('Time end:', str(end_time))
    print('Time difference:', str(end_time - start_time))
