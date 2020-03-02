from src.misc import json_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


class YF_comments_analyzer:

    def __init__(self):
        self.xp_elems = json_reader(file_name=r"json/xp_elems.json")
        self.soup_elems = json_reader(file_name=r"json/soup_elems.json")

    def set_up_driver_options(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('headless')
        self.options.add_argument("--log-level=3")

    def driver_get_link(self, web_link):
        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.driver.get(web_link)

    def driver_select_newest(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, self.xp_elems["top_react"]))
        )
        self.driver.find_element_by_xpath(self.xp_elems["top_react"]).click()
        self.driver.find_element_by_xpath(self.xp_elems["newest"]).click()
        time.sleep(10)

    def driver_load_all(self):
        while not self.driver.find_elements_by_xpath(self.xp_elems["old_time_stamp"]):
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, self.xp_elems["show_more"]))
            )
            self.driver.find_element_by_xpath(self.xp_elems["show_more"]).click()
            print("Clicking [Show More] to load more comments")
        time.sleep(5)

    def print_stock_info(self):
        print(f'\nTitle: {self.driver.find_element_by_xpath(self.xp_elems["title"]).text}')
        # print(f'Index: {self.driver.find_element_by_xpath(self.xp_elems["index"]).text}')
        # print(f'Movement: {self.driver.find_element_by_xpath(self.xp_elems["movement"]).text}')

    def get_comment_block_list(self):
        print("\nComments within past 24 hours\n")
        comment_list_ele = self.driver.find_element_by_xpath(self.xp_elems["comment_list"])
        comment_list_html = comment_list_ele.get_attribute('innerHTML')
        comment_list_soup = BeautifulSoup(comment_list_html, 'html.parser')
        self.comment_block_list = comment_list_soup.find_all("li", self.soup_elems["comment_block"])

    def get_comment_info(self):
        for comment_block in self.comment_block_list:
            user = comment_block.find("button", self.soup_elems["user_tag"])
            time_stamp = comment_block.find("span", self.soup_elems["time_stamp"]).find("span")
            comment_texts = comment_block.find_all("div", self.soup_elems["comment_text"])

            thumb_up_ct = self.get_vote_ct(str(comment_block), vote="Up")
            thumb_down_ct = self.get_vote_ct(str(comment_block),vote="Down")

            if re.match(r".*(second|minute|hour).*", time_stamp.text):
                print("+"*80)
                print(f"[{user.text}] [{time_stamp.text}] [{thumb_up_ct}-Up][{thumb_down_ct}-Down]")
                for comment_text in comment_texts:
                    self.comment_text_list.append(comment_text.text)
                    # try:
                    #     print(comment_text.text)
                    # except:
                    #     print("The comment contains utf-8 character and will not be displayed")


    @classmethod
    def get_vote_ct(self, comment_block_html, vote):
        pattern = r"aria-label=\"(\d{1,2}) Thumbs " + vote + r"\""
        thumb_se = re.search(pattern, comment_block_html)
        if thumb_se:
            return int(thumb_se.group(1))
        return 0

    def draw_word_map(self):
        from nltk.corpus import stopwords
        from nltk.tokenize import wordpunct_tokenize
        from wordcloud import WordCloud as wc
        import matplotlib.pyplot as plt

        comments = " ".join(self.comment_text_list)
        stop = set(stopwords.words('english'))
        list_of_words = [i.lower() for i in wordpunct_tokenize(comments)
            if i.lower() not in stop and i.isalpha()]

        words_block = " ".join(list_of_words)

        for word in ("market", "week", "tsla", "going", "tesla", "https", "http", "stock"):
            words_block = words_block.replace(word, "")

        wc1 = wc(max_words=200, background_color="white").generate(words_block)
        plt.imshow(wc1, interpolation="bilinear")
        plt.axis("off")
        plt.show()


    def fetch_data(self, link):
        self.set_up_driver_options()
        try:
            print("="*80)
            self.driver_get_link(link)
            self.driver_select_newest()
            self.driver_load_all()
            self.print_stock_info()
            self.get_comment_block_list()
            self.comment_text_list = []
            self.get_comment_info()
        finally:
            print("="*80)
            self.driver.quit()


if __name__ == '__main__':
    # download_driver()
    web_links = json_reader(file_name=r"json/web_links.json")
    analyzer = YF_comments_analyzer()
    for link in web_links:
        analyzer.fetch_data(link)
        analyzer.draw_word_map()
