# find relevant text before adding words to frequency dictionary
# -*- coding: utf-8 -*-

import re
import urllib
from bs4 import BeautifulSoup
from bs4.element import Comment

dansk_tal_str = re.compile(unicode('^[a-zæøåA-ZÆØÅéÉ0-9"\'\s,.:!?]*$', 'utf-8'))
dansk_str = re.compile(unicode('^[a-zæøåA-ZÆØÅéÉ]*$', 'utf-8'))


def tag_visible_lines(element):
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


if __name__ == '__main__':
    # Normal Unless you encounter certificate problems
    url = 'http://ordnet.dk/korpusdk'

    document = urllib.urlopen(url)

    html = document.read()

    soup = BeautifulSoup(html, 'html.parser')

    texts = soup.findAll(text=True)
    visible_text_lines = filter(tag_visible_lines, texts)
    words_list = []
    for line in visible_text_lines:
        for l in line.split():
            l = l.strip()
            if re.match(dansk_str, l):
                words_list.append(l)
    print visible_text_lines