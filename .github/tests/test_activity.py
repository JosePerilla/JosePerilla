import importlib.util
from datetime import date, timedelta
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("activity", Path(__file__).parents[1] / "scripts" / "render_activity.py")
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)


class CalendarTests(unittest.TestCase):
    today = date(2026, 9, 28)

    def days(self, values):
        return [{"date": (self.today - timedelta(days=offset)).isoformat(), "contributionCount": count}
                for offset, count in values.items()]

    def test_quiet_today_preserves_yesterdays_streak(self):
        data = activity.summarize(self.days({0: 0, 1: 2, 2: 3, 3: 0, 4: 4}), self.today)
        self.assertEqual(data["current_streak"], 2)
        self.assertEqual(data["longest_streak"], 2)
        self.assertEqual(data["total"], 9)
        self.assertEqual(data["active_days"], 3)

    def test_gap_breaks_current_streak_but_preserves_longest(self):
        data = activity.summarize(self.days({0: 1, 2: 2, 3: 3, 4: 4}), self.today)
        self.assertEqual(data["current_streak"], 1)
        self.assertEqual(data["longest_streak"], 3)
        self.assertEqual(activity.summarize(self.days({2: 1}), self.today)["current_streak"], 0)

    def test_year_and_chart_boundaries_exclude_old_and_future_days(self):
        data = activity.summarize(self.days({-1: 100, 0: 1, 6: 2, 7: 4, 83: 8, 84: 16, 364: 32, 365: 64}), self.today)
        self.assertEqual(data["total"], 63)
        self.assertEqual(len(data["weekly"]), 12)
        self.assertEqual(data["weekly"][-1], 3)
        self.assertEqual(data["weekly"][-2], 4)
        self.assertEqual(data["weekly"][0], 8)
        self.assertEqual(data["recent_total"], 15)

    def test_leap_day_and_year_boundary_are_consecutive(self):
        for today in (date(2024, 3, 1), date(2026, 1, 1)):
            days = [{"date": (today - timedelta(days=i)).isoformat(), "contributionCount": 1} for i in range(3)]
            self.assertEqual(activity.summarize(days, today)["current_streak"], 3)

    def test_empty_calendar_renders_honest_zero_values(self):
        metrics = activity.summarize([], self.today)
        self.assertEqual(metrics["longest_streak"], 0)
        self.assertEqual(metrics["weekly"], [0] * 12)
        root = ET.fromstring(activity.render(metrics, "test-user", self.today))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("0 contributions", "".join(root.itertext()))

    def test_invalid_or_duplicate_counts_fail(self):
        with self.assertRaises(ValueError):
            activity.summarize(self.days({0: -1}), self.today)
        day = self.days({0: 1})[0]
        with self.assertRaises(ValueError):
            activity.summarize([day, day], self.today)


if __name__ == "__main__":
    unittest.main()
