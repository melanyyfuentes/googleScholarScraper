"""
Melany Fuentes
Google Scholar Web Scraper
"""
import argparse
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import re
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# spoofing headers for bs4 to look legit
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


# To theoretically go through a list of names, search it
# then get the top url from the search
# put this into a csv file

# initial just getting user's actual profile link
def get_urls(querylist, save_url):
    user_data = []
    # making data frame
    url_frame = pd.DataFrame(columns=['person', 'user_url'])

    for query in querylist:
        url = 'https://scholar.google.com/citations?view_op=search_authors&mauthors=' + query.replace(" ",
                                                                                                      "+") + '&hl=en&oi=ao'
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        # gives results from search query
        person_results = soup.find_all(class_='gs_ai_pho')

        if len(person_results) == 0:
            url_frame.loc[len(url_frame.index)] = [query, 'NA']
        else:
            url_got = 'https://scholar.google.com' + person_results[0].get('href')
            url_frame.loc[len(url_frame.index)] = [query, url_got]

    url_frame.to_csv(save_url, index=False)


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')


# gets the information and adds it to dataframe
def get_info(user_urls):
    paper_frame = pd.DataFrame(columns=['author', 'title', 'link', 'year', 'coauthors', 'publish_location', 'pages'])

    csv_use = open(user_urls, "r")
    mycsv = csv.reader(csv_use)
    next(mycsv)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
       # chrome_options=options,
       #                       executable_path=r"/Users/melanyfuentes/PycharmProjects/googleScholarScraper/chromedriver")
    for row in mycsv:
        if row[1] != "NA":
            url = str(row[1])
            driver.get(url)
            elem = driver.find_element('xpath',
                                       '//*[@id="gsc_bpf_more"]')  # just clicking through, make this nicer later
            # clicking through the more thing
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_papers = soup.find_all(class_='gsc_a_tr')

            if len(soup) > 0:
                for paper in all_papers:
                    author = row[0]
                    titles = paper.find(attrs={"class": "gsc_a_at"})  # (class_='gsc_a_at')
                    paper_link = "https://scholar.google.com/" + titles.get("href")
                    titles = re.sub("\<.*?\>", "", str(titles))

                    info_dict = get_paper_info(author, titles)
                    paper_frame.append(info_dict)
                    print(paper_frame)


                    # paper_frame.loc[len(paper_frame.index)] = [row[0], ]


def get_paper_info(authored, title):
    driver1 = webdriver.Chrome(options=options,
                               executable_path=r"/Users/melanyfuentes/PycharmProjects/googleScholarScraper/chromedriver")

    add_part = urllib.parse.quote_plus(authored) + " " + urllib.parse.quote_plus(title)
    link = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C34&q=' + add_part + '&btnG='
    driver1.get(link)


    elem1 = driver1.find_element(By.XPATH,
                                '//*[@id="gs_res_ccl_mid"]/div[1]/div[2]/div[3]/a[2]')
    elem1.click()

    elem2 = driver1.find_element(By.XPATH, '//*[@id="gs_citi"]/a[1]')
    elem2.click()

    elem3 = driver1.find_element(By.XPATH, "/html/body/pre").text
        #elem2.text #driver1.find_element(By.XPATH, '/html/body/pre/text()').text

    return bibtex_helper(elem3)


# @article{yudell2016taking,
#   title={Taking race out of human genetics},
#   author={Yudell, Michael and Roberts, Dorothy and DeSalle, Rob and Tishkoff, Sarah},
#   journal={Science},
#   volume={351},
#   number={6273},
#   pages={564--565},
#   year={2016},
#   publisher={American Association for the Advancement of Science}
# }

# input entire bibtex citation page. Pass argument as bs4 class
def bibtex_helper(fulltext):
    mydict = {}
    type = fulltext[1: fulltext.index("{")]
    mydict["type"] = type

    print(type)
    rest_split = fulltext[fulltext.index("{")+1: ]
    rest_split = rest_split.splitlines()[1:] #getting rid of first line
    #rest_split = [word.strip() for word in rest_split.split(',')]
    print(rest_split)

    for elem in rest_split:
        elem_pair = elem.split('=')
        key = str(elem_pair[0].strip())
        print("key is: " + key)
        lock = str(elem_pair[1][elem_pair[1].index("{")+1:elem_pair[1].index("}")-1])
        print("Lock is: " + lock)
        mydict[key] = lock

    return mydict

    # returns
    # authors, publication date, publisher


if __name__ == '__main__':
    # needed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--authorData', default='data/sampleData.xlsx')
    parser.add_argument('--columnName', default='Name')

    args = parser.parse_args()

    # Getting names
    df = pd.ExcelFile(args.authorData).parse('Sheet1')
    queries = [x for x in df[args.columnName]]
    # queries = ['Dorothy+Roberts']

    # getting URLs and saving into dataframe
    saveDir = "data/user_links" + str(datetime.now().strftime("%m.%d.%Y_%H:%M:%S")) + ".csv"
    get_urls(queries, saveDir)
    #saveDir = "data/10.10.2022_15:59:39.csv"

    get_info(saveDir)

    #get_paper_info('dorothy roberts', 'Killing the black body: Race, reproduction, and the meaning of liberty')

    # Take existing dataframe URLs and get csv entries
    # get_info()
