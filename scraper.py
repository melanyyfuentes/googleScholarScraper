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

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
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


def get_info(user_urls):
    csv_use = open(user_urls, "r")
    mycsv = csv.reader(csv_use)
    next(mycsv)
    for row in mycsv:
        print(row)
        if row[1] != "NA":
            url = 'https://scholar.google.com' + str(row[1])
            driver = webdriver.Chrome('/Users/melanyfuentes/PycharmProjects/googleScholarScraper/chromedriver', options=chrome_options)
            try:
                driver.get(url)
            except WebDriverException:
                print("page down")

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
            page = driver.page_source

            soup = BeautifulSoup(page, 'html.parser')
            results = soup.find_all(class_='gsc_a_tr')


# def make_pretty(html_code)


if __name__ == '__main__':
    # needed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--authorData', default='data/sampleData.xlsx')
    parser.add_argument('--columnName', default='Name')

    args = parser.parse_args()

    # Getting names
    df = pd.ExcelFile(args.authorData).parse('Sheet1')
    queries = [x for x in df[args.columnName]]

    # getting URLs and saving into dataframe
    saveDir = "data/" + str(datetime.now().strftime("%m.%d.%Y_%H:%M:%S")) + ".csv"
    get_urls(queries, saveDir)

    get_info(saveDir)

    # Take existing dataframe URLs and get csv entries
    # get_info()
