#!/usr/bin/env python3
"""Renders the header/footer logo and favicon set from the client's own
circular sign artwork (assets/img/logo-source.webp — already a clean cutout,
alpha 0 outside the disc).

Three outputs:
  assets/img/logo.webp        the full disc, trimmed to its own bounding box,
                               for the header, footer and hero brand mark.
  assets/img/favicon-*.png    the disc's house+cup+burger emblem alone,
                               composited onto a solid espresso backing --
                               the full disc's fine print (three lines of
                               tracked-out caps) does not survive down to
                               16-32px, the emblem does.
  assets/img/apple-touch-icon.png   same emblem, 180px, opaque (iOS applies
                               its own squircle mask over a transparent PNG
                               unevenly across versions, so this one ships
                               filled).

Run:  python3 tools/make-logo.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "img", "logo-source.webp")
OUT = os.path.join(ROOT, "assets", "img")

ESPRESSO = (43, 31, 26, 255)  # --espresso, so the favicon backing matches the site


def main():
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size

    # 1 · the full disc, trimmed to its own alpha bounding box
    disc = im.crop(im.getbbox())
    for size, name in ((640, "logo.webp"), (256, "logo-256.webp")):
        disc.resize((size, size), Image.LANCZOS).save(
            os.path.join(OUT, name), "WEBP", quality=92, method=6
        )

    # 2 · the emblem alone -- house, hanging lamp, cup, burger, palm, sunset --
    # cropped clear of the sign's brass ring and its three lines of small type
    emblem = im.crop((round(w * 0.265), round(h * 0.155), round(w * 0.775), round(h * 0.535)))

    def on_espresso(square_size):
        canvas = Image.new("RGBA", (square_size, square_size), ESPRESSO)
        # pad the emblem to square first so it isn't stretched
        ew, eh = emblem.size
        side = max(ew, eh)
        padded = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        padded.paste(emblem, ((side - ew) // 2, (side - eh) // 2), emblem)
        fitted = padded.resize((square_size, square_size), Image.LANCZOS)
        canvas.alpha_composite(fitted)
        return canvas

    on_espresso(512).convert("RGB").save(os.path.join(OUT, "favicon-512.png"), "PNG")
    on_espresso(180).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"), "PNG")
    for size in (32, 16):
        on_espresso(size).convert("RGB").save(os.path.join(OUT, f"favicon-{size}.png"), "PNG")

    # a .ico carrying both small sizes, for browsers that still ask for one
    icon_32 = on_espresso(32).convert("RGB")
    icon_16 = on_espresso(16).convert("RGB")
    icon_32.save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32)])

    print("wrote logo.webp, logo-256.webp, favicon-512/180/32/16.png, favicon.ico")


if __name__ == "__main__":
    main()
