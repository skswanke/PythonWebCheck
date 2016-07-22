from datetime import datetime
import re
import sys
from queue import Queue
from threading import Thread
import Setup as config
import DownloadWorker as DW
if (config.SPELLCHECK):
    from spellcheck import SpellCheck
if (config.BASECAMP):
    from handleAPI import sendToBaseCamp
if (SLACK):
    from handleAPI import sendToSlack

# These are for file operations
COUNT = 0
DATE = datetime.now()
FILENAME = 'Logs/BadLinks_' + str(DATE.month) + '_' \
    + str(DATE.day) + '_' + str(DATE.year) + '.txt'

if (config.DEBUG):
    print(str(DATE.hour) + ':' + str(DATE.minute) + ':' + str(DATE.second))

# This prevents repitition in the recursion 
CHECKEDLINKS = set()

# Where spelling errors are kept
SPELLINGERRORS = []

# Where bad link information is kept
BADLINKS = []

# Queue holds all links that will be visited
urlsToVisit = Queue()

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
    for x in range(config.THREADS):
        # Set the worker to do the Download worker method
        worker = DW(x)
        # Set the threads to execute until all work is done
        worker.daemon = True
        # Start the workers
        worker.start()

    # Add the base url to the queue
    urlsToVisit.put([config.BASEURL, config.BASEURL])

    # Join the queue 
    # (ensure that all the work is done, and all links have been crawled)
    urlsToVisit.join()

    # Open our bad links file for logging
    file = open(FILENAME,'w')
    if (config.DEBUG):
        print('badLinks Length:'+str(len(BADLINKS)))
    
    # If there are no issues print "all clear!"
    if (len(BADLINKS) == 0):
        if (config.DEBUG):
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
        if (config.SPELLCHECK):
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
    if (config.BASECAMP):
        sendToBaseCamp(config.USERNAME, config.PASSWORD, FILENAME)
    # Send to Slack (method located in handleAPI.py)
    if (config.SLACK):
        sendToSlack(config.SLACKHOOK, FILENAME)
    # Debug info
    print("Finished {}".format(datetime.now() - ts))
    print(len(CHECKEDLINKS))

# Run the program
main()
print("Done")
# Debug information
if (config.DEBUG):
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
    if(config.SPELLCHECK):
        for i in spell.errors:
            file.write(i + ", ")   
        file.close()
    print('CheckedLinks length: '+str(c))
