import requests

ENDPOINT = 'https://foo.bar.com/'
BODY = {'foo': 'bar'}

def main():
    requests.post(ENDPOINT, json=BODY, auth=('user','pass'))
