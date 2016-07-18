#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_twindb_cloudflare
----------------------------------

Tests for `twindb_cloudflare` module.
"""
import mock as mock
import pytest
from twindb_cloudflare.twindb_cloudflare import CloudFlare, CloudFlareException


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


@mock.patch('twindb_cloudflare.twindb_cloudflare.requests')
def test_api_call_calls_request(mock_requests, cloudflare, headers):
    cloudflare._api_call('some url')

    for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        cloudflare._api_call('some url', method=method)

    mock_requests.get.assert_called_with('some url', headers=headers)
    assert mock_requests.get.call_count == 2

    mock_requests.post.assert_called_once_with('some url', headers=headers)
    mock_requests.put.assert_called_once_with('some url', headers=headers)
    mock_requests.patch.assert_called_once_with('some url', headers=headers)
    mock_requests.delete.assert_called_once_with('some url', headers=headers)



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

    for method in ['POST', 'PUT', 'PATCH']:
        cloudflare._api_call('some url', method=method, data=data)

    mock_requests.post.assert_called_once_with('some url',
                                               headers=headers,
                                               data=data)
    mock_requests.put.assert_called_once_with('some url', headers=headers,
                                              data=data)
    mock_requests.patch.assert_called_once_with('some url', headers=headers,
                                                data=data)
