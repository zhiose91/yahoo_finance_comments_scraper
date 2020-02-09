from src.misc import json_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def yahoo_finance_top_comments_fetcher(*, web_links: list):
    xp_elems = json_reader(file_name="xp_elems.json")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    for web_link in web_links:
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(web_link)

        # comments_xp = "//div[text()[contains(., 'react-text')]]"
        comment_timestamp_xp = "//span[@class='C($c-fuji-grey-g) Fz(12px)']//span"
        comments_xp = "//div[@class='Wow(bw)']//div[@class='C($c-fuji-grey-l) Mb(2px) Fz(14px) Lh(20px) Pend(8px)']"
        # comments_xp = "//div[@class='Wow(bw)']//div[@class='canvass-see-more']/div/div"

        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xp_elems["top_react"]))
            )

            print("="*30)
            print(xp_elems["title"])
            print(f'\nTitle: {driver.find_element_by_xpath(xp_elems["title"]).text}')
            print(f'Index: {driver.find_element_by_xpath(xp_elems["index"]).text}')
            print(f'Movement: {driver.find_element_by_xpath(xp_elems["movement"]).text}')
            print('\nFetching Newest Comments...\n')

            driver.find_element_by_xpath(xp_elems["top_react"]).click()
            driver.find_element_by_xpath(xp_elems["newest"]).click()

            time.sleep(10)
            time_stamps = driver.find_elements_by_xpath(xp_elems["comment_timestamp"])
            for time_stamp in time_stamps[:8]:
                print(time_stamp.text)
            print("\n")
            comments = driver.find_elements_by_xpath(comments_xp)
            for comment in comments[:8]:
                print(comment.text, "\n")

            # for time_stamp, comment in list(zip(time_stamps, comments))[0:10]:
            #     print(f'{time_stamp.text}: {comment.text}\n')
        finally:
            print("="*30)
            time.sleep(3)
            driver.quit()

if __name__ == '__main__':
    # download_driver()
    web_links = json_reader(file_name="web_links.json")
    yahoo_finance_top_comments_fetcher(web_links=web_links)
