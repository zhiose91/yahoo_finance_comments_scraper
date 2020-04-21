# YF_comments_analyzer - [Zhiheng Dong](https://www.linkedin.com/in/zhihengdong)
---
- Scrapping Yahoo Finance comments and their attributes within past 24 hours
  - Username
  - Time Stamp
  - Thumb Up count
  - Thumb Down count
  - Comment text
  - Urls
  - Media
- Storing comments locally as tab delimited csv file
- Generating word cloud using fetched comments+
---
### Prerequisites

Requirements
```
Python 3.6 and up
```
Modules
```
certifi==2019.11.28
chardet==3.0.4
cycler==0.10.0
idna==2.8
kiwisolver==1.1.0
matplotlib==3.1.3
nltk==3.4.5
numpy==1.18.1
Pillow==7.0.0
pyparsing==2.4.6
python-dateutil==2.8.1
requests==2.22.0
selenium==3.141.0
six==1.14.0
soupsieve==2.0
urllib3==1.25.8
wordcloud==1.6.0
```
Additional file
```
chromedriver
```
The script will auto download for
[Windows](https://chromedriver.chromium.org/downloads)
&
[Linux](https://chromedriver.storage.googleapis.com)

---
### Installation
Linux:
```
virtualenv venv
venv\bin\activate
pip3 install -r requirements.txt
```
Windows:
```
virtualenv venv
venv\scripts\activate
pip install -r requirements.txt
```
---
### Sample Usage - CLI
Modifying **`SITES`** variable in config.py for custom Yahoo Finance Page
**Please use the link for the conversation page**
`python3 web_fetcher.py`

---
### Sample Usage - Import
```
from web_fetcher import YF_comments_analyzer

analyzer = YF_comments_analyzer()
analyzer.fetch_comments(instance_name="Sample", link="https://") # Use the link for the conversation page
comments = analyzer.fetched_comments # Get the fetched comments stored in list object

analyzer.save_fetched_comments(file_name="//") # Save the fetched comments locally
analyzer.draw_word_cloud(wc_show=True, ignore_words=["stock", "market"]) # Generate word cloud using the fetched comments
analyzer.save_word_cloud(file_name="//") # Save the word cloud image locally
```
---

### License

This project is licensed under the MIT License - see the [LICENSE.txt](https://github.com/zhiose91/web_fetcher/blob/master/LICENSE.txt)  file for details

---
### Acknowledgments

[CUNY Data Challenge word cloud_tutorial](https://www.kaggle.com/jelkinp72/cuny-data-challenge-word-cloud-tutorial)
[PurpleBooth/README-Template.md](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
[Yaakov Bressler' BeautifulSoup Tutorial](https://github.com/ybressler/Web-Scraping/blob/master/Web%20Scraping%20Overview%20%E2%80%93%20NYC%20Python%20Meetup.ipynb)
[Running ChromeDriver and Selenium in Python on an AWS EC2 Instance](https://medium.com/@praneeth.jm/running-chromedriver-and-selenium-in-python-on-an-aws-ec2-instance-2fb4ad633bb5)
