import requests
from application.ports import HttpOutboundPort


class HttpOutboundAdapter(HttpOutboundPort):
    def post(self, url: str, json):
        requests.post(url, json=json)