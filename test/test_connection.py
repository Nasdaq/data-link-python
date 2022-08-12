from nasdaqdatalink.connection import Connection
from nasdaqdatalink.api_config import ApiConfig
from nasdaqdatalink.errors.data_link_error import (
    DataLinkError, LimitExceededError, InternalServerError,
    AuthenticationError, ForbiddenError, InvalidRequestError,
    NotFoundError, ServiceUnavailableError)
from test.test_retries import ModifyRetrySettingsTestCase
from test.helpers.httpretty_extension import httpretty
import requests
import json
from mock import patch, call
from nasdaqdatalink.version import VERSION
from parameterized import parameterized


class ConnectionTest(ModifyRetrySettingsTestCase):

    def setUp(self):
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()

    @parameterized.expand(['GET', 'POST'])
    def test_nasdaqdatalink_exceptions_no_retries(self, request_method):
        ApiConfig.use_retries = False
        data_link_errors = [('QELx04', 429, LimitExceededError),
                            ('QEMx01', 500, InternalServerError),
                            ('QEAx01', 400, AuthenticationError),
                            ('QEPx02', 403, ForbiddenError),
                            ('QESx03', 422, InvalidRequestError),
                            ('QECx05', 404, NotFoundError),
                            ('QEXx01', 503, ServiceUnavailableError),
                            ('QEZx02', 400, DataLinkError)]

        httpretty.register_uri(getattr(httpretty, request_method),
                               "https://data.nasdaq.com/api/v3/databases",
                               responses=[httpretty.Response(body=json.dumps(
                                   {'quandl_error':
                                    {'code': x[0], 'message': 'something went wrong'}}),
                                   status=x[1]) for x in data_link_errors]
                               )

        for expected_error in data_link_errors:
            self.assertRaises(
                expected_error[2], lambda: Connection.request(request_method, 'databases'))

    @parameterized.expand(['GET', 'POST'])
    def test_parse_error(self, request_method):
        ApiConfig.retry_backoff_factor = 0
        httpretty.register_uri(getattr(httpretty, request_method),
                               "https://data.nasdaq.com/api/v3/databases",
                               body="not json", status=500)
        self.assertRaises(
            DataLinkError, lambda: Connection.request(request_method, 'databases'))

    @parameterized.expand(['GET', 'POST'])
    def test_non_data_link_error(self, request_method):
        ApiConfig.retry_backoff_factor = 0
        httpretty.register_uri(getattr(httpretty, request_method),
                               "https://data.nasdaq.com/api/v3/databases",
                               body=json.dumps(
                                {'foobar':
                                 {'code': 'blah', 'message': 'something went wrong'}}), status=500)
        self.assertRaises(
            DataLinkError, lambda: Connection.request(request_method, 'databases'))

    @parameterized.expand(['GET', 'POST'])
    @patch('nasdaqdatalink.connection.Connection.execute_request')
    def test_build_request(self, request_method, mock):
        ApiConfig.api_key = 'api_token'
        ApiConfig.api_version = '2015-04-09'
        params = {'per_page': 10, 'page': 2}
        headers = {'x-custom-header': 'header value'}
        Connection.request(request_method, 'databases', headers=headers, params=params)
        expected = call(request_method, 'https://data.nasdaq.com/api/v3/databases',
                        headers={'x-custom-header': 'header value',
                                 'x-api-token': 'api_token',
                                 'accept': ('application/json, '
                                            'application/vnd.data.nasdaq+json;version=2015-04-09'),
                                 'request-source': 'python',
                                 'request-source-version': VERSION},
                        params={'per_page': 10, 'page': 2})
        self.assertEqual(mock.call_args, expected)

    @parameterized.expand(['GET', 'POST'])
    @patch('nasdaqdatalink.connection.Connection.execute_request')
    def test_build_request_with_custom_api_config(self, request_method, mock):
        ApiConfig.api_key = 'api_token'
        ApiConfig.api_version = '2015-04-09'
        api_config = ApiConfig()
        api_config.api_key = 'custom_api_token'
        api_config.api_version = '2022-06-09'
        session = requests.session()
        params = {'per_page': 10, 'page': 2, 'api_config': api_config, 'session': session}
        headers = {'x-custom-header': 'header value'}
        Connection.request(request_method, 'databases', headers=headers, params=params)
        expected = call(request_method, 'https://data.nasdaq.com/api/v3/databases',
                        headers={'x-custom-header': 'header value',
                                 'x-api-token': 'custom_api_token',
                                 'accept': ('application/json, '
                                            'application/vnd.data.nasdaq+json;version=2022-06-09'),
                                 'request-source': 'python',
                                 'request-source-version': VERSION},
                        params={'per_page': 10, 'page': 2,
                                'session': session, 'api_config': api_config})
        self.assertEqual(mock.call_args, expected)

    def test_remove_session_and_api_config_param(self):
        ApiConfig.api_key = 'api_token'
        ApiConfig.api_version = '2015-04-09'
        ApiConfig.verify_ssl = True
        api_config = ApiConfig()
        api_config.api_key = 'custom_api_token'
        api_config.api_version = '2022-06-09'
        api_config.verify_ssl = False
        session = requests.Session()
        params = {'per_page': 10, 'page': 2, 'api_config': api_config, 'session': session}
        headers = {'x-custom-header': 'header value'}
        dummy_response = requests.Response()
        dummy_response.status_code = 200
        with patch.object(session, 'request', return_value=dummy_response) as mock:
            Connection.execute_request(
                'GET', 'https://data.nasdaq.com/api/v3/databases', headers=headers, params=params)
            mock.assert_called_once_with(method='GET',
                                         url='https://data.nasdaq.com/api/v3/databases',
                                         verify=False,
                                         headers=headers,
                                         params={'per_page': 10, 'page': 2})
