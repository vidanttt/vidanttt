from pathlib import Path
import html

from PIL import Image


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

# Number of ASCII characters across.
# Around 90-110 usually looks good.
COLS = 100

# Character density:
# bright -> sparse, dark -> dense
RAMP = " .`:-=+*cs#%@"

# Appearance
FONT_SIZE = 8
CHAR_WIDTH = 5.0
LINE_HEIGHT = 9.0

TEXT_COLOR = "#b8b8b8"

# Animation
ROW_DELAY = 0.035
ROW_DURATION = 0.45


# ------------------------------------------------------------
# LOAD IMAGE
# ------------------------------------------------------------

if not INPUT.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT}. "
        "Run prep_photo.py first."
    )

image = Image.open(INPUT).convert("L")

width, height = image.size

# Characters are taller than they are wide, so compensate
# for the aspect ratio of terminal characters.
aspect = height / width

rows = max(1, int(COLS * aspect * 0.52))

image = image.resize((COLS, rows))

pixels = image.load()


# ------------------------------------------------------------
# CONVERT IMAGE TO ASCII
# ------------------------------------------------------------

ascii_rows = []

for y in range(rows):
    line = []

    for x in range(COLS):
        brightness = pixels[x, y]

        # Bright = low ramp index
        # Dark = high ramp index
        index = int(
            (255 - brightness)
            / 255
            * (len(RAMP) - 1)
        )

        char = RAMP[index]

        line.append(char)

    ascii_rows.append("".join(line))


# ------------------------------------------------------------
# SVG DIMENSIONS
# ------------------------------------------------------------

svg_width = COLS * CHAR_WIDTH
svg_height = rows * LINE_HEIGHT


# ------------------------------------------------------------
# BUILD SVG
# ------------------------------------------------------------

parts = []

parts.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{svg_width:.0f}"
    height="{svg_height:.0f}"
    viewBox="0 0 {svg_width:.0f} {svg_height:.0f}"
    role="img">

    <title>Animated ASCII portrait</title>

    <style>
        .ascii {{
            font-family:
                "Courier New",
                "Liberation Mono",
                monospace;

            font-size: {FONT_SIZE}px;
            font-weight: 400;
            fill: {TEXT_COLOR};

            white-space: pre;
        }}

        .row {{
            opacity: 0;
            animation:
                reveal {ROW_DURATION}s
                ease-out forwards;
        }}

        @keyframes reveal {{
            from {{
                opacity: 0;
                transform: translateX(-8px);
            }}

            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
    </style>
'''
)


# ------------------------------------------------------------
# DRAW EACH ROW
# ------------------------------------------------------------

for y, line in enumerate(ascii_rows):

    # Don't render completely empty rows
    if not line.strip():
        continue

    escaped = html.escape(line)

    delay = y * ROW_DELAY

    x = 2
    baseline = (y + 1) * LINE_HEIGHT

    parts.append(
        f'''
        <text
            class="ascii row"
            x="{x}"
            y="{baseline:.1f}"
            style="animation-delay:{delay:.3f}s"
        >{escaped}</text>
        '''
    )


# ------------------------------------------------------------
# CLOSE SVG
# ------------------------------------------------------------

parts.append("</svg>")

OUTPUT.write_text(
    "".join(parts),
    encoding="utf-8"
)

print()
print("✅ ASCII SVG created!")
print(f"Input : {INPUT}")
print(f"Output: {OUTPUT}")
print(f"Grid  : {COLS} × {rows}")
print()