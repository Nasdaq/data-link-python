from nasdaqdatalink.api_config import ApiConfig
from nasdaqdatalink.get import get
from nasdaqdatalink.bulkdownload import bulkdownload
from nasdaqdatalink.export_table import export_table
from nasdaqdatalink.get_table import get_table
from nasdaqdatalink.get_point_in_time import get_point_in_time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import urllib


def get_retries(api_config=ApiConfig):
    retries = None
    if not api_config.use_retries:
        return Retry(total=0)

    Retry.BACKOFF_MAX = api_config.max_wait_between_retries
    retries = Retry(total=api_config.number_of_retries,
                    connect=api_config.number_of_retries,
                    read=api_config.number_of_retries,
                    status_forcelist=api_config.retry_status_codes,
                    backoff_factor=api_config.retry_backoff_factor,
                    raise_on_status=False)
    return retries


class AuthorizedSession:
    def __init__(self, api_config=ApiConfig) -> None:
        super(AuthorizedSession, self).__init__()
        if not isinstance(api_config, ApiConfig):
            api_config = ApiConfig
        self._api_config = api_config
        self._auth_session = requests.Session()
        retries = get_retries(self._api_config)
        adapter = HTTPAdapter(max_retries=retries)
        self._auth_session.mount(api_config.api_protocol, adapter)

        proxies = urllib.request.getproxies()
        if proxies is not None:
            self._auth_session.proxies.update(proxies)

    def get(self, dataset, **kwargs):
        get(dataset, session=self._auth_session, api_config=self._api_config, **kwargs)

    def bulkdownload(self, database, **kwargs):
        bulkdownload(database, session=self._auth_session, api_config=self._api_config, **kwargs)

    def export_table(self, datatable_code, **kwargs):
        export_table(datatable_code, session=self._auth_session,
                     api_config=self._api_config, **kwargs)

    def get_table(self, datatable_code, **options):
        get_table(datatable_code, session=self._auth_session,
                  api_config=self._api_config, **options)

    def get_point_in_time(self, datatable_code, **options):
        get_point_in_time(datatable_code, session=self._auth_session,
                          api_config=self._api_config, **options)
