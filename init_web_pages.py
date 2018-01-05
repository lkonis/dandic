#!/usr/bin/env python
# -*- coding: utf-8 -*-

class url_starter():
    starturl=list('')
    def init_urls(self):
        self.starturl.append('http://ordnet.dk/ddo/ordbog?query=pusten')
        self.starturl.append('http://jyllands-posten.dk')
        self.starturl.append('https://www.dr.dk/ligetil')
        self.starturl.append('https://mediavejviseren.dk/aviser/danske-aviser-danmark.htm')

    def draw_link(self):
        from random import randint as rndi
        i = rndi(0,len(self.starturl)-1)
        return self.starturl[i]

if __name__ == '__main__':
    urls = url_starter()
    urls.init_urls()
    for l in urls.starturl:
        print 'url: '+ l
    print 'chosen url: ' + urls.draw_link()