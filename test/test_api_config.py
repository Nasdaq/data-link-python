# flake8: noqa

import os
from unittest import TestCase, mock
from nasdaqdatalink.api_config import *

TEST_KEY_FILE = os.path.join(
  os.path.dirname(os.path.realpath(__file__)), ".nasdaq-config", "testkeyfile"
)


class ApiConfigTest(TestCase):
    @mock.patch.dict(os.environ, {"NASDAQ_DATA_LINK_API_KEY": "setinenv"})
    def test_read_key_when_environment_variable_set(self):
        ApiConfig.api_key = None
        read_key()
        self.assertEqual(ApiConfig.api_key, "setinenv")
        del os.environ['NASDAQ_DATA_LINK_API_KEY']


    def test_read_key_when_environment_variable_not_set(self):
        if not os.path.exists(os.path.dirname(TEST_KEY_FILE)):
            try:
                os.makedirs(os.path.dirname(TEST_KEY_FILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        ApiConfig.api_key = None
        save_key("keyforfile", TEST_KEY_FILE)
        read_key(TEST_KEY_FILE)
        self.assertEqual(ApiConfig.api_key, 'keyforfile')
        if os.path.exists(TEST_KEY_FILE):
            os.remove(TEST_KEY_FILE)



    def test_read_key_when_file_not_set(self):
        if os.path.exists(TEST_KEY_FILE):
            os.remove(TEST_KEY_FILE)

        ApiConfig.api_key = None
        read_key()
        self.assertEqual(ApiConfig.api_key, None)
