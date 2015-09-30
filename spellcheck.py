from bs4 import BeautifulSoup
import requests
import datetime
import urllib.request
import sys
import re
import string

'''
This function checks the spelling for every word on the given page
@params
    -Page HTML
    -current URL
@returns
    -List of misspelled words
'''
class SpellCheck():
    def __init__(self):
        self.errors = set()
        self.hash = {}
        self.names = {}
        spellwords = open("words_en.txt").readlines()
        spellwords = spellwords + open("FirstNames.txt").readlines()
        spellwords = spellwords + open("LastNames.txt").readlines()
        spellwords = map(lambda x: x.strip(), spellwords)
        for word in spellwords : self.hash[word] = True

    def checktext(self, soup, url, SLACK):
        soup = re.sub(r'<script.*?>[\s\S]*?<\/script>|<head>[\s\S]*?<\/head>|<style.*?>[\s\S]*?<\/style>|<!--.*?-->|<nav.*?>[\s\S]*?<\/nav>', '', str(soup), 0, re.X)
        soup = BeautifulSoup(soup, "html.parser")
        texts = soup.body.getText()
        text = texts
        text = re.sub(r'\w*\d\w*', '', str(text)).strip()
        text = re.sub(r'\b[A-Z]+\b', '', str(text)).strip()
        text = re.sub(r'\w+[a-zA-Z0-9.+-][\d\.\/\@\*-][a-zA-Z.@/?=0-9]*\w+', '', str(text)).strip()
        text = re.sub(r'\w+[~`!-^@_*.%:;+=/,|#]+\w+([~`!#-^@_*.%:;+=/,|]?\w*)*', '', str(text)).strip()
        findwords = re.compile(r"\b[A-Za-z][A-Za-z][A-Za-z]+\b")
        words = findwords.findall(text)
        badwords = self.spellCheckHash(words)
        if badwords:
            if SLACK:
                return "Spelling Errors on page: <" + url + "|Link> :: " + str(badwords)
            return str(badwords)
            #"Spelling Errors on page: " + url + " :: " + str(badwords)
        else:
            return False

    def spellCheckHash(self, words):
        misspelled = [word for word in words if not word.lower() in self.hash]
        seterrors = set()
        for error in misspelled:
            seterrors.add(error)
        return seterrors