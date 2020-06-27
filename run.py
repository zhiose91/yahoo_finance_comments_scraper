#!/usr/bin/env python3
from web_scrapers import CommentsScraper
from src.aws_utils import DynamodbCommentsLoader


SITES = [
    ("SP500", "https://finance.yahoo.com/quote/%5EGSPC/community?p=%5EGSPC"),
    ("DowJones", "https://finance.yahoo.com/quote/%5EDJI/community?p=%5EDJI"),
    ("Facebook", "https://finance.yahoo.com/quote/FB/community?p=FB"),
    ("Amazon", "https://finance.yahoo.com/quote/AMZN/community?p=AMZN"),
    ("Apple", "https://finance.yahoo.com/quote/AAPL/community?p=AAPL"),
    ("Netflix", "https://finance.yahoo.com/quote/NFLX/community?p=NFLX"),
    ("Google", "https://finance.yahoo.com/quote/GOOG/community?p=GOOG"),
]


scraper = CommentsScraper()
for instance_name, link in SITES:
    scraper.fetch_comments(link=link, instance_name=instance_name)

loader = DynamodbCommentsLoader()
loader.connect("dynamodb")
loader.set_table("Yahoo_Fin_Comments")

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

    scraper.log(f"Dynamodb-Ops: Inserted successfully", mode="sub")
