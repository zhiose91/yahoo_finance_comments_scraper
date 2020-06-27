# misc
import json
import decimal


class Logger:
    def __init__(self):
        self.__log_file = None

    @classmethod
    def current_datetime(cls):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_open(self, file_name: str = ""):
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


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def sp_translate(text: str):
    return text.encode('ascii', 'ignore').decode('ascii')


def check_n_mkdir(directory: str):
    import os
    if directory:
        directory = directory.replace("\\", "/")
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory
    else:
        return ""


def is_valid_yahoo_finance_link(link: str):
    import re
    return re.match(r"(https://|)finance\.yahoo\.com/quote/.*/community\?p=.*" ,link)


class WordCloudGenerator:

    def __init__(self):
        self.__word_cloud_output_folder = ""
        self.wc_plot = None

    def draw_word_cloud(self, words_chunck: str, wc_show=False):
        """Generating word cloud using the stored comments"""
        from wordcloud import WordCloud as wc
        import matplotlib.pyplot as plt

        wc_graph = wc(
            max_words=200, background_color="white",
            collocations = False).generate(words_chunck)

        self.wc_plot = plt

        self.wc_plot.figure(figsize=(12,8))
        self.wc_plot.imshow(wc_graph, interpolation="bilinear")
        self.wc_plot.axis("off")
        self.wc_plot.tight_layout(pad=1)

        if wc_show:
            self.wc_plot.show()


    def save_word_cloud(self, file_name: str = ""):
        """Save word cloud locally"""
        self.wc_plot.savefig(file_name)
