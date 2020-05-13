#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from src.misc import check_n_mkdir
import time
import os
import re


class YF_comments_scraper:

    def __init__(self, configs: dict={}):

        """"Getting xp_elems and soup_elems for json folder"""
        self.log_datetime = datetime.now()
        self.log_date_str = datetime.now().strftime('%Y-%m-%d')
        self.__fetched_instances = dict()
        self.__log_output_folder = check_n_mkdir("tmp")
        self.__csv_output_folder = check_n_mkdir("tmp")
        self.__word_cloud_output_folder = check_n_mkdir("tmp")
        self.__json_output_folder = check_n_mkdir("tmp")
        self.__log_file = None

        if configs:
            self.load_config(configs)
        self.load_xp_elems()
        self.set_up_driver_options()

    @property
    def log_output_folder(self):
        return self.__log_output_folder

    @log_output_folder.setter
    def log_output_folder(self, folder_name: str):
        self.__log_output_folder = check_n_mkdir(folder_name)

    @property
    def csv_output_folder(self):
        return self.__csv_output_folder

    @csv_output_folder.setter
    def csv_output_folder(self, folder_name: str):
        self.__csv_output_folder = check_n_mkdir(folder_name)

    @property
    def word_cloud_output_folder(self):
        return self.__word_cloud_output_folder

    @word_cloud_output_folder.setter
    def word_cloud_output_folder(self, folder_name: str):
        self.__word_cloud_output_folder = check_n_mkdir(folder_name)

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


    @classmethod
    def current_datetime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def log_open(self, file_name: str=""):
        if not file_name:
            file_name = os.path.join(self.__log_output_folder, f'{self.log_date_str}.log')
        self.__log_file = open(file_name, "a")


    def log(self, log_text, mode="main"):

        if mode == "main":
            pre_fix = ">>> "
        elif mode == "sub":
            pre_fix = "    "
        elif mode == "sub+":
            pre_fix = "        "
        else:
            pre_fix = ">>> "

        log_message = f'{self.current_datetime()} {pre_fix}{log_text}'
        print(log_message)
        if self.__log_file: self.__log_file.write(f'{log_message}\n')


    def log_close(self):
        self.__log_file.write("\n")
        self.__log_file.close()


    def load_xp_elems(self):
        self.log(f'Loading XP_ELEMS')
        from src.xp_elems import XP_ELEMS
        self.xp_elems = XP_ELEMS


    def load_config(self, configs: dict):
        """"Loading config file"""

        self.log(f'Loading config file')
        self.__log_output_folder = check_n_mkdir(configs.get("log_output_folder", "/"))
        self.__csv_output_folder = check_n_mkdir(configs.get("csv_output_folder", "/"))
        self.__word_cloud_output_folder = check_n_mkdir(configs.get("word_cloud_output_folder", "/"))
        self.__json_output_folder = check_n_mkdir(configs.get("json_output_folder", "/"))


    def set_up_driver_options(self):
        """Setting options for the driver, ignore browser UI an logging"""
        self.log(f'Setting driver options')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('headless')
        self.options.add_argument("--log-level=3")


    def driver_get_link(self, link: str):
        """Launching the driver with options and loading assigned link"""
        from selenium.common.exceptions import WebDriverException

        self.log(f'Opening: {link}')
        try:
            self.driver = webdriver.Chrome(chrome_options=self.options)
        except WebDriverException:
            from src.chrome_utils import download_driver
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
        from itertools import count
        self.log(f'Loading comments')

        click_num = count(start=1, step=1)
        while not self.driver.find_elements_by_xpath(self.xp_elems["old_time_stamp"]):
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, self.xp_elems["show_more"]))
            )
            self.driver.find_element_by_xpath(self.xp_elems["show_more"]).click()
            self.log(f'Clicking [More] ({next(click_num)})', mode="sub")
        time.sleep(5)


    def get_stock_info(self):
        """Printing stock information including name, index, and movement"""
        self.log(f'Getting instance information')

        self.ins_title = self.driver.find_element_by_xpath(self.xp_elems["title"]).text
        self.log(f'Title: {self.ins_title}', mode="sub")

        self.ins_index = float(self.driver.find_element_by_xpath(
            self.xp_elems["index"]).text.replace(",", "")
        )
        self.log(f'Index: {self.ins_index}', mode="sub")

        self.movement = self.driver.find_element_by_xpath(self.xp_elems["movement"]).text
        self.movem_perc = float(re.search("([+-]\d{1,}\.\d{2})%", self.movement).group(1))
        self.movem_val = float(re.search("([+-]\d{1,}\.\d{2}) ", self.movement).group(1))
        self.log(f'Movement: {self.movement}', mode="sub")


    def get_comment_block_list(self):
        """Getting the soup objects for each comment block"""
        self.log(f'Getting comment block list')

        comment_list_ele = self.driver.find_element_by_xpath(self.xp_elems["comment_list"])
        self.comment_block_elem_list = self.driver.find_elements_by_xpath(self.xp_elems["comment_block"])


    @classmethod
    def get_vote_ct(self, label: str):
        """Getting the number count for thumbup and thumpdown vote for each comment"""

        thumb_se = re.search("\d+", label)
        if thumb_se:
            return int(thumb_se.group(0))
        return 0


    def get_post_time(self, time_stamp_text):
        """Getting the post time and total_minutes from the time_stamp_text"""

        time_pattern = "(\d+) (minute|hour)"
        result = re.search(time_pattern, time_stamp_text)
        time_digit = int(result.group(1))
        time_type = result.group(2)

        minutes = hours = 0
        if time_type == "minute":
            minutes = time_digit
        elif time_type == "hour":
            hours = time_digit

        duration = timedelta(hours=hours, minutes=minutes)

        post_time = self.log_datetime - duration
        total_minutes = int(duration.total_seconds()/60)

        return post_time.strftime("%H:%M"), total_minutes


    def get_comment_info(self):
        """Printin comment inforation and storing all comments"""
        from src.misc import sp_translate
        self.log(f'Fetching comments:')

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
                comment_urls = [url.text for url in comment_url_elems if url.text != ""]

                if comment_urls:
                    for url in comment_urls:
                        comment_text = comment_text.replace(url ," ")

                comment_media = [media.get_attribute("src") for media in comment_media_elems]

                post_time, total_minutes = self.get_post_time(time_stamp_elem.text)

                self.__fetched_comments.append({
                    "UserName"      :      user_elem.text,
                    "PostTime"      :      post_time,
                    "DurationMins"  :      total_minutes,
                    "ThumbUp"       :      thumb_up_ct,
                    "ThumbDown"     :      thumb_down_ct,
                    "CommentText"   :      sp_translate(comment_text),
                    "CommentUrl"    :      comment_urls,
                    "CommentMedia"  :      comment_media
                })

        self.log(f'Found {len(self.__fetched_comments)} comments:', mode="sub")


    def save_fetched_comments(self, file_name: str="", delimiter: str="\t"):
        """Write fetched comments as text file"""
        self.log(f'Saving fetched comments CSV:')

        if file_name:
            self.csv_file_name = file_name
        else:
            self.csv_file_name = os.path.join(
                check_n_mkdir(self.__csv_output_folder),
                f'{self.ins_title} - {self.log_date_str}.csv'
            )

        header = self.__fetched_comments[0].keys()

        with open(self.csv_file_name, "w", encoding="utf-8") as w_f:
            w_f.write(f'{delimiter.join(header)}\n')
            for comment_details in self.__fetched_comments:
                new_line = delimiter.join([
                    str(val).replace(delimiter, "")
                    for val in comment_details.values()
                ])
                w_f.write(f'{new_line}\n')

        self.log(f'Saved as: {self.csv_file_name}', mode="sub")


    def get_chunck_of_words(self, ignore_words: list=[]):
        """Generating chunck of words with no stopwords"""
        from nltk.tokenize import wordpunct_tokenize
        import nltk
        nltk.download('stopwords')
        from nltk.corpus import stopwords

        comments = " ".join([x["CommentText"] for x in self.__fetched_comments])

        # getting set of stopwords
        _stopwords = set(stopwords.words('english'))
        if ignore_words:
            _stopwords.update(ignore_words)
        list_of_words = [i.lower() for i in wordpunct_tokenize(comments)
            if i.lower() not in _stopwords and i.isalpha()]

        self.words_chunck = " ".join(list_of_words)


    def draw_word_cloud(self, wc_show=False):
        """Generating word cloud using the stored comments"""
        from wordcloud import WordCloud as wc
        import matplotlib.pyplot as plt

        self.log(f'Generating word cloud: [{self.ins_title}]')

        wc_graph = wc(
            max_words=200, background_color="white",
            collocations = False).generate(self.words_chunck)

        self.wc_plot = plt

        self.wc_plot.figure(figsize=(12,8))
        self.wc_plot.imshow(wc_graph, interpolation="bilinear")
        self.wc_plot.title(f"[{self.ins_title}]\n[{self.ins_index}]  [{self.movement}]")
        self.wc_plot.axis("off")
        self.wc_plot.tight_layout(pad=1)

        if wc_show:
            self.wc_plot.show()


    def save_word_cloud(self, file_name: str=""):
        """Save word cloud locally"""
        if file_name:
            self.wc_file_name = file_name
        else:
            self.wc_file_name = os.path.join(
                check_n_mkdir(self.__word_cloud_output_folder),
                f"{self.ins_title} - {self.log_date_str}.JPG"
            )

        self.log(f'Saved word cloud as: {self.wc_file_name}', mode="sub")
        self.wc_plot.savefig(self.wc_file_name)


    def save_instance_info(self):
        """Save instance inforation and push it to instances dict"""
        if self.fetched_comments:
            self.log(f'Generating instance json: [{self.ins_title}]')
            data_values = [list(c.values()) for c in self.fetched_comments]
            data_columns = list(self.fetched_comments[0].keys())
            self.__fetched_instances.update({
                self.ins_title: {
                    "ins_title" : self.ins_title,
                    "ins_index" : self.ins_index,
                    "movem_str" : self.movement,
                    "movem_perc": self.movem_perc,
                    "movem_val" : self.movem_val,
                    "columns"   : data_columns,
                    "comments"  : {
                            "data"    : data_values
                        }
                }
            })


    def dump_instance_json(self, file_name: str=""):
        """Save fetched instances info in json file"""
        import json

        if file_name:
            self.instance_json_file_name = file_name
        else:
            self.instance_json_file_name = os.path.join(
                check_n_mkdir(self.__json_output_folder),
                f"{self.log_date_str}.json"
            )

        self.log(f'Saved fetched instances info as: {self.instance_json_file_name}', mode="sub")
        with open(self.instance_json_file_name, "w") as w_f:
            json.dump(self.__fetched_instances, w_f)


    def fetch_comments(self, instance_name, link):
        """Getting commments from the target site"""
        try:
            self.driver_get_link(link)
            self.log(f'Processing [{instance_name}]')
            self.driver_select_newest()
            self.driver_load_all()
            self.get_stock_info()
            self.get_comment_block_list()
            self.get_comment_info()
            self.save_instance_info()
        except Exception as e:
            self.log(f'Unexpected Error occurred: {str(e)}')
        finally:
            self.driver.quit()
            try:
                return self.fetched_comments
            except AttributeError:
                return list()
