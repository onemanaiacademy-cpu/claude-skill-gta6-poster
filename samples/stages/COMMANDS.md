# Stages of one image (sample_city.png), all 1600x2400, same crop (centering 0.5, 0.4)
Run from gta6-poster/ with the Pillow python (any Python 3 with Pillow).
Input: ../samples/inputs/sample_city.png (procedural drawing, no real photo/logo).

1. stage1_original.png  (crop only, no grade, no text)
   python scripts/make_poster.py ../samples/inputs/sample_city.png -o tmp --original
2. stage2_graded.png  (colour grade + glow, no grain, no vignette, no text)
   python scripts/make_poster.py ../samples/inputs/sample_city.png -o tmp --no-text --grain 0 --vignette 0
3. stage3_poster.png  (defaults: grain 0.35, vignette 0.55, title, tagline, footer)
   python scripts/make_poster.py ../samples/inputs/sample_city.png -o tmp --title "VICE NIGHTS"

Each run writes tmp/poster_single_sample_city.png; it was renamed to the stage name.

# 3-image collage (../collage3/poster_collage_sample_city.png)
   python scripts/make_poster.py ../samples/inputs/sample_city.png ../samples/inputs/sample_lake.png ../samples/inputs/sample_road.png -o ../samples/collage3 --mode collage --palette neon --title "VICE NIGHTS" --tagline "Three views. One sunset."
Collage mode accepts 1 to 6 images (code: paths[:6]; extra images are ignored). Layouts: 1 full, 2 stacked, 3 = one wide on top + two below, 4 = 2x2, 5-6 = 2 columns x 3 rows or 3 columns x 2 rows.
Note: the first image also becomes the blurred background.
