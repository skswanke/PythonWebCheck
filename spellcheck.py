import enchant
'''
This function checks the spelling for every word on the given page
@params
    -Page HTML
    -current URL
@returns
    -List of misspelled words
'''
def spellCheck(words, url):
    badWords = []
    english = enchant.Dict('en_US')
    first = True
    checkWords = re.findall(r"[\w]+", words)
    for word in checkWords:
        #print(word)
        if (len(str(word)) > 2 and not any(char.isdigit() for char in word)):
            try:
                word = str(word)
                print(word)
                if(first and not english.check(word)):
                    badWords.append('\nSpelling Error on: '+url)
                    badWords.append(word)
                elif(not english.check(word)):
                    badWords.append(word)
            except Exception as e:
                print(str(e))
    return badWords

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True


'''
from bs4 import BeautifulSoup
import requests
import datetime
import urllib.request
import sys
import re
import string

def checktext():
    pageFile = urllib.request.urlopen("http://www.uvm.edu/~cems/")
    pageHTML = pageFile.read()
    pageFile.close()
    soup = BeautifulSoup(pageHTML)
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()
    text.encode(sys.stdout.encoding, errors='replace')
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = re.sub(r'\w*\d\w*', '', str(text)).strip()
    uprint(str(text))
    findwords = re.compile(r"\b[A-Za-z][A-Za-z][A-Za-z]+\b")
    words = findwords.findall(text)
    print(words)


def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


checktext()

#checktext()
#def getWordHash():
#start = datetime.datetime.now()
words = open("spell.words").readlines()
words = map(lambda x: x.strip(), words)
hash = {}
for word in words : hash[word] = True
#end = datetime.datetime.now()
#print(end-start)
#return hash

def spellCheckHash(words, hash):
    #secondstart = datetime.datetime.now()
    for i in words : 
        a = i in hash
    #Secondend = datetime.datetime.now()
    #print(Secondend-secondstart)

words = open("spell.words").readlines()
words = map(lambda x: x.strip(), words)
start = datetime.datetime.now()
for i in range(10000):
    spellCheckHash(words, hash)
end = datetime.datetime.now()
print(end-start)

'''