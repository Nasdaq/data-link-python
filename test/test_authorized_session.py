import unittest
from nasdaqdatalink.model.authorized_session import AuthorizedSession
from nasdaqdatalink.api_config import ApiConfig
from requests.sessions import Session
from requests.adapters import HTTPAdapter
from mock import patch


class AuthorizedSessionTest(unittest.TestCase):
    def test_authorized_session_assign_correct_internal_config(self):
        authed_session = AuthorizedSession()
        self.assertTrue(issubclass(authed_session._api_config, ApiConfig))
        authed_session = AuthorizedSession(None)
        self.assertTrue(issubclass(authed_session._api_config, ApiConfig))
        api_config = ApiConfig()
        authed_session = AuthorizedSession(api_config)
        self.assertTrue(isinstance(authed_session._api_config, ApiConfig))

    def test_authorized_session_pass_created_session(self):
        ApiConfig.use_retries = True
        ApiConfig.number_of_retries = 130
        authed_session = AuthorizedSession()
        self.assertTrue(isinstance(authed_session._auth_session, Session))
        adapter = authed_session._auth_session.get_adapter(ApiConfig.api_protocol)
        self.assertTrue(isinstance(adapter, HTTPAdapter))
        self.assertEqual(adapter.max_retries.connect, 130)

    @patch("nasdaqdatalink.get")
    def test_call_get_with_session_and_api_config(self, mock):
        api_config = ApiConfig()
        authed_session = AuthorizedSession(api_config)
        authed_session.get('WIKI/AAPL')
        mock.assert_called_with('WIKI/AAPL', api_config=api_config,
                                session=authed_session._auth_session)

    @patch("nasdaqdatalink.bulkdownload")
    def test_call_bulkdownload_with_session_and_api_config(self, mock):
        api_config = ApiConfig()
        authed_session = AuthorizedSession(api_config)
        authed_session.bulkdownload('NSE')
        mock.assert_called_with('NSE', api_config=api_config,
                                session=authed_session._auth_session)

    @patch("nasdaqdatalink.export_table")
    def test_call_export_table_with_session_and_api_config(self, mock):
        authed_session = AuthorizedSession()
        authed_session.export_table('WIKI/AAPL')
        mock.assert_called_with('WIKI/AAPL', api_config=ApiConfig,
                                session=authed_session._auth_session)

    @patch("nasdaqdatalink.get_table")
    def test_call_get_table_with_session_and_api_config(self, mock):
        authed_session = AuthorizedSession()
        authed_session.get_table('WIKI/AAPL')
        mock.assert_called_with('WIKI/AAPL', api_config=ApiConfig,
                                session=authed_session._auth_session)

    @patch("nasdaqdatalink.get_point_in_time")
    def test_call_get_point_in_time_with_session_and_api_config(self, mock):
        authed_session = AuthorizedSession()
        authed_session.get_point_in_time('DATABASE/CODE', interval='asofdate', date='2020-01-01')
        mock.assert_called_with('DATABASE/CODE', interval='asofdate',
                                date='2020-01-01', api_config=ApiConfig,
                                session=authed_session._auth_session)
