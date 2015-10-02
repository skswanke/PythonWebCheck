import urllib.request
import requests
import datetime

'''
This function sends the relevant information to Basecamp using their api
'''
def sendToBaseCamp(USERNAME, PASSWORD, FILENAME):
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

def sendToSlack(SLACKHOOK, FILENAME):
    now = datetime.datetime.now()
    text = "Bot findings for " + str(now.month) + '/' + str(now.day) + '/' + str(now.year) + '\n'
    file = open(FILENAME, 'r')
    for line in file:
        text = text + line.rstrip() + '\n'
    file.close()

    post = '{"text": "' + text + '"}'

    resp = requests.post(SLACKHOOK, data=post)