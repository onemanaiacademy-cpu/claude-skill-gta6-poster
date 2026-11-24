#!/usr/bin/env python3
"""contact_sheet.py OUT.png img1 img2 ... : thumbnails side by side (Pillow only)."""
import sys
from PIL import Image
out, files = sys.argv[1], sys.argv[2:]
th = 900
ims = []
for f in files:
    im = Image.open(f).convert("RGB")
    ims.append(im.resize((int(im.width * th / im.height), th)))
gap = 24
sheet = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) + 1), th + 2 * gap), (24, 24, 28))
x = gap
for i in ims:
    sheet.paste(i, (x, gap))
    x += i.width + gap
sheet.save(out)
print("wrote " + out)
