"""Review data stored in the local CSV cache."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Review:
    appid: int
    recommendationid: str
    author_id: str
    review: str
    weighted_vote_score: float
    votes_up: int
    voted_up: bool | None = None
