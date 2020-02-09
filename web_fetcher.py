from src.web_utils import json_link_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def yahoo_finance_top_comments_fetcher(*, web_links: list):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(chrome_options=options)
    for web_link in web_links:
        driver.get(web_link)

        time.sleep(1000)
    driver.quit()

if __name__ == '__main__':
    # download_driver()
    web_links = json_link_reader(file_name="web_links.json")
    yahoo_finance_top_comments_fetcher(web_links=web_links)
