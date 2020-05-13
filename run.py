#!/usr/bin/env python3
from web_fetcher import YF_comments_scraper



CONFIGS = {
    "csv_output_folder"       :   r"/home/ec2-user/web_fetcher/Saved_comments",
    "json_output_folder"      :   r"/home/ec2-user/web_fetcher/Saved_comments",
    "word_cloud_output_folder":   r"/home/ec2-user/web_fetcher/Saved_daily_word_clouds",
    "log_output_folder"       :   r"/home/ec2-user/web_fetcher/Work_log"
}

SITES = [
    ("SP500", "https://finance.yahoo.com/quote/%5EGSPC/community?p=%5EGSPC"),
    ("DowJones", "https://finance.yahoo.com/quote/%5EDJI/community?p=%5EDJI"),
    ("Facebook", "https://finance.yahoo.com/quote/FB/community?p=FB"),
    ("Amazon", "https://finance.yahoo.com/quote/AMZN/community?p=AMZN"),
    ("Apple", "https://finance.yahoo.com/quote/AAPL/community?p=AAPL"),
    ("Netflix", "https://finance.yahoo.com/quote/NFLX/community?p=NFLX"),
    ("Google", "https://finance.yahoo.com/quote/GOOG/community?p=GOOG"),
]


scraper = YF_comments_scraper(configs=CONFIGS)
for instance_name, link in SITES:
    scraper.fetch_comments(instance_name, link)
scraper.dump_instance_json()
