from src.web_utils import json_link_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def yahoo_finance_top_comments_fetcher(*, web_links: list):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    for web_link in web_links:
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(web_link)

        # Top Reactions
        top_react_xp = "//span[text()[contains(.,'Top Reactions')]]"
        # Newest Reactions
        newest_xp = "//span[text()[contains(.,'Newest Reactions')]]"
        # Title
        title_xp = "//h1[@class='D(ib) Fz(18px)']"
        index_xp = "//span[@class='Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)']"
        mov_xp = "//span[@class='Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($dataRed)']"

        # comments_xp = "//div[text()[contains(., 'react-text')]]"
        comments_xp = "//div[@class='Wow(bw)']//div[@class='C($c-fuji-grey-l) Mb(2px) Fz(14px) Lh(20px) Pend(8px)']"

        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, top_react_xp))
            )
            print("="*30)
            print(f"\nTitle: {driver.find_element_by_xpath(title_xp).text}")
            print(f"Index: {driver.find_element_by_xpath(index_xp).text}")
            print(f"Movement: {driver.find_element_by_xpath(mov_xp).text}")
            print(f"\nFetching Newest Comments...\n")
            driver.find_element_by_xpath(top_react_xp).click()
            driver.find_element_by_xpath(newest_xp).click()
            time.sleep(10)
            print(f"{driver.find_element_by_xpath(comments_xp).text}")

        finally:
            print("="*30)
            time.sleep(3)
            driver.quit()

if __name__ == '__main__':
    # download_driver()
    web_links = json_link_reader(file_name="web_links.json")
    yahoo_finance_top_comments_fetcher(web_links=web_links)
