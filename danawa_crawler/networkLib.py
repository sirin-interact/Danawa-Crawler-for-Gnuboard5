import os
import random
import string
import time
import platform
import traceback
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def retry_req_get(url, header, proxy_server=None):
    res = False

    with requests.Session() as s:
        try:
            retries = 3
            backoff_factor = 0.3
            status_forcelist = (500, 502, 504)

            retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor,
                          status_forcelist=status_forcelist)

            adapter = HTTPAdapter(max_retries=retry)
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            res = s.get(url, headers=header, proxies=proxy_server)
        except:
            traceback.print_exc()

    return res


def retry_req_post(url, header, data, proxy_server=None):
    res = False

    with requests.Session() as s:
        try:
            retries = 5
            backoff_factor = 0.3
            status_forcelist = (500, 502, 504)

            retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor,
                          status_forcelist=status_forcelist)

            adapter = HTTPAdapter(max_retries=retry)
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            res = s.post(url, data, headers=header, proxies=proxy_server)
        except:
            traceback.print_exc()

    return res


def retry_req_json(url, header, data, proxy_server=None):
    res = False

    header['content-type'] = 'application/json'

    with requests.Session() as s:
        try:
            retries = 5
            backoff_factor = 0.3
            status_forcelist = (500, 502, 504)

            retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor,
                          status_forcelist=status_forcelist)

            adapter = HTTPAdapter(max_retries=retry)
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            res = s.post(url, data=json.dumps(data), headers=header, proxies=proxy_server)
        except:
            traceback.print_exc()

    return res
