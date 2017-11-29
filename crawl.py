#!/usr/bin/env python
# -*- coding: utf-8 -*-

# explain the interface of this function
# put it in the koggle
# create 3 tables:
# pages: web-pages (url, html(empty if not visited yet), error )
#   can be a list of many links of unvisited web-pages
# links: linkes between pages (by id)
# webs: ?

import sqlite3
import urllib
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin
import re


def init_pages_table():
    global starturl, conn, cur, ddd
    #starturl = 'http://ordnet.dk/ddo/ordbog?query=pusten'
    starturl = 'http://jyllands-posten.dk'
    conn = sqlite3.connect('spider.sqlite')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Words
    (
    id INTEGER PRIMARY KEY,
    text TEXT UNIQUE,
    freq INTEGER
    )''')
    cur.execute('''SELECT text,freq FROM Words''')
    words = cur.fetchall()
    ddd = {}
    for k, v in words:
        ddd[k] = v
    cur.execute('''CREATE TABLE IF NOT EXISTS Pages 
    (
     id INTEGER PRIMARY KEY,
     url TEXT UNIQUE,
     error INTEGER,
     html INTEGER
    )''')
    # count how many entries with html exist
    cur.execute('''SELECT id,url FROM Pages WHERE html == 1''')
    rows = cur.fetchall()
    l = len(rows)
    print "There is an initial table of pages with " + str(l) + " lines"


def ignore_tags(url, href):
    ignore = False
    if (href is None):
        return False
    if '@' in href:
        return False
    if 'javascript' in href:
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


def extract_from_new_link():

    # 1. pick one random unused link
    # 2. extract other links from it
    # 3. extract all text words and update word-database

    # 1. pick a random unused link
    url = pick_unused_link(cur)

    try:

        # Normal Unless you encounter certificate problems
        document = urllib.urlopen(url)

        html = document.read()
        if document.getcode() != 200 :
            print "Error on page: ",document.getcode()
            cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), url) )

        if 'text/html' != document.info().gettype() :
            print "Ignore non text/html page"
            cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
            conn.commit()
            return

        print '(this page has '+str(len(html))+' characters)',

    except KeyboardInterrupt:
        print ''
        print 'Program interrupted by user...'
        return
    except:
        print "Unable to retrieve or parse page"
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
        conn.commit()
        return

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

    body_text = text_from_html(html)
    words = body_text.split()
    extract_words(words,ddd)
    soup = BeautifulSoup(html)
    # - test if language is danish
    # - test if document is legal...
    # - extract text from it
    # find relevant text before adding words to frequency dictionary
    # TODO: consider adding soup.find_all('p') and soup.find_all('div') and then search for text in each member
    '''
    # 1. jyllan post
    metas = soup.find_all('meta')
    for m in metas:
        if ('name' in m.attrs ) and ('description' in m.attrs['name']):
            words = m['content'].split()
            extract_words(words,ddd)

    divs = soup.find_all('div')
    for d in divs:
        if len(d.contents)==0:
            words = d.text.split()
            extract_words(words,ddd)
    # 2. DDO - in this type of html, the 'span' tag contains the text if it has 'class=definition'x
    spans = soup.find_all('span', recursive=True)
    for sp in spans:
        try:
            if 'definition' in sp.attrs['class']:
                words = sp.text.split()

                extract_words(words,ddd)

        except:
            continue
    '''
    # region Description
#    for div in soup.find_all('div', recursive=True):
#        try:
#            words = div.text
#            extract_words(words,ddd)
#        except:
#            continue
        # endregion
    cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, 0)', ( url, ) ) # I think this line is redundant and will always ignored
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (1, url ) )
    conn.commit()
    # Retrieve all of the anchor tags
    tags = soup('a')
    tag_count = 0
    for tag in tags:
        href = tag.get('href', None)
        href = ignore_tags(url, href)
        if not href: continue
        # found new url? add it to the pages table with NULL html
        cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, 0 )', ( href, ) )
        tag_count = tag_count + 1
    conn.commit()
    print ', ' + str(tag_count) + ' new links where added to page table'


def pick_unused_link(cur):
    cur.execute('SELECT id,url FROM Pages WHERE html == 0 ORDER BY RANDOM() LIMIT 1')
    try:
        row = cur.fetchone()
        # print row
        fromid = row[0]
        url = row[1]
    except:
        print 'Empty table or no unretrieved HTML pages found'
        url = starturl
        fromid = 0
    print 'extract words from page: ', url,
    return url


def extract_words(words,ddd):
    for word in words:
        word = word.strip()
        if word == '':
            continue
        if len(re.findall('[0-9_@#"%&/()=+?-]', word)):
            continue
        word = re.sub('[.,]', '', word.lower())
        # initialize or update word count
        ddd[word] = ddd.get(word, 0) + 1
        cur.execute('INSERT OR IGNORE INTO Words (text, freq) VALUES (?, 0)', (word,))
        cur.execute('UPDATE Words SET freq=? WHERE text=?', (ddd[word], word))
    #                    cur.execute('UPDATE Words SET freq=freq+1 WHERE text=?', (word,))


if __name__ == '__main__':
    init_pages_table()
    for i in range(10):
        extract_from_new_link()
    cur.close()