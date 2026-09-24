from pathlib import Path
import json
from datetime import datetime


DATA_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("contrib-heatmap.svg")


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

CELL_SIZE = 12
GAP = 3

LEFT = 35
TOP = 45

LEGEND_HEIGHT = 45
FOOTER_HEIGHT = 45

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {DATA_FILE}. "
        "Run fetch_contributions.py first."
    )


data = json.loads(
    DATA_FILE.read_text(
        encoding="utf-8"
    )
)


days = data["days"]
stats = data["stats"]
username = data["username"]


# ------------------------------------------------------------
# ORGANIZE DAYS INTO WEEKS
# ------------------------------------------------------------

# GitHub's contribution calendar starts on Sunday.

weeks = []

current_week = []

for day in days:

    date = datetime.strptime(
        day["date"],
        "%Y-%m-%d"
    )

    weekday = date.weekday()

    # Python:
    # Monday = 0
    # Sunday = 6
    #
    # Convert so Sunday = 0

    github_weekday = (
        weekday + 1
    ) % 7


    # If this is the first day and it isn't Sunday,
    # pad the beginning.

    if not weeks and not current_week:

        for _ in range(github_weekday):
            current_week.append(None)


    current_week.append(day)


    # Saturday is the final day of the week.

    if github_weekday == 6:

        weeks.append(
            current_week
        )

        current_week = []


if current_week:

    weeks.append(
        current_week
    )


# ------------------------------------------------------------
# DIMENSIONS
# ------------------------------------------------------------

columns = len(weeks)

grid_width = (
    columns * CELL_SIZE
    + (columns - 1) * GAP
)

grid_height = (
    7 * CELL_SIZE
    + 6 * GAP
)


WIDTH = (
    LEFT * 2
    + grid_width
)

HEIGHT = (
    TOP
    + grid_height
    + LEGEND_HEIGHT
    + FOOTER_HEIGHT
)


# ------------------------------------------------------------
# SVG HEADER
# ------------------------------------------------------------

svg = []

svg.append(
    f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
>

<title>
{username} GitHub contribution graph
</title>

<style>

    .cell {{
        opacity: 0;

        animation:
            appear 0.35s ease-out
            forwards;
    }}

    @keyframes appear {{

        from {{
            opacity: 0;
            transform:
                translateY(-8px);
        }}

        to {{
            opacity: 1;
            transform:
                translateY(0);
        }}

    }}

    .footer {{
        font-family:
            "Courier New",
            monospace;

        fill: #8b949e;

        font-size: 12px;
    }}

    .legend {{
        font-family:
            "Courier New",
            monospace;

        fill: #8b949e;

        font-size: 11px;
    }}

</style>
'''
)


# ------------------------------------------------------------
# DRAW CONTRIBUTION CELLS
# ------------------------------------------------------------

for week_index, week in enumerate(weeks):

    for weekday, day in enumerate(week):

        if day is None:
            continue


        level = int(
            day.get(
                "level",
                0
            )
        )


        level = max(
            0,
            min(
                level,
                len(PALETTE) - 1
            )
        )


        x = (
            LEFT
            + week_index
            * (CELL_SIZE + GAP)
        )

        y = (
            TOP
            + weekday
            * (CELL_SIZE + GAP)
        )


        # Diagonal animation:
        # cells farther right and lower
        # appear later.

        delay = (
            week_index * 0.025
            + weekday * 0.045
        )


        svg.append(
            f'''
<rect
    class="cell"
    x="{x}"
    y="{y}"
    width="{CELL_SIZE}"
    height="{CELL_SIZE}"
    rx="3"
    fill="{PALETTE[level]}"
    style="animation-delay:{delay:.3f}s"
>
    <title>
        {day["date"]}: {day["count"]} contributions
    </title>
</rect>
'''
        )


# ------------------------------------------------------------
# LEGEND
# ------------------------------------------------------------

legend_y = (
    TOP
    + grid_height
    + 22
)


svg.append(
    f'''
<text
    class="legend"
    x="{LEFT}"
    y="{legend_y}"
>
Less
</text>
'''
)


legend_x = LEFT + 35


for i, color in enumerate(PALETTE):

    x = (
        legend_x
        + i * 18
    )

    svg.append(
        f'''
<rect
    x="{x}"
    y="{legend_y - 10}"
    width="12"
    height="12"
    rx="3"
    fill="{color}"
/>
'''
    )


svg.append(
    f'''
<text
    class="legend"
    x="{legend_x + len(PALETTE) * 18 + 4}"
    y="{legend_y}"
>
More
</text>
'''
)


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

footer_y = (
    legend_y
    + 35
)


total = stats["total"]


svg.append(
    f'''
<text
    class="footer"
    x="{LEFT}"
    y="{footer_y}"
>
{total:,} contributions in the last year
</text>
'''
)


svg.append(
    f'''
<text
    class="footer"
    x="{WIDTH - LEFT}"
    y="{footer_y}"
    text-anchor="end"
>
@{username}
</text>
'''
)


# ------------------------------------------------------------
# CLOSE SVG
# ------------------------------------------------------------

svg.append(
    "</svg>"
)


# ------------------------------------------------------------
# WRITE FILE
# ------------------------------------------------------------

OUTPUT_FILE.write_text(
    "".join(svg),
    encoding="utf-8"
)


print()
print("===================================")
print("       HEATMAP CREATED")
print("===================================")
print()
print(f"Username : {username}")
print(f"Days     : {len(days)}")
print(f"Columns  : {columns}")
print(f"Size     : {WIDTH} × {HEIGHT}")
print()
print(f"Output   : {OUTPUT_FILE}")
print()