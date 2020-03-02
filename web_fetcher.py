from src.misc import json_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


def get_vote_ct(comment_block_html, vote):
    pattern = r"aria-label=\"(\d{1,2}) Thumbs " + vote + r"\""
    thumb_se = re.search(pattern, comment_block_html)
    if thumb_se:
        return int(thumb_se.group(1))
    return 0

def YF_comments_fetcher(*, web_links: list):
    xp_elems = json_reader(file_name="xp_elems.json")
    soup_elems = json_reader(file_name="soup_elems.json")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('headless')
    options.add_argument("--log-level=3")
    for web_link in web_links:
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(web_link)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xp_elems["top_react"]))
            )

            print("="*80)
            print(f'\nTitle: {driver.find_element_by_xpath(xp_elems["title"]).text}')
            print(f'Index: {driver.find_element_by_xpath(xp_elems["index"]).text}')
            print(f'Movement: {driver.find_element_by_xpath(xp_elems["movement"]).text}')
            print('\nFetching Newest Comments...\n')

            driver.find_element_by_xpath(xp_elems["top_react"]).click()
            driver.find_element_by_xpath(xp_elems["newest"]).click()
            for i in range(3):
                time.sleep(3)
                print("Clicking [Show More]")
                driver.find_element_by_xpath(xp_elems["show_more"]).click()

            # wait for 15 seconds before parsing through the file
            time.sleep(10)
            print("\nComments within past 24 hours\n")

            # Now trying - get comment block element instead
            # ------------------------------------------------------------------
            comment_list_ele = driver.find_element_by_xpath(xp_elems["comment_list"])
            comment_list_html = comment_list_ele.get_attribute('innerHTML')

            comment_list_soup = BeautifulSoup(comment_list_html, 'html.parser')
            comment_block_list = comment_list_soup.find_all("li", soup_elems["comment_block"])

            comment_text_list = []

            for comment_block in comment_block_list:
                user = comment_block.find("button", soup_elems["user_tag"])
                time_stamp = comment_block.find("span", soup_elems["time_stamp"]).find("span")
                comment_texts = comment_block.find_all("div", soup_elems["comment_text"])

                thumb_up_ct = get_vote_ct(str(comment_block), "Up")
                thumb_down_ct = get_vote_ct(str(comment_block), "Down")

                if re.match(r".*(second|minute|hour).*", time_stamp.text):
                    print("+"*80)
                    print(f"[{user.text}] [{time_stamp.text}] [{thumb_up_ct}-Up][{thumb_down_ct}-Down]")
                    for comment_text in comment_texts:
                        print(comment_text.text)
                        comment_text_list.append(comment_text.text)
            # ------------------------------------------------------------------


        finally:
            print("="*80)
            driver.quit()
            return comment_text_list

if __name__ == '__main__':
    # download_driver()
    web_links = json_reader(file_name="web_links.json")
    comments = YF_comments_fetcher(web_links=web_links)
    with open("test_input.txt", "w") as write_file:
        write_file.write(" ".join(comments))
