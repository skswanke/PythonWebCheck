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
        self.names = {}
        spellwords = open("words_en.txt").readlines()
        spellwords = map(lambda x: x.strip(), spellwords)
        firstnames = open("FirstNames.txt").readlines()
        print(firstnames[1])
        for name in firstnames : 
            name = re.sub(r'\d|\W', '', str(name).lower())
            print(name)
        print(firstnames[7])
        #firstnames = map(lambda x: re.sub(r'\d|\W', '', str(firstnames)).strip(), firstnames)
        for word in spellwords : self.hash[word] = True
        for name in firstnames : self.names[name] = True
        #print(self.names)

    def checktext(self, soup, url, SLACK):
        print("++--Soup--++")
        # kill all script and style elements
        #for script in soup(['style', 'script', '[document]', 'head', 'title']):
        #    script.extract()    # rip it out
        #self.uprint(str(soup))
        soup = re.sub(r'<script.*?>[\s\S]*?<\/script>|<head>[\s\S]*?<\/head>|<style.*?>[\s\S]*?<\/style>|<!--.*?-->|<nav.*?>[\s\S]*?<\/nav>', '', str(soup), 0, re.X)
        #self.uprint(soup)
        print("++---####----POST REGEX---#####---++")
        #[s.extract() for s in soup('script')]
        #[s.extract() for s in soup('style')]
        #[s.extract() for s in soup('head')]
        #[s.extract() for s in soup('title')]
        #[x.extract() for x in soup.findAll('script')]
        soup = BeautifulSoup(soup, "html.parser")
        #self.uprint(soup)
        texts = soup.body.getText() #findAll(text=True)
        print("++--soup.findAll--++")
        #self.uprint(texts)
        #visible_texts = filter(self.visible, texts)
        print("++--visible_texts--++")
        #self.uprint(list(visible_texts))


        # get text
        text = texts
        #print("++--script.extract()--++")
        #self.uprint(soup)
        #print("++--Get_Text()--++")
        #self.uprint(soup.get_text())
        # break into lines and remove leading and trailing space on each
        #lines = (line.strip() for line in text.splitlines())
        #print("++--Lines--++")
        #self.uprint(lines)
        # break multi-headlines into a line each
        #chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        #print("++--Chunks--++")
        #self.uprint(chunks)
        # drop blank lines
        #text = '\n'.join(chunk for chunk in chunks if chunk)
        #print("++--Joined Chunks--++")
        #self.uprint(text)
        text = re.sub(r'\w*\d\w*', '', str(text)).strip()
        text = re.sub(r'\b[A-Z]+\b', '', str(text)).strip()
        print("++--Regex 1--++")
        #self.uprint(text)
        text = re.sub(r'\w+[a-zA-Z0-9.+-][\d\.\/\@\*-][a-zA-Z.@/?=0-9]*\w+', '', str(text)).strip()
        print("++--Regex 2--++")
        #self.uprint(text)
        findwords = re.compile(r"\b[A-Za-z][A-Za-z][A-Za-z]+\b")
        words = findwords.findall(text)
        print("++--Words--++")
        #self.uprint(words)
        badwords = self.spellCheckHash(words)
        print(badwords)
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

    def visible(self, element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element)):
            return False
        return True
    
    def uprint(self, *objects, sep=' ', end='\n', file=sys.stdout):
        enc = file.encoding
        if enc == 'UTF-8':
            print(*objects, sep=sep, end=end, file=file)
        else:
            f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
            print(*map(f, objects), sep=sep, end=end, file=file)