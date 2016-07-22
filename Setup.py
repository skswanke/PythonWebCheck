# This is the start point for the recursion
BASEURL = "http://www.uvm.edu/~cems/"

# This is what would make the link bad (to the wrong place)
CHECK = "sandbox"

# This limits the iteration to links containing this phrase
REPEAT = "http://www.uvm.edu/~cems/"

# This helps optimise by ignoring links with these phrases
EXCEPT = [
  'magic',           '.pdf',         'calendar', '#bannermenu',  '#local', \
  '#uvmmaincontent', 'cems&howmany', '.jpg',     'Page=Courses', 'mailto:', \
  'tel:',            '#',            '.zip',     '.mp4',         '.mov']

# This will enable spell checking for all pages
SPELLCHECK = True

# This will check ALL links for 404 It will take Significantly more time
CHECK404 = False

# Enables Debug features
DEBUG = True

#Post result to a slack webhook
SLACK = False
#Link to Slack with slack hook
SLACKHOOK = "https://hooks.slack.com/services/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"

# This is for the Basecamp API
BASECAMP = False
# Your Basecamp Username and Password
USERNAME = ""
PASSWORD = ""


#The number of threads to operate in (rule of thumb: 1 thread for each core)
THREADS = 4
