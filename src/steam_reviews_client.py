"""
Documentation: https://partner.steamgames.com/doc/webapi/IUserReviewsService
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ENDPOINT = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"


def get_game_reviews(
    appid: int,
    day_range: int = 0,
    filter: int = 0,
    num_per_page: int = 100,
    *,
    cursor: str = "*",
    timeout: float = 30,
) -> dict:
    """Fetch one page and return the complete decoded JSON response.

    filter: 0 = helpful, 1 = recent, 2 = updated, 3 = funny.
    day_range: 0 = unlimited, otherwise 1–365; only used by helpful.
    Pass the returned response's cursor on the next call for pagination.
    Steam applies its defaults to other filters (including English language).

    Raises ValueError for invalid inputs and RuntimeError for request errors.
    """
    for name, value, minimum, maximum in (
        ("appid", appid, 1, 2**32 - 1),
        ("day_range", day_range, 0, 365),
        ("filter", filter, 0, 3),
        ("num_per_page", num_per_page, 1, 100),
    ):
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"{name} must be an integer between {minimum} and {maximum}")
    if timeout <= 0:
        raise ValueError("timeout must be positive")

    parameters = {
        "appid": appid,
        "day_range": day_range,
        "filter": filter,
        "num_per_page": num_per_page,
        "cursor": cursor,
    }
    query = urlencode({"input_json": json.dumps(parameters)})
    request = Request(
        f"{ENDPOINT}?{query}",
        headers={"Accept": "application/json", "User-Agent": "GameRecommender/1.0"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Steam returned HTTP {exc.code}: {exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Could not reach Steam: {exc}") from exc
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("Steam returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Steam returned an unexpected JSON response")
    return result
