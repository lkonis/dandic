# -*- coding: utf-8 -*-
#implementation of tutorial in http://splinter.readthedocs.io/en/latest/tutorial.html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from splinter import Browser

path_to_url = 'http://ordnet.dk/korpusdk'

# open a browser

# width, height
driver = webdriver.Firefox()
driver.set_window_size(1640,700)
driver.get(path_to_url)
assert 'Korpus' in driver.title
elem = driver.find_element_by_id('searchform')
elem.send_keys(u'hjælp')
try:
    elem.send_keys(Keys.RETURN)
except ValueError:
    print "didn't work: " + ValueError.message

