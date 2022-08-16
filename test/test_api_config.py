# flake8: noqa

import os
from unittest import TestCase, mock
from nasdaqdatalink.api_config import *

TEST_BASE_PATH = os.path.join(
  os.path.dirname(os.path.realpath(__file__)), ".nasdaq-config"
)

TEST_KEY_FILE = os.path.join(
  TEST_BASE_PATH, "testkeyfile"
)

TEST_DEFAULT_FILE = os.path.join(
  TEST_BASE_PATH, "defaultkeyfile"
)

TEST_DEFAULT_FILE_CONTENTS = 'keyfordefaultfile'


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

        os.removedirs(TEST_BASE_PATH)


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


    def test_read_key_empty_file(self):
        with mock.patch("nasdaqdatalink.api_config.default_config_filename") as mock_default_config_filename:
            mock_default_config_filename.return_value = TEST_DEFAULT_FILE
            save_key("")
            with self.assertRaises(ValueError):
                read_key()


    def test_read_key_when_env_key_empty(self):
        os.environ['NASDAQ_DATA_LINK_API_KEY'] = ''
        with self.assertRaises(ValueError):
            read_key()


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


    def _read_key_from_file_helper(self, given, expected):
        save_key(given, TEST_DEFAULT_FILE)
        ApiConfig.api_key = None # Set None, we are not testing save_key

        with mock.patch("nasdaqdatalink.api_config.default_config_filename") as mock_default_config_filename:
            mock_default_config_filename.return_value = TEST_DEFAULT_FILE
            read_key()

        self.assertEqual(ApiConfig.api_key, expected)


    def test_read_key_from_file_with_newline(self):
        given = f"{TEST_DEFAULT_FILE_CONTENTS}\n"
        self._read_key_from_file_helper(given, TEST_DEFAULT_FILE_CONTENTS)


    def test_read_key_from_file_with_leading_newline(self):
        given = f"\n{TEST_DEFAULT_FILE_CONTENTS}\n"
        self._read_key_from_file_helper(given, TEST_DEFAULT_FILE_CONTENTS)


    def test_read_key_from_file_with_space(self):
        given = f" {TEST_DEFAULT_FILE_CONTENTS} "
        self._read_key_from_file_helper(given, TEST_DEFAULT_FILE_CONTENTS)


    def test_read_key_from_file_with_tab(self):
        given = f"\t{TEST_DEFAULT_FILE_CONTENTS}\t"
        self._read_key_from_file_helper(given, TEST_DEFAULT_FILE_CONTENTS)


    def test_read_key_from_file_with_multi_newline(self):
        given = "keyfordefaultfile\n\nanotherkey\n"
        self._read_key_from_file_helper(given, TEST_DEFAULT_FILE_CONTENTS)

    def test_default_instance_will_have_share_values_with_singleton(self):
        os.environ['NASDAQ_DATA_LINK_API_KEY'] = 'setinenv'
        ApiConfig.api_key = None
        read_key()
        api_config = ApiConfig()
        self.assertEqual(api_config.api_key, "setinenv")
        # make sure change in instance will not affect the singleton
        api_config.api_key = None
        self.assertEqual(ApiConfig.api_key, "setinenv")

    def test_get_config_from_kwargs_return_api_config_if_present(self):
        api_config = get_config_from_kwargs({
            'params': {
                'api_config': ApiConfig()
            }
        })
        self.assertTrue(isinstance(api_config, ApiConfig))

    def test_get_config_from_kwargs_return_singleton_if_not_present_or_wrong_type(self):
        api_config = get_config_from_kwargs(None)
        self.assertTrue(issubclass(api_config, ApiConfig))
        self.assertFalse(isinstance(api_config, ApiConfig))
        api_config = get_config_from_kwargs(1)
        self.assertTrue(issubclass(api_config, ApiConfig))
        self.assertFalse(isinstance(api_config, ApiConfig))
        api_config = get_config_from_kwargs({
            'params': None
        })
        self.assertTrue(issubclass(api_config, ApiConfig))
        self.assertFalse(isinstance(api_config, ApiConfig))

    def test_instance_read_key_should_raise_error(self):
        api_config = ApiConfig()
        with self.assertRaises(TypeError):
            api_config.read_key(None)
        with self.assertRaises(ValueError):
            api_config.read_key('')

    def test_instance_read_key_should_raise_error_when_empty(self):
        save_key("", TEST_KEY_FILE)
        api_config = ApiConfig()
        with self.assertRaises(ValueError):
            # read empty file
            api_config.read_key(TEST_KEY_FILE)

    def test_instance_read_the_right_key(self):
        expected_key = 'ilovepython'
        save_key(expected_key, TEST_KEY_FILE)
        api_config = ApiConfig()
        api_config.api_key = ''
        api_config.read_key(TEST_KEY_FILE)
        self.assertEqual(ApiConfig.api_key, expected_key)
        
        
