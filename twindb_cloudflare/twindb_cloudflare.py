# -*- coding: utf-8 -*-
import json

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
        """
        See “API Key” on https://www.cloudflare.com/a/account/my-account

        :return: CloudFlare authentication key
        """
        return self._email

    @property
    def auth_key(self):
        """
        See “API Key” on https://www.cloudflare.com/a/account/my-account

        :return: CloudFlare email
        """
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
        r_json = r.json()
        try:
            if r_json['success']:
                return r_json
            else:
                msg = 'CloudFlare API call failed with errors'
                if 'errors' in r_json:
                    msg += ': %r' % r_json['errors']
                raise CloudFlareException(msg)
        except (KeyError, TypeError) as err:
            raise CloudFlareException(err)

    def get_zone_id(self, name):
        """
        Get zone id of a given zone

        :param name: zone name
        :return: id of the zone
        :raise: CloudFlareException if zone is not found or other error
        """
        try:
            response = self._api_call("/zones?name=%s" % name)
            return response["result"][0]["id"]
        except IndexError as err:
            raise CloudFlareException(err)

    def get_record_id(self, domain_name, zone_id):
        """
        Get record id by its name

        :param domain_name: DNS record name "example.com"
        :param zone_id: zone identified (returned by get_zone_id())
        :return: id of the record
        :raise: CloudFlareException if record is not found or other error
        """
        try:
            response = self._api_call("/zones/%s/dns_records?name=%s" %
                                      (zone_id, domain_name))
            return response["result"][0]["id"]
        except IndexError as err:
            raise CloudFlareException(err)

    def update_dns_record(self, name, zone, content, record_type="A", ttl=1):
        """
        Update DNS record

        :param name: domain name
        :param zone: zone identifier
        :param content: content of DNS record. For A records that would be
                        IP address
        :param record_type: DNS record type. "A" by default
        :param ttl: TTL of DNS record. 1 by default
        :raise: CloudFlareException if record is not found or other error
        """
        zone_id = self.get_zone_id(zone)

        record_id = self.get_record_id(name, zone_id)

        url = "/zones/%s/dns_records/%s" % (zone_id, record_id)
        data = {
            "id": record_id,
            "name": name,
            "content": content,
            "type": record_type,
            "ttl": ttl
        }

        self._api_call(url, method="PUT", data=json.dumps(data))

    def create_dns_record(self, name, zone, content,
                          data=None, record_type="A", ttl=1):
        """
        Create a new DNS record for a zone.

        :param name: DNS record name - "example.com"
        :param zone: zone name
        :param content: DNS record content - "127.0.0.1"
        :param data: Optional parameters for DNS record.
                     For example, an SRV record for etcd server needs this::

                         {
                             "name": "twindb.com",
                             "port": 2380,
                             "priority": 0,
                             "proto": "_tcp",
                             "service": "_etcd-server",
                             "target": "node0.twindb.com",
                             "weight": 0
                         }
        :param record_type: DNS record type - "A".
        :param ttl: Time to live for DNS record. Value of 1 is 'automatic'
        :raise: CloudFlareException if error
        """
        zone_id = self.get_zone_id(zone)

        url = "/zones/%s/dns_records" % zone_id
        request = {
            "name": name,
            "content": content,
            "type": record_type,
            "ttl": ttl
        }

        if data:
            request["data"] = data

        self._api_call(url, method="POST", data=json.dumps(request))

    def delete_dns_record(self, name, zone):
        """
        Delete DNS record

        :param name: DNS record name
        :param zone: zone name
        :raise: CloudFlareException if error
        """
        zone_id = self.get_zone_id(zone)
        record_id = self.get_record_id(name, zone_id)

        url = "/zones/%s/dns_records/%s" % (zone_id, record_id)

        self._api_call(url, method="DELETE")
