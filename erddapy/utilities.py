"""
utilities

"""

import functools
import io

from datetime import datetime
from typing import Dict, Optional, Union
from typing.io import BinaryIO

import pytz
import requests


try:
    from pandas.core.indexes.period import parse_time_string
except ImportError:
    from pandas._libs.tslibs.parsing import parse_time_string


def urlopen(url, auth: Optional[tuple] = None, **kwargs: Dict) -> BinaryIO:
    """Thin wrapper around requests get content.

    See requests.get docs for the `params` and `kwargs` options.

    """
    response = requests.get(url, allow_redirects=True, auth=auth, **kwargs)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise requests.exceptions.HTTPError(f"{response.content.decode()}") from err
    return io.BytesIO(response.content)


@functools.lru_cache(maxsize=None)
def check_url_response(url: str, **kwargs: Dict) -> str:
    """
    Shortcut to `raise_for_status` instead of fetching the whole content.
    One should only use this is passing URLs that are known to work is necessary.
    Otherwise let it fail later and avoid fetching the head.

    """
    r = requests.head(url, **kwargs)
    r.raise_for_status()
    return url


def _clean_response(response: str) -> str:
    """Allow for `ext` or `.ext` format.

    The user can, for example, use either `.csv` or `csv` in the response kwarg.

    """
    return response.lstrip(".")


def parse_dates(date_time: Union[datetime, str]) -> float:
    """
    ERDDAP ReSTful API standardizes the representation of dates as either ISO
    strings or seconds since 1970, but internally ERDDAPY uses datetime-like
    objects. `timestamp` returns the expected strings in seconds since 1970.

    """
    if isinstance(date_time, str):
        # pandas returns a tuple with datetime, dateutil, and string representation.
        # we want only the datetime obj.
        parse_date_time = parse_time_string(date_time)[0]
    else:
        parse_date_time = date_time

    if not parse_date_time.tzinfo:
        parse_date_time = pytz.utc.localize(parse_date_time)
    else:
        parse_date_time = parse_date_time.astimezone(pytz.utc)

    return parse_date_time.timestamp()


def quote_string_constraints(kwargs: Dict) -> Dict:
    """
    For constraints of String variables,
    the right-hand-side value must be surrounded by double quotes.

    """
    return {k: f'"{v}"' if isinstance(v, str) else v for k, v in kwargs.items()}


def show_iframe(src):
    """Helper function to show HTML returns."""
    from IPython.display import IFrame

    return IFrame(src=src, width="100%", height=950)
