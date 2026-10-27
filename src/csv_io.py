"""Save Steam review responses and load cached reviews for an application."""

import csv
from bisect import bisect_left
from pathlib import Path
from tempfile import NamedTemporaryFile

from .review import Review

REVIEWS_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "reviews"
CACHE_FIELDS = (
    "appid", "recommendationid", "author_id", "review", "weighted_vote_score", "votes_up",
    "voted_up",
)


def _parse_voted_up(value: str | None) -> bool | None:
    """Keep missing legacy sentiment distinct from a negative review."""
    if value is None or value.strip() == "":
        return None
    normalized = value.strip().lower()
    if normalized in ("true", "1"):
        return True
    if normalized in ("false", "0"):
        return False
    raise ValueError(f"Invalid voted_up value: {value!r}")


def _upgrade_csv_header(cache_file: Path) -> None:
    """Add the sentiment column to older CSVs before appending new rows."""
    with cache_file.open("r", encoding="utf-8", newline="") as cache:
        reader = csv.DictReader(cache)
        fields = reader.fieldnames
        if not fields or "voted_up" in fields:
            return
        rows = list(reader)
    temporary_path = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=cache_file.parent,
            suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            writer = csv.DictWriter(temporary, fieldnames=[*fields, "voted_up"])
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(cache_file)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _find_reviews_file(app_id: int) -> Path | None:
    """Binary-search numerically sorted CSV filenames for a game.

    Directory enumeration and sorting happen before the binary search. Ignore
    unrelated filenames; game files use canonical positive integer app IDs.
    """
    if type(app_id) is not int or not 1 <= app_id <= 2**32 - 1:
        raise ValueError("app_id must be a positive uint32 integer")
    files = sorted(
        (path for path in REVIEWS_DATA_DIR.glob("*.csv")
         if path.is_file() and path.stem.isascii() and path.stem.isdigit()
         and str(int(path.stem)) == path.stem),
        key=lambda path: int(path.stem),
    )
    app_ids = [int(path.stem) for path in files]
    index = bisect_left(app_ids, app_id)
    if index < len(files) and app_ids[index] == app_id:
        return files[index]
    return None


def save_reviews(app_id: int, response: dict) -> None:
    """Append a Steam response to data/reviews/<app_id>.csv, with one header.
    """
    cache_file = _find_reviews_file(app_id)
    reviews = response.get("response", {}).get("reviews", [])
    if not reviews:
        return
    REVIEWS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if cache_file is None:
        cache_file = REVIEWS_DATA_DIR / f"{app_id}.csv"
    elif cache_file.stat().st_size:
        _upgrade_csv_header(cache_file)
    with cache_file.open("a", encoding="utf-8", newline="") as cache:
        writer = csv.DictWriter(cache, fieldnames=CACHE_FIELDS)
        if cache.tell() == 0:
            writer.writeheader()
        for review in reviews:
            writer.writerow({
                "appid": app_id,
                "recommendationid": review.get("recommendationid", ""),
                "author_id": review.get("author", {}).get("steamid", ""),
                "review": review.get("review", ""),
                "weighted_vote_score": review.get("weighted_vote_score", ""),
                "votes_up": review.get("votes_up", ""),
                "voted_up": review.get("voted_up", ""),
            })


def load_reviews(app_id: int) -> list[Review]:
    """Return typed reviews for app_id, converting numeric CSV fields.

    Returns an empty list if the file does not exist or no rows match.
    Raises ValueError if a matching row contains invalid numeric values.
    voted_up is None for older rows where sentiment was not saved.
    """
    cache_file = _find_reviews_file(app_id)
    if cache_file is None:
        return []
    with cache_file.open("r", encoding="utf-8", newline="") as cache:
        return [
            Review(
                appid=int(row["appid"]),
                recommendationid=row["recommendationid"],
                author_id=row["author_id"],
                review=row["review"],
                weighted_vote_score=float(row["weighted_vote_score"]),
                votes_up=int(row["votes_up"]),
                voted_up=_parse_voted_up(row.get("voted_up")),
            )
            for row in csv.DictReader(cache)
            if row["appid"] == str(app_id)
        ]


def has_fetched_reviews(app_id: int) -> bool:
    """Whether the game's CSV contains more than 50 review records.

    Excludes the header and counts multiline review text as one CSV record.
    Stops as soon as the 51st review is found.
    """
    cache_file = _find_reviews_file(app_id)
    if cache_file is None:
        return False
    with cache_file.open("r", encoding="utf-8", newline="") as cache:
        for count, _ in enumerate(csv.DictReader(cache), start=1):
            if count > 50:
                return True
    return False
