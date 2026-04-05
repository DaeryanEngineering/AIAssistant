# core/career_tracker.py

import json
import os
from typing import Optional


CAREER_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "career.json")

YEAR_TO_WARMTH = {
    1: 0,   # F2
    2: 1,   # F1 rookie
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 6,
    8: 7,
    9: 8,
    10: 9,
    11: 10,
}


class CareerTracker:
    """
    Tracks career progression and maps it to Saul's personality warmth.
    Reads/writes career.json.
    """

    def __init__(self):
        self.career_year: int = 1
        self.series: str = "F2"
        self.warmth: int = 0
        self.consecutive_titles: int = 0
        self.total_titles: int = 0
        self.first_f1_title_year: Optional[int] = None

        self._load()

    # ---------------------------------------------------------
    # FILE I/O
    # ---------------------------------------------------------

    def _load(self):
        if not os.path.exists(CAREER_FILE):
            self._save()
            return

        try:
            with open(CAREER_FILE, "r") as f:
                data = json.load(f)

            self.career_year = data.get("career_year", 1)
            self.series = data.get("series", "F2")
            self.warmth = data.get("warmth", 0)
            self.consecutive_titles = data.get("consecutive_titles", 0)
            self.total_titles = data.get("total_titles", 0)
            self.first_f1_title_year = data.get("first_f1_title_year", None)

            # Auto-calculate warmth from career year if not manually set
            if "warmth" not in data:
                self.warmth = YEAR_TO_WARMTH.get(self.career_year, 0)

        except (json.JSONDecodeError, KeyError):
            self._save()

    def _save(self):
        data = {
            "career_year": self.career_year,
            "series": self.series,
            "warmth": self.warmth,
            "consecutive_titles": self.consecutive_titles,
            "total_titles": self.total_titles,
            "first_f1_title_year": self.first_f1_title_year,
        }
        os.makedirs(os.path.dirname(CAREER_FILE), exist_ok=True)
        with open(CAREER_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def set_career_year(self, year: int):
        """Manually set career year (called via text command or config)."""
        self.career_year = max(1, min(11, year))
        self.warmth = YEAR_TO_WARMTH.get(self.career_year, 0)
        self._save()

    def set_series(self, series: str):
        """Manually set series (F2 or F1)."""
        self.series = series.upper()
        self._save()

    def record_f2_championship(self):
        """Called when user reports winning F2 title."""
        self.total_titles += 1
        self.consecutive_titles += 1
        self.warmth = min(10, self.warmth + 1)
        self.series = "F1"
        self._save()

    def record_f1_championship(self):
        """Called when user reports winning F1 title."""
        self.total_titles += 1

        if self.first_f1_title_year is None:
            # First F1 title starts the F1 streak at 1
            self.consecutive_titles = 1
            self.first_f1_title_year = self.career_year
        else:
            self.consecutive_titles += 1

        self.warmth = min(10, self.warmth + 1)
        self._save()

    def reset_consecutive(self):
        """Called when the title streak is broken."""
        self.consecutive_titles = 0
        self._save()

    # ---------------------------------------------------------
    # WARMTH HELPERS
    # ---------------------------------------------------------

    @property
    def warmth_tier(self) -> str:
        """Returns the current warmth tier name."""
        w = self.warmth
        if w <= 2:
            return "sharp"
        elif w <= 5:
            return "professional"
        elif w <= 8:
            return "supportive"
        else:
            return "partnership"

    @property
    def name_frequency(self) -> float:
        """Probability of including driver name in a line."""
        w = self.warmth
        if w <= 3:
            return 0.40
        elif w <= 7:
            return 0.25
        else:
            return 0.15

    @property
    def is_year_5(self) -> bool:
        return self.career_year == 5

    @property
    def is_year_10(self) -> bool:
        return self.career_year == 10
