import requests

try:
    from urllib.parse import urlencode
    from urllib.request import build_opener, Request, HTTPHandler
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import build_opener, Request, HTTPHandler, HTTPError, URLError
import json


def payments_first():
    url = "https://eu-test.oppwa.com/v1/checkouts"
    data = {
        'entityId': '8a8294174e735d0c014e78cf26461790',
        'amount': '190.00',
        'currency': 'ZAR',
        'paymentType': 'DB'
    }
    headers = {
        'Authorization': 'Bearer OGE4Mjk0MTc0ZTczNWQwYzAxNGU3OGNmMjY2YjE3OTR8cXl5ZkhDTjgzZQ=='
    }

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        check_id = data.get("id")
        return check_id, data
    else:
        return None

    # url = "https://eu-test.oppwa.com/v1/checkouts"
    # data = {
    #     'entityId': '8a8294174e735d0c014e78cf26461790',
    #     'amount': '190.00',
    #     'currency': 'ZAR',
    #     'paymentType': 'DB'
    # }
    # try:
    #     opener = build_opener(HTTPHandler)
    #     print(opener)
    #     request = Request(url, data=urlencode(data).encode('utf-8'))
    #     print(request)
    #     request.add_header('Authorization', 'Bearer OGE4Mjk0MTc0ZTczNWQwYzAxNGU3OGNmMjY2YjE3OTR8cXl5ZkhDTjgzZQ==')
    #     request.get_method = lambda: 'POST'
    #     response = opener.open(request)
    #     print(response)
    #
    #     data = response.json()
    #     checkout_id = data.get("id")
    #     return checkout_id
    #     # return json.loads(response.read())
    # except HTTPError as e:
    #     return json.loads(e.read())
    # except URLError as e:
    #     return e.reason


def payments_last(check_id):
    url = f"https://eu-test.oppwa.com/v3/query/{check_id}"
    url += '?entityId=8a8294174b7ecb28014b9699220015ca'
    try:
        opener = build_opener(HTTPHandler)
        request = Request(url, data=b'')
        request.add_header('Authorization', 'Bearer OGE4Mjk0MTc0YjdlY2IyODAxNGI5Njk5MjIwMDE1Y2N8c3k2S0pzVDg=')
        request.get_method = lambda: 'GET'
        response = opener.open(request)
        return json.loads(response.read())
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return e.reason
