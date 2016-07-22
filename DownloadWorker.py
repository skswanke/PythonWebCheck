# Each thread will run a Download Worker
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
                    if (config.SPELLCHECK):
                        checked = spellcheck(soup, newlink, config.SLACK)
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
                            if (config.CHECK in link['href']):
                                if (config.SLACK):
                                    BADLINKS.append('Bad Link in <'+newlink+'|link> linking to: <'+link['href'] + '|link>')
                                else:
                                    BADLINKS.append('Bad Link in '+newlink+'\nlinking to: '+link['href'])
                                if (config.DEBUG):
                                    print('foundbadlink: '+newlink)
                            # If the link is a part of the site we are searching add it to the queue
                            elif (config.REPEAT in link['href'] \
                                and link["href"] not in CHECKEDLINKS \
                                and not any(x in link['href'] for x in config.EXCEPT)):
                                urlsToVisit.put([link["href"], newlink])
                            # If we are checking for 404 links then get the response code from every link on the page
                            elif (config.CHECK404 \
                                and link['href'] not in CHECKEDLINKS \
                                and not any(x in link['href'] for x in config.EXCEPT) \
                                and self.getResponseCode(link['href'])):
                                CHECKEDLINKS.add(link['href'])
                                if (config.SLACK):
                                    BADLINKS.append(["404 in page: <" + newlink + "|link> Linking to: <" + link['href'] + "|link>"])
                                else:
                                    BADLINKS.append(["404 in page: " + newlink + "\nLinking to: " + link['href']])
            # General exception catch
            # This needs to get more specific
            except Exception as e:
                # if the exception is due to 404 append it to blinks
                if ("404" in str(e)):
                    if (config.DEBUG):
                        print("404 in page: " + reflink + "\nLinking to: " + newlink)
                    if (config.SLACK):
                        BADLINKS.append(["404 in page: <" + reflink + "|link> Linking to: <" + newlink + "|link>"])
                    return ["404 in page: " + reflink + "\nLinking to: " + newlink]
                # if it is another exception print what it is
                elif ("href" in str(e)):
                    if (config.DEBUG):
                        print("Error: href")
                    pass
                else:
                    if (config.DEBUG):
                        print('Error: ' + str(e))
                    pass
            # report the url as checked in urls to visit
            urlsToVisit.task_done()
