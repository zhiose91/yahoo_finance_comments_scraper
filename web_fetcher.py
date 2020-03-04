from src.misc import json_reader
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


class YF_comments_analyzer:

    def __init__(self):
        """"Getting xp_elems and soup_elems for json folder"""
        self.xp_elems = json_reader(file_name=r"json/xp_elems.json")
        self.soup_elems = json_reader(file_name=r"json/soup_elems.json")

    def set_up_driver_options(self):
        """Setting options for the driver, ignore browser UI an logging"""
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('headless')
        self.options.add_argument("--log-level=3")

    def driver_get_link(self, web_link):
        """Launching the driver with options and loading assigned link"""
        try:
            self.driver = webdriver.Chrome(chrome_options=self.options)
        except WebDriverException:
            download_driver()
            self.driver = webdriver.Chrome(chrome_options=self.options)

        self.driver.get(web_link)

    def driver_select_newest(self):
        """Waiting for Top React element to show up and changing filter to Newest"""
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, self.xp_elems["top_react"]))
        )
        self.driver.find_element_by_xpath(self.xp_elems["top_react"]).click()
        self.driver.find_element_by_xpath(self.xp_elems["newest"]).click()
        time.sleep(10)

    def driver_load_all(self):
        """Clicking on Show More button to load all the comments within past 24 hrs"""
        print("*"*80)
        print("Clicking [Show More] : ", end="")
        while not self.driver.find_elements_by_xpath(self.xp_elems["old_time_stamp"]):
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, self.xp_elems["show_more"]))
            )
            self.driver.find_element_by_xpath(self.xp_elems["show_more"]).click()
            print("~", end="")
        print("")
        time.sleep(5)

    def get_stock_info(self):
        """Printing stock information including name, index, and movement"""
        self.title = self.driver.find_element_by_xpath(self.xp_elems["title"]).text
        self.index = self.driver.find_element_by_xpath(self.xp_elems["index"]).text
        self.movement = self.driver.find_element_by_xpath(self.xp_elems["movement"]).text
        print("*"*80)
        print(f'Title: {self.title}')
        print(f'Index: {self.index}')
        print(f'Movement: {self.movement}')
        print("*"*80)

    def get_comment_block_list(self):
        """Getting the soup objects for each comment block"""
        print("\nComments within past 24 hours\n")
        comment_list_ele = self.driver.find_element_by_xpath(self.xp_elems["comment_list"])
        comment_list_html = comment_list_ele.get_attribute('innerHTML')
        comment_list_soup = BeautifulSoup(comment_list_html, 'html.parser')
        self.comment_block_list = comment_list_soup.find_all("li", self.soup_elems["comment_block"])

    def get_comment_info(self):
        """Printin comment inforation and storing all comments"""
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
                    print(repr(comment_text.text))

    @classmethod
    def get_vote_ct(self, comment_block_html, vote):
        """Getting the number count for thumbup and thumpdown vote for each comment"""
        pattern = r"aria-label=\"(\d{1,2}) Thumbs " + vote + r"\""
        thumb_se = re.search(pattern, comment_block_html)
        if thumb_se:
            return int(thumb_se.group(1))
        return 0

    def draw_word_map(self):
        """Generating word map using the stored comments"""
        from nltk.tokenize import wordpunct_tokenize
        from wordcloud import WordCloud as wc
        import matplotlib.pyplot as plt
        try:
            from nltk.corpus import stopwords
        except LookupError:
            nltk.download('stopwords')
            from nltk.corpus import stopwords

        # some words can be ignored, stock name and abbreviation are recommended
        # to ignore when analyzing indivdual stock
        ignore_words = [
            "https", "http", "stock", "market", "week", "going", "people"
        ]

        comments = " ".join(self.comment_text_list)
        _stopwords = set(stopwords.words('english'))
        list_of_words = [i.lower() for i in wordpunct_tokenize(comments)
            if i.lower() not in _stopwords and i.isalpha()]

        words_block = " ".join(list_of_words)

        for word in ignore_words:
            words_block = words_block.replace(word, "")

        wc1 = wc(max_words=200, background_color="white").generate(words_block)
        plt.imshow(wc1, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"[{self.title}]\n[{self.index}]  [{self.movement}]")
        plt.show()


    def fetch_data(self, link):
        """Pipeline"""
        self.set_up_driver_options()
        try:
            print("="*80)
            self.driver_get_link(link)
            self.driver_select_newest()
            self.driver_load_all()
            self.get_stock_info()
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
