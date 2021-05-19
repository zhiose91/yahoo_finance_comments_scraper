#!/usr/bin/env python3
import pprint
import logging
from web_scrapers import CommentsScraper


logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)


SITES = [
    ("SP500", "https://finance.yahoo.com/quote/%5EGSPC/community?p=%5EGSPC"),
    ("DowJones", "https://finance.yahoo.com/quote/%5EDJI/community?p=%5EDJI"),
    ("Facebook", "https://finance.yahoo.com/quote/FB/community?p=FB"),
    ("Amazon", "https://finance.yahoo.com/quote/AMZN/community?p=AMZN"),
    ("Apple", "https://finance.yahoo.com/quote/AAPL/community?p=AAPL"),
    ("Netflix", "https://finance.yahoo.com/quote/NFLX/community?p=NFLX"),
    ("Google", "https://finance.yahoo.com/quote/GOOG/community?p=GOOG"),
]

pp = pprint.PrettyPrinter(indent=4)

scraper = CommentsScraper()
for instance_name, link in SITES:
    scraper.fetch_comments(link=link, instance_name=instance_name)

for ins_title, ins_info in scraper.fetched_instances.items():
    print(ins_title)
    pp.pprint(ins_info["meta"])
    pp.pprint(
        dict(zip(
            ins_info["comments"]["header"],
            ins_info["comments"]["rows"][0]
        ))
    )
