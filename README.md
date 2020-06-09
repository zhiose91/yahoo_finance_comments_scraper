# Yahoo Finance Comments Scraper - [Zhiheng Dong](https://www.linkedin.com/in/zhihengdong)
---
- Scraping Yahoo Finance comments and their attributes within past 24 hours
  - UserName
  - PostTime
  - DurationMins
  - ThumbUp
  - ThumbDown
  - CommentText
  - CommentUrl
  - CommentMedia
```
scraper.fetch_comments(instance_name="Sample", link="https://") # Use the link for the conversation page
for comment in scraper.fetched_comments:
    print(comment["CommentText"])
```
- Storing comments locally as tab delimited csv file
- Storing comments locally as json format with additional information as follows
```
self.ins_title: {
    "ins_title"     :   "VelocityShares Daily 2x VIX Short-Term ETN (TVIX)",
    "ins_index"     :   151.27,
    "fetched_date"  :   "2020-05-13",
    "movem_str"     :   "-2.33 (-1.52%)",
    "movem_perc"    :   -1.52,
    "movem_val"     :   -2.33,
    "comments_wd_ct":   [["market", 12], ["amazon", 9], ...],
    "comments"      :   {
        "data_cols" : ["UserName", "PostTime", "DurationMins", ...],
        "data_vals" : [
            ["user1", "20:00", "240", ...],
            ["user2", "18:00", "360", ...],
            ...
          ]
      }
}
```
---
### Prerequisites

Requirements
```
Python 3.6 and up
```

Core Modules
```
selenium==3.141.0
requests==2.23.0
nltk==3.5
```

Optional Modules
```
boto3==1.13.16
```

Additional Files
```
chromedriver
```

The script will auto download for
[Windows](https://chromedriver.chromium.org/downloads)
&
[Linux](https://chromedriver.storage.googleapis.com)

---
### Installation
```
virtualenv venv
venv\scripts\activate
pip install -r requirements.txt
```
---
### Sample Usage - CLI
Modifying **`SITES`** variable in run.py for custom Yahoo Finance Page -
**Please use the link for the conversation page**
```python run.py```

---
### Sample Usage - Import
```
from web_fetcher import YF_comments_scraper

analyzer = YF_comments_analyzer()
scraper.fetch_comments(link="https://", instance_name="Sample") # Use the link for the conversation page
comments = scraper.fetched_comments # Get the fetched comments stored in list object

scraper.save_fetched_comments(file_name="//") # Save the fetched tab delimited comments locally
scraper.dump_instance_json(file_name="//") # Save the site comments with meta data like index and movement
```
---

### License

This project is licensed under the MIT License - see the [LICENSE.txt](https://github.com/zhiose91/web_fetcher/blob/master/LICENSE.txt)  file for details

---
### Acknowledgments

- [CUNY Data Challenge word cloud_tutorial](https://www.kaggle.com/jelkinp72/cuny-data-challenge-word-cloud-tutorial)
- [PurpleBooth/README-Template.md](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
- [Yaakov Bressler' BeautifulSoup Tutorial](https://github.com/ybressler/Web-Scraping/blob/master/Web%20Scraping%20Overview%20%E2%80%93%20NYC%20Python%20Meetup.ipynb)
- [Running ChromeDriver and Selenium in Python on an AWS EC2 Instance](https://medium.com/@praneeth.jm/running-chromedriver-and-selenium-in-python-on-an-aws-ec2-instance-2fb4ad633bb5)
