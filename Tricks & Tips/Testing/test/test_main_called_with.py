from mock import patch, ANY

from code.something import main, ENDPOINT

PATCH_PREFIX = 'code.something.'


@patch(PATCH_PREFIX + 'requests')
def test_main__calls_correct_endpoint(mock_request):
    main()

    mock_request.post.assert_called_with(ENDPOINT, json=ANY)


@patch(PATCH_PREFIX + 'requests')
def test_main__includes_post_body_json(mock_request):
    main()

    mock_request.post.assert_called_with(ANY, json={'foo': 'bar'})


@patch(PATCH_PREFIX + 'requests')
def test_main__includes_basic_auth_header(mock_request):
    main()

    mock_request.post.assert_called_with(ANY, json=ANY, auth=('user', 'pass'))
