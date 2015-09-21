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

    def checktext(self, soup, url, SLACK):
        print("++--Soup.get_text()--++")
        self.uprint(soup)
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()
        print("++--script.extract()--++")
        self.uprint(soup)
        print("++--Get_Text()--++")
        self.uprint(soup.get_text())
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        print("++--Lines--++")
        self.uprint(lines)
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        print("++--Chunks--++")
        self.uprint(chunks)
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        print("++--Joined Chunks--++")
        self.uprint(text)
        text = re.sub(r'\w*\d\w*', '', str(text)).strip()
        print("++--Regex 1--++")
        self.uprint(text)
        text = re.sub(r'\w+[a-zA-Z0-9.+-][\d\.\/\@\*-][a-zA-Z.@/?=0-9]*\w+', '', str(text)).strip()
        print("++--Regex 2--++")
        self.uprint(text)
        findwords = re.compile(r"\b[A-Za-z][A-Za-z][A-Za-z]+\b")
        words = findwords.findall(text)
        print("++--Words--++")
        self.uprint(words)
        badwords = self.spellCheckHash(words)
        if badwords:
            if SLACK:
                return "Spelling Errors on page: <" + url + "|Link> :: " + str(badwords)
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
    
    def uprint(self, *objects, sep=' ', end='\n', file=sys.stdout):
        enc = file.encoding
        if enc == 'UTF-8':
            print(*objects, sep=sep, end=end, file=file)
        else:
            f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
            print(*map(f, objects), sep=sep, end=end, file=file)