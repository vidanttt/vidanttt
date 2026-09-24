from pathlib import Path
import json
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


USERNAME = "vidanttt"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT = Path("data/contributions.json")


print(f"Fetching contributions for @{USERNAME}...")
print(URL)


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


response = requests.get(
    URL,
    headers=headers,
    timeout=30,
)

response.raise_for_status()

print(f"GitHub response: {response.status_code}")


soup = BeautifulSoup(
    response.text,
    "html.parser",
)


days = []


# ------------------------------------------------------------
# FIND CONTRIBUTION CELLS
# ------------------------------------------------------------

cells = soup.select(
    "[data-date][data-level]"
)

print(f"Found {len(cells)} contribution cells.")


for cell in cells:

    date = cell.get("data-date")
    level = cell.get("data-level")

    if not date or level is None:
        continue

    count = 0

    # --------------------------------------------------------
    # Try the cell's own text
    # --------------------------------------------------------

    text = cell.get_text(
        " ",
        strip=True,
    )

    match = re.search(
        r"(\d[\d,]*)\s+contributions?",
        text,
        re.IGNORECASE,
    )

    if match:
        count = int(
            match.group(1).replace(",", "")
        )

    # --------------------------------------------------------
    # Try aria-label
    # --------------------------------------------------------

    if count == 0:

        aria = cell.get(
            "aria-label",
            "",
        )

        match = re.search(
            r"(\d[\d,]*)\s+contributions?",
            aria,
            re.IGNORECASE,
        )

        if match:
            count = int(
                match.group(1).replace(",", "")
            )

    # --------------------------------------------------------
    # Try title
    # --------------------------------------------------------

    if count == 0:

        title = cell.get(
            "title",
            "",
        )

        match = re.search(
            r"(\d[\d,]*)\s+contributions?",
            title,
            re.IGNORECASE,
        )

        if match:
            count = int(
                match.group(1).replace(",", "")
            )

    days.append(
        {
            "date": date,
            "count": count,
            "level": int(level),
        }
    )


# ------------------------------------------------------------
# FALLBACK:
# CURRENT GITHUB MARKUP MAY STORE COUNTS IN TOOLTIP ELEMENTS
# ------------------------------------------------------------

if days:

    # Build a mapping from contribution-day IDs to counts.
    tooltip_counts = {}

    for tooltip in soup.select(
        "tool-tip[for]"
    ):

        target = tooltip.get("for")

        if not target:
            continue

        text = tooltip.get_text(
            " ",
            strip=True,
        )

        match = re.search(
            r"(\d[\d,]*)\s+contributions?",
            text,
            re.IGNORECASE,
        )

        if match:
            tooltip_counts[target] = int(
                match.group(1).replace(",", "")
            )
        elif re.search(
            r"no contributions",
            text,
            re.IGNORECASE,
        ):
            tooltip_counts[target] = 0


    # Match cells with tooltip data.
    for cell in cells:

        cell_id = cell.get("id")

        if not cell_id:
            continue

        if cell_id not in tooltip_counts:
            continue

        date = cell.get("data-date")

        for day in days:

            if day["date"] == date:

                day["count"] = tooltip_counts[
                    cell_id
                ]

                break


# ------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------

if not days:

    raise RuntimeError(
        "No contribution cells were found."
    )


days.sort(
    key=lambda item: item["date"]
)


print(
    f"Parsed {len(days)} days."
)


# ------------------------------------------------------------
# STATISTICS
# ------------------------------------------------------------

total = sum(
    day["count"]
    for day in days
)


best_day = max(
    days,
    key=lambda day: day["count"]
)


# Current streak
current_streak = 0

for day in reversed(days):

    if day["count"] > 0:

        current_streak += 1

    else:

        break


# Longest streak
longest_streak = 0
running = 0

for day in days:

    if day["count"] > 0:

        running += 1

        longest_streak = max(
            longest_streak,
            running,
        )

    else:

        running = 0


# ------------------------------------------------------------
# MONTHLY TOTALS
# ------------------------------------------------------------

monthly = {}

for day in days:

    month = day["date"][:7]

    monthly.setdefault(
        month,
        0,
    )

    monthly[month] += day["count"]


# ------------------------------------------------------------
# SAVE JSON
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)


data = {
    "username": USERNAME,
    "updated_at": datetime.utcnow().isoformat() + "Z",

    "days": days,

    "stats": {
        "total": total,

        "current_streak": current_streak,

        "longest_streak": longest_streak,

        "best_day": {
            "date": best_day["date"],
            "count": best_day["count"],
        },

        "monthly": monthly,
    },
}


OUTPUT.write_text(
    json.dumps(
        data,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("===================================")
print("        CONTRIBUTION DATA")
print("===================================")
print()
print(f"Days parsed       : {len(days)}")
print(f"Total contributions: {total}")
print(f"Current streak    : {current_streak} days")
print(f"Longest streak    : {longest_streak} days")
print(
    f"Best day          : "
    f"{best_day['date']} "
    f"({best_day['count']} contributions)"
)
print()
print(f"Saved to: {OUTPUT}")
print()