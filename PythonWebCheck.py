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

# This will enable spell checking for all pages
SPELLCHECK = True

# This will check ALL links for 404 It will take Significantly more time
CHECK404 = False

# Enables Debug features
DEBUG = True

#Post result to a slack webhook
SLACK = False

# This is for the Basecamp API
# Set to false if you are testing
BASECAMP = False

# This prevents repitition in the recursion 
CHECKEDLINKS = set()

# These are for file operations
COUNT = 0
DATE = datetime.now()
FILENAME = 'Logs/BadLinks_' + str(DATE.month) + '_' \
    + str(DATE.day) + '_' + str(DATE.year) + '.txt'

if (SPELLCHECK):
    from spellcheck import SpellCheck
    spell = SpellCheck()
    spellcheck = spell.checktext

if (BASECAMP):
    from handleAPI import sendToBaseCamp
    # Your Basecamp Username and Password
    USERNAME = ""
    PASSWORD = ""


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
    # Badlinks will store all of the problem links
    global BADLINKS
    # Spelling errors will store all misspelled words
    global SPELLINGERRORS
    # Checkedlinks is a set of all crawled links (to prevent recrawling)
    global CHECKEDLINKS
    # urls to visit is a queue of all links found in searched pages that
    #   contain the Repeat variable
    global urlsToVisit
    print('Started')
    # get an initial time (to get runtime)
    ts = datetime.now()
    # Initialize threads
    for x in range(THREADS):
        # Set the worker to do the Download worker method
        worker = DownloadWorker(x)
        # Set the threads to execute until all work is done
        worker.daemon = True
        # Start the workers
        worker.start()

    # Add the base url to the queue
    urlsToVisit.put([BASEURL, BASEURL])

    # Join the queue 
    # (ensure that all the work is done, and all links have been crawled)
    urlsToVisit.join()

    # Open our bad links file for logging
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
        # Add the bad links to the file
        file.write("Bad Links:\n\n")
        isBadLink = False
        for i in BADLINKS:
            # Seperate out 404 errors
            if ("404" in i):
                f404.append(i)
            # Seperate out spelling errors
            elif ("Spelling" in i or i == []):
                spell.append(i)
            # Write the linking errors to the file
            else:
                file.write(str(i)+'\n')
                isBadLink = True
        
        if (not isBadLink):
            file.write("All Clear!\n")
        
        # If there are 404 errors, add them to the file
        if (f404):
            file.write("\n404 Errors:\n\n")
            for j in f404:
                file.write(j+'\n')
        
        # If there are spellcheck errors add that to the page
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
    # Initialize thread and thread id
    def __init__(self, i):
        Thread.__init__(self)
        self.i = i
    
    # This is where the work happens
    def run(self):
        #import global variables
        global urlsToVisit
        global CHECKEDLINKS
        global BADLINKS
        # Running an infinite loop for the worker
        # This will end when the queue is empty because of the deamon
        while True:
            # General Error Catch here
            # TODO make specific error handling
            try:
                # seperate out the new link from the old link
                # this is necessary for describing where the link is
                newlinkpair = urlsToVisit.get()
                newlink = newlinkpair[0]
                reflink = newlinkpair[1]
                # Check to make sure that we haven't processed this link before
                if newlink not in CHECKEDLINKS:
                    # show the thread id and the page
                    print("{:2}".format(self.i) + ": " + newlink)
                    # get page from server
                    page = requests.get(newlink)
                    headers = page.headers
                    if ("text" not in headers["content-type"]):
                    	raise Exception("Not Text")
                    CHECKEDLINKS.add(newlink)
                    # parse the html and extract the links into a list
                    soup = BeautifulSoup(page.text, "html.parser")
                    links = soup.find_all('a')
                    # Send the page to spellcheck and get results
                    if (SPELLCHECK):
                        checked = spellcheck(soup, newlink, SLACK)
                        # if there were spelling errors add them to bad links
                        if (checked):
                            BADLINKS.append(checked)
                            SPELLINGERRORS.append(checked)

                    # Here we look through all of the links we extracted
                    for link in links:
                        # make sure that the links have an href
                        if link.has_attr('href'):
                            # reconstruct the url (for relative urls)
                            link['href'] = self.urlReconstruct(newlink, link['href'])
                            # if the link points to the sandbox add it to the badlinks with the current page
                            if (CHECK in link['href']):
                                if (SLACK):
                                    BADLINKS.append('Bad Link in <'+newlink+'|link> linking to: <'+link['href'] + '|link>')
                                else:
                                    BADLINKS.append('Bad Link in '+newlink+'\nlinking to: '+link['href'])
                                if (DEBUG):
                                    print('foundbadlink: '+newlink)
                            # If the link is a part of the site we are searching add it to the queue
                            elif (REPEAT in link['href'] \
                                and link["href"] not in CHECKEDLINKS \
                                and not any(x in link['href'] for x in EXCEPT)):
                                urlsToVisit.put([link["href"], newlink])
                            # If we are checking for 404 links then get the response code from every link on the page
                            elif (CHECK404 \
                                and link['href'] not in CHECKEDLINKS \
                                and not any(x in link['href'] for x in EXCEPT) \
                                and self.getResponseCode(link['href'])):
                                CHECKEDLINKS.add(link['href'])
                                if (SLACK):
                                    BADLINKS.append(["404 in page: <" + newlink + "|link> Linking to: <" + link['href'] + "|link>"])
                                else:
                                    BADLINKS.append(["404 in page: " + newlink + "\nLinking to: " + link['href']])
            # General exception catch
            # This needs to get more specific
            except Exception as e:
                # if the exception is due to 404 append it to blinks
                if ("404" in str(e)):
                    if (DEBUG):
                        print("404 in page: " + reflink + "\nLinking to: " + newlink)
                    if (SLACK):
                        BADLINKS.append(["404 in page: <" + reflink + "|link> Linking to: <" + newlink + "|link>"])
                    return ["404 in page: " + reflink + "\nLinking to: " + newlink]
                # if it is another exception print what it is
                elif ("href" in str(e)):
                    if (DEBUG):
                        print("Error: href")
                    pass
                else:
                    if (DEBUG):
                        print('Error: ' + str(e))
                    pass
            # report the url as checked in urls to visit
            urlsToVisit.task_done()

    # This will reconstruct a relative url or return an absolute url unchanged
    def urlReconstruct(self, base, url):
        return str(urljoin(str(base.replace("https", "http")), str(url.replace("https", "http"))))

    def getResponseCode(self, url):
        try:
            r = requests.get(url)
            return r.status_code == "404"
        except e:
            print(e)
            return False

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