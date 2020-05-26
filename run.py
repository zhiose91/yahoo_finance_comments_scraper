#!/usr/bin/env python3
from web_fetcher import YF_comments_scraper
from src.dynamodb_utils import Comment_loader


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

loader = Comment_loader()
loader.connect_to_db()
loader.set_table("Yahoo_fin_comment")

for ins_title, ins_info in scraper.fetched_instances.items():
    scraper.log(
        f"Dynamodb-Ops: Inserting pKey:[{ins_title}] sKey:[{ins_info['fetched_date']}]",
        mode="main"
    )

    loader.table.put_item(
        Item={
            "instance_name" : ins_info["ins_title"],
            "fetched_date"  : ins_info["fetched_date"],
            "fetch_info"    : ins_info
        }
    )

    scraper.log(f"Dynamodb-Ops: Valid insertion", mode="sub")
