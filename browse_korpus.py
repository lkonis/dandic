# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import  re
# gets query word
# returns a list of links to search-results with appearance of input word
def pick_url(word):
    path_to_url = 'http://ordnet.dk/korpusdk'

    # convert to searchable text (unicode)
    if isinstance(word, unicode):
        word = word.encode('utf-8')
    # open a browser

    # width, height
    driver = webdriver.Firefox()
    driver.set_window_size(1640,700)
    driver.implicitly_wait(10)
    driver.get(path_to_url)
    assert 'Korpus' in driver.title
    elem = driver.find_element_by_id('searchform')
    elem.send_keys(word.decode('utf-8'))
    try:
        elem.send_keys(Keys.RETURN)
        driver.implicitly_wait(10)
        elem = driver.find_elements_by_css_selector('a[href*=export_page]')
        if len(elem)==1:
            elem[0].click()
        #driver.find_elements_by_css_selector('')
        #exporter = driver.find_element_by_   ('Eksportér denne side til ren tekst')
    except ValueError:
        print "didn't work: " + ValueError.message
        return

    try:
        soup = BeautifulSoup(driver.page_source)
        all_text = soup.get_text()
    except ValueError:
        print "didn't work: " + ValueError.message
        return

    driver.quit()
    ret_text = []
    for line in all_text.split():
        if not re.match("<[\w,.]+>",line):
            ret_text.append(line)
    return ret_text

if __name__ == '__main__':
    ret_text = pick_url('hjlp')
    print ret_text[0:10]

