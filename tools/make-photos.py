#!/usr/bin/env python3
"""Turns the client-supplied screenshots into web-ready photography.

Each source is a phone screenshot, so it carries a status bar, app chrome and
in some cases Google's "Images may be subject to copyright" banner. `crop` is
the usable picture inside that chrome, as fractions of the source. `focus` is
the point to keep centred when re-cropping to a different aspect ratio.

Run:  python3 tools/make-photos.py
"""
import os, json
from PIL import Image, ImageOps

SRC = "/root/.claude/uploads/7d969982-7431-5130-b512-593f4c1a4612"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "photos")
os.makedirs(OUT, exist_ok=True)

# source, crop(x0,y0,x1,y1), focus(fx,fy), credit
SOURCES = {
    "lamb-chops":      ("8097b036-image.jpg", (0.00, 0.200, 1.00, 0.760), (0.50, 0.66), "Seaside Grill / Family Room promotional artwork"),
    "avocado-toast":   ("d4519ecd-image.jpg", (0.00, 0.300, 1.00, 0.768), (0.45, 0.48), "@familyroomcoffee.mv Instagram post, 15 Dec 2020"),
    "chicken-burger":  ("3888b3ea-image.jpg", (0.00, 0.345, 1.00, 0.660), (0.42, 0.55), "Seaside Grill / Family Room promotional artwork"),
    "bolognese":       ("04a25036-image.jpg", (0.17, 0.318, 0.83, 0.610), (0.50, 0.50), "Seaside Grill / Family Room promotional artwork"),
    "beef-burger-ad":  ("3471669f-image.jpg", (0.15, 0.205, 0.85, 0.795), (0.50, 0.50), "Seaside Grill / Family Room promotional artwork"),
    "thai-curry":      ("96facb16-image.jpg", (0.15, 0.330, 0.85, 0.600), (0.50, 0.50), "Seaside Grill / Family Room promotional artwork"),
    "chicken-wings":   ("0ec921d8-image.jpg", (0.15, 0.318, 0.85, 0.592), (0.50, 0.50), "Seaside Grill / Family Room promotional artwork"),
    "latte-blue":      ("1302bbc0-image.jpg", (0.145, 0.170, 0.855, 0.845), (0.50, 0.62), "Guest photo by @nishaaarl, reshared by the cafe 14 Sep 2020"),
    "beans":           ("abc596dc-image.jpg", (0.00, 0.430, 1.00, 1.000), (0.50, 0.40), "Family Room Coffee retail packaging"),
    "beef-burger":     ("353e3119-image.jpg", (0.06, 0.140, 0.94, 0.890), (0.50, 0.52), "Family Room Coffee / Seaside Grill product shot"),
    "tea-jasmine":     ("1f4ea03f-image.jpg", (0.08, 0.140, 0.82, 0.800), (0.40, 0.46), "Tea Drop supplier marketing image"),
    "tea-fruits":      ("93570108-image.jpg", (0.08, 0.140, 0.82, 0.800), (0.40, 0.46), "Tea Drop supplier marketing image"),
    "latte-donut":     ("2e2cca05-image.jpg", (0.00, 0.232, 1.00, 0.845), (0.45, 0.62), "Guest photo, Google Maps (credited 'Raya Ss')"),
    "chicken-rice":    ("fc1e431b-image.jpg", (0.00, 0.135, 1.00, 0.900), (0.48, 0.55), "Guest photo, Google Maps (credited 'Hussain Shareef')"),
    "room":            ("66d465b2-image.jpg", (0.00, 0.266, 0.74, 0.889), (0.40, 0.72), "Guest photo, Google Maps (credited 'Raya Ss')"),
    # One crop per bag out of the same shelf photograph, so each origin card on
    # our-coffee.html shows its own coffee rather than all three repeated.
    "bean-kenya":      ("abc596dc-image.jpg", (0.055, 0.545, 0.375, 0.930), (0.50, 0.50), "Family Room Coffee retail packaging"),
    "bean-colombia":   ("abc596dc-image.jpg", (0.355, 0.545, 0.670, 0.930), (0.50, 0.50), "Family Room Coffee retail packaging"),
    "bean-ethiopia":   ("abc596dc-image.jpg", (0.645, 0.545, 0.960, 0.930), (0.50, 0.50), "Family Room Coffee retail packaging"),
    # Same photograph as "beans", framed low for use as a darkened hero backdrop.
    "beans-shelf":     ("abc596dc-image.jpg", (0.00, 0.470, 1.00, 1.000), (0.50, 0.44), "Family Room Coffee retail packaging"),
}

# name -> (width, height) renditions
RENDITIONS = {
    "hero":    [("beans-shelf", 2000, 1125)],
    "card":    [(n, 1000, 750) for n in ("latte-blue", "avocado-toast", "lamb-chops",
                                         "beef-burger", "chicken-burger", "latte-donut")],
    "tile":    [(n, 900, 900) for n in ("room", "latte-donut", "beans", "thai-curry",
                                        "chicken-wings", "bolognese")],
    "wide":    [("beans", 1400, 950), ("latte-blue", 1400, 950)],
    "bag":     [(n, 700, 875) for n in ("bean-kenya", "bean-colombia", "bean-ethiopia")],
    "thumb":   [(n, 320, 320) for n in ("latte-blue", "latte-donut", "tea-jasmine", "tea-fruits",
                                        "avocado-toast", "beef-burger", "chicken-burger",
                                        "lamb-chops", "thai-curry", "bolognese", "chicken-wings",
                                        "chicken-rice", "beans")],
}


def load(name):
    fn, crop, focus, _ = SOURCES[name]
    im = Image.open(os.path.join(SRC, fn)).convert("RGB")
    w, h = im.size
    box = (round(crop[0] * w), round(crop[1] * h), round(crop[2] * w), round(crop[3] * h))
    return im.crop(box), focus


def render(name, tw, th):
    """Crop to the target aspect around the focus point, then resize."""
    im, (fx, fy) = load(name)
    w, h = im.size
    target = tw / th
    if w / h > target:                     # too wide: trim the sides
        nw, nh = round(h * target), h
    else:                                  # too tall: trim top/bottom
        nw, nh = w, round(w / target)
    x = min(max(round(fx * w - nw / 2), 0), w - nw)
    y = min(max(round(fy * h - nh / 2), 0), h - nh)
    out = im.crop((x, y, x + nw, y + nh)).resize((tw, th), Image.LANCZOS)
    return ImageOps.autocontrast(out, cutoff=(0.2, 0.0), preserve_tone=True)


manifest = {}
for kind, items in RENDITIONS.items():
    for name, tw, th in items:
        out_name = f"{name}-{kind}.jpg"
        img = render(name, tw, th)
        img.save(os.path.join(OUT, out_name), "JPEG", quality=82, optimize=True, progressive=True)
        manifest.setdefault(name, {"credit": SOURCES[name][3], "files": []})
        manifest[name]["files"].append(out_name)

with open(os.path.join(OUT, "credits.json"), "w") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)

total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith(".jpg"))
print(f"wrote {sum(len(v['files']) for v in manifest.values())} renditions "
      f"from {len(SOURCES)} sources, {total / 1024 / 1024:.2f} MB total")
