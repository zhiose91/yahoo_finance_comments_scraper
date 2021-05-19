#!/usr/bin/env python3
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from src.misc import check_n_mkdir, Logger
from collections import defaultdict
import time
import os
import re


class CommentsScraper:

    def __init__(self, configs=None):

        """"Getting xp_elems and soup_elems for json folder"""
        # log variables
        self.log_datetime = datetime.now()
        self.log_date_str = datetime.now().strftime('%Y-%m-%d')
        self.logger = Logger()

        # default output folders
        self.__csv_output_folder = ""
        self.__json_output_folder = ""

        # driver variables
        self.driver = None
        self.options = None

        # instance info variables
        self.xp_elems = None
        self.ins_title = None
        self.ins_index = None
        self.movement = None
        self.movem_val = None
        self.movem_perc = None
        self.list_of_words = None
        self.word_counts = None
        self.comment_block_elem_list = None
        self.__fetched_comments = None
        self.__fetched_instances = dict()

        # set config
        if configs:
            self.load_config(configs)

        # set driver driver settings
        self.load_xp_elems()
        self.set_up_driver_options()

        # attempt counter:
        self.driver_attempts = defaultdict(int)

    @property
    def csv_output_folder(self):
        return self.__csv_output_folder

    @csv_output_folder.setter
    def csv_output_folder(self, folder_name: str):
        self.__csv_output_folder = check_n_mkdir(folder_name)

    @property
    def json_output_folder(self):
        return self.__json_output_folder

    @json_output_folder.setter
    def json_output_folder(self, folder_name: str):
        self.__json_output_folder = check_n_mkdir(folder_name)

    @property
    def fetched_comments(self):
        return self.__fetched_comments

    @property
    def fetched_instances(self):
        return self.__fetched_instances

    def load_xp_elems(self):
        self.logger.log(f'Loading XP_ELEMS')
        from src.xp_elems import XP_ELEMS
        self.xp_elems = XP_ELEMS

    def load_config(self, configs: dict):
        """"Loading config file"""

        self.logger.log(f'Loading config file')
        self.__csv_output_folder = check_n_mkdir(configs.get("csv_output_folder", "/"))
        self.__json_output_folder = check_n_mkdir(configs.get("json_output_folder", "/"))

    def set_up_driver_options(self):
        """Setting options for the driver, ignore browser UI an logging"""
        self.logger.log(f'Setting driver options')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('headless')
        self.options.add_argument("--log-level=3")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def driver_get_link(self, link: str):
        """Launching the driver with options and loading assigned link"""
        from selenium.common.exceptions import WebDriverException

        self.logger.log(f'Opening: {link}')
        try:
            self.driver = webdriver.Chrome(chrome_options=self.options)
        except WebDriverException:
            if sys.platform == "win32":
                driver_name = "chromedriver.exe"
            else:
                driver_name = "chromedriver"

            tmp_driver_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "tmp",
                driver_name
            )

            if not os.path.isfile(tmp_driver_path):
                from src.chrome_utils import download_driver
                tmp_driver_path = download_driver(file=__file__)

            self.driver = webdriver.Chrome(
                chrome_options=self.options,
                executable_path=tmp_driver_path
            )

        self.driver.get(link)

    def driver_select_newest(self):
        """Waiting for Top React element to show up and changing filter to Newest"""

        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, self.xp_elems["top_react"]))
        )
        self.logger.log(f'Clicking [Top React]')
        self.driver.find_element_by_xpath(self.xp_elems["top_react"]).click()
        self.logger.log(f'Clicking [Newest]')
        self.driver.find_element_by_xpath(self.xp_elems["newest"]).click()
        time.sleep(10)

    def driver_load_all(self):
        """Clicking on Show More button to load all the comments within past 24 hrs"""
        from itertools import count
        self.logger.log(f'Loading comments')

        click_num = count(start=1, step=1)
        while not self.driver.find_elements_by_xpath(self.xp_elems["old_time_stamp"]):
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, self.xp_elems["show_more"]))
            )
            self.driver.find_element_by_xpath(self.xp_elems["show_more"]).click()
            self.logger.log(f'Clicking [More] ({next(click_num)})', mode="sub")
        time.sleep(5)

    def get_stock_info(self):
        """Printing stock information including name, index, and movement"""
        self.logger.log(f'Getting instance information')

        self.ins_title = self.driver.find_element_by_xpath(self.xp_elems["title"]).text
        self.logger.log(f'Title: {self.ins_title}', mode="sub")

        self.ins_index = self.driver.find_element_by_xpath(self.xp_elems["index"]).text.replace(",", "")
        self.logger.log(f'Index: {self.ins_index}', mode="sub")

        self.movement = self.driver.find_element_by_xpath(self.xp_elems["movement"]).text
        movem_temp = self.movement.split(" ")
        self.movem_val = movem_temp[0]
        self.movem_perc = movem_temp[1][1:-2]
        self.logger.log(f'Movement: {self.movement}', mode="sub")

    def get_comment_block_list(self):
        """Getting the soup objects for each comment block"""
        self.logger.log(f'Getting comment block list')
        self.comment_block_elem_list = self.driver.find_elements_by_xpath(self.xp_elems["comment_block"])

    @classmethod
    def get_vote_ct(cls, label: str):
        """Getting the number count for thumbup and thumpdown vote for each comment"""

        thumb_se = re.search("\d+", label)
        if thumb_se:
            return int(thumb_se.group(0))
        return 0

    def get_post_time(self, time_stamp_text):
        """Getting the post time and total_minutes from the time_stamp_text"""

        time_pattern = "(\d+) (second|minute|hour)"
        result = re.search(time_pattern, time_stamp_text)
        time_digit = int(result.group(1))
        time_type = result.group(2)

        time_ct = defaultdict(int)
        time_ct[time_type] = time_digit

        duration = timedelta(
            hours=time_ct["hour"],
            minutes=time_ct["minute"],
            seconds=time_ct["second"]
        )

        post_time = self.log_datetime - duration
        total_minutes = int(duration.total_seconds() / 60)

        return post_time.strftime("%H:%M"), total_minutes

    def get_comment_info(self):
        """Getting all comment information and storing all comments"""
        from src.misc import sp_translate
        self.logger.log(f'Fetching comments:')

        self.log_datetime = datetime.now()
        self.__fetched_comments = list()
        for comment_block in self.comment_block_elem_list:
            time_stamp_elem = comment_block.find_element_by_xpath(self.xp_elems["time_stamp"])

            if re.match(r".*(second|minute|hour).*", time_stamp_elem.text):

                user_elem = comment_block.find_element_by_xpath(self.xp_elems["comment_user"])
                comment_text_elem = comment_block.find_element_by_xpath(self.xp_elems["comment_text"])

                comment_thumbup_elem = comment_block.find_element_by_xpath(self.xp_elems["thumbup"])
                comment_thumbdown_elem = comment_block.find_element_by_xpath(self.xp_elems["thumbdown"])

                comment_url_elems = comment_text_elem.find_elements_by_xpath(self.xp_elems["comment_urls"])
                comment_media_elems = comment_text_elem.find_elements_by_xpath(self.xp_elems["comment_media"])

                thumb_up_ct = self.get_vote_ct(comment_thumbup_elem.get_attribute('aria-label'))
                thumb_down_ct = self.get_vote_ct(comment_thumbdown_elem.get_attribute('aria-label'))

                comment_text = comment_text_elem.text.replace("\n", " ")
                if comment_text == "": comment_text = "Empty-Comment"
                comment_urls = [url.text for url in comment_url_elems if url.text != ""]

                if comment_urls:
                    for url in comment_urls:
                        comment_text = comment_text.replace(url, " ")

                comment_media = [media.get_attribute("src") for media in comment_media_elems]

                post_time, total_minutes = self.get_post_time(time_stamp_elem.text)

                self.__fetched_comments.append({
                    "UserName": user_elem.text,
                    "PostTime": post_time,
                    "DurationMins": total_minutes,
                    "ThumbUp": thumb_up_ct,
                    "ThumbDown": thumb_down_ct,
                    "CommentText": sp_translate(comment_text),  # filter out special characters
                    "CommentUrl": comment_urls,
                    "CommentMedia": comment_media
                })

        self.logger.log(f'Found {len(self.__fetched_comments)} comments:', mode="sub")

    def save_fetched_comments(self, file_name: str = "", delimiter: str = "\t"):
        """Write fetched comments as text file"""
        self.logger.log(f'Saving fetched comments CSV:')

        if not self.__fetched_comments:
            self.logger.log(f'No comments found', mode="sub")
            return

        if file_name:
            csv_file_name = file_name
        else:
            csv_file_name = os.path.join(
                check_n_mkdir(self.__csv_output_folder),
                f'{self.ins_title} - {self.log_date_str}.csv'
            )

        header = self.__fetched_comments[0].keys()

        with open(csv_file_name, "w", encoding="utf-8") as w_f:
            w_f.write(f'{delimiter.join(header)}\n')
            for comment_details in self.__fetched_comments:
                new_line = delimiter.join([
                    str(val).replace(delimiter, "")
                    for val in comment_details.values()
                ])
                w_f.write(f'{new_line}\n')

        self.logger.log(f'Saved as: {csv_file_name}', mode="sub")

    def get_list_of_words(self, skip_words=None):
        """Generating list of words with no stopwords"""
        if skip_words is None:
            skip_words = []
        self.logger.log(f'Getting list of words')

        from nltk.tokenize import wordpunct_tokenize
        from src.stopwords import english_stopwords as _stopwords

        comments = " ".join([x["CommentText"] for x in self.__fetched_comments])

        # getting set of stopwords
        if skip_words: _stopwords.update(skip_words)

        self.list_of_words = [
            word.lower()
            for word in wordpunct_tokenize(comments)
            if word.lower() not in _stopwords and word.isalpha()
        ]

    def get_word_counts(self):
        """Store word counts for the use of word cloud"""
        self.logger.log(f'Getting word usage counts')

        from nltk import FreqDist
        self.word_counts = list()
        for word, ct in FreqDist(self.list_of_words).items():
            self.word_counts.append([word, ct])

        self.word_counts = sorted(self.word_counts, key=lambda x: x[1], reverse=True)

    def save_instance_info(self):
        """Save instance information and push it to instances dict"""
        import decimal

        self.logger.log(f'Generating instance [{self.ins_title}]')
        if self.fetched_comments:
            data_cols = list(self.fetched_comments[0].keys())
            data_vals = [list(c.values()) for c in self.fetched_comments]
        else:
            data_cols = list()
            data_vals = list()

        self.__fetched_instances.update({
            self.ins_title: {
                "ins_title"      : self.ins_title,
                "ins_index"      : decimal.Decimal(self.ins_index),
                "fetched_date"   : self.log_date_str,
                "num_of_comments": len(self.fetched_comments),
                "movem_str"      : self.movement,
                "movem_perc"     : decimal.Decimal(self.movem_perc),
                "movem_val"      : decimal.Decimal(self.movem_val),
                "comments_wd_ct" : self.word_counts,
                "comments"       : {"data_cols": data_cols, "data_vals": data_vals}
            }
        })

    def dump_instance_json(self, file_name: str = ""):
        """Save fetched instances info in json file"""
        import json
        from src.misc import DecimalEncoder

        if file_name:
            instance_json_file_name = file_name
        else:
            instance_json_file_name = os.path.join(
                check_n_mkdir(self.__json_output_folder),
                f"{self.log_date_str}.json"
            )

        self.logger.log(f'Saved fetched instances info as: {instance_json_file_name}', mode="sub")
        with open(instance_json_file_name, "w") as w_f:
            json.dump(self.__fetched_instances, w_f, indent=4, cls=DecimalEncoder)

    def fetch_comments(self, link: str, instance_name=None, max_attempts: int = 3):
        """Getting comments from the target site"""
        self.driver_attempts[link] += 1
        try:
            self.driver_get_link(link)
            self.logger.log(f'Processing [{instance_name if instance_name else link}]: Attempt[{self.driver_attempts[link]}]')
            self.driver_select_newest()
            self.driver_load_all()
            self.get_stock_info()
            self.get_comment_block_list()
            self.get_comment_info()
            self.get_list_of_words()
            self.get_word_counts()
            self.save_instance_info()
        except Exception as e:
            self.logger.log(f'Unexpected Error occurred: {str(e)}')
            if self.driver_attempts[link] < max_attempts:
                self.fetch_comments(link=link, instance_name=instance_name)
            else:
                self.logger.log(f'Max attempts reached for [{instance_name if instance_name else link}]')
        finally:
            if self.driver:
                self.driver.quit()
            try:
                return self.fetched_comments
            except AttributeError:
                return list()


class CommentsScraperBinary(CommentsScraper):
    # For AWS deployment
    # 21buttons' github repository: https://github.com/21buttons/pychromeless
    # Setting up a Selenium web scraper on AWS Lambda with Python (ROBERTO ROCHA):
    # https://robertorocha.info/setting-up-a-selenium-web-scraper-on-aws-lambda-with-python/

    def set_up_driver_options(self):
        """Setting options for the driver, ignore browser UI an logging"""
        self.logger.log(f'Setting driver options')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1280x1696')
        self.options.add_argument('--user-data-dir=/tmp/user-data')
        self.options.add_argument('--hide-scrollbars')
        self.options.add_argument('--enable-logging')
        self.options.add_argument('--log-level=0')
        self.options.add_argument('--v=99')
        self.options.add_argument('--single-process')
        self.options.add_argument('--data-path=/tmp/data-path')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--homedir=/tmp')
        self.options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        self.options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        self.options.binary_location = os.getcwd() + "/bin/headless-chromium"

    def driver_get_link(self, link: str):
        """Launching the driver with options and loading assigned link"""

        self.logger.log(f'Opening: {link}')
        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.driver.get(link)
