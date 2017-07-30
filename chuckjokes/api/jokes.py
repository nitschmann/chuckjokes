import urllib

from .request import Request

def random(category=None):
    path = "/jokes/random"

    if category:
        path += "?" + urllib.parse.urlencode({"category": category})

    result = Request(path).execute()
    return result

def categories():
    path = "/jokes/categories"
    result = Request(path).execute()
    return result
