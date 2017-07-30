import requests

class Request:
    API_BASE_URL = "https://api.chucknorris.io"

    def __init__(self, path):
        if not path.startswith("/"):
            error_msg = "path param has to start with a leading slash"
            raise ValueError(error_msg)

        self.path = path
        self.executed = False
        self.result = None


    def execute(self):
        r = requests.get(self.request_url())
        self.result = r.json()
        self.executed = True

        return self.result


    def request_url(self):
        return self.API_BASE_URL + self.path
