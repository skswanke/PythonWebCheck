from bs4 import BeautifulSoup
import urllib.request

BASEURL = "http://www.uvm.edu/~cems/"
CHECK = "sandbox"
REPEAT = "~cems"
EXCEPT = ['magic','.pdf','calendar','#bannermenu','#local','#uvmmaincontent','cems&howmany']
CHECKEDLINKS = [BASEURL]
COUNT = 0
FILENAME = 'BadLinks.txt'


def main():
    badLinks = []
    badLinks.extend(getBadLinks(BASEURL))
    file = open(FILENAME,'w')
    
    for i in badLinks:
        file.write(i+'\n')
        print(i)
    file.close()

def getBadLinks(url):
    try:
        pageFile = urllib.request.urlopen(url)
        pageHTML = pageFile.read()
        pageFile.close()
        bLinks = []
        global COUNT
        global CHECKEDLINKS

        print(url)
        COUNT += 1
        print(COUNT)
        
        soup = BeautifulSoup(pageHTML)

        linkSoup = soup.find_all("a")
        
        for link in linkSoup:
            if (CHECK in link['href']):
                rurl = url.split('edu/',1)[1]
                bLinks.append('Bad Link in '+rurl+' linking to: '+link['href'])
                print('foundbadlink: '+url)
            elif (REPEAT in link['href'] and not any(x in link['href'] for x in EXCEPT)):
                if ('www' in link['href'] and link['href'] not in CHECKEDLINKS):
                    CHECKEDLINKS.append(link['href'])
                    bLinks.extend(getBadLinks(link['href']))
                elif (link['href'] not in CHECKEDLINKS):
                    CHECKEDLINKS.append(link['href'])
                    bLinks.extend(getBadLinks('http://www.uvm.edu'+link['href']))

        COUNT -= 1
                                    
        return bLinks
    
    except Exception as e:
        print("Error: " + str(e))
        return bLinks

main()
