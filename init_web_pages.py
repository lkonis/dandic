#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randint as rndi
starturl=list('')
def init_urls():

    starturl.append('http://ordnet.dk/ddo/ordbog?query=pusten')
    starturl.append('http://jyllands-posten.dk')
    starturl.append('http://')
    return starturl

def draw_link():
    i = rndi(0,len(starturl)-1)
    return starturl[i]

if __name__ == '__main__':
    starturl = init_urls()
    for l in starturl:
        print 'url: '+ l
    print 'chosen url: ' + draw_link()