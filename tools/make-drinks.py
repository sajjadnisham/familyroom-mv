#!/usr/bin/env python3
"""Renders the hero orbit's drink stills from the client-supplied photographs.

One square still per drink. The orbit scales them with transforms rather than
swapping sources, so a single resolution stays sharp in the featured position
and costs nothing extra as a satellite. Each is a real
photograph of that drink -- there is deliberately no espresso, americano, mocha
or iced coffee here, because no photograph of those was supplied and darkening
a cappuccino to stand in for them would be a fabricated menu item.

Run:  python3 tools/make-drinks.py
"""
import json, math, os
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

SRC = "/root/.claude/uploads/7d969982-7431-5130-b512-593f4c1a4612"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "drinks")

# slug: (source file, square crop as source fractions, credit)
DRINKS = {
    "cappuccino":   ("2e2cca05-image.jpg", (0.020, 0.380, 0.950, 0.799),
                     "Guest photo, Google Maps (credited 'Raya Ss')", 0.42, 1.00),
    "flat-white":   ("1302bbc0-image.jpg", (0.145, 0.430, 0.855, 0.749),
                     "Guest photo by @nishaaarl, reshared by the cafe", 0.50, 0.94),
    "jasmine":      ("1f4ea03f-image.jpg", (0.085, 0.280, 0.575, 0.770),
                     "Tea Drop supplier marketing image", 0.46, 0.97),
    "fruits-eden":  ("93570108-image.jpg", (0.085, 0.280, 0.575, 0.770),
                     "Tea Drop supplier marketing image", 0.46, 0.97),
    # The only still shot against a pale wall, so it needs the most help to
    # sit in the hero's darkness rather than read as a bright disc.
    "single-origin":("abc596dc-image.jpg", (0.020, 0.470, 0.600, 0.934),
                     "Family Room Coffee retail packaging", 0.66, 0.86),
}

SIZE = 760   # one size; the orbit scales with transforms, not with srcset


def warm(im, r, g, b):
    """A gentle channel tilt toward the roast, applied after desaturation so
    the grey it leaves behind is warm rather than neutral."""
    a = np.asarray(im).astype(np.float32) * np.array([r, g, b], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def vignette(im, amount):
    """Darken toward the edge so every still dissolves into the hero's dark
    scene at the same rate, whatever the photograph's own background."""
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / (w - 1) - 0.5) * 2
    ny = (yy / (h - 1) - 0.5) * 2
    r = np.sqrt(nx ** 2 + ny ** 2) / math.sqrt(2)
    fall = (1.0 - amount * np.clip((r - 0.22) / 0.78, 0, 1) ** 1.5)[..., None]
    return Image.fromarray(np.clip(a * fall, 0, 255).astype(np.uint8), "RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest, total = {}, 0
    for slug, (fn, box, credit, vig, bright) in DRINKS.items():
        im = Image.open(os.path.join(SRC, fn)).convert("RGB")
        w, h = im.size
        px = (round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h))
        crop = im.crop(px)
        # square it off centre-out, in case a box is a pixel or two out
        side = min(crop.size)
        cx, cy = crop.width // 2, crop.height // 2
        crop = crop.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
        crop = ImageOps.autocontrast(crop, cutoff=(0.3, 0.0), preserve_tone=True)
        # One restrained grade across the set. The photographs are of bright
        # ceramic -- teal, cobalt, red -- on orange wood, and at full
        # saturation five of them orbiting together read as a colour wheel
        # rather than a coffee bar. Pulling the saturation down and warming
        # what is left keeps them photographic while letting the espresso
        # background carry the palette.
        crop = ImageEnhance.Color(crop).enhance(0.66)
        crop = warm(crop, 1.045, 1.0, 0.915)
        crop = ImageEnhance.Contrast(crop).enhance(1.07)
        if bright != 1.0:
            crop = ImageEnhance.Brightness(crop).enhance(bright)
        crop = vignette(crop, vig)
        p = os.path.join(OUT, f"{slug}.webp")
        crop.resize((SIZE, SIZE), Image.LANCZOS).save(p, "WEBP", quality=82, method=5)
        total += os.path.getsize(p)
        manifest[slug] = {"credit": credit, "source": fn}
    with open(os.path.join(OUT, "credits.json"), "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(f"wrote {len(DRINKS)} stills, {total / 1024:.0f} KB total")


if __name__ == "__main__":
    main()
