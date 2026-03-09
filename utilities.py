from urllib.parse import urlparse
from settings import url, headers
import requests

# Global variables/Config
errorCodes = {
    400: ["Bad Request"],
    401: ["Unauthorized"],
    403: ["Forbidden"],
    404: ["Not Found"],
    405: ["Method Not Allowed"],
    429: ["Too Many Requests"],
    500: ["Internal Server Error"],
    502: ["Bad Gateway"],
    503: ["Service Unavailable"],
    504: ["Gateway Timeout"]
}


# functions
def showError(status_code):
    if status_code in errorCodes:
        print(f"Error: {errorCodes[status_code][0]}")
    else: 
        print(f"Error with code: {status_code}")

def cleanUrl(url_to_clean):
    if not url_to_clean.startswith(('http://', 'https://')):
        url_to_clean = 'https://' + url_to_clean
    domain =  urlparse(url_to_clean).netloc
    return domain 

def getFolderName(url):
    return cleanUrl(url)

def getResponse():
    response = requests.get(url, headers=headers)
    return response
