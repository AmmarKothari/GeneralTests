
import urllib2
import os
import pdb
import datetime
import time
from bs4 import BeautifulSoup
import io

import pycurl
import StringIO

from selenium import webdriver

DELAY_BETWEEN_SAVES = 10 # time between saving pages in seconds


def check_folder(folder_name):
    # makes a folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    else:
        print('Folder already exists')

def get_url_lib(url):
    response = urllib2.urlopen(url)
    webContent = response.read()
    return webContent


def curl_save(url):
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    return c,b

def get_selenium(url):
    browser = webdriver.Firefox()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    pdb.set_trace()
    with io.open("scraped.html", "w", encoding="utf-8") as f:
        f.write(soup.get_text())
        f.close()
    pdb.set_trace()


def get_file_name(game):
    cur_time = datetime.datetime.now()
    hour = cur_time.hour
    minute = cur_time.minute
    sec = cur_time.second
    file_name = ('%s/%s_%s_%s.html' %(game, hour, minute, sec))
    return file_name


# url = 'https://sports.bovada.lv/basketball/nba/golden-state-warriors-portland-trail-blazers-201802142230'
url = 'https://sports.bovada.lv/basketball/rest-of-world/philippines/ncruclaa/ama-titans-de-la-salle-university-dasmarinas-patriots-201802150100'
game = url.split('/')[-1]
get_selenium(url)
check_folder(game)

pdb.set_trace()

# c, b = curl_save(url)


i = 0
while i < 100:
    c.perform()
    html = b.getvalue()
    # html = get_url_lib(url)
    file_name = get_file_name(game)
    i += 1
    with open(file_name, 'w') as f_html:
        f_html.write(html)
        print('File Saved %s_%s_%s' %(hour, minute, sec))
    time.sleep(DELAY_BETWEEN_SAVES) # wait before next pickup

# f = open('obo-t17800628-33.html', 'w')
# f.write(webContent)
# f.close
