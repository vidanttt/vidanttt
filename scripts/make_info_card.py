from pathlib import Path


OUTPUT = Path("info-card.svg")

WIDTH = 490
HEIGHT = 330

TEXT = {
    "username": "vidanttt@github",
    "name": "Vidant",
    "role": "Creative Developer",
    "stack": "Next.js · TypeScript · Python",
    "focus": "AI · Web · Design",
    "projects": "Friday · VS_Downloader · Forsakened",
}


def esc(value):
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
>

<title>{esc(TEXT["username"])}</title>

<style>

    .panel {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1;
    }}

    .title {{
        fill: #f0f6fc;
        font-family:
            "Courier New",
            monospace;
        font-size: 17px;
        font-weight: bold;
    }}

    .label {{
        fill: #69f0a0;
        font-family:
            "Courier New",
            monospace;
        font-size: 14px;
        font-weight: bold;
    }}

    .value {{
        fill: #b8b8b8;
        font-family:
            "Courier New",
            monospace;
        font-size: 14px;
    }}

    .line {{
        opacity: 0;
        animation:
            appear 0.45s ease-out forwards;
    }}

    @keyframes appear {{
        from {{
            opacity: 0;
            transform: translateX(12px);
        }}

        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

</style>


<!-- PANEL -->

<rect
    class="panel"
    x="0.5"
    y="0.5"
    width="{WIDTH - 1}"
    height="{HEIGHT - 1}"
    rx="8"
/>


<!-- TITLE -->

<text
    class="title"
    x="25"
    y="42"
>
$ whoami
</text>


<!-- SEPARATOR -->

<line
    x1="25"
    y1="58"
    x2="{WIDTH - 25}"
    y2="58"
    stroke="#30363d"
/>


<!-- CONTENT -->

<g class="line" style="animation-delay:0.15s">
    <text class="label" x="25" y="95">NAME</text>
    <text class="value" x="150" y="95">{esc(TEXT["name"])}</text>
</g>


<g class="line" style="animation-delay:0.30s">
    <text class="label" x="25" y="135">ROLE</text>
    <text class="value" x="150" y="135">{esc(TEXT["role"])}</text>
</g>


<g class="line" style="animation-delay:0.45s">
    <text class="label" x="25" y="175">STACK</text>
    <text class="value" x="150" y="175">{esc(TEXT["stack"])}</text>
</g>


<g class="line" style="animation-delay:0.60s">
    <text class="label" x="25" y="215">FOCUS</text>
    <text class="value" x="150" y="215">{esc(TEXT["focus"])}</text>
</g>


<g class="line" style="animation-delay:0.75s">
    <text class="label" x="25" y="255">PROJECTS</text>
    <text class="value" x="150" y="255">{esc(TEXT["projects"])}</text>
</g>


<!-- FOOTER -->

<text
    class="value"
    x="25"
    y="300"
    opacity="0.55"
>
$ exit
</text>

</svg>
"""


OUTPUT.write_text(svg, encoding="utf-8")

print()
print("✅ Info card created!")
print(f"Output: {OUTPUT}")