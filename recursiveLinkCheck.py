from bs4 import BeautifulSoup
import urllib.request
import requests
import datetime
import re
from urllib.parse import urljoin

# This is the start point for the recursion
BASEURL = "http://www.uvm.edu/~cems/"

# This is to help when following local links
URLSTART = "http://www.uvm.edu/"

# This is what would make the link bad (to the wrong place)
CHECK = "sandbox"

# This limits the recursion to links containing this phrase
REPEAT = "~cems"

# This helps optimise by ignoring links with these phrases
EXCEPT = ['magic','.pdf','calendar','#bannermenu','#local','#uvmmaincontent','cems&howmany','.jpg','menu.html', 'Page=Courses']

# This prevents repitition in the recursion 
CHECKEDLINKS = [BASEURL]

# These are for file operations
COUNT = 0
DATE = datetime.datetime.now()
FILENAME = 'Logs/BadLinks_' + str(DATE.month) + '_' + str(DATE.day) + '_' + str(DATE.year) + '.txt'

# This will enable spell checking for all pages
# Currently Not working.
SPELLCHECK = False
if (SPELLCHECK):
    from spellcheck import spellCheck

# This is for the Basecamp API
# Set to false if you are testing
BASECAMP = False
if (BASECAMP):
    from handleAPI import sendToBaseCamp
# Your Basecamp Username and Password
USERNAME = ""
PASSWORD = ""

# This will check ALL links for 404 It will take Significantly more time
CHECK404 = False
if (CHECK404):
    from handleAPI import getResponseCode

# Enables Debug features
DEBUG = True

#Post result to a slack webhook
SLACK = True
SLACKHOOK = "https://hooks.slack.com/services/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"
if (SLACK):
    from handleAPI import sendToSlack

if (DEBUG):
    print(str(DATE.hour) + ':' + str(DATE.minute) + ':' + str(DATE.second))

'''
This function runs the file operations and starts the other functions
'''
def main():
    print('Started')
    badLinks = []
    badLinks.extend(getBadLinks(BASEURL,BASEURL))
    file = open(FILENAME,'w')
    if (DEBUG):
        print('badLinks Length:'+str(len(badLinks)))
    if (len(badLinks) == 0):
        if (DEBUG):
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
        sendToBaseCamp(USERNAME, PASSWORD, FILENAME)
    if (SLACK):
        sendToSlack(SLACKHOOK, FILENAME)
    
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

        COUNT += 1
        
        soup = BeautifulSoup(pageHTML)

        if (SPELLCHECK):
            textSoup = soup.get_text()
            bLinks.append(spellCheck(textSoup, url))

        linkSoup = soup.find_all("a")
        
        for link in linkSoup:
            if link.has_attr('href'):
                link['href'] = urlReconstruct(link['href'])
                if (CHECK in link['href']):
                    if (SLACK):
                        bLinks.append('Bad Link in <'+url+'|link> linking to: <'+link['href'] + '|link>')
                    else:
                        bLinks.append('Bad Link in '+url+'\nlinking to: '+link['href'])
                    if (DEBUG):
                        print('foundbadlink: '+url)
                elif (REPEAT in link['href'] and not any(x in link['href'] for x in EXCEPT)):
                    if (link['href'] not in CHECKEDLINKS):
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
                    if (SLACK):
                        bLinks.append(["404 in page: <" + url + "|link> Linking to: <" + link['href'] + "|link>"])
                    else:
                        bLinks.append(["404 in page: " + url + "\nLinking to: " + link['href']])

        COUNT -= 1

        return bLinks
    
    except Exception as e:
        if ("404" in str(e)):
            if (DEBUG):
                print("404 in page: " + lastUrl + "\nLinking to: " + url)
            if (SLACK):
                return ["404 in page: <" + lastUrl + "|link> Linking to: <" + url + "|link>"]
            return ["404 in page: " + lastUrl + "\nLinking to: " + url]
        elif ("href" in str(e)):
            if (DEBUG):
                print("Error: href")
            pass
        else:
            if (DEBUG):
                print('Error: ' + str(e))
            pass
        return bLinks

def urlReconstruct(url):
    if ('http' in url):
        return str(url)
    elif ('//www' in url):
        return 'http:' + url
    elif ('uvm.edu' in url):
        return str('http://www.' + url)
    else:
        return str(urljoin(str(BASEURL), str(url)))


# Run the program
main()
print("Done")
if (DEBUG):
    finished = datetime.datetime.now()
    print(str(finished.hour) + ':' + str(finished.minute) + ':' + str(finished.second))

if(DEBUG):
    file = open('Logs/Checkedlinks.txt', 'w+')
    c = 0
    d = []
    for i in CHECKEDLINKS:
        file.write(i + "\n")
    file.close()
    print('CheckedLinks length: '+str(c))