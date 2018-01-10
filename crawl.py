#!/usr/bin/env python
# -*- coding: utf-8 -*-

# explain the interface of this function
# put it in the coggle
# save output into 3 SQL tables:
# 1. pages: a list of many links of unvisited web-pages
#   a status field show for each entry if its visited or not
# 2. words: a list of words with frequency of occurence
# 3. links: links between ...


import sqlite3
import urllib
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin
import re
import init_web_pages as iwp
import browse_korpus as krp
# if Pages table is empty, initiate it with fixed
# TODO: alternative: always initiate with random url (from a fixed list)
from bs4_utilities import *


def init_pages_table():
    global starturl, conn, cur, ddd
    u = iwp.url_starter()
    u.init_urls()
    starturl = u.draw_link()# draw a random link from a list
    # open sql database file
    conn = sqlite3.connect('spider.sqlite')
    cur = conn.cursor()
    # handle 'Words' table
    cur.execute('''CREATE TABLE IF NOT EXISTS Words
    (
    id INTEGER PRIMARY KEY,
    text TEXT UNIQUE,
    used_in_korpus BOOL default False,
    freq INTEGER
    )''')
    cur.execute('''SELECT text,freq FROM Words''')
    words = cur.fetchall()
    ddd = {}
    for k, v in words:
        ddd[k] = v
    cur.execute('''SELECT id, text, used_in_korpus FROM Words''')
    words = cur.fetchall()
    # handle 'Pages' table
    cur.execute('''CREATE TABLE IF NOT EXISTS Pages 
    (
     id INTEGER PRIMARY KEY,
     url TEXT UNIQUE,
     error INTEGER,
     html INTEGER
    )''')

    # count how many entries exist
    cur.execute('''SELECT id,url FROM Pages''')
    rows = cur.fetchall()
    pl = len(rows)
    # count how many used entries (with html ==1)
    cur.execute('''SELECT id,url FROM Pages WHERE html == 1''')
    rows = cur.fetchall()
    l = len(rows)
    print "A table of "+str(pl)+" pages already exists, in which " + str(l) + " of them were used"

    # or....
def extract_from_korpus(query_word):
    return krp.pick_url(query_word)

def extract_from_new_link():

    # 1. pick one random unused link
    # 2. extract other links from it
    # 3. extract all text words and update word-database


    '''
    # find relevant text before adding words to frequency dictionary
    def tag_visible(element):
        from bs4.element import Comment
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        if element.isspace():
            return False
        dansk_str = re.compile(unicode('^[a-zæøåA-ZÆØÅ\s,.:!?]*$', 'utf-8'))
        try:
            if dansk_str.match(element):
                return True
        except:
            return False

    def text_from_html(body):
        soup = BeautifulSoup(body, 'html.parser')

        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)
    '''
    # before extracting new url links, choose which to ignore
    def ignore_tags(url, href):
        forbidden_words='''
            javascript
            facebook
            tweeter
            '''
        if (href is None):
            return False
        if '@' in href:
            return False
        for w in forbidden_words.split():
            if w in href:
                return False
        # Resolve relative references like href="/contact"
        up = urlparse(href)
        if (len(up.scheme) < 1):
            href = urljoin(url, href)
        if (len(up.query) > 0 or len(up.params) > 0 or len(up.fragment) > 0):
            return False
        ipos = href.find('#')  # ignore anchors (bookmarks)
        if (ipos > 1): href = href[:ipos]

        if (href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif')):
            return False
        if (href.endswith('.mp3') or href.endswith('.avi')):
            return False
        if (href.endswith('/')): href = href[:-1]

        if (len(href) < 1):
            return False

        return href


    def extract_urls(soup, url):
        #  Retrieve all of the anchor tags
        # update the page table in sql file, adding new urls
        tags = soup.find_all('a',href=True)
        MAX_NEW_LINKS_FROM_PAGE = 12
        MAX_SAME_DOMAIN_LINKS = 8
        tag_count = 0
        tag_same_domain_count = 0
        same_domain = False
        for tag in tags:
            if tag_count>=MAX_NEW_LINKS_FROM_PAGE:
                break
            href = tag.get('href', None)
            if not tag['href'].startswith('http'):
                same_domain = True
            else:
                same_domain = False
            href = ignore_tags(url, href)
            if not href: continue
            if same_domain:
                tag_same_domain_count = tag_same_domain_count + 1
                if tag_same_domain_count >= MAX_SAME_DOMAIN_LINKS:
                    continue
            # found new url? add it to the pages table with NULL html
            cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, 0 )', (href,))
            tag_count = tag_count + 1
        conn.commit()
        print ', ' + str(tag_count) + ' new links were added to Pages table'

    def try_read(url):
        # try to read a page using the new url, update the SQL Pages table
        # TODO - test if language is danish
        try:

            # Normal Unless you encounter certificate problems
            document = urllib.urlopen(url)

            # verify language is danish
            soup = BeautifulSoup(document,'html.parser')
            if not soup.find('html',lang='da'):
                if not 'watchmedier.dk' in url:
                    print 'language is not danish'
                    return
            document = urllib.urlopen(url)
            html = document.read()
            # - test if document is legal...
            if document.getcode() != 200 :
                print "Error on page: ",document.getcode()
                cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), url) )

            if 'text/html' != document.info().gettype() :
                print "Ignore non text/html page"
                cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
                conn.commit()
                return

            print '('+str(len(html))+' characters):'

        except KeyboardInterrupt:
            print ''
            print 'Program interrupted by user...'
            return html
        except:
            print "Unable to retrieve or parse page"
            cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
            conn.commit()
            try:
                return html
            except:
                return None
        return html

    url = pick_unused_link(cur, starturl)

    html = try_read(url)
    if html==None:
        return
    # 3. extract text from html
    words = extr_danish_w(html)
#    body_text = text_from_html(html)
#    words = body_text.split()
    # add words into temporary dictionary, ans also update SQL word table
    update_database(words,ddd,cur)
    # update the page table in sql file, checking the current page url as 'used'
    soup = BeautifulSoup(html,'lxml')
    cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, 0)', ( url, ) )
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (1, url ) )
    conn.commit()

    # 2. extract and add new links
    extract_urls( soup, url)
def add_from_korpus():
    cur.execute('SELECT text FROM Words WHERE freq >= 5 AND NOT used_in_korpus ORDER BY RANDOM() LIMIT 1')
    extr = cur.fetchall()
    if len(extr)==1:
        try_word = extr.pop()
        try_word = try_word[0]
        if try_word==u'cookies':
            return
        words = extract_from_korpus(try_word)
        update_database(words, ddd, cur)
        cur.execute('UPDATE Words SET used_in_korpus=? WHERE text=?', (True, try_word))
        conn.commit()


if __name__ == '__main__':
    init_pages_table()
    extract_from_new_link()
    for i in range(10):
        extract_from_new_link()
        add_from_korpus()
    cur.close()