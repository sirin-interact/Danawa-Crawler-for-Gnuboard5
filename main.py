# -*- coding: utf-8 -*-
import time
import os
import sys
import os.path
import traceback
import json
import datetime
import gc
import pyautogui
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from danawa_crawler import config
from danawa_crawler import commonLib
from danawa_crawler import networkLib



from danawa_crawler.config import LOGLEVEL

commonLib.print_log(LOGLEVEL.I, "Main : Begin")

cur_dir = os.getcwd()
user_data_dir = f"{cur_dir}/Profiles"

options = webdriver.ChromeOptions()

#options.add_argument("user-data-dir=" + user_data_dir)
options.add_argument("profile-directory=Default")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--ignore-certificate-error")
options.add_argument("--ignore-ssl-errors")
options.add_argument('--window-size=1920,1080')
options.add_argument("--mute-audio")
options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-features=UserAgentClientHint')
options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
options.add_experimental_option('useAutomationExtension', False)

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)
    driver.implicitly_wait(20)
    driver.set_page_load_timeout(20)

    url = "https://shop.danawa.com/virtualestimate/?controller=estimateMain&methods=index&marketPlaceSeq=16"
    driver.get(url)

except:
    commonLib.print_log(LOGLEVEL.E, "Main : Driver Get Error")
    traceback.print_exc()
    sys.exit()


time.sleep(2)

els_cate = driver.find_elements(By.CSS_SELECTOR, "#wish_product_list > div > dl > dd > a")

cate_index = 0

html = ''
#
need_cate_list = ['CPU', '쿨러/튜닝', '메인보드', '메모리', '그래픽카드', 'SSD', '케이스', '파워', '하드디스크', '모니터', '노트북',
                  '외장HDD/SSD', '키보드', '마우스', 'ODD', '소프트웨어', '스피커', '사운드바', 'PC헤드셋', '마이크', '사운드카드',
                  '케이블', '서버']

for el_cate in els_cate:
    cate_name = el_cate.get_attribute("innerHTML").strip()

    if cate_name not in need_cate_list:
        continue

    commonLib.clickElement(driver, el_cate)

    time.sleep(2)

    page = 0

    # 클릭후 페이징
    while True:
        page += 1

        is_find_element = False

        for i in range(0, 3):
            try:
                els = driver.find_elements(By.CSS_SELECTOR,
                                       "#estimateMainProduct div.scroll_box > table.tbl_list tbody > tr")

                is_find_element = True
            except:
                time.sleep(3)

            break

        if not is_find_element:
            break

        for el in els:
            cpu_type = ""
            danawa_product_idx = ""

            try:
                class_name = el.get_attribute("class")
                danawa_product_idx = class_name.replace("productList_", "")

                html = el.get_attribute("innerHTML").strip()
                soup = BeautifulSoup(html, 'html.parser')

                subject = soup.select_one("td.title_price > p.subject > a").getText().strip()
                spec = soup.select_one("td.title_price div.spec_bg > a").getText().strip()
                price = soup.select_one("td.rig_line > p.low_price > span")

                del soup

                if price is None:
                    continue

                price = price.getText().strip().replace(",", "")
                price = int(price)
                price -= 100

                if cate_index == 0 or cate_index == 2:
                    if "인텔" in spec:
                        cpu_type = "INTEL"
                    else:
                        cpu_type = "AMD"

                data = {'cate_name': cate_name, 'it_name': subject, 'it_price': price, 'cpu_type': cpu_type,
                        'danawa_product_idx': danawa_product_idx,
                        'it_stock_qty': '99999', 'it_order': '0', 'it_use': '1', 'it_info_gubun': 'wear'}

                url = "https://mycom.kr/adm/shop_admin/itemformupdate_api.php"
                res = networkLib.retry_req_post(url, {}, data)
                res_html = res.text

                commonLib.print_log(LOGLEVEL.D, f"Update Server DB ({page}P)  : " + str(data))

                if 'OK_SUCCESS' not in res_html:
                    commonLib.print_log(LOGLEVEL.E, "서버와 통신중 에러가 발생했습니다. 개발자에게 문의하세요.")
                    print(res_html)
                    driver.quit()
                    sys.exit()

                del res
            except:
                traceback.print_exc()
                print(html)

        del els
        gc.collect()

        try:
            el = driver.find_element(By.CSS_SELECTOR, "div.pagination-box > ul > li.pagination--now")
            now_page = el.get_attribute("innerHTML").strip()
            now_page = int(now_page)
            next_page = now_page + 1

            els_page = driver.find_elements(By.CSS_SELECTOR, f"div.pagination-box > ul > li[page='{next_page}']")

            if len(els_page) == 0:
                break

            el = els_page[0]

            commonLib.moveElement(driver, el)
            commonLib.clickElement(driver, el)
            time.sleep(4)
        except:
            pass

    cate_index += 1

driver.quit()

sys.exit()
