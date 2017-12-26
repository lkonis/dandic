# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# gets query word
# returns a list of links to search-results with appearance of input word
def pick_url(word):
    path_to_url = 'http://ordnet.dk/korpusdk'

    # open a browser

    # width, height
    driver = webdriver.Firefox()
    driver.set_window_size(1640,700)
    driver.get(path_to_url)
    assert 'Korpus' in driver.title
    elem = driver.find_element_by_id('searchform')
    elem.send_keys(word)
    try:
        elem.send_keys(Keys.RETURN)
    except ValueError:
        print "didn't work: " + ValueError.message

    try:
        soup = BeautifulSoup(driver.page_source)
        all_text = soup.get_text()
    except ValueError:
        print "didn't work: " + ValueError.message
    return all_text.split()

if __name__ == '__main__':
    ret_text = pick_url(u'hjælp')
    print ret_text[0:10]

