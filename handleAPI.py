import urllib.request
import requests
import datetime

# This function sends the results to basecamp using their
def sendToBaseCamp(USERNAME, PASSWORD, FILENAME):
    now = datetime.datetime.now()
    # Add headers to request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent' : 'PythonBotPoster (skswanke@gmail.com)'
        }
    # Add subject with date
    subject = 'Bot Findings for ' + str(now.month) + '/' + str(now.day) + '/' + str(now.year)
    # Choose who will be notified by email
    # (you will have to look this up on basecamp)
    subscribers = [859621, 9321794]
    content = ""
    # Open and read the file that was created
    file = open(FILENAME, 'r')
    for line in file:
        content = content + line.rstrip() + '\\n'

    file.close()

    # Make the post
    postn = '{"subject": "' + subject + '", "content": "Made by your friendly neighborhood spider-bot!\\n\\n' + content +'", "subscribers": ' + str(subscribers) + '}'
    # Convert to bytes (for request)
    post = bytes(str(postn), encoding="UTF-8")
    # Sent POST to basecamp
    resp = requests.post("https://www.basecamp.com/1800866/api/v1/projects/7236326/messages.json", data=post, auth=(USERNAME, PASSWORD), headers=headers)
    print(resp.status_code)

# This function sends the results to Slack using a slackhook
def sendToSlack(SLACKHOOK, FILENAME):
    now = datetime.datetime.now()
    # Create the 'subject' line
    text = "Bot findings for " + str(now.month) + '/' + str(now.day) + '/' + str(now.year) + '\n'
    # Read the file into the message
    file = open(FILENAME, 'r')
    for line in file:
        text = text + line.rstrip() + '\n'
    file.close()
    # Compose the message in json
    post = '{"text": "' + text + '"}'
    # Send the POST to the server
    resp = requests.post(SLACKHOOK, data=post)