#!/usr/bin/env python3
"""Build terminal.svg: the ASCII art and the profile text in one CRT window.

Edit LINES below, then run:  python3 scripts/build-terminal.py [--theme green|amber|github] [--out PATH]
ascii-art.svg stays the source for the art and is not modified.
"""

import argparse
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

THEMES = {
    "green": {"fg": "#33ff66", "dim": "#1c9c3e", "bright": "#c6ffd4", "accent": "#e8ff7a", "bg": "#04140a", "edge": "#000402"},
    "amber": {"fg": "#ffb000", "dim": "#a86c00", "bright": "#ffe3a6", "accent": "#fff1c9", "bg": "#160d00", "edge": "#030200"},
    "github": {"fg": "#c9d1d9", "dim": "#6e7681", "bright": "#f0f6fc", "accent": "#7ee787", "bg": "#0d1117", "edge": "#0d1117"},
}


def cmd(text: str, comment: str = "") -> list[tuple[str, str]]:
    line = [("accent", "$ "), ("bright", text)]
    return line + [("dim", comment)] if comment else line


def entry(year: str, name: str, desc: str, tag: str = "") -> list[tuple[str, str]]:
    if not tag:
        return [("dim", f"{year}  "), ("bright", f"{name:<20}"), ("fg", desc)]
    return [("dim", f"{year}  "), ("bright", f"{name:<20}"), ("fg", f"{desc:<40}"), ("accent", tag)]


# Each line is a list of (style, text). Styles: fg, dim, bright, accent, cursor.
# Copy comes from content/site.ts and the case-study summaries on christenjacquottet.com.
LINES = [
    cmd("whoami"),
    [("bright", "christen jacquottet"), ("fg", " · creative technologist · LERMA/, dallas")],
    [("fg", "from imagination to implementation.")],
    [],
    cmd("cat README"),
    [("fg", "i turn wild ideas into real things.")],
    [("fg", "part design, part engineering, constantly asking “what if?”")],
    [],
    cmd("ls -t ~/shipped", "                           # stories on the site"),
    entry("2026", "world-cup-host/", "ai host calling matches in english + spanish"),
    entry("2025", "super-bowl-ai/", "classified 113,000+ answers, replied to each"),
    entry("2025", "gateway-to-dallas/", "web ar at reunion tower", "[2026 eTSY award]"),
    entry("2025", "william-booth/", "a talking salvation army founder, by phone"),
    entry("2024", "ragformation/", "text to cloud architecture", "[box award]"),
    entry("2023", "ai-bartender/", "the demo that won the hornitos pitch"),
    [],
    cmd("ls ~/open", "                                 # take these"),
    entry("    ", "crashers/", "invite an ai to your meeting", "[wip]"),
    entry("    ", "rag-crawler/", "crawl any site into llm-ready markdown", "[soon]"),
    [],
    cmd("open christenjacquottet.com"),
    [("accent", "$ "), ("cursor", "")],
]

TITLE = " christen@dallas: ~ "
WIDTH = 560
ART_TOP = 18  # the art's own y values start at 10
TEXT_X = 20
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
FONT_SIZE = 10
LINE_HEIGHT = 15
CHAR_WIDTH = FONT_SIZE * 0.602  # Menlo/SF Mono advance width


def art_rows() -> list[str]:
    svg = (ROOT / "ascii-art.svg").read_text(encoding="utf-8")
    return re.findall(r"<tspan [^>]*>.*?</tspan>", svg)


def build(theme: dict) -> str:
    rows = art_rows()
    art_bottom = ART_TOP + 10 + 3.6 * len(rows)
    text_top = art_bottom + 26
    height = round(text_top + LINE_HEIGHT * len(LINES) + 14)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="100%" role="img" aria-label="ASCII art scene above a terminal: Christen Jacquottet, creative technologist at LERMA/, Dallas">',
        "<defs>",
        f'<radialGradient id="screen" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="{theme["bg"]}"/><stop offset="1" stop-color="{theme["edge"]}"/></radialGradient>',
        '<radialGradient id="vignette" cx="50%" cy="50%" r="72%"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient>',
        '<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.28"/></pattern>',
        '<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.6"/><feComponentTransfer result="b"><feFuncA type="linear" slope="0.45"/></feComponentTransfer><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="artglow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.8"/><feComponentTransfer result="b"><feFuncA type="linear" slope="0.6"/></feComponentTransfer><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        f'<clipPath id="win"><rect x="4" y="4" width="{WIDTH - 8}" height="{height - 8}" rx="8"/></clipPath>',
        "</defs>",
        f'<rect width="{WIDTH}" height="{height}" fill="{theme["edge"]}"/>',
        '<g clip-path="url(#win)">',
        f'<rect width="{WIDTH}" height="{height}" fill="url(#screen)"/>',
        # The art, recoloured to the phosphor.
        f'<g transform="translate(0 {ART_TOP})" filter="url(#artglow)"><text font-family="monospace" font-size="3" fill="{theme["fg"]}">',
        *rows,
        "</text></g>",
        f'<g filter="url(#glow)" font-family="{FONT}" font-size="{FONT_SIZE}">',
    ]

    for i, line in enumerate(LINES):
        y = text_top + i * LINE_HEIGHT
        col = 0
        spans = []
        for style, text in line:
            if style == "cursor":
                x = TEXT_X + col * CHAR_WIDTH
                out.append(
                    f'<rect x="{x:.1f}" y="{y - FONT_SIZE + 1}" width="{CHAR_WIDTH:.1f}" height="{FONT_SIZE + 1}" fill="{theme["bright"]}">'
                    '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
                )
                continue
            spans.append(f'<tspan fill="{theme[style]}">{escape(text, quote=False)}</tspan>')
            col += len(text)
        if spans:
            out.append(f'<text x="{TEXT_X}" y="{y}" xml:space="preserve">{"".join(spans)}</text>')

    out += [
        "</g>",
        f'<rect width="{WIDTH}" height="{height}" fill="url(#scan)"/>',
        f'<rect width="{WIDTH}" height="{height}" fill="url(#vignette)"/>',
        "</g>",
        # Frame with the title cut into the top border.
        f'<rect x="4.5" y="4.5" width="{WIDTH - 9}" height="{height - 9}" rx="8" fill="none" stroke="{theme["dim"]}" stroke-width="1"/>',
        f'<rect x="{WIDTH / 2 - len(TITLE) * 3.6}" y="0" width="{len(TITLE) * 7.2}" height="10" fill="{theme["edge"]}"/>',
        f'<text x="{WIDTH / 2}" y="8" text-anchor="middle" font-family="{FONT}" font-size="9" fill="{theme["dim"]}" xml:space="preserve">{escape(TITLE)}</text>',
        "</svg>",
    ]
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", choices=THEMES, default="github")
    parser.add_argument("--out", type=Path, default=ROOT / "terminal.svg")
    args = parser.parse_args()
    args.out.write_text(build(THEMES[args.theme]), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
