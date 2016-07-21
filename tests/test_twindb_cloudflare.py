#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_twindb_cloudflare
----------------------------------

Tests for `twindb_cloudflare` module.
"""
import json
import mock as mock
import pytest
import requests
from twindb_cloudflare.twindb_cloudflare import CloudFlare, \
    CloudFlareException, \
    CF_API_ENDPOINT


@pytest.fixture
def cloudflare():
    return CloudFlare("a@a.com", "foo")


@pytest.fixture
def headers():
    return {
        'X-Auth-Email': 'a@a.com',
        'X-Auth-Key': 'foo',
        'Content-Type': 'application/json'
    }


def test_cf_init_set_attr(cloudflare):
    assert cloudflare.email == "a@a.com"
    assert cloudflare.auth_key == "foo"
    assert cloudflare._api_endpoint == CF_API_ENDPOINT


@mock.patch('twindb_cloudflare.twindb_cloudflare.requests')
def test_api_call_calls_request(mock_requests, cloudflare, headers):
    api_request = '/foo'
    cloudflare._api_call(api_request)

    for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        cloudflare._api_call(api_request, method=method)

    mock_requests.get.assert_called_with(CF_API_ENDPOINT + api_request,
                                         headers=headers)
    assert mock_requests.get.call_count == 2

    mock_requests.post.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                               headers=headers)
    mock_requests.put.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                              headers=headers)
    mock_requests.patch.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                                headers=headers)
    mock_requests.delete.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                                 headers=headers)


def test_api_call_exception_if_get_data(cloudflare):
    data = {
        'some': 'data'
    }
    with pytest.raises(CloudFlareException):
        cloudflare._api_call('some url', method='GET', data=data)


def test_api_call_exception_if_delete_data(cloudflare):
    data = {
        'some': 'data'
    }
    with pytest.raises(CloudFlareException):
        cloudflare._api_call('some url', method='DELETE', data=data)


@mock.patch('twindb_cloudflare.twindb_cloudflare.requests')
def test_api_call_calls_request_with_data(mock_requests, cloudflare, headers):
    data = {
        'some': 'data'
    }
    api_request = '/foo'

    for method in ['POST', 'PUT', 'PATCH']:
        cloudflare._api_call(api_request, method=method, data=data)

    mock_requests.post.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                               headers=headers,
                                               data=data)
    mock_requests.put.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                              headers=headers,
                                              data=data)
    mock_requests.patch.assert_called_once_with(CF_API_ENDPOINT + api_request,
                                                headers=headers,
                                                data=data)


@mock.patch('twindb_cloudflare.twindb_cloudflare.requests')
def test_api_call_raises_exception_connection_error(mock_requests,
                                                    cloudflare):

    for ex in [requests.exceptions.RequestException,
               requests.exceptions.HTTPError,
               requests.exceptions.ConnectionError,
               requests.exceptions.ProxyError,
               requests.exceptions.SSLError,
               requests.exceptions.Timeout,
               requests.exceptions.ConnectTimeout,
               requests.exceptions.ReadTimeout,
               requests.exceptions.URLRequired,
               requests.exceptions.TooManyRedirects,
               requests.exceptions.MissingSchema,
               requests.exceptions.InvalidSchema,
               requests.exceptions.InvalidURL,
               requests.exceptions.ChunkedEncodingError,
               requests.exceptions.ContentDecodingError,
               requests.exceptions.StreamConsumedError,
               requests.exceptions.RetryError]:

        mock_requests.get.side_effect = ex('Some error')
        with pytest.raises(CloudFlareException):
            cloudflare._api_call('/foo')


@mock.patch.object(requests.Response, 'raise_for_status')
def test_exception_on_non200(mock_raise_for_status, cloudflare):
    mock_raise_for_status.side_effect = requests.HTTPError('error')
    with pytest.raises(CloudFlareException):
        cloudflare._api_call('/foo')


@pytest.mark.parametrize('api_response', [
    (
        {u'errors': [],
         u'messages': [],
         u'result': [],
         u'result_info': {u'count': 0,
                          u'page': 1,
                          u'per_page': 20,
                          u'total_count': 0,
                          u'total_pages': 0},
         u'success': False}

    ),
    (
        {u'success': False}
    ),
    (
        {}
    ),
    (
        None
    )
])
@mock.patch('twindb_cloudflare.twindb_cloudflare.requests')
def test_call_api_raises_exception_if_success_false(mock_requests,
                                                    api_response,
                                                    cloudflare):

    class MockResponse(object):
        _api_response = api_response

        def json(self):
            return self._api_response

        def raise_for_status(self):
            pass

    mock_requests.get.return_value = MockResponse()
    with pytest.raises(CloudFlareException):
        cloudflare._api_call('foo')


@pytest.mark.parametrize('api_response,expected_value', [
    (
        {u'errors': [],
         u'messages': [],
         u'result': [{u'created_on': u'2014-10-04T02:15:17.107427Z',
                      u'development_mode': -25346890,
                      u'id': u'02cffc58027ebabbe29614c6bf6e3716',
                      u'meta': {u'custom_certificate_quota': 0,
                                u'multiple_railguns_allowed': False,
                                u'page_rule_quota': 3,
                                u'phishing_detected': False,
                                u'step': 4,
                                u'wildcard_proxiable': False},
                      u'modified_on': u'2016-07-16T22:33:38.193745Z',
                      u'name': u'twindb.com',
                      u'name_servers': [u'becky.ns.cloudflare.com',
                                        u'rick.ns.cloudflare.com'],
                      u'original_dnshost': u'GoDaddy',
                      u'original_name_servers': [u'NS55.DOMAINCONTROL.COM',
                                                 u'NS56.DOMAINCONTROL.COM'],
                      u'original_registrar': u'GoDaddy',
                      u'owner': {u'email': u'aleks@twindb.com',
                                 u'id': u'16e84aea14777e7f16b074409d956b82',
                                 u'type': u'user'},
                      u'paused': False,
                      u'permissions': [u'#analytics:read',
                                       u'#billing:edit',
                                       u'#billing:read',
                                       u'#cache_purge:edit',
                                       u'#dns_records:edit',
                                       u'#dns_records:read',
                                       u'#lb:edit',
                                       u'#lb:read',
                                       u'#logs:read',
                                       u'#organization:edit',
                                       u'#organization:read',
                                       u'#ssl:edit',
                                       u'#ssl:read',
                                       u'#waf:edit',
                                       u'#waf:read',
                                       u'#zone:edit',
                                       u'#zone:read',
                                       u'#zone_settings:edit',
                                       u'#zone_settings:read'],
                      u'plan': {u'can_subscribe': None,
                                u'currency': u'USD',
                                u'externally_managed': False,
                                u'frequency': u'',
                                u'id': u'0feeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
                                u'is_subscribed': None,
                                u'legacy_discount': False,
                                u'legacy_id': u'free',
                                u'name': u'Free Website',
                                u'price': 0},
                      u'status': u'active',
                      u'type': u'full'}],
         u'result_info': {u'count': 1,
                          u'page': 1,
                          u'per_page': 20,
                          u'total_count': 1,
                          u'total_pages': 1},
         u'success': True},
        '02cffc58027ebabbe29614c6bf6e3716'
    )
])
@mock.patch.object(CloudFlare, '_api_call')
def test_get_zone_returns_value(mock_api_call, cloudflare, api_response,
                              expected_value):
    mock_api_call.return_value = api_response
    assert cloudflare.get_zone_id('foo') == expected_value


@mock.patch.object(CloudFlare, '_api_call')
def test_get_zone_exceptio_if_zone_not_found(mock_api_call, cloudflare):
    mock_api_call.return_value = {u'errors': [],
                                  u'messages': [],
                                  u'result': [],
                                  u'result_info': {u'count': 0,
                                                   u'page': 1,
                                                   u'per_page': 20,
                                                   u'total_count': 0,
                                                   u'total_pages': 0},
                                  u'success': True}
    with pytest.raises(CloudFlareException):
        cloudflare.get_zone_id('foo')


@mock.patch.object(CloudFlare, '_api_call')
def test_get_zone_exception_if_api_error(mock_api_call, cloudflare):
    mock_api_call.side_effect = CloudFlareException('error')
    with pytest.raises(CloudFlareException):
        cloudflare.get_zone_id('foo')


@pytest.mark.parametrize('api_response,expected_value', [
    (
        {u'errors': [],
         u'messages': [],
         u'result': [{u'content': u'twindb.com',
                      u'created_on': u'2015-10-23T22:01:45.752426Z',
                      u'id': u'168b11c171959cd45c71437837382437',
                      u'locked': False,
                      u'meta': {u'auto_added': False},
                      u'modified_on': u'2015-10-23T22:01:45.752426Z',
                      u'name': u'www.twindb.com',
                      u'proxiable': True,
                      u'proxied': False,
                      u'ttl': 1,
                      u'type': u'CNAME',
                      u'zone_id': u'02cffc58027ebabbe29614c6bf6e3716',
                      u'zone_name': u'twindb.com'}],
         u'result_info': {u'count': 1,
                          u'page': 1,
                          u'per_page': 20,
                          u'total_count': 1,
                          u'total_pages': 1},
         u'success': True},
        '168b11c171959cd45c71437837382437'
    )
])
@mock.patch.object(CloudFlare, '_api_call')
def test_get_record_id_returns_value(mock_api_call, cloudflare, api_response,
                                     expected_value):
    mock_api_call.return_value = api_response
    assert cloudflare.get_record_id('foo', 'bar') == expected_value


@mock.patch.object(CloudFlare, '_api_call')
def test_get_record_exception_if_zone_not_found(mock_api_call, cloudflare):
    mock_api_call.return_value = {u'errors': [],
                                  u'messages': [],
                                  u'result': [],
                                  u'result_info': {u'count': 0,
                                                   u'page': 1,
                                                   u'per_page': 20,
                                                   u'total_count': 0,
                                                   u'total_pages': 0},
                                  u'success': True}
    with pytest.raises(CloudFlareException):
        cloudflare.get_record_id('foo', 'bar')


@mock.patch.object(CloudFlare, '_api_call')
def test_get_record_exception_if_api_error(mock_api_call, cloudflare):
    mock_api_call.side_effect = CloudFlareException('error')
    with pytest.raises(CloudFlareException):
        cloudflare.get_record_id('foo', 'bar')


@mock.patch.object(CloudFlare, 'get_zone_id')
@mock.patch.object(CloudFlare, 'get_record_id')
@mock.patch.object(CloudFlare, '_api_call')
def test_update_record_updates_record(mock_api_call, mock_get_record_id,
                                      mock_get_zone_id, cloudflare):
    mock_get_record_id.return_value = 'some_record_id'
    mock_get_zone_id.return_value = 'some_zone_id'
    cloudflare.update_dns_record('name', 'zone', 'ip', 'a', 123)
    data = {
        "id": 'some_record_id',
        "name": 'name',
        "content": 'ip',
        "type": 'a',
        "ttl": 123
    }
    mock_api_call.assert_called_once_with("/zones/some_zone_id/"
                                          "dns_records/some_record_id",
                                          method="PUT",
                                          data=json.dumps(data))


@mock.patch.object(CloudFlare, 'get_zone_id')
@mock.patch.object(CloudFlare, '_api_call')
def test_create_record_creates_record(mock_api_call,
                                      mock_get_zone_id,
                                      cloudflare):

    mock_get_zone_id.return_value = 'zone_id'

    cloudflare.create_dns_record('some name',
                                 'some zone',
                                 'some content',
                                 data={'some key': 'some value'},
                                 record_type='some type',
                                 ttl=123)

    request = {
        "name": 'some name',
        "content": 'some content',
        "type": 'some type',
        "ttl": 123,
        "data": {'some key': 'some value'}
    }
    mock_api_call.assert_called_once_with("/zones/zone_id/dns_records",
                                          method="POST",
                                          data=json.dumps(request))


@mock.patch.object(CloudFlare, 'get_zone_id')
@mock.patch.object(CloudFlare, 'get_record_id')
@mock.patch.object(CloudFlare, '_api_call')
def test_delete_record_deletes_record(mock_api_call, mock_get_record_id,
                                      mock_get_zone_id, cloudflare):

    mock_get_record_id.return_value = 'some_record_id'
    mock_get_zone_id.return_value = 'some_zone_id'
    cloudflare.delete_dns_record('name', 'zone')
    mock_api_call.assert_called_once_with("/zones/some_zone_id/"
                                          "dns_records/some_record_id",
                                          method="DELETE")
