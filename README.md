# YF_comments_analyzer

This script can be use to scrap newest Yahoo Finance comments within past 24 hours, and to generate corresponding WordCloud

## Getting Started

### Prerequisites

What things you need to install the software and how to install them

```
Python 3.6 and up
beautifulsoup4==4.8.2
bs4==0.0.1
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

### Installing


Switch to your virtualenv and run following command to install all the required modules

```
virtualenv venv
```
```
pip install -r requirements.txt
```
```
venv\Scripts\activate
```

## Running the tests

Modifying json\web_links.json
*Please use the link for the conversation page*

Run following command line to start the process
```
python web_fetcher.py
```

## Authors

-   **Zhiheng Dong** -> [Linkedin](https://www.linkedin.com/in/zhihengdong)


## License

This project is licensed under the MIT License - see the  [LICENSE.txt](https://gist.github.com/PurpleBooth/LICENSE.md)  file for details

## Acknowledgments

-   [CUNY_Data_Challenge_word_cloud_tutorial](https://www.kaggle.com/jelkinp72/cuny-data-challenge-word-cloud-tutorial)
