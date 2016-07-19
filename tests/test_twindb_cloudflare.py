#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_twindb_cloudflare
----------------------------------

Tests for `twindb_cloudflare` module.
"""
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

    #mock_requests.get.side_effect = requests.Timeout('Some error')
    #with pytest.raises(CloudFlareException):
    #    cloudflare._api_call('/foo')
