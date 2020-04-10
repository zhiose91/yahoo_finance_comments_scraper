from src.misc import json_reader, sp_translate, check_n_mkdir, Logging
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from itertools import count
from datetime import datetime
from config import CONFIG, SITES
import time
import re
import os


class YF_comments_analyzer(Logging):

    def __init__(self):
        """"Getting xp_elems and soup_elems for json folder"""
        self.current_date = datetime.now().strftime('%b_%d_%Y')


    def load_config(self, CONFIG):
        """"Loading config file"""
        self.log(f'Loading config file')
        self.xp_elems = json_reader(file_name=CONFIG["xp_elems"])
        self.soup_elems = json_reader(file_name=CONFIG["soup_elems"])

        self.csv_output_folder = check_n_mkdir(CONFIG["csv_output_folder"])
        self.wordmap_output_folder = check_n_mkdir(CONFIG["wordmap_output_folder"])

        self.ignore_words = CONFIG["ignore_words"]


    def set_up_driver_options(self):
        """Setting options for the driver, ignore browser UI an logging"""
        self.log(f'Setting driver options')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('headless')
        self.options.add_argument("--log-level=3")


    def driver_get_link(self, link):
        """Launching the driver with options and loading assigned link"""
        self.log(f'Opening: {link}')
        try:
            self.driver = webdriver.Chrome(chrome_options=self.options)
        except WebDriverException:
            download_driver()
            self.driver = webdriver.Chrome(chrome_options=self.options)

        self.driver.get(link)


    def driver_select_newest(self):
        """Waiting for Top React element to show up and changing filter to Newest"""
        self.log(f'Loading newest comments')
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, self.xp_elems["top_react"]))
        )
        self.driver.find_element_by_xpath(self.xp_elems["top_react"]).click()
        self.driver.find_element_by_xpath(self.xp_elems["newest"]).click()
        time.sleep(10)


    def driver_load_all(self):
        """Clicking on Show More button to load all the comments within past 24 hrs"""
        self.log(f'Clicking [More] to load more comments:')
        click_num = count(start=1, step=1)
        while not self.driver.find_elements_by_xpath(self.xp_elems["old_time_stamp"]):
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, self.xp_elems["show_more"]))
            )
            self.driver.find_element_by_xpath(self.xp_elems["show_more"]).click()
            self.log(f'Attempt ({next(click_num)})', mode="sub")
        time.sleep(5)


    def get_stock_info(self):
        """Printing stock information including name, index, and movement"""
        self.log(f'Getting instance information')
        self.title = self.driver.find_element_by_xpath(self.xp_elems["title"]).text
        self.index = self.driver.find_element_by_xpath(self.xp_elems["index"]).text
        self.movement = self.driver.find_element_by_xpath(self.xp_elems["movement"]).text
        self.log(f'Title: {self.title}', mode="sub")
        self.log(f'Index: {self.index}', mode="sub")
        self.log(f'Movement: {self.movement}', mode="sub")


    def get_comment_block_list(self):
        """Getting the soup objects for each comment block"""
        self.log(f'Getting comment block list')
        comment_list_ele = self.driver.find_element_by_xpath(self.xp_elems["comment_list"])
        comment_list_html = comment_list_ele.get_attribute('innerHTML')
        comment_list_soup = BeautifulSoup(comment_list_html, 'html.parser')
        self.comment_block_list = comment_list_soup.find_all("li", self.soup_elems["comment_block"])


    @classmethod
    def get_vote_ct(self, comment_block_html, vote):
        """Getting the number count for thumbup and thumpdown vote for each comment"""
        pattern = r"aria-label=\"(\d{1,2}) Thumbs " + vote + r"\""
        thumb_se = re.search(pattern, comment_block_html)
        if thumb_se:
            return int(thumb_se.group(1))
        return 0


    def get_comment_info(self):
        """Printin comment inforation and storing all comments"""
        self.log(f'Fetching comments:')

        self.fetched_comments = []
        for comment_block in self.comment_block_list:

            # Temporary for solution for finding user ID
            user = comment_block.find("button")
            time_stamp = comment_block.find("span", self.soup_elems["time_stamp"]).find("span")
            comment_texts = comment_block.find_all("div", self.soup_elems["comment_text"])

            thumb_up_ct = self.get_vote_ct(str(comment_block), vote="Up")
            thumb_down_ct = self.get_vote_ct(str(comment_block),vote="Down")

            if re.match(r".*(second|minute|hour).*", time_stamp.text):
                join_comment_text = " ".join([
                    sp_translate(comment.text)
                    for comment in comment_texts
                ])

                self.fetched_comments.append({
                    "Username"      :      user.text,
                    "TimeStamp"     :      time_stamp.text,
                    "ThumbUp"       :      thumb_up_ct,
                    "ThumbDown"     :      thumb_down_ct,
                    "Comment"       :      join_comment_text
                })
        self.log(f'Found {len(self.fetched_comments)} comments:', mode="sub")


    def save_fetched_comments(self, delimiter="\t"):
        """Write fetched comments as text file"""
        self.log(f'Saving fetched comments CSV:')

        file_name = os.path.join(
            self.csv_output_folder,
            f'{self.title} - {self.current_date}.csv'
        )


        header = ["Username", "TimeStamp", "ThumbUp", "ThumbDown", "Comment" ]
        with open(file_name, "w") as w_f:
            w_f.write(f'{delimiter.join(header)}\n')
            for comment in self.fetched_comments:
                new_line = delimiter.join([
                    str(val).replace(delimiter, "")
                    for val in comment.values()
                ])
                w_f.write(f'{new_line}\n')
        self.log(f'Saved as: {file_name}', mode="sub")


    def draw_word_map(self):
        """Generating word map using the stored comments"""
        self.log(f'Generating wordmap:')

        from nltk.tokenize import wordpunct_tokenize
        from wordcloud import WordCloud as wc
        import matplotlib.pyplot as plt
        import nltk
        nltk.download('stopwords')
        from nltk.corpus import stopwords

        # some words can be ignored, stock name and abbreviation are recommended
        # to ignore when analyzing indivdual stock
        comments = " ".join([x["Comment"] for x in self.fetched_comments])

        # getting set of stopwords
        _stopwords = set(stopwords.words('english'))
        list_of_words = [i.lower() for i in wordpunct_tokenize(comments)
            if i.lower() not in _stopwords and i.isalpha()]

        words_block = " ".join(list_of_words)

        for word in self.ignore_words:
            words_block = words_block.replace(word, "")

        wc1 = wc(max_words=200, background_color="white").generate(words_block)
        plt.imshow(wc1, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"[{self.title}]\n[{self.index}]  [{self.movement}]")

        file_name = os.path.join(
            self.wordmap_output_folder,
            f"{self.title} - {self.current_date}.JPG"
        )
        plt.savefig(file_name)

        self.log(f'Saved as: {file_name}', mode="sub")


    def fetch_data(self, instance_name, link):
        import string
        self.log_open(f'Work_log/{self.current_date}.log')
        self.log(f'Processing [{instance_name}]')
        try:
            self.load_config(CONFIG)
            self.set_up_driver_options()
            self.driver_get_link(link)
            self.driver_select_newest()
            self.driver_load_all()
            self.get_stock_info()
            self.get_comment_block_list()
            self.get_comment_info()
            self.save_fetched_comments()
            self.draw_word_map()
        except:
            self.log("Unexpected Error occurred")
        finally:
            self.driver.quit()
            self.log_close()


if __name__ == '__main__':
    # download_driver()
    analyzer = YF_comments_analyzer()
    for instance_name, link in SITES:
        analyzer.fetch_data(instance_name, link)
