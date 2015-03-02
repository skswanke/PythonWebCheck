from bs4 import BeautifulSoup
import urllib.request

BASEURL = "http://www.uvm.edu/~cems/"
CHECK = "sandbox"
REPEAT = "~cems"
EXCEPT = ['magic','.pdf','calendar']
CHECKEDLINKS = ["http://www.uvm.edu/~cems/"]
COUNT = 0


def main():
    badLinks = []
    badLinks.extend(getBadLinks(BASEURL))

    for i in badLinks:
        print(i)

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
                bLinks.append('Bad Link in '+url+' linking to: '+link['href'])
                print('foundbadlink: '+url)
            elif (REPEAT in link['href'] and b_any(x in link['href'] for x in EXCEPT)):
                if ('www' in link['href'] and link['href'] not in CHECKEDLINKS):
                    CHECKEDLINKS.append(link['href'])
                    bLinks.extend(getBadLinks(link['href']))
                elif (link['href'] not in CHECKEDLINKS):
                    CHECKEDLINKS.append(link['href'])
                    bLinks.extend(getBadLinks('http://www.uvm.edu'+link['href']))

        COUNT -= 1
                                    
        return bLinks
    
    except:
        print('bad link')
        return bLinks

main()
