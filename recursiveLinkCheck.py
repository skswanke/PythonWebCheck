from bs4 import BeautifulSoup
import urllib.request
import requests
import datetime
import enchant
import re

# This is the start point for the recursion
BASEURL = "http://www.uvm.edu/~cems/"

# This is to help when following local links
URLSTART = "http://www.uvm.edu/"

# This is what would make the link bad (to the wrong place)
CHECK = "sandbox"

# This limits the recursion to links containing this phrase
REPEAT = "~cems"

# This helps optimise by ignoring links with these phrases
EXCEPT = ['magic','.pdf','calendar','#bannermenu','#local','#uvmmaincontent','cems&howmany']

# This prevents repitition in the recursion 
CHECKEDLINKS = [BASEURL]

# These are for file operations
COUNT = 0
DATE = datetime.datetime.now()
FILENAME = 'Logs/BadLinks_' + str(DATE.month) + '_' + str(DATE.day) + '_' + str(DATE.year) + '.txt'

# This will enable spell checking for all pages
# Currently Not working.
SPELLCHECK = False

# This is for the Basecamp API
# Set to false if you are testing
BASECAMP = False

# This will check ALL links for 404 It will take Significantly more time
CHECK404 = False

# Enables Debug features
DEBUG = True

# Your Basecamp Username and Password
USERNAME = ""
PASSWORD = ""

if (DEBUG):
    print(str(DATE.hour) + ':' + str(DATE.minute) + ':' + str(DATE.second))

'''
This function runs the file operations and starts the other functions
'''
def main():
    print('Started')
    badLinks = []
    badLinks.extend(getBadLinks(BASEURL,BASEURL))
    file = open(FILENAME,'w+')
    print('badLinks Length:'+str(len(badLinks)))
    if (len(badLinks) == 0):
        print("All Clear!")
        file.write("All Clear!")
    else:
        f404 = []
        spell = []
        file.write("Bad Links:\n\n")
        isBadLink = False
        for i in badLinks:
            if ("404" in i):
                f404.append(i)
            elif ("Spelling" in i or i == []):
                spell.append(i)
            else:
                file.write(str(i)+'\n\n')
                isBadLink = True
            #print(i)
        if (not isBadLink):
            file.write("All Clear!\n")
        file.write("\n404 Errors:\n\n")
        for j in f404:
            file.write(j+'\n\n')
        if (not f404):
            file.write("All Clear!\n\n")
        if (SPELLCHECK):
            file.write("Spelling Errors:\n\n")
        for k in spell:
            if(k != []):
                file.write(k+'\n')
        isSpell = False
        for k in spell:
            if(k != [] or k):
                isSpell = True
                
        if (not isSpell and SPELLCHECK):
            file.write("All Clear!")
    file.close()
    if (BASECAMP):
        sendToBaseCamp()
    
'''
@params:
    Base url
    last url (blank if none)

@returns:
    bLinks: a list of discovered bad links including 
        the links referer

This function recursively crawls an entire sitemap by 
following every link with the same base url on every
page on the site.

It uses 
    -BASEURL as a start point
    -URLSTART for links that are local
    -CHECK to check the links against for an error
    -REPEAT to limit where it recurses
    -EXCEPT to optimize against repetitive/unwanted links
    -CHECKEDLINKS to prevent repetition
'''
def getBadLinks(url, lastUrl):
    try:
        bLinks = []
        
        pageFile = urllib.request.urlopen(url)
        pageHTML = pageFile.read()
        pageFile.close()

        global COUNT
        global CHECKEDLINKS

        #print(url)
        COUNT += 1
        #print(COUNT)
        
        soup = BeautifulSoup(pageHTML)

        if (SPELLCHECK):
            textSoup = soup.get_text()
            bLinks.append(spellCheck(textSoup, url))

        linkSoup = soup.find_all("a")
        
        for link in linkSoup:
            if link.has_attr('href'):
                if (CHECK in link['href']):
                    bLinks.append('Bad Link in '+url+'\nlinking to: '+link['href'])
                    #print('foundbadlink: '+url)
                elif (REPEAT in link['href'] and not any(x in link['href'] for x in EXCEPT)):
                    if ('http' and 'www' in link['href'] and link['href'] not in CHECKEDLINKS):
                        CHECKEDLINKS.append(link['href'])
                        bLinks.extend(getBadLinks(link['href'],url))
                    elif (link['href'] not in CHECKEDLINKS):
                        CHECKEDLINKS.append(link['href'])
                        if('http' not in link['href']):
                            bLinks.extend(getBadLinks('http:' + URLSTART + link['href'], url))
                        else:
                            bLinks.extend(getBadLinks(URLSTART+link['href'],url))
                elif (CHECK404 and link['href'] not in CHECKEDLINKS and 404 == getResponseCode(link['href'])):
                    CHECKEDLINKS.append(link['href'])
                    #print(link['href'])
                    bLinks.append(["404 in page: " + url + "\nLinking to: " + link['href']])

        COUNT -= 1
                                    
        return bLinks
    
    except Exception as e:
        if ("404" in str(e)):
            #print("404 in page: " + lastUrl + "\nLinking to: " + url)
            return ["404 in page: " + lastUrl + "\nLinking to: " + url]
        elif ("href" in str(e)):
            #print("Error: href")
            pass
        else:
            print('Error: ' + str(e))
            pass
        return bLinks

'''
This method check the http response of a given link
@params
    -url to check status of
'''
def getResponseCode(url):
    try:
        conn = urllib.request.urlopen(url)
        #print(str(conn.getcode()))
        return conn.getcode()
    except urllib.error.HTTPError:
        return 404

'''
This function checks the spelling for every word on the given page
@params
    -Page HTML
    -current URL
@returns
    -List of misspelled words
'''
def spellCheck(words, url):
    #print("spell check start")
    #print(words)
    #words = words.decode('utf-8')
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

'''
This function sends the relevant information to Basecamp using their api
'''
def sendToBaseCamp():
    now = datetime.datetime.now()
    headers = {
        'Content-Type': 'application/json',
        'User-Agent' : 'PythonBotPoster (skswanke@gmail.com)'
        }
    subject = 'Bot Findings for ' + str(now.month) + '/' + str(now.day) + '/' + str(now.year)
    subscribers = [859621, 9321794]
    content = ""
    file = open(FILENAME, 'r')
    for line in file:
        content = content + line.rstrip() + '\\n'

    file.close()

    postn = '{"subject": "' + subject + '", "content": "Made by your friendly neighborhood spider-bot!\\n\\n' + content +'", "subscribers": ' + str(subscribers) + '}'

    post = bytes(str(postn), encoding="UTF-8")

    resp = requests.post("https://www.basecamp.com/1800866/api/v1/projects/7236326/messages.json", data=post, auth=(USERNAME, PASSWORD), headers=headers)
    
    file2 = open(FILENAME, 'w')

    file2.write(str(resp))
    file2.write(resp.text)
    file2.close()
    #print(resp.text)
    #print(content)

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

# Run the program
main()
print("Done")
if (DEBUG):
    finished = datetime.datetime.now()
    print(str(finished.hour) + ':' + str(finished.minute) + ':' + str(finished.second))

if(DEBUG):
    file = open('Checkedlinks.txt', 'w+')
    c = 0
    d = []
    for i in CHECKEDLINKS:
        c += 1
        if(c != 1):
            try:
                if ('http' in i):
                    s = i.split('/')[4] + i.split('/')[5]
                elif('www' in i):
                    s = i.split('/')[3] + i.split('/')[4]
                else:
                    s = i.split('/')[1] + i.split('/')[2]
            except: 
                s = str(i)
        else:
            s = 'base'
        if (s not in d):
            d.append(s)
        
    for j in d:
        file.write(j + "\n")
    print('CheckedLinks length: '+str(c))