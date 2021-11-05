import os


class ApiConfig:
    api_key = None
    api_protocol = 'https://'
    api_base = '{}data.nasdaq.com/api/v3'.format(api_protocol)
    api_version = None  # This is not used but keeping for backwards compatibility
    page_limit = 100

    use_retries = True
    number_of_retries = 5
    retry_backoff_factor = 0.5
    max_wait_between_retries = 8
    retry_status_codes = [429] + list(range(500, 512))
    verify_ssl = True


def create_file(config_filename):
    # Create the file as well as the parent dir if needed.
    dirname = os.path.split(config_filename)[0]
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with os.fdopen(os.open(config_filename,
                           os.O_WRONLY | os.O_CREAT, 0o600), 'w'):
        pass


def create_file_if_necessary(config_filename):
    if not os.path.isfile(config_filename):
        create_file(config_filename)


def default_config_filename():
    config_file = os.path.join('~', '.nasdaq', 'data_link_apikey')
    return os.path.expanduser(config_file)


def default_config_file_exists():
    config_filename = default_config_filename()
    return os.path.isfile(config_filename)


def save_key(apikey, filename=None):
    if filename is None:
        filename = default_config_filename()
        create_file_if_necessary(filename)

    fileptr = open(filename, 'w')
    fileptr.write(apikey)
    fileptr.close()
    ApiConfig.api_key = apikey


def raise_empty_file(config_filename):
    raise ValueError("File '{:s}' is empty.".format(config_filename))


def read_key(filename=None):
    if filename is None:
        filename = default_config_filename()

    if not os.path.isfile(filename):
        raise_empty_file(filename)

    with open(filename, 'r') as f:
        apikey = f.read()

    if not apikey:
        raise_empty_file(filename)

    ApiConfig.api_key = apikey
