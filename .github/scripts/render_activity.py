"""Render a compact, accessible contribution dashboard from GitHub's calendar."""

from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def summarize(days, today):
    """Use 365 calendar days; an unfinished today does not break yesterday's streak."""
    counts = {}
    for day in days:
        day_date = date.fromisoformat(day["date"])
        count = day["contributionCount"]
        if not isinstance(count, int) or count < 0:
            raise ValueError("Invalid contribution count")
        if day_date in counts:
            raise ValueError("Duplicate calendar date")
        counts[day_date] = count
    first = today - timedelta(days=364)
    dates = [first + timedelta(days=i) for i in range(365)]
    window = [counts.get(day, 0) for day in dates]
    longest = running = 0
    for count in window:
        running = running + 1 if count else 0
        longest = max(longest, running)
    end = today if counts.get(today, 0) else today - timedelta(days=1)
    current = 0
    while end >= first and counts.get(end, 0):
        current += 1
        end -= timedelta(days=1)
    recent = window[-84:]
    weekly = [sum(recent[i:i + 7]) for i in range(0, 84, 7)]
    return {
        "total": sum(window), "active_days": sum(count > 0 for count in window),
        "current_streak": current, "longest_streak": longest,
        "weekly": weekly, "recent_total": sum(recent),
        "period_start": today - timedelta(days=83), "period_end": today,
    }


def render(metrics, login, today):
    summary = (
        f"{escape(login)}: {metrics['total']} contributions on {metrics['active_days']} active days "
        f"in 365 days. Current streak: {metrics['current_streak']} days. "
        f"Longest streak in this window: {metrics['longest_streak']} days. "
        f"Last 12 weeks: {metrics['recent_total']} contributions."
    )
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" '
        'viewBox="0 0 960 370" role="img" aria-labelledby="title desc">',
        '<title id="title">Activity &amp; consistency</title>',
        f'<desc id="desc">{summary}</desc>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif}.number{font-weight:600}'
        '.spark{animation:breathe 5s ease-in-out infinite}'
        '@keyframes breathe{0%,100%{opacity:.4}50%{opacity:1}}'
        '@media(prefers-reduced-motion:reduce){.spark{animation:none;opacity:1}}</style>',
        '<rect width="960" height="370" rx="12" fill="#0D1117"/>',
        '<rect x=".5" y=".5" width="959" height="369" rx="12" fill="none" stroke="#262B35"/>',
        '<circle class="spark" cx="30" cy="30" r="4" fill="#DC143C"/>',
        '<text x="44" y="35" fill="#C7CBD1" font-size="14">Contribution rhythm</text>',
        f'<text x="930" y="35" text-anchor="end" fill="#8B8B8B" font-size="12">'
        f'365-day window · {today.isoformat()} UTC</text>',
    ]
    fields = [("Contributions", metrics["total"]), ("Active days", metrics["active_days"]),
              ("Current streak", metrics["current_streak"]), ("Longest streak", metrics["longest_streak"])]
    for index, (caption, value) in enumerate(fields):
        x = 30 + index * 235
        svg.extend([
            f'<text class="number" x="{x}" y="88" fill="#ECEEF2" font-size="32">{value:,}</text>',
            f'<text x="{x}" y="111" fill="#8B8B8B" font-size="13">{caption}</text>',
        ])
        if index:
            svg.append(f'<path d="M{x - 18}62v53" stroke="#262B35"/>')
    svg.extend([
        '<path d="M30 132H930" stroke="#262B35"/>',
        '<text x="30" y="159" fill="#DC143C" font-size="14">LAST 12 WEEKS</text>',
        f'<text x="930" y="159" text-anchor="end" fill="#8B8B8B" font-size="12">'
        f'{metrics["recent_total"]:,} contributions · 7-day buckets</text>',
    ])
    maximum = max(max(metrics["weekly"]), 1)
    for tick in (0, .5, 1):
        y = 295 - tick * 104
        svg.append(f'<path d="M30 {y}H930" stroke="#1E232C"/>')
    for index, count in enumerate(metrics["weekly"]):
        x = 42 + index * 75
        height = 104 * count / maximum
        if count:
            color = "#DC143C" if index == 11 else "#791B32"
            svg.append(f'<rect x="{x}" y="{295 - height:.2f}" width="52" height="{height:.2f}" '
                       f'rx="4" fill="{color}"><title>Week {index + 1}: {count} contributions</title></rect>')
        else:
            svg.append(f'<path d="M{x}295h52" stroke="#343945" stroke-width="2"/>')
        svg.append(f'<text x="{x + 26}" y="{max(182, 285 - height):.2f}" '
                   f'text-anchor="middle" fill="#8B8B8B" font-size="11">{count}</text>')
    svg.extend([
        f'<text x="30" y="320" fill="#8B8B8B" font-size="11">{metrics["period_start"].isoformat()}</text>',
        f'<text x="930" y="320" text-anchor="end" fill="#8B8B8B" font-size="11">{today.isoformat()}</text>',
        '<text x="30" y="349" fill="#8B8B8B" font-size="11">'
        'Publicly visible activity · Streaks count consecutive active days, including yesterday if today is still quiet.</text>',
        '</svg>',
    ])
    return "\n".join(svg) + "\n"


def fetch_days(login, token):
    request = Request("https://api.github.com/graphql",
                      data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                               "User-Agent": "JosePerilla-profile-metrics"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload.get("errors") or not payload.get("data", {}).get("user"):
                raise RuntimeError("GitHub did not return a valid contribution calendar")
            weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            days = [day for week in weeks for day in week["contributionDays"]]
            if not days:
                raise RuntimeError("GitHub returned an empty contribution calendar")
            return days
        except (HTTPError, URLError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main():
    login = os.environ["PROFILE_LOGIN"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", login):
        raise ValueError("Invalid GitHub login")
    today = datetime.now(timezone.utc).date()
    days = fetch_days(login, os.environ["GITHUB_TOKEN"])
    output = Path("dist")
    output.mkdir(exist_ok=True)
    (output / "activity.svg").write_text(render(summarize(days, today), login, today), encoding="utf-8")
    print("Generated activity.svg from GitHub's contribution calendar.")


if __name__ == "__main__":
    main()
