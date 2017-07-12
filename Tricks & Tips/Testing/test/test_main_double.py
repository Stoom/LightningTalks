import json

import requests
import requests_mock
from mock import MagicMock
from requests.auth import HTTPBasicAuth

from code.something import main, ENDPOINT

PATCH_PREFIX = 'code.something.'


@requests_mock.mock()
def test_main__calls_correct_endpoint(mock_request):
    mock_request.post(ENDPOINT, status_code=requests.codes.no_content)

    main()

    request = mock_request.last_request
    assert request.method == 'POST'
    assert request.url == ENDPOINT


@requests_mock.mock()
def test_main__includes_post_body_json(mock_request):
    mock_request.post(ENDPOINT, status_code=requests.codes.no_content)

    main()

    request = mock_request.last_request
    assert request.text == json.dumps({'foo': 'bar'})


@requests_mock.mock()
def test_main__includes_basic_auth_header(mock_request):
    basic_auth = HTTPBasicAuth('user', 'pass')
    expected_auth = basic_auth(MagicMock(headers={})).headers['Authorization']

    mock_request.post(ENDPOINT, status_code=requests.codes.no_content)

    main()

    request = mock_request.last_request
    assert request.headers.get('Authorization') == expected_auth
