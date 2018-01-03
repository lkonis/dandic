# find relevant text before adding words to frequency dictionary
# -*- coding: utf-8 -*-

import re
import urllib
from bs4 import BeautifulSoup
from bs4.element import Comment

dansk_tal_str = re.compile(unicode('^[a-zæøåA-ZÆØÅéÉ0-9"\'\s,.:!?]*$', 'utf-8'))
dansk_str = re.compile(unicode('^[a-zæøåA-ZÆØÅéÉ]*$', 'utf-8'))


def valid_text_rules(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    if element.isspace():
        return False
    element_str = element.strip()
    if len(element_str)<2:
        return False
    try:
        if dansk_tal_str.match(element_str):
            return True
        return False
    except:
        return False


def extr_danish_w(html):
    #document = urllib.urlopen(url)
    #html = document.read()
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(text=True)
    visible_text_lines = filter(valid_text_rules, texts)
    words_list = []
    words_cnt = dict()
    MAX_WORD_CNT_IN_PAGE = 2
    for line in visible_text_lines:
        for l in line.split():
            l = l.strip()
            if len(l)<2:
                break
            if re.match(dansk_str, l):
                words_cnt[l] = words_cnt.get(l,0) + 1
                if words_cnt[l] <= MAX_WORD_CNT_IN_PAGE:
                    words_list.append(l)
    return words_list

# update both the temporary dictionary and the SQL Words table
def update_database(words, ddd, cur):
    for word in words:
        word = word.strip()
        if word == '':
            continue
        if not (re.findall(dansk_str, word)):
            continue
        word = re.sub('[.,]', '', word.lower())
        if word=='korpusdk':
            continue
        # initialize or update word count
        ddd[word] = ddd.get(word, 0) + 1
        cur.execute('INSERT OR IGNORE INTO Words (text, freq) VALUES (?, 0)', (word,))
        cur.execute('UPDATE Words SET freq=? WHERE text=?', (ddd[word], word))
    print str(len(words)) + ' words added to Words table',


if __name__ == '__main__':
    # main routine for testing the methods above
    url = 'http://ordnet.dk/korpusdk'

    words_list = extr_danish_w(url)
    for w in words_list:
        print w