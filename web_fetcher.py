from src.misc import json_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


def yahoo_finance_top_comments_fetcher(*, web_links: list):
    xp_elems = json_reader(file_name="xp_elems.json")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('headless')
    options.add_argument("--log-level=3")
    for web_link in web_links:
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(web_link)

        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                            (By.XPATH, xp_elems["top_react"])))

            print("="*60)
            print(f'\nTitle: {driver.find_element_by_xpath(xp_elems["title"]).text}')
            print(f'Index: {driver.find_element_by_xpath(xp_elems["index"]).text}')
            print(f'Movement: {driver.find_element_by_xpath(xp_elems["movement"]).text}')
            print('\nFetching Newest Comments...\n')

            driver.find_element_by_xpath(xp_elems["top_react"]).click()
            driver.find_element_by_xpath(xp_elems["newest"]).click()
            for i in range(1):
                time.sleep(3)
                driver.find_element_by_xpath(xp_elems["show_more"]).click()

            # wait for 15 seconds before parsing through the file
            time.sleep(10)

            # Now trying - get comment block element instead
            # ------------------------------------------------------------------
            comment_list_ele = driver.find_element_by_xpath(xp_elems["comment_list"])
            comment_list_html = comment_list_ele.get_attribute('innerHTML')

            comment_list_soup = BeautifulSoup(comment_list_html, 'html.parser')
            comment_block_list = comment_list_soup.find_all("li", xp_elems["comment_block"])

            for comment_block in comment_block_list:
                user = comment_block.find("button", xp_elems["user_tag"])
                time_stamp = comment_block.find("span", xp_elems["time_stamp"]).find("span")
                # thumb_up_ct = comment_block.find("button", xp_elems["thumb_up_block"]) # .find("span", xp_elems["thumb_up_ct"])
                # print(thumb_up_ct.text)
                # thumb_down_ct = pass
                if re.match(r".*(second|minute|hour).*", time_stamp.text):
                    print(f"{user.text}[{time_stamp.text}]")

            # ------------------------------------------------------------------


        finally:
            print("="*60)
            driver.quit()

if __name__ == '__main__':
    # download_driver()
    web_links = json_reader(file_name="web_links.json")
    yahoo_finance_top_comments_fetcher(web_links=web_links)
