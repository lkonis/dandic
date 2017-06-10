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

scontext = None
starturl = 'http://ordnet.dk/ddo/ordbog?query=pusten'
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

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
print "there are " + str(l) + " html rows"
many = 2
ddd = {}
while many>0:

    many = many - 1

    # pick one random unused link and exract other links from it
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

    print fromid, url,

    try:
        # document = urllib.urlopen(url, context=scontext)

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
            continue

        print '('+str(len(html))+')',

        soup = BeautifulSoup(html)
        # - test if language is danish
        # - test if document is legal...
        # - extract text from it
        # find relevant text before adding words to frequency dictionary
        # TODO: learn how to use soup instance
        # in this type of html, the 'span' tag contains the text if it has 'class=definition'
        spans = soup.find_all('span', recursive=True)
        for sp in spans:
            try:
                if 'definition' in sp.attrs['class']:
                   words = sp.text.split()
                   for word in words:
                       word = word.strip()
                       if word == '':
                           continue
                       # initialize or update word count
                       ddd[word] = ddd.get(word,0)+1
            except:
                continue
    except KeyboardInterrupt:
        print ''
        print 'Program interrupted by user...'
        break
    except:
        print "Unable to retrieve or parse page"
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
        conn.commit()
        continue

    cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, 0)', ( url, ) ) # I think this line is redundant and will always ignored
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (1, url ) )
    conn.commit()
    # Retrieve all of the anchor tags
    tags = soup('a')
    tag_count = 0
    for tag in tags:
        href = tag.get('href', None)
        if ( href is None ) : continue
        # Resolve relative references like href="/contact"
        up = urlparse(href)
        if ( len(up.scheme) < 1 ) :
            href = urljoin(url, href)
        ipos = href.find('#') # ignore anchors (bookmarks)
        if ( ipos > 1 ) : href = href[:ipos]

        if ( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif') ) : continue
        if ( href.endswith('/') ) : href = href[:-1]

        if ( len(href) < 1 ) : continue

        # found new url? add it to the pages table with NULL html
        cur.execute('INSERT OR IGNORE INTO Pages (url, html) VALUES ( ?, 0 )', ( href, ) )
        tag_count = tag_count + 1
        conn.commit()



    print tag_count

cur.close()

