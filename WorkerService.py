from urllib.parse import urljoin
import requests

# This will reconstruct a relative url or return an absolute url unchanged
def urlReconstruct(base, url):
    return str(urljoin(str(base.replace("https", "http")), str(url.replace("https", "http"))))

# Creates a new request to get the status (very slow)
def getResponseCode(url):
    try:
        r = requests.get(url)
        return r.status_code == "404"
    except e:
        print(e)
        return False
