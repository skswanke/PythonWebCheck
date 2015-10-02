from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
from urllib.parse import urljoin
import sys
from queue import Queue
from threading import Thread

# This is the start point for the recursion
BASEURL = "http://www.uvm.edu/~cems/"

# This is what would make the link bad (to the wrong place)
CHECK = "sandbox"

# This limits the iteration to links containing this phrase
REPEAT = "http://www.uvm.edu/~cems/"

# This helps optimise by ignoring links with these phrases
EXCEPT = ['magic','.pdf','calendar','#bannermenu','#local', \
    '#uvmmaincontent','cems&howmany','.jpg', 'Page=Courses', \
    'mailto:', 'tel:', '#', '.zip', '.mp4', '.mov']

# This prevents repitition in the recursion 
CHECKEDLINKS = set()

# These are for file operations
COUNT = 0
DATE = datetime.now()
FILENAME = 'Logs/BadLinks_' + str(DATE.month) + '_' \
    + str(DATE.day) + '_' + str(DATE.year) + '.txt'

# This will enable spell checking for all pages
# Currently Not working.
SPELLCHECK = False
if (SPELLCHECK):
    from spellcheck import SpellCheck
    spell = SpellCheck()
    spellcheck = spell.checktext

# This is for the Basecamp API
# Set to false if you are testing
BASECAMP = False
if (BASECAMP):
    from handleAPI import sendToBaseCamp
    # Your Basecamp Username and Password
    USERNAME = ""
    PASSWORD = ""

# This will check ALL links for 404 It will take Significantly more time
CHECK404 = True

# Enables Debug features
DEBUG = True

#Post result to a slack webhook
SLACK = True
SLACKHOOK = "https://hooks.slack.com/services/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"
if (SLACK):
    from handleAPI import sendToSlack

if (DEBUG):
    print(str(DATE.hour) + ':' + str(DATE.minute) + ':' + str(DATE.second))

# Where spelling errors are kept
SPELLINGERRORS = []

# Where bad link information is kept
BADLINKS = []

# Queue holds all links that will be visited
urlsToVisit = Queue()

#The number of threads to operate in
THREADS = 4

def main():
    # Import global variables for editing
    global BADLINKS
    global SPELLINGERRORS
    global CHECKEDLINKS
    global urlsToVisit
    print('Started')
    ts = datetime.now()
    # Initialize queue
    queue = Queue()
    # Initialize threads
    for x in range(THREADS):
        # Set the worker to do the Download worker method
        worker = DownloadWorker(queue, x)
        # Set the threads to execute until all work is done
        worker.daemon = True
        # Start the workers
        worker.start()

    # Add the base url to the queue
    urlsToVisit.put([BASEURL, BASEURL])

    # Join the queue (ensure that all the work is done)
    urlsToVisit.join()

    # Open our bad links file
    file = open(FILENAME,'w')
    if (DEBUG):
        print('badLinks Length:'+str(len(BADLINKS)))
    
    # If there are no issues print "all clear!"
    if (len(BADLINKS) == 0):
        if (DEBUG):
            print("All Clear!")
        file.write("All Clear!")
    # If there are issues print them into their catagories
    else:
        f404 = []
        spell = []
        file.write("Bad Links:\n\n")
        isBadLink = False
        for i in BADLINKS:
            if ("404" in i):
                f404.append(i)
            elif ("Spelling" in i or i == []):
                spell.append(i)
            else:
                file.write(str(i)+'\n')
                isBadLink = True
        if (not isBadLink):
            file.write("All Clear!\n")
        if (f404):
            file.write("\n404 Errors:\n\n")
            for j in f404:
                file.write(j+'\n')
        if (SPELLCHECK):
            file.write("\nSpelling Errors:\n\n")
        for k in spell:
            if(k != []):
                file.write(k+'\n')
        isSpell = False
        for k in spell:
            if(k != [] or k):
                isSpell = True
        if (not isSpell and SPELLCHECK):
            file.write("All Clear!")
    # Close the file
    file.close()
    # Send to BaseCamp (method located in handleAPI.py)
    if (BASECAMP):
        sendToBaseCamp(USERNAME, PASSWORD, FILENAME)
    # Send to Slack (method located in handleAPI.py)
    if (SLACK):
        sendToSlack(SLACKHOOK, FILENAME)
    # Debug info
    print("Finished {}".format(datetime.now() - ts))
    print(len(CHECKEDLINKS))

# Where the magic happens
class DownloadWorker(Thread):
    # Initialize thread and queue
    def __init__(self, queue, i):
        Thread.__init__(self)
        self.queue = queue
        self.i = i
    
    # Run
    def run(self):
        global urlsToVisit
        global CHECKEDLINKS
        global BADLINKS
        while True:
            try:
                newlinkpair = urlsToVisit.get()
                newlink = newlinkpair[0]
                reflink = newlinkpair[1]
                #process
                if newlink not in CHECKEDLINKS:
                    print("{:2}".format(self.i) + ": " + newlink)
                    page = requests.get(newlink)
                    CHECKEDLINKS.add(newlink)
                    soup = BeautifulSoup(page.text, "html.parser")
                    links = soup.find_all('a')
                    if (SPELLCHECK):
                        checked = spellcheck(soup, newlink, SLACK)
                        if (checked):
                            BADLINKS.append(checked)
                            SPELLINGERRORS.append(checked)
                    for link in links:
                        if link.has_attr('href'):
                            link['href'] = self.urlReconstruct(newlink, link['href'])
                            if (CHECK in link['href']):
                                if (SLACK):
                                    BADLINKS.append('Bad Link in <'+newlink+'|link> linking to: <'+link['href'] + '|link>')
                                else:
                                    BADLINKS.append('Bad Link in '+newlink+'\nlinking to: '+link['href'])
                                if (DEBUG):
                                    print('foundbadlink: '+newlink)
                            elif (REPEAT in link['href'] \
                                and link["href"] not in CHECKEDLINKS \
                                and not any(x in link['href'] for x in EXCEPT)):
                                urlsToVisit.put([link["href"], newlink])
                            elif (CHECK404 \
                                and link['href'] not in CHECKEDLINKS \
                                and not any(x in link['href'] for x in EXCEPT) \
                                and self.getResponseCode(link['href'])):
                                CHECKEDLINKS.add(link['href'])
                                if (SLACK):
                                    BADLINKS.append(["404 in page: <" + newlink + "|link> Linking to: <" + link['href'] + "|link>"])
                                else:
                                    BADLINKS.append(["404 in page: " + newlink + "\nLinking to: " + link['href']])
            except Exception as e:
                if ("404" in str(e)):
                    if (DEBUG):
                        print("404 in page: " + reflink + "\nLinking to: " + newlink)
                    if (SLACK):
                        BADLINKS.append(["404 in page: <" + reflink + "|link> Linking to: <" + newlink + "|link>"])
                    return ["404 in page: " + reflink + "\nLinking to: " + newlink]
                elif ("href" in str(e)):
                    if (DEBUG):
                        print("Error: href")
                    pass
                else:
                    if (DEBUG):
                        print('Error: ' + str(e))
                    pass

            urlsToVisit.task_done()

    # This will reconstruct a relative url
    def urlReconstruct(self, base, url):
        return str(urljoin(str(base.replace("https", "http")), str(url.replace("https", "http"))))

    def getResponseCode(self, url):
        try:
            r = requests.get(url)
            return r.status_code == requests.codes.ok
        except e:
            print(e)
            return False

# This function will print anything (no matter the encoding)
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

# Run the program
main()
print("Done")
# Debug information
if (DEBUG):
    finished = datetime.now()
    print("Checked Links: " + str(len(CHECKEDLINKS)))
    print(str(finished.hour) + ':' + str(finished.minute) + ':' + str(finished.second))
    print("Time elapsed: " + str(finished - DATE))
    file = open('Logs/Checkedlinks.txt', 'w+')
    c = 0
    d = []
    for i in CHECKEDLINKS:
        file.write(i + "\n")
    file.write("\nSpellingErrors:\n")
    if(SPELLCHECK):
        for i in spell.errors:
            file.write(i + ", ")   
        file.close()
    print('CheckedLinks length: '+str(c))