#!/usr/bin/env python3
"""Procedural, copyright-free test images (blue sky/green palette, so the grade is obvious)."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
random.seed(3)
W, H = 1600, 1200

def vgrad(d, top, bot, y0=0, y1=H):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))

def city():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    vgrad(d, (40, 110, 200), (190, 225, 245), 0, 800)
    x = 0
    while x < W:
        bw = random.randint(80, 190); bh = random.randint(300, 900)
        g = random.randint(40, 90)
        d.rectangle([x, H - 250 - bh, x + bw, H], fill=(g, g + 10, g + 30))
        for wy in range(H - 230 - bh, H - 270, 38):
            for wx in range(x + 12, x + bw - 14, 26):
                if random.random() < 0.55:
                    d.rectangle([wx, wy, wx + 12, wy + 20], fill=(250, 230, 150))
        x += bw + random.randint(0, 12)
    d.rectangle([0, H - 250, W, H], fill=(55, 55, 65))
    d.rectangle([0, H - 135, W, H - 120], fill=(230, 230, 230))
    return im

def beach():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    vgrad(d, (60, 150, 230), (200, 235, 250), 0, 700)
    d.ellipse([1050, 300, 1250, 500], fill=(255, 255, 230))
    vgrad(d, (20, 150, 190), (60, 200, 210), 700, 880)
    vgrad(d, (235, 215, 160), (210, 185, 130), 880, H)
    for (px, lean, hh) in ((260, 90, 700), (1300, -110, 760)):
        top = (px + lean, 880 - hh)
        d.line([(px, 960), top], fill=(30, 30, 40), width=26)
        for a in range(-80, 81, 32):
            ang = math.radians(a - 90)
            for L in (260,):
                ex = top[0] + math.cos(ang) * L; ey = top[1] + math.sin(ang) * L * 0.8 + 90
                d.line([top, ((top[0] + ex) / 2, top[1] - 50 + abs(a) * 0.3), (ex, ey)], fill=(25, 110, 60), width=18)
    return im

def road():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    vgrad(d, (90, 170, 235), (225, 240, 250), 0, 620)
    d.polygon([(0, 620), (400, 380), (700, 620)], fill=(90, 130, 110))
    d.polygon([(500, 620), (1100, 330), (1600, 620)], fill=(70, 115, 100))
    d.rectangle([0, 620, W, H], fill=(70, 160, 90))
    d.polygon([(760, 620), (840, 620), (1500, H), (100, H)], fill=(60, 62, 70))
    for i in range(8):
        t0, t1 = i / 8, (i + 0.5) / 8
        y0 = 620 + (H - 620) * t0 ** 1.7; y1 = 620 + (H - 620) * t1 ** 1.7
        w0 = 3 + 22 * t0 ** 1.7; w1 = 3 + 22 * t1 ** 1.7
        d.polygon([(800 - w0, y0), (800 + w0, y0), (800 + w1, y1), (800 - w1, y1)], fill=(245, 245, 245))
    d.rounded_rectangle([560, 880, 1000, 1040], 40, fill=(200, 30, 40))
    d.rounded_rectangle([650, 810, 920, 900], 30, fill=(150, 20, 30))
    d.rectangle([675, 825, 895, 885], fill=(120, 180, 220))
    for cx in (660, 900):
        d.ellipse([cx - 50, 990, cx + 50, 1090], fill=(20, 20, 24))
    return im

def lake():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    vgrad(d, (50, 100, 190), (200, 220, 240), 0, 700)
    for k, c in enumerate(((150, 170, 200), (100, 130, 160), (50, 80, 70))):
        pts = [(0, 800)]
        for x in range(0, W + 1, 40):
            pts.append((x, 700 - k * 40 - 220 * abs(math.sin(x / 300 + k * 1.7)) - 80 * math.sin(x / 90 + k)))
        pts.append((W, 800))
        d.polygon(pts, fill=c)
    vgrad(d, (50, 120, 170), (20, 70, 110), 800, H)
    for i in range(60):
        y = random.randint(820, H); x = random.randint(0, W)
        d.line([(x, y), (x + random.randint(40, 160), y)], fill=(170, 210, 235), width=3)
    return im.filter(ImageFilter.GaussianBlur(0.8))

for n, f in (("city", city), ("beach", beach), ("road", road), ("lake", lake)):
    f().save(os.path.join(out, "sample_%s.png" % n)); print(n)
