"""Rule-based aspect and sentiment keyword matching for parsed reviews."""

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass
class SentenceAnalysis:
    """Matches for one clause; sentence contains the original input tokens."""

    sentence: list[str]
    potential_aspects: list[str]
    semantic_keywords: dict[str, list[str]]


class SemanticAnalyzer:
    """Match whole tokens against configurable aspect and sentiment lexicons.

    Matches identify keywords, not an overall sentiment score. Negation and
    sarcasm are not interpreted: "not great" still matches positive "great".
    The parser's tokens cannot recover the original unprocessed sentence text.
    """

    ASPECTS = {
        "gameplay": [
            "gameplay", "combat", "movement", "parkour", "controls", "control",
            "mechanics", "fighting", "stealth", "difficulty", "balance",
        ],
        "story": [
            "story", "plot", "narrative", "writing", "dialogue", "characters",
            "character", "quests", "quest", "ending", "lore",
        ],
        "graphics": [
            "graphics", "visuals", "textures", "lighting", "animation",
            "animations", "art", "scenery",
        ],
        "audio": [
            "audio", "sound", "sounds", "music", "soundtrack", "voice", "acting",
        ],
        "performance": [
            "performance", "optimization", "fps", "framerate", "stuttering",
            "lag", "bugs", "bug", "crashes", "crash", "loading",
        ],
        "world": [
            "world", "exploration", "map", "environment", "atmosphere", "immersion",
        ],
        "value": ["price", "cost", "value", "content", "replayability", "replay"],
        "multiplayer": [
            "multiplayer", "coop", "cooperative", "pvp", "servers", "matchmaking",
        ],
    }
    POSITIVE_WORDS = [
        "great", "good", "excellent", "amazing", "fantastic", "fun", "enjoyable",
        "smooth", "responsive", "beautiful", "immersive", "engaging", "compelling",
        "polished", "satisfying", "brilliant", "wonderful", "superb", "love", "loved"
    ]

    NEGATIVE_WORDS = [
        "terrible", "bad", "awful", "clunky", "boring", "broken", "buggy",
        "frustrating", "tedious", "repetitive", "unresponsive", "ugly", "poor",
        "disappointing", "annoying", "unplayable", "unfinished", "hate", "hated",
    ]

    # Manually curated from the 100 highest-association candidates in
    # data/potential_semantic_words.csv.
    LEARNT_POSITIVE_WORDS = [
        "interesting", "rewarding", "fluid", "relaxing", "entertaining",
        "exciting", "creative", "cool", "memorable", "fresh", "funny",
        "balanced", "solid", "nice", "intuitive", "enjoy", "fair",
        "hilarious", "innovative", "challenging", "realistic" , "awesome", "incredible"
    ]
    LEARNT_EXTENDED = [
        "bland", "dull", "confusing", "grindy", "flawed"
    ]

    def __init__(
        self,
        aspects: Mapping[str, Iterable[str]] | None = None,
        positive_words: Iterable[str] | None = None,
        negative_words: Iterable[str] | None = None,
    ):
        self.aspects = {
            aspect: {word.lower() for word in words}
            for aspect, words in (self.ASPECTS if aspects is None else aspects).items()
        }
        self.positive_words = {
            word.lower() for word in
            (self.POSITIVE_WORDS if positive_words is None else positive_words)
        }
        self.negative_words = {
            word.lower() for word in
            (self.NEGATIVE_WORDS if negative_words is None else negative_words)
        }

    def analyze(self, review: list[list[str]]) -> list[SentenceAnalysis]:
        """Return clauses with at least one aspect or semantic keyword match.

        Each clause can match multiple aspects. Semantic matches are lowercase,
        unique, and retain their first occurrence order. Input is not modified.
        """
        results = []
        for sentence in review:
            words = list(dict.fromkeys(token.lower() for token in sentence))
            word_set = set(words)
            analysis = SentenceAnalysis(
                sentence=list(sentence),
                potential_aspects=[
                    aspect for aspect, keywords in self.aspects.items()
                    if word_set.intersection(keywords)
                ],
                semantic_keywords={
                    "positive": [word for word in words if word in self.positive_words],
                    "negative": [word for word in words if word in self.negative_words],
                },
            )
            if len(analysis.potential_aspects) > 0 or any(analysis.semantic_keywords.values()):
                results.append(analysis)
        return results
