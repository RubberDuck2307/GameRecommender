"""Dependency-free English review preprocessing using simple text rules.

Sentence boundaries are punctuation (. ! ?) or line breaks. This lightweight
splitter may split abbreviations such as "Dr."; it is not a linguistic model.
"""

import re
from typing import Iterable


class ReviewParser:
    """Split reviews into clauses, tokenize them, and remove stop words.

    Negations such as "not", "no", and "never" are intentionally retained
    because they change the meaning of a review.
    """

    CONFLICT_WORDS = frozenset({
        "but", "however", "while", "although", "though", "yet",
        "nevertheless", "nonetheless", "whereas",
    })
    NEGATION_WORDS = frozenset({"not", "no", "never", "neither", "nor", "cannot"})

    STOP_WORDS = frozenset("""
        a an the and or as at by for from in into of on onto to with
        i me my mine we us our ours you your yours he him his she her hers
        it its they them their theirs this that these those
        am is are was were be been being do does did have has had
        having will would shall should can could may might must
        i'm you're he's she's it's we're they're i've you've we've they've
        i'd you'd he'd she'd we'd they'd i'll you'll he'll she'll we'll they'll
        that's there's here's who's what's
    """.split())

    def __init__(
        self,
        conflict_words: Iterable[str] = CONFLICT_WORDS,
        stop_words: Iterable[str] = STOP_WORDS,
    ):
        self.conflict_words = frozenset(word.lower() for word in conflict_words if word)
        self.stop_words = frozenset(word.lower() for word in stop_words)
        alternatives = "|".join(
            re.escape(word) for word in sorted(self.conflict_words, key=len, reverse=True)
        )
        self._conflict_pattern = (
            re.compile(r"\b(?:" + alternatives + r")\b", re.IGNORECASE)
            if alternatives else None
        )

    def split_sentences(self, review: str) -> list[str]:
        """Split review text at sentence punctuation or line breaks."""
        if not isinstance(review, str):
            raise TypeError("review must be a string")
        return [
            sentence.strip()
            for sentence in re.split(r'(?<=[.!?])\s+|[\r\n]+', review)
            if sentence.strip()
        ]

    def is_negated(self, tokens: list[str], index: int, window: int = 3) -> bool:
        """Whether a word has an odd number of nearby preceding negations.

        Recognizes n't contractions and stops at contrast words or "and".
        "Not only" is not treated as negation. This is a local heuristic,
        not a grammatical analysis; pass tokens before removing stop words.
        """
        if not 0 <= index < len(tokens):
            raise IndexError("index must refer to a token")
        if type(window) is not int or window < 1:
            raise ValueError("window must be a positive integer")
        normalized = [token.replace("’", "'").lower() for token in tokens]
        count = 0
        for position in range(index - 1, max(-1, index - window - 1), -1):
            token = normalized[position]
            if token in self.conflict_words or token in {"and", ",", ";", ":", ".", "!", "?"}:
                break
            if token == "not" and normalized[position + 1] == "only":
                continue
            if token in self.NEGATION_WORDS or token.endswith("n't"):
                count += 1
        return count % 2 == 1

    def split_conflicting_parts(self, sentences: list[str]) -> list[str]:
        """Split at whole contrast words, discarding the contrast word itself.

        For example, "Fun, but short." becomes ["Fun", "short"]. Words such
        as "butter" are not split. "While" is split even when used temporally.
        """
        parts = []
        for sentence in sentences:
            fragments = (
                self._conflict_pattern.split(sentence)
                if self._conflict_pattern else [sentence]
            )
            for fragment in fragments:
                fragment = fragment.strip(" \t\r\n,;:.!?\"“”")
                if fragment:
                    parts.append(fragment)
        return parts

    def tokenize(self, sentences: list[str]) -> list[list[str]]:
        """Return lowercase word tokens for each sentence or clause.

        Preserve numbers and contractions (including negations like "isn't").
        Normalize curly apostrophes and discard punctuation.
        """
        return [
            re.findall(r"\b\w+(?:'\w+)*\b", sentence.replace("’", "'").lower())
            for sentence in sentences
        ]

    def remove_stop_words(self, sentences: list[list[str]]) -> list[list[str]]:
        """Remove common English function words, retaining clause grouping."""
        return [
            [token for token in tokens if token.lower() not in self.stop_words]
            for tokens in sentences
        ]

    def process(self, review: str) -> list[list[str]]:
        """Run sentence splitting, contrast splitting, tokens, then stop words.

        Return one token list per clause, omitting clauses with no tokens left.
        Example: "The combat is fun, but the story is not good."
        returns [["combat", "fun"], ["story", "not", "good"]].
        """
        sentences = self.split_sentences(review)
        # parts = self.split_conflicting_parts(sentences)
        tokens = self.tokenize(sentences)
        return [part for part in self.remove_stop_words(tokens) if part]
