from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pymongo import MongoClient
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


def store_professors(name, title, office, phone, email, website):
    # Connecting to the database
    db = connectDataBase()
    # Creating a collection
    professors = db.professors

    # Value to be inserted
    professorsDoc = {
        "name": name,
        "title": title,
        "office": office,
        "phone": phone,
        "email": email,
        "website": website
    }

    # Insert the document
    professors.insert_one(professorsDoc)


def parser(target_page_url):
    # Connecting to the database
    db = connectDataBase()

    document = db.pages.find_one({'url': target_page_url})

    professors = []
    req = requests.get(document['url'])
    html = req.text
    bs = BeautifulSoup(html, 'html.parser')
    professor = bs.find_all('div', {'class': 'clearfix'})

    for prof in professor:
        h2_tag = prof.find('h2')
        if h2_tag:
            name = h2_tag.text.strip()
            print(name)
        else:
            continue
        # name, title, office, phone, email, and, website
        title_tag = prof.find('strong', string=re.compile("Title"))
        title = title_tag.next_sibling.replace(":", "").strip()
        print(title)

        office_tag = prof.find('strong', string=re.compile("Office"))
        office = office_tag.next_sibling.replace(":", "").strip()
        print(office)

        phone_tag = prof.find('strong', string=re.compile("Phone"))
        phone = phone_tag.next_sibling.replace(":", "").strip()
        print(phone)

        email_tag = prof.find('strong', string=re.compile("Email"))
        email = email_tag.find_next('a').get_text().replace(":", "")
        print(email)

        web_tag = prof.find('strong', string=re.compile("Web"))
        website = web_tag.find_next('a').get_text().replace(":", "")
        print(website)

        print()

        store_professors(name, title, office, phone, email, website)
