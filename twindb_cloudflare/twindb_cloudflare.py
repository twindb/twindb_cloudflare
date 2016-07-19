# -*- coding: utf-8 -*-

import requests
from requests.exceptions import RequestException

CF_API_ENDPOINT = "https://api.cloudflare.com/client/v4"


class CloudFlareException(Exception):
    """
    Exception for CloudFlare errors
    """
    pass


class CloudFlare(object):
    """
    Class to work with CloudFlare API
    https://api.cloudflare.com/
    """
    _email = None
    """CloudFlare email"""
    _auth_key = None
    """CloudFlare authentication key
    See "API Key" on https://www.cloudflare.com/a/account/my-account
    """
    _api_endpoint = None
    """The stable HTTPS endpoint for the latest version"""

    def __init__(self, email, auth_key, api_endpoint=CF_API_ENDPOINT):
        """
        CloudFlare class constructor
        :param str email: CloudFlare e-mail
        :param str auth_key: CloudFlare authentication key
        :param str api_endpoint: CloudFlare API endpoint
        """
        self._api_endpoint = api_endpoint
        self._auth_key = auth_key
        self._email = email

    @property
    def email(self):
        return self._email

    @property
    def auth_key(self):
        return self._auth_key

    def _api_call(self, url, method="GET", data=None):
        """
        Do API call
        :param url: API endpoint
        :param method: HTTP method
        :param data: dictionary with CloudFlare parameters
        :return json: Response from API in JSON object
        :raise: CloudFlareException if API response is not 200
            or error in input parameters
        """
        headers = {
            'X-Auth-Email': self._email,
            'X-Auth-Key': self._auth_key,
            'Content-Type': 'application/json'
        }
        if method in ['GET', 'DELETE'] and data:
                raise CloudFlareException("Method %s does not allow data"
                                          % method)

        req_params = {
            'headers': headers
        }
        if data:
            req_params['data'] = data

        real_url = self._api_endpoint + url
        try:
            if method == "GET":
                r = requests.get(real_url, **req_params)
            elif method == "POST":
                r = requests.post(real_url, **req_params)
            elif method == "PUT":
                r = requests.put(real_url, **req_params)
            elif method == "PATCH":
                r = requests.patch(real_url, **req_params)
            elif method == "DELETE":
                r = requests.delete(real_url, **req_params)
            else:
                raise CloudFlareException("Method %s is not supported")

            r.raise_for_status()
        except RequestException as err:
            raise CloudFlareException(err)
        return r.json()
