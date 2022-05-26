from app import app
from flask import (Flask, jsonify, render_template, request, redirect, flash,
                   url_for, current_app)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from time import sleep
from xml.etree.ElementTree import Comment
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# @app.route('/')
# @app.route('/index')
# def index():
    
@app.route("/getData", methods=("GET", "POST"), strict_slashes=False)
def index():
    if request.method == "POST":
        try:
            print(request.json)
            URL = request.json.get('url')
            Page = request.json.get("page_limit")
            if URL == "":
                return {
                    "code": 400,
                    "body": {},
                    "status": False,
                    "message": "Please provide Url"
                }
            _service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=_service)
            driver.implicitly_wait(100)
            driver.minimize_window()
            #driver.maximize_window()
            driver.set_page_load_timeout(40)
            try:
                driver.get(URL)
                WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//*[@id="shopify-section-store-selector"]/store-selector/div/div/button'
                    ))).click()
            except TimeoutException:
                driver.execute_script("window.stop();")
            sleep(2)
            page = BeautifulSoup(driver.page_source, "html.parser")
            total_products = page.find('span', {
                'class': 'boost-pfs-filter-total-product'
            }).get_text().replace("Items", "").strip() if page.find(
                'span', {'class': 'boost-pfs-filter-total-product'}) else ""
            if (int(total_products) > 0 and (total_products != "")):
                product_list = []
                x = 1
                while (x <= int(Page) and len(product_list) < int(total_products)):
                    if x > 1:
                        NEW_URL = URL + "?page=" + str(x)
                    else:
                        NEW_URL = URL
                    try:
                        driver.get(NEW_URL)
                    except TimeoutException:
                        driver.execute_script("window.stop();")
                    sleep(2)
                    _new_page = BeautifulSoup(driver.page_source, "html.parser")
                    product_link = _new_page.find_all(
                        'div',
                        {'class': 'prd-Card_OverlayContainer util-FauxLink'})
                    if (len(product_link)) > 0:
                        products = ""
                        for i in range(len(product_link)):
                            try:
                                products = product_link[i].find(
                                    'a', {
                                        'class':
                                        'prd-Card_FauxLink util-FauxLink_Link'
                                    })
                                if (products['href']) not in product_list:
                                    product_list.append("https://www.ohpolly.com" +
                                                        products['href'])
                            except:
                                pass
                    else:
                        break
                    x += 1
            else:
                product_list = []
            data_set = {"product_list": product_list}
            return {
                "code": 200,
                "body": data_set,
                "status": True,
                "message": "response data."
            }

        except:
            return {
                    "code": 500,
                    "body": {},
                    "status": False,
                    "message": "Internal server error."
                }

if __name__ == "__main__":
    app.run(debug=True,port=8000, ssl_context='adhoc')
