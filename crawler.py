from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pymongo import MongoClient
from parser import *
import re
import requests


def connectDataBase():
    # Creating a database connection object using psycopg2
    DB_NAME = "pages"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")


def storePage(url, html):
    # Value to be inserted
    pagesDoc = {
        "url": url,
        "html": html
    }

    # Insert the document
    pages.insert_one(pagesDoc)


def get_crawler_thread(frontier):
    while frontier:
        url = frontier.pop(0)
        req = requests.get(url)
        html = req.text
        bs = BeautifulSoup(html, 'html.parser')
        stop_criteria = bs.find('h1', string="Permanent Faculty")
        includeCPPUrl = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc) #https://www.cpp.edu
        print(url)
        storePage(url, html)

        if stop_criteria:
            frontier.clear()
            print('Found')
            return url
        else:
            for link in bs.find_all('a', href=re.compile('^(/|.*' + includeCPPUrl + ')')):
                if 'href' in link.attrs:
                    if link.attrs['href'] not in pagesSet:
                        if link.attrs['href'].startswith('/'):
                            frontier.append(includeCPPUrl + link.attrs['href'])
                            pagesSet.add(includeCPPUrl + link.attrs['href'])
                        else:
                            newPage = link.attrs['href']
                            frontier.append(newPage)
                            pagesSet.add(newPage)


if __name__ == '__main__':
    frontier = ['https://www.cpp.edu/sci/computer-science/']
    # Connecting to the database
    db = connectDataBase()

    # Creating a collection
    pages = db.pages
    pagesSet = set()
    target_page_url = get_crawler_thread(frontier)
    parser(target_page_url)

