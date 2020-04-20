#!/usr/bin/env python3


from src.misc import json_reader, sp_translate, check_n_mkdir, Logging
from src.chrome_utils import download_driver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itertools import count
from datetime import datetime
from config import CONFIG, SITES, XP_ELEMS
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

        self.xp_elems = XP_ELEMS

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
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, self.xp_elems["top_react"]))
        )
        self.log(f'Clicking [Top React]')
        self.driver.find_element_by_xpath(self.xp_elems["top_react"]).click()
        self.log(f'Clicking [Newest]')
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
        self.log(f'Title: {self.title}', mode="sub")

        self.index = self.driver.find_element_by_xpath(self.xp_elems["index"]).text
        self.log(f'Index: {self.index}', mode="sub")

        self.movement = self.driver.find_element_by_xpath(self.xp_elems["movement"]).text
        self.log(f'Movement: {self.movement}', mode="sub")


    def get_comment_block_list(self):
        """Getting the soup objects for each comment block"""
        self.log(f'Getting comment block list')

        comment_list_ele = self.driver.find_element_by_xpath(self.xp_elems["comment_list"])
        self.comment_block_elem_list = self.driver.find_elements_by_xpath(self.xp_elems["comment_block"])


    @classmethod
    def get_vote_ct(self, label):
        """Getting the number count for thumbup and thumpdown vote for each comment"""
        thumb_se = re.search("\d+", label)
        if thumb_se:
            return int(thumb_se.group(0))
        return 0

    def get_comment_info(self):
        """Printin comment inforation and storing all comments"""
        self.log(f'Fetching comments:')

        self.fetched_comments = []
        for comment_block in self.comment_block_elem_list:

            user_elem = comment_block.find_element_by_xpath(self.xp_elems["comment_user"])
            time_stamp_elem = comment_block.find_element_by_xpath(self.xp_elems["time_stamp"])
            comment_text_elem = comment_block.find_element_by_xpath(self.xp_elems["comment_text"])

            comment_thumbup_elem = comment_block.find_element_by_xpath(self.xp_elems["thumbup"])
            comment_thumbdown_elem = comment_block.find_element_by_xpath(self.xp_elems["thumbdown"])

            comment_url_elems = comment_text_elem.find_elements_by_xpath(self.xp_elems["comment_urls"])
            comment_media_elems = comment_text_elem.find_elements_by_xpath(self.xp_elems["comment_media"])

            thumb_up_ct = self.get_vote_ct(comment_thumbup_elem.get_attribute('aria-label'))
            thumb_down_ct = self.get_vote_ct(comment_thumbdown_elem.get_attribute('aria-label'))

            comment_text = comment_text_elem.text.replace("\n", " ")
            comment_urls = [url.text for url in comment_url_elems if url.text != ""]

            if comment_urls:
                for url in comment_urls:
                    comment_text = comment_text.replace(url ," ")

            comment_media = [media.get_attribute("src") for media in comment_media_elems]

            if re.match(r".*(second|minute|hour).*", time_stamp_elem.text):

                self.fetched_comments.append({
                    "Username"      :      user_elem.text,
                    "TimeStamp"     :      time_stamp_elem.text,
                    "ThumbUp"       :      thumb_up_ct,
                    "ThumbDown"     :      thumb_down_ct,
                    "Comment"       :      sp_translate(comment_text),
                    "Url"           :      comment_urls,
                    "Media"         :      comment_media
                })

        self.log(f'Found {len(self.fetched_comments)} comments:', mode="sub")


    def save_fetched_comments(self, delimiter="\t", file_name=""):
        """Write fetched comments as text file"""
        self.log(f'Saving fetched comments CSV:')

        if not file_name:
            file_name = os.path.join(
                self.csv_output_folder,
                f'{self.title} - {self.current_date}.csv'
            )

        header = self.fetched_comments[0].keys()

        with open(file_name, "w") as w_f:
            w_f.write(f'{delimiter.join(header)}\n')
            for comment_details in self.fetched_comments:
                new_line = delimiter.join([
                    str(val).replace(delimiter, "")
                    for val in comment_details.values()
                ])
                w_f.write(f'{new_line}\n')

        self.log(f'Saved as: {file_name}', mode="sub")


    def draw_word_cloud(self, file_name="", wc_show=False):
        """Generating word cloud using the stored comments"""
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

        wc_graph = wc(max_words=200, background_color="white").generate(words_block)
        plt.imshow(wc_graph, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"[{self.title}]\n[{self.index}]  [{self.movement}]")

        if wc_show:
            plt.show()

        if not file_name:
            file_name = os.path.join(
                self.wordmap_output_folder,
                f"{self.title} - {self.current_date}.JPG"
            )

        plt.savefig(file_name)

        self.log(f'Saved as: {file_name}', mode="sub")


    def fetch_data(self, instance_name, link):
        log_name = os.path.join(
            check_n_mkdir(CONFIG["log_output_folder"]),
            f'{self.current_date}.log'
        )
        self.log_open(log_name)
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
            self.draw_word_cloud()
        except Exception as e:
            self.log(f'Unexpected Error occurred: {str(e)}')
        finally:
            self.driver.quit()
            self.log_close()


if __name__ == '__main__':
    # download_driver()
    analyzer = YF_comments_analyzer()
    for instance_name, link in SITES:
        analyzer.fetch_data(instance_name, link)
