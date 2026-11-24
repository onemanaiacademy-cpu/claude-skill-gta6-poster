#!/usr/bin/env python3
"""make_poster.py - turn images into "GTA 6 inspired" sunset-neon colour-theme posters.

Only Pillow is required (numpy is NOT needed). No network, no credits.
This is a colour theme only: no Rockstar/GTA logo, art or fonts are used or imitated.

Examples
  python3 make_poster.py photo.jpg -o out/ --title "VICE NIGHTS"
  python3 make_poster.py ./folder -o out/ --mode collage --title "SUMMER CITY"
  python3 make_poster.py a.png b.png c.png -o out/ --mode each
"""
import argparse
import os
import random
import sys

try:
    from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                     ImageFont, ImageOps)
except ImportError:
    sys.exit("Pillow is required: python3 -m pip install Pillow  "
             "(or use a venv that has it)")

try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # old Pillow
    LANCZOS = Image.LANCZOS

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# Gradient-map stops (position 0..1, hex colour): shadows -> highlights.
PALETTES = {
    # teal shadows, purple, hot pink, orange, warm cream highlight
    "sunset": [(0.00, "#03121f"), (0.16, "#0b5d6b"), (0.34, "#4b1a8c"),
               (0.55, "#ff2e88"), (0.78, "#ff8a2a"), (1.00, "#ffe9b0")],
    # more teal and pink, less orange (night city feel)
    "neon":   [(0.00, "#050818"), (0.20, "#0d7f86"), (0.40, "#2a1b86"),
               (0.62, "#ff2fa8"), (0.85, "#ff9f5a"), (1.00, "#fff0d0")],
    # purple dusk into orange
    "dusk":   [(0.00, "#0a0420"), (0.25, "#3b0f78"), (0.50, "#c4237f"),
               (0.75, "#ff6b2c"), (1.00, "#ffd98a")],
}
TITLE_GRAD = ("#ff4fa3", "#ff9a3c")  # top -> bottom fill of the title


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def build_lut(stops):
    pts = [(p, hex2rgb(c)) for p, c in stops]
    lut = []
    for i in range(256):
        t = i / 255.0
        for (p0, c0), (p1, c1) in zip(pts, pts[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0
                lut.append(tuple(c0[j] + (c1[j] - c0[j]) * k for j in range(3)))
                break
    return lut


def gradient_map(gray, palette):
    lut = build_lut(PALETTES[palette])
    chans = []
    for j in range(3):
        table = [int(round(c[j])) for c in lut]
        chans.append(gray.point(table))
    return Image.merge("RGB", chans)


def load(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (20, 10, 40, 255))
        im = Image.alpha_composite(bg, im)
    return im.convert("RGB")


def grade(img, palette="sunset", strength=0.85, glow=0.6, grain=0.35, vignette=0.55):
    """Sunset-neon grade. strength 0..1 = gradient map vs saturated original."""
    gray = ImageOps.autocontrast(ImageOps.grayscale(img), cutoff=1)
    gray = gray.point([int(255 * ((i / 255.0) ** 0.9)) for i in range(256)])
    gm = gradient_map(gray, palette)
    base = ImageEnhance.Color(img).enhance(1.8)
    base = ImageEnhance.Contrast(base).enhance(1.2)
    out = Image.blend(base, gm, max(0.0, min(1.0, strength)))
    # keep a little of the real colour in the lights: pushes variation
    out = ImageEnhance.Contrast(out).enhance(1.08)

    w, h = out.size
    if glow > 0:  # bloom: blur the brights and screen them back
        bright = out.point([max(0, int((i - 150) * 255 / 105)) for i in range(256)] * 3)
        r = max(6, int(min(w, h) * 0.025))
        bloom = bright.filter(ImageFilter.GaussianBlur(r))
        bloom = bloom.point([min(255, int(i * glow * 1.8)) for i in range(256)] * 3)
        out = ImageChops.screen(out, bloom)
        wide = out.filter(ImageFilter.GaussianBlur(r * 3)).point(
            [min(255, int(i * glow * 0.35)) for i in range(256)] * 3)
        out = ImageChops.screen(out, wide)
    if vignette > 0:
        rad = Image.radial_gradient("L").resize((w, h), LANCZOS)  # 0 centre, 255 edge
        k = vignette
        mask = rad.point([int(255 - min(255, max(0, (i - 90) * 255 / 165)) * k) for i in range(256)])
        dark = Image.new("RGB", (w, h), (12, 4, 30))
        out = Image.composite(out, dark, mask)
    if grain > 0:
        noise = Image.effect_noise((w, h), 38 * grain + 1).convert("RGB")
        out = ImageChops.add(out, noise, 1.0, -128)
    return out


# ------------------------------------------------------------------ fonts
FONT_CANDIDATES = [
    ("/System/Library/Fonts/Avenir Next.ttc", {"heavy": 8, "bold": 0, "demi": 2, "medium": 5, "regular": 7}),
    ("/System/Library/Fonts/Avenir Next Condensed.ttc", {"heavy": 8, "bold": 0, "demi": 2, "medium": 5, "regular": 7}),
]
FALLBACKS = ["/System/Library/Fonts/Helvetica.ttc",
             "/Library/Fonts/Arial Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "C:/Windows/Fonts/arialbd.ttf"]


def get_font(size, weight="bold", custom=None):
    if custom and os.path.exists(custom):
        return ImageFont.truetype(custom, size)
    for path, idx in FONT_CANDIDATES:
        if os.path.exists(path):
            for i in (idx.get(weight, 0), 0):
                try:
                    return ImageFont.truetype(path, size, index=i)
                except Exception:
                    pass
    for path in FALLBACKS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size)  # Pillow >= 10.1
    except Exception:
        return ImageFont.load_default()


def text_w(font, s, spacing=0):
    return sum(font.getlength(c) + spacing for c in s) - spacing if spacing else font.getlength(s)


def draw_spaced(draw, xy, s, font, fill, spacing):
    x, y = xy
    for c in s:
        draw.text((x, y), c, font=font, fill=fill)
        x += font.getlength(c) + spacing


def fit_lines(title, width, font_path, max_size, weight):
    """Largest size (<= max_size) where every line fits in width; wraps on spaces."""
    words = title.upper().replace("\\n", "\n").split()
    manual = "\n" in title.replace("\\n", "\n")
    for size in range(max_size, 60, -8):
        f = get_font(size, weight, font_path)
        if manual:
            lines = title.upper().replace("\\n", "\n").split("\n")
        else:
            lines, cur = [], ""
            for wd in words:
                t = (cur + " " + wd).strip()
                if text_w(f, t, size * 0.04) <= width or not cur:
                    cur = t
                else:
                    lines.append(cur)
                    cur = wd
            lines.append(cur)
            if len(lines) > 3:
                continue
        if all(text_w(f, l, size * 0.04) <= width for l in lines):
            return f, lines, size
    f = get_font(60, weight, font_path)
    return f, [title.upper()], 60


def add_text(poster, title, tagline, footer, font_path=None, palette="sunset"):
    W, H = poster.size
    # dark gradient at the bottom (and slight at top) for legibility
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    y0 = int(H * 0.52)
    for y in range(y0, H):
        t = (y - y0) / (H - y0)
        sd.line([(0, y), (W, y)], fill=int(215 * t ** 1.4))
    for y in range(0, int(H * 0.12)):
        sd.line([(0, y), (W, y)], fill=int(90 * (1 - y / (H * 0.12))))
    poster = Image.composite(Image.new("RGB", (W, H), (10, 3, 26)), poster, shade)

    margin = int(W * 0.08)
    max_w = W - 2 * margin
    f, lines, size = fit_lines(title, max_w, font_path, int(W * 0.2), "heavy")
    sp = size * 0.04
    lh = int(size * 1.02)
    block_h = lh * len(lines)
    foot_size = int(W * 0.0175)
    ff = get_font(foot_size, "demi", font_path)
    ff_small = None
    tag_size = int(W * 0.03)
    tf = get_font(tag_size, "medium", font_path)

    foot_y = H - int(H * 0.05) - foot_size
    tag_y = foot_y - int(H * 0.045) - tag_size
    ty = tag_y - int(H * 0.03) - block_h

    # title layers
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for i, line in enumerate(lines):
        lw = text_w(f, line, sp)
        draw_spaced(md, ((W - lw) / 2, ty + i * lh), line, f, 255, sp)
    c0, c1 = hex2rgb(TITLE_GRAD[0]), hex2rgb(TITLE_GRAD[1])
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = min(1, max(0, (y - ty) / max(1, block_h)))
        gd.line([(0, y), (W, y)], fill=tuple(int(c0[j] + (c1[j] - c0[j]) * t) for j in range(3)))
    # neon glow behind the title
    glow = Image.new("RGB", (W, H), hex2rgb("#ff2e88"))
    gmask = mask.filter(ImageFilter.GaussianBlur(size * 0.12)).point(lambda v: min(255, int(v * 1.1)))
    poster = Image.composite(glow, poster, gmask.point(lambda v: int(v * 0.75)))
    # thin dark outline for contrast, then the gradient fill
    outline = mask.filter(ImageFilter.MaxFilter(5))
    poster = Image.composite(Image.new("RGB", (W, H), (14, 4, 34)), poster, outline.point(lambda v: int(v * 0.9)))
    poster = Image.composite(grad, poster, mask)

    d = ImageDraw.Draw(poster)
    if tagline:
        s = tagline.upper()
        spc = tag_size * 0.22
        draw_spaced(d, ((W - text_w(tf, s, spc)) / 2, tag_y), s, tf, (255, 233, 176), spc)
    if footer:
        for k, s in enumerate(footer.upper().split("|")):
            s = s.strip()
            spc = foot_size * 0.3
            while text_w(ff, s, spc) > max_w and spc > 0:  # keep inside the margins
                spc -= 0.5
            draw_spaced(d, ((W - text_w(ff, s, spc)) / 2, foot_y + k * int(foot_size * 1.7)), s, ff,
                        (255, 170, 205), spc)
    # thin accent rule above the footer
    d.line([(W * 0.38, foot_y - int(H * 0.012)), (W * 0.62, foot_y - int(H * 0.012))], fill=(255, 138, 42), width=3)
    return poster


# ------------------------------------------------------------------ layouts
def grid_cells(n, x, y, w, h, gap):
    """Return n rectangles (x0,y0,x1,y1) inside the box."""
    if n == 1:
        return [(x, y, x + w, y + h)]
    if n == 2:
        hh = (h - gap) // 2
        return [(x, y, x + w, y + hh), (x, y + hh + gap, x + w, y + h)]
    if n == 3:
        top = int((h - gap) * 0.55)
        cw = (w - gap) // 2
        return [(x, y, x + w, y + top),
                (x, y + top + gap, x + cw, y + h),
                (x + cw + gap, y + top + gap, x + w, y + h)]
    cols = 2 if n <= 4 else 3
    rows = (n + cols - 1) // cols
    cw = (w - gap * (cols - 1)) // cols
    ch = (h - gap * (rows - 1)) // rows
    cells = []
    for i in range(n):
        r, c = divmod(i, cols)
        cells.append((x + c * (cw + gap), y + r * (ch + gap), x + c * (cw + gap) + cw, y + r * (ch + gap) + ch))
    return cells


def make_single(path, size, opt):
    W, H = size
    img = ImageOps.fit(load(path), (W, H), LANCZOS, centering=(0.5, 0.4))
    return grade(img, opt.palette, opt.strength, opt.glow, opt.grain, opt.vignette)


def make_collage(paths, size, opt):
    W, H = size
    paths = paths[:6]
    gap = int(W * 0.012)
    pad = int(W * 0.04)
    box = (pad, pad, W - 2 * pad, int(H * 0.58))
    canvas = Image.new("RGB", (W, H), (22, 6, 44))
    # background: first image, heavily graded and blurred
    bg = ImageOps.fit(load(paths[0]), (W, H), LANCZOS)
    bg = grade(bg, opt.palette, 1.0, 0, 0, 0.6).filter(ImageFilter.GaussianBlur(45))
    bg = ImageEnhance.Brightness(bg).enhance(0.7)  # no bright blob (e.g. a sun) bleeding as grey haze at the edges
    canvas = Image.blend(canvas, bg, 0.55)
    for p, (x0, y0, x1, y1) in zip(paths, grid_cells(len(paths), *box, gap)):
        tile = ImageOps.fit(load(p), (x1 - x0, y1 - y0), LANCZOS, centering=(0.5, 0.4))
        tile = grade(tile, opt.palette, opt.strength, opt.glow, opt.grain, opt.vignette * 0.6)
        canvas.paste(tile, (x0, y0))
    out = grade(canvas, opt.palette, 0.15, opt.glow * 0.3, opt.grain * 0.6, opt.vignette)
    return out


def collect(inputs):
    files = []
    for p in inputs:
        if os.path.isdir(p):
            for n in sorted(os.listdir(p)):
                if os.path.splitext(n)[1].lower() in EXTS and not n.startswith("."):
                    files.append(os.path.join(p, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            print("skip (not found): " + p, file=sys.stderr)
    return files


def parse_size(s):
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError("size must look like 1600x2400")


def main():
    ap = argparse.ArgumentParser(description="GTA 6 inspired colour-theme poster maker (colour theme only).")
    ap.add_argument("inputs", nargs="+", help="image files and/or folders")
    ap.add_argument("-o", "--out", default="posters", help="output folder")
    ap.add_argument("--mode", choices=["auto", "single", "collage", "each"], default="auto",
                    help="single: first image; collage: up to 6 images on one poster; "
                         "each: one poster per image; auto: single for 1 image, collage for several")
    ap.add_argument("--title", default=None, help="big title (default: file name). Use \\n for a line break")
    ap.add_argument("--tagline", default="Sun. Neon. Open road.")
    ap.add_argument("--footer", default="Coming soon | Fan-made colour study - not affiliated with any game or studio",
                    help="small footer text; use | for a second line")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="sunset")
    ap.add_argument("--size", type=parse_size, default=(1600, 2400), help="WxH, keep 2:3 (default 1600x2400)")
    ap.add_argument("--strength", type=float, default=0.85, help="0..1 gradient-map strength")
    ap.add_argument("--glow", type=float, default=0.6, help="0..1.5 bloom")
    ap.add_argument("--grain", type=float, default=0.35, help="0..1.5 film grain")
    ap.add_argument("--vignette", type=float, default=0.55, help="0..1 edge darkening")
    ap.add_argument("--font", default=None, help="optional .ttf/.ttc path (default Avenir Next, then fallbacks)")
    ap.add_argument("--original", action="store_true",
                    help="only crop to the poster size (same crop as the poster), no grade, no text; "
                         "for before/after comparisons (single mode)")
    ap.add_argument("--no-text", action="store_true", help="grade only, no title/tagline/footer")
    ap.add_argument("--seed", type=int, default=7)
    opt = ap.parse_args()

    random.seed(opt.seed)
    files = collect(opt.inputs)
    if not files:
        sys.exit("No images found.")
    os.makedirs(opt.out, exist_ok=True)
    mode = opt.mode if opt.mode != "auto" else ("single" if len(files) == 1 else "collage")

    jobs = []
    if mode == "single":
        jobs.append(("single", [files[0]]))
    elif mode == "collage":
        jobs.append(("collage", files))
    else:
        jobs = [("single", [f]) for f in files]

    for kind, paths in jobs:
        stem = os.path.splitext(os.path.basename(paths[0]))[0]
        if kind == "single" and opt.original:
            poster = ImageOps.fit(load(paths[0]), opt.size, LANCZOS, centering=(0.5, 0.4))
            opt.no_text = True
        elif kind == "single":
            poster = make_single(paths[0], opt.size, opt)
        else:
            poster = make_collage(paths, opt.size, opt)
        title = opt.title or (stem.replace("_", " ").replace("-", " ") if kind == "single" else "SUMMER CITY")
        if not opt.no_text:
            poster = add_text(poster, title, opt.tagline, opt.footer, opt.font, opt.palette)
        name = "poster_%s_%s.png" % (kind, stem)
        dest = os.path.join(opt.out, name)
        poster.save(dest)
        print("wrote " + dest)
    # contact sheet when several posters were written
    print("done: %d poster(s), mode=%s" % (len(jobs), mode))


if __name__ == "__main__":
    main()
