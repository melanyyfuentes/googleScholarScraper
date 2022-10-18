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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# spoofing headers for bs4 to look legit
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


# gets user's profile links and returns a csv with this info
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


# options for selenium
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')


# gets preliminary paper information and makes a csv
def get_info(user_urls):
    # initializing list of all papers and info
    every_paper = []

    # reading in csv file
    csv_use = open(user_urls, "r")
    mycsv = csv.reader(csv_use)
    next(mycsv) # skipping headers

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) # driver for searches
    for row in mycsv:
        if row[1] != "NA":
            url = str(row[1]) # user profile URL
            driver.get(url)

            # clicking through to show all papers
            elem = driver.find_element('xpath',
                                       '//*[@id="gsc_bpf_more"]')  # make this nicer later
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()
            elem.click()

            # getting html for each user
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_papers = soup.find_all(class_='gsc_a_tr') # list of all user papers

            # getting individual paper info, checking they have written 1+ papers
            if len(all_papers) > 0:
                for paper in all_papers:
                    # getting href for paper (link)
                    paper_info = paper.find(attrs={"class": "gsc_a_at"})
                    paper_link = "https://scholar.google.com/" + paper_info.get("href")

                    # getting citation info
                    paper_gray_text = paper.findAll(attrs={"class": "gs_gray"})
                    if len(paper_gray_text) > 1: # if more than 1 line
                        paper_first_line = paper_gray_text[0].findAll(text=True)
                        paper_second_line = paper_gray_text[1].findAll(text=True)
                    else: # if only 1 line
                        paper_first_line = paper_gray_text.findAll(text=True)
                        paper_second_line = "NA"

                    titles = re.sub("\<.*?\>", "", str(paper_info))  # getting paper string
                    author = row[0]  # adding to every paper

                    # add entry to our larger list
                    every_paper.append([author, paper_link, titles, paper_first_line, paper_second_line])

    # converting to dataframe then csv
    my_df = pd.DataFrame(every_paper, columns=['author', 'paper_link', 'paper_title',
                                               'paper_first_line', 'paper_second_line'])
    save_at = user_urls[:-4] + "_user_info.csv"
    my_df.to_csv(save_at, index=False)


# Independently searches author and title to get info
def get_paper_info(authored, title):
    driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    add_part = urllib.parse.quote_plus(authored) + "+" + urllib.parse.quote_plus(title)
    link = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C34&q=' + add_part + '&btnG='
    driver1.get(link)
    print(link)

    # find and click citation button
    # elem1 = driver1.find_element(By.CLASS_NAME,
    #                              'gs_or_cit.gs_or_btn')
    # driver1.execute_script("arguments[0].click();", elem1)
    elem1 = driver1.find_element(By.XPATH,
                                 '//*[@id="gs_res_ccl_mid"]/div[1]/div[2]/div[3]/a[2]')
    elem1.click()
    # find and click bibtex reference

    soup = BeautifulSoup(driver1.page_source, 'html.parser')
    print(driver1.page_source)
    print("SOUP IS")
    print(soup.find_all(class_='gs_citi'))
    # pass_to = soup.find_all(class_='gs_citi')
    # print(pass_to)
    # return bibtex_helper(pass_to)


# input entire bibtex citation page. Pass argument as bs4 class
def bibtex_helper(fulltext):
    mydict = {}

    type = fulltext[1: fulltext.index("{")]
    mydict["type"] = type
    print("type is:")
    print(type)

    rest_split = fulltext[fulltext.index("{") + 1:]
    rest_split = rest_split.splitlines()[1:-1]  # getting rid of first line
    # rest_split = [word.strip() for word in rest_split.split(',')]
    print(rest_split)

    for elem in rest_split:
        elem_pair = elem.split('=')
        key = str(elem_pair[0].strip())
        print("key is: " + key)
        lock = str(elem_pair[1][elem_pair[1].index("{") + 1:elem_pair[1].index("}")])
        print("Lock is: " + lock)
        mydict[key] = lock

    return mydict


if __name__ == '__main__':
    # needed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--authorData', default='data/sampleData.xlsx') # CHANGE FOR ORIGINAL AUTHOR OF INTEREST DATAFRAME
    parser.add_argument('--columnName', default='Name') # WHERE AUTHOR COLUMN IS STORED IN EXCEL
    parser.add_argument('--saveDir', default= "data/user_links" + str(datetime.now().strftime("%m.%d.%Y_%H:%M:%S")) + ".csv") # default save_dir
    args = parser.parse_args()

    # Getting query names
    df = pd.ExcelFile(args.authorData).parse('Sheet1') # make sure to parse correct sheet
    queries = [x for x in df[args.columnName]]

    # getting user profile URLs and saving into dataframe
    get_urls(queries, args.saveDir)

    # getting paper info into CSV
    get_info(args.saveDir)

