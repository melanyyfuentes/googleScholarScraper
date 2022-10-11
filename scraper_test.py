"""
 Melany Fuentes
 Google Scholar Web Scraper
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')

# spoofing headers to look legit
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


def get_urls(querylist):
    df = pd.DataFrame(columns=['person', 'user_url'])

    for query in querylist:
        url = 'https://scholar.google.com/citations?view_op=search_authors&mauthors=' + query + '&hl=en&oi=ao'
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        # gives results from search query
        person_results = soup.find_all(class_='gs_ai_pho')
        print('persons results:' + str(person_results[0]))

        # appending first URL and name to dataframe
        person_url = person_results[0].get('href')
        df.loc[len(df.index)] = [query, person_url]
        # for cell in soup.select('table#foobar td.empformbody'):
        # Do something with these table cells.
        get_info(person_url)


def get_info(user_url):
    url = 'https://scholar.google.com' + str(user_url)
    driver = webdriver.Chrome(chrome_options=options,
                              executable_path=r"/Users/melanyfuentes/PycharmProjects/googleScholarScraper/chromedriver")
    driver.get(url)

    more = True
    # while more:
    elem = driver.find_element('xpath', '//*[@id="gsc_bpf_more"]')

    # just clicking through, make this nicer later
    elem.click()
    elem.click()
    elem.click()
    elem.click()
    elem.click()
    elem.click()
    elem.click()
    elem.click()

    # print(driver.page_source)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)

    results = soup.find_all(class_='gsc_a_tr')
    print(results[0])

    # gives results from the


# print(soup.prettify())

if __name__ == '__main__':
    # Get names and top URL
    querys = ['Dorothy+Roberts']  # edit the list here
    get_urls(querys)

    # Take existing dataframe URLs and get csv entries
