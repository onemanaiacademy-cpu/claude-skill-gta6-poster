---
name: gta6-poster
description: Turn one image, several images or a folder into "GTA 6 inspired" colour-theme posters (hot pink, orange, purple, teal sunset-neon grade with glow, grain, vignette, big title, tagline and a fake "coming soon" footer). Use when the user asks for a GTA 6 style, vice-city, sunset neon or retro game-poster look. Colour theme only: never reproduces any official logo, art or fonts.
---

# gta6-poster

Makes 2:3 posters (default 1600x2400) in a "GTA 6 inspired colour theme". It is a colour study, not official art: no Rockstar/GTA logo, no official fonts, no real branding. The footer says it is fan-made and not affiliated.

## Requirements
Python 3 with Pillow (numpy is not needed). Offline, no credits, no network.
Install Pillow once: `python3 -m pip install pillow` (or in a venv: `python3 -m venv .venv && .venv/bin/pip install pillow`). Then run the commands below with that python (`python3`, or `.venv/bin/python`).

## Steps
1. Collect the input images (files or a folder). Use only images the user owns or that are non-personal; do not process photos of other people without the user saying it is fine.
2. Pick a mode:
   - `single`: first image becomes one poster.
   - `collage`: up to 6 images on one poster (1 full, 2 stacked, 3 one big + two, 4-6 grid).
   - `each`: one poster per image.
   - `auto` (default): single for 1 image, collage for several.
3. Run (path is relative to this skill folder; use the Python that has Pillow):
   ```
   python3 scripts/make_poster.py INPUT [INPUT ...] -o OUTDIR --mode each --title "VICE NIGHTS"
   ```
4. Open the PNGs, check the title is readable and nothing important is cropped. If an image is landscape, the 2:3 crop cuts the sides: say so and suggest a portrait or centred subject.
5. Optional contact sheet: `python3 scripts/contact_sheet.py OUT/sheet.png OUTDIR/*.png`.

## Options
`--title` (use `\n` for a line break; default file name), `--tagline`, `--footer` (use `|` for 2 lines), `--palette sunset|neon|dusk`, `--size 1600x2400`, `--strength 0-1` (gradient map vs original colour), `--glow`, `--grain` (default 0.35), `--vignette`, `--font path.ttf`, `--no-text`, `--original` (crop only, for before/after).
Font: Avenir Next if present (macOS), otherwise Helvetica/DejaVu/Arial/Pillow default.

## Rules
- Do not add the GTA or Rockstar logo, the "VI" mark, or copy official poster layouts or art. Do not suggest titles that imitate official ones for upload as official material; call the result "GTA 6 inspired colour theme".
- Keep the "not affiliated" footer when publishing.
