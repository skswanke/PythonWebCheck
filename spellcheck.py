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
        #SpellCheck.__init__(self)
        #print("SpellCheck Init")
        self.errors = set()
        self.hash = {}
        spellwords = open("words_en.txt").readlines()
        spellwords = map(lambda x: x.strip(), spellwords)
        for word in spellwords : self.hash[word] = True

    def checktext(self, soup, url):
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()
        #text = text.encode(sys.stdout.encoding, errors='replace')
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = re.sub(r'\w*\d\w*', '', str(text)).strip()
        text = re.sub(r'\w*([a-zA-Z])[\d.]([a-zA-Z]).*\w*', '', str(text)).strip()
        findwords = re.compile(r"\b[A-Za-z][A-Za-z][A-Za-z]+\b")
        words = findwords.findall(text)
        #print(words)
        badwords = self.spellCheckHash(words)
        if badwords:
            return "Spelling Errors on page: " + url + " :: " + str(badwords)
        else:
            return False

    def spellCheckHash(self, words):
        misspelled = [word for word in words if not word.lower() in self.hash]
        seterrors = set()
        for error in misspelled:
            seterrors.add(error)
        # for i in words :
        #     if (not i.lower() in self.hash):
        #         misspelled.extend(i)
        #         print(i)
        #print(misspelled)
        return seterrors