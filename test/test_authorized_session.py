from unittest import TestCase
from unittest.mock import patch

from nasdaqdatalink.model.authorized_session import AuthorizedSession
from nasdaqdatalink.api_config import ApiConfig
from requests.sessions import Session
from requests.adapters import HTTPAdapter


class AuthorizedSessionTest(TestCase):
    def test_authorized_session_assign_correct_internal_config(self):
        authed_session = AuthorizedSession()
        self.assertTrue(issubclass(authed_session._api_config, ApiConfig))
        authed_session = AuthorizedSession(None)
        self.assertTrue(issubclass(authed_session._api_config, ApiConfig))
        api_config = ApiConfig()
        authed_session = AuthorizedSession(api_config)
        self.assertTrue(isinstance(authed_session._api_config, ApiConfig))

    def test_authorized_session_pass_created_session(self):
        authed_session = AuthorizedSession()
        self.assertTrue(isinstance(authed_session._auth_session, Session))
        adapter = authed_session._auth_session.get_adapter(ApiConfig.api_protocol)
        self.assertTrue(isinstance(adapter, HTTPAdapter))
