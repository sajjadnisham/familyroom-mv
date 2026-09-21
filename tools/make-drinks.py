#!/usr/bin/env python3
"""Renders the hero orbit's drink stills from the client-supplied photographs.

Each drink is cut out of its photograph -- no disc, no frame, no vignette --
so the cup floats free against the hero's own dark field: "coffee in vacuum",
not a photo in a circle. Cutting out replaces the circular-mask-over-a-square-
crop approach the first version of this file used.

Segmentation runs locally (rembg / u2net, CPU, no account or API key) rather
than through a hosted background-removal API, because this container's
outbound network is allow-listed and does not reach one. The u2net weights
(176 MB) download once from a GitHub release on first run and then cache in
~/.rembg -- expect that first run to take a little longer.

There is deliberately no espresso, americano, mocha or iced coffee here,
because no photograph of those was supplied and darkening the cappuccino to
stand in for them would be a fabricated menu item.

Run:  python3 tools/make-drinks.py
"""
import io
import json
import math
import os

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from scipy import ndimage

SRC = "/root/.claude/uploads/7d969982-7431-5130-b512-593f4c1a4612"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "drinks")

# slug: (source file, crop box as source fractions (l, t, r, b), credit)
# The crop is generous rather than square -- it only needs to contain the
# whole cup with room to spare; the cutout's own silhouette decides the
# final shape and aspect ratio, not this box.
DRINKS = {
    "cappuccino":   ("2e2cca05-image.jpg", (0.0, 0.421, 1.0, 0.890),
                      "Guest photo, Google Maps (credited 'Raya Ss')"),
    "flat-white":   ("1302bbc0-image.jpg", (0.145, 0.430, 0.855, 0.749),
                      "Guest photo by @nishaaarl, reshared by the cafe"),
    "jasmine":      ("1f4ea03f-image.jpg", (0.085, 0.210, 0.575, 0.700),
                      "Tea Drop supplier marketing image"),
    "fruits-eden":  ("93570108-image.jpg", (0.085, 0.210, 0.575, 0.700),
                      "Tea Drop supplier marketing image"),
    "single-origin":("abc596dc-image.jpg", (0.020, 0.470, 0.600, 0.934),
                      "Family Room Coffee retail packaging"),
}

LONG_EDGE = 1100  # input resolution handed to segmentation


def cut_out(im):
    """Segments the subject with u2net, then cleans the raw mask up: only the
    largest connected blob survives (drops stray flecks -- a crumb of text, a
    fleck of reflection -- that read as "salient" on their own), the edge is
    feathered by a couple of pixels so it anti-aliases instead of aliasing,
    and near-zero alpha is snapped to fully transparent so a faint halo of
    the old background doesn't ride along at low opacity.
    """
    from rembg import remove, new_session

    session = cut_out.session
    if session is None:
        session = new_session("u2net")
        cut_out.session = session

    cut = remove(im, session=session)
    a = np.asarray(cut)
    alpha = a[..., 3]

    mask = alpha > 32
    labeled, n = ndimage.label(mask)
    if n > 1:
        sizes = ndimage.sum(mask, labeled, range(1, n + 1))
        biggest = int(np.argmax(sizes)) + 1
        keep = labeled == biggest
        alpha = np.where(keep, alpha, 0).astype(np.uint8)

    alpha_im = Image.fromarray(alpha, "L").filter(ImageFilter.GaussianBlur(1.4))
    alpha = np.asarray(alpha_im)
    alpha = np.where(alpha < 10, 0, alpha).astype(np.uint8)

    out = a.copy()
    out[..., 3] = alpha
    return Image.fromarray(out, "RGBA")


cut_out.session = None


def trim_to_subject(im, pad_frac=0.015):
    """Crops to the cutout's own bounding box, so the exported image's aspect
    ratio is the cup's, not the square (or near-square) the source photo
    happened to be cropped to -- the point of a cutout is that its edges are
    the subject's, nothing else's."""
    bbox = im.getbbox()
    if not bbox:
        return im
    w, h = im.size
    px = round((bbox[2] - bbox[0]) * pad_frac)
    py = round((bbox[3] - bbox[1]) * pad_frac)
    box = (
        max(0, bbox[0] - px), max(0, bbox[1] - py),
        min(w, bbox[2] + px), min(h, bbox[3] + py),
    )
    return im.crop(box)


def warm(im, r, g, b):
    """A gentle channel tilt toward the roast, applied after desaturation so
    the grey it leaves behind is warm rather than neutral. RGB only -- the
    caller keeps the alpha channel untouched."""
    a = np.asarray(im).astype(np.float32) * np.array([r, g, b], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def grade(im):
    """One restrained grade across the set. The photographs are of bright
    ceramic -- teal, cobalt, red -- on orange wood, and at full saturation
    five of them floating together read as a colour wheel rather than a
    coffee bar. Pulling the saturation down and warming what is left keeps
    them photographic while letting the espresso background carry the
    palette. Runs on the RGB channels only; alpha is preserved as-is."""
    rgb = im.convert("RGB")
    rgb = ImageOps.autocontrast(rgb, cutoff=(0.3, 0.0), preserve_tone=True)
    rgb = ImageEnhance.Color(rgb).enhance(0.66)
    rgb = warm(rgb, 1.045, 1.0, 0.915)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.07)
    out = Image.merge("RGBA", (*rgb.split(), im.split()[3]))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest, total = {}, 0
    for slug, (fn, box, credit) in DRINKS.items():
        im = Image.open(os.path.join(SRC, fn)).convert("RGB")
        w, h = im.size
        px = (round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h))
        crop = im.crop(px)
        scale = LONG_EDGE / max(crop.size)
        crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)

        cutout = cut_out(crop)
        cutout = trim_to_subject(cutout)
        cutout = grade(cutout)

        p = os.path.join(OUT, f"{slug}.webp")
        cutout.save(p, "WEBP", quality=88, method=6)
        total += os.path.getsize(p)
        manifest[slug] = {"credit": credit, "source": fn, "size": cutout.size}
        print(f"{slug}: {cutout.size[0]}x{cutout.size[1]}, {os.path.getsize(p)/1024:.0f} KB")

    with open(os.path.join(OUT, "credits.json"), "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True, default=list)
    print(f"wrote {len(DRINKS)} cutouts, {total / 1024:.0f} KB total")


if __name__ == "__main__":
    main()
