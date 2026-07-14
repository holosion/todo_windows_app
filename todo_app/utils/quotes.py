"""Curated list of motivational quotes shown on the dashboard."""
from __future__ import annotations

import random
from typing import List, Tuple


_QUOTES: List[Tuple[str, str]] = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Success is the sum of small efforts repeated day in and day out.", "Robert Collier"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
    ("Discipline is the bridge between goals and accomplishment.", "Jim Rohn"),
    ("Well done is better than well said.", "Benjamin Franklin"),
    ("Action is the foundational key to all success.", "Pablo Picasso"),
    ("Focus on being productive instead of busy.", "Tim Ferriss"),
    ("The future depends on what you do today.", "Mahatma Gandhi"),
    ("A goal without a plan is just a wish.", "Antoine de Saint-Exupéry"),
    ("Quality is not an act, it is a habit.", "Aristotle"),
    ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ("Small steps in the right direction can turn out to be the biggest step of your life.",
     "Anonymous"),
    ("Don't count the days, make the days count.", "Muhammad Ali"),
    ("If you can dream it, you can do it.", "Walt Disney"),
    ("Push yourself, because no one else is going to do it for you.", "Anonymous"),
    ("The harder you work for something, the greater you'll feel when you achieve it.",
     "Anonymous"),
    ("Dream big. Start small. Act now.", "Robin Sharma"),
]


class QuoteProvider:
    """Provides a motivational quote. Cycles deterministically by date
    unless the caller explicitly asks for a random one.
    """

    @staticmethod
    def quote_for_today() -> Tuple[str, str]:
        """Return a quote that is stable for the current day."""
        import datetime as _dt
        today = _dt.date.today()
        idx = today.toordinal() % len(_QUOTES)
        return _QUOTES[idx]

    @staticmethod
    def random_quote() -> Tuple[str, str]:
        return random.choice(_QUOTES)

    @staticmethod
    def all_quotes() -> List[Tuple[str, str]]:
        return list(_QUOTES)
