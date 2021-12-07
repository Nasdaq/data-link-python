# flake8: noqa

import os
from unittest import TestCase, mock
from nasdaqdatalink.api_config import *

TEST_KEY_FILE = os.path.join(
  os.path.dirname(os.path.realpath(__file__)), ".nasdaq-config", "testkeyfile"
)

TEST_DEFAULT_FILE = os.path.join(
  os.path.dirname(os.path.realpath(__file__)), ".nasdaq-config", "defaultkeyfile"
)


class ApiConfigTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.dirname(TEST_KEY_FILE)):
            try:
                os.makedirs(os.path.dirname(TEST_KEY_FILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def tearDown(self):
        if NASDAQ_DATA_LINK_API_KEY in os.environ:
            del os.environ['NASDAQ_DATA_LINK_API_KEY']

        if os.path.exists(TEST_KEY_FILE):
            os.remove(TEST_KEY_FILE)

        if os.path.exists(TEST_DEFAULT_FILE):
            os.remove(TEST_DEFAULT_FILE)


    def test_read_key_when_environment_variable_set(self):
        os.environ['NASDAQ_DATA_LINK_API_KEY'] = 'setinenv'
        ApiConfig.api_key = None
        read_key()
        self.assertEqual(ApiConfig.api_key, "setinenv")


    def test_read_key_environment_variable_takes_precedence(self):
        os.environ['NASDAQ_DATA_LINK_API_KEY'] = 'setinenvprecedence'
        save_key("keyforfilenot", TEST_KEY_FILE)
        ApiConfig.api_key = None
        read_key()
        self.assertEqual(ApiConfig.api_key, "setinenvprecedence")


    def test_read_key_when_environment_variable_not_set(self):
        save_key("keyforfile", TEST_KEY_FILE)
        ApiConfig.api_key = None # Set None, we are not testing save_key
        read_key(TEST_KEY_FILE)
        self.assertEqual(ApiConfig.api_key, 'keyforfile')


    def test_read_key_when_files_not_set(self):
        ApiConfig.api_key = None
        with mock.patch("nasdaqdatalink.api_config.default_config_filename") as mock_default_config_filename:
             mock_default_config_filename.return_value = TEST_DEFAULT_FILE
             read_key()

        mock_default_config_filename.assert_called_once
        self.assertEqual(ApiConfig.api_key, None)


    def test_read_key_when_default_file_set(self):
        save_key("keyfordefaultfile", TEST_DEFAULT_FILE)
        ApiConfig.api_key = None # Set None, we are not testing save_key

        with mock.patch("nasdaqdatalink.api_config.default_config_filename") as mock_default_config_filename:
             mock_default_config_filename.return_value = TEST_DEFAULT_FILE
             read_key()

        self.assertEqual(ApiConfig.api_key, 'keyfordefaultfile')
