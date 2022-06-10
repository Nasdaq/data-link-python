from nasdaqdatalink.model.datatable import Datatable
from nasdaqdatalink.errors.data_link_error import LimitExceededError
from .api_config import get_config_from_kwargs
from .message import Message
import warnings
import copy


def get_table(datatable_code, **options):
    if 'paginate' in options.keys():
        paginate = options.pop('paginate')
    else:
        paginate = None

    data = None
    page_count = 0
    api_config = get_config_from_kwargs(options)

    while True:
        next_options = copy.deepcopy(options)
        next_data = Datatable(datatable_code).data(params=next_options)

        if data is None:
            data = next_data
        else:
            data.extend(next_data)

        if page_count >= api_config.page_limit:
            raise LimitExceededError(
                Message.WARN_DATA_LIMIT_EXCEEDED % (datatable_code,
                                                    api_config.api_key
                                                    )
            )

        next_cursor_id = next_data.meta['next_cursor_id']

        if next_cursor_id is None:
            break
        elif paginate is not True and next_cursor_id is not None:
            warnings.warn(Message.WARN_PAGE_LIMIT_EXCEEDED, UserWarning)
            break

        page_count = page_count + 1
        options['qopts.cursor_id'] = next_cursor_id
    return data.to_pandas()
