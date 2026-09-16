#!/usr/bin/env python3
"""Renders the hero's scroll-driven coffee sequence as an image sequence.

Every frame is derived from a real photograph of a flat white (client-supplied),
so the result is photographic rather than an illustration of a cup. The scroll
progress p in [0,1] drives, in order:

  p 0.00-0.18  the finished cup, a slow camera push-in
  p 0.14-0.40  out-of-focus coffee beans drift into the foreground
  p 0.30-0.70  a pour: a soft stream, an impact highlight, expanding ripples
  p 0.34-0.86  the crema swirls, destroying then re-forming the latte art
  p 0.70-1.00  focus pull onto the cup; the art resolves and the cup settles

The crema effect is a real rotational motion blur with a radius-dependent
twist, computed on the liquid disc after circularising the ellipse, so the
swirl follows the surface in perspective instead of sliding across it.

Run:  python3 tools/make-hero-frames.py [--frames N] [--test]
"""
import argparse, math, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "/root/.claude/uploads/7d969982-7431-5130-b512-593f4c1a4612/2e2cca05-image.jpg"
OUT = os.path.join(ROOT, "assets", "hero")

# Usable picture inside the phone chrome (matches tools/make-photos.py, with the
# letterbox at the foot of the screenshot trimmed).
DECHROME = (0.000, 0.232, 1.000, 0.828)

# The liquid surface, in dechromed pixels: an ellipse seen in perspective.
LIQ = dict(cx=567, cy=811, rx=504, ry=296)
# Camera: a 1090px window that can drift +/-20px and tighten by 6%.
WIN, CENTER, DRIFT, PUSH = 1090, (567, 751), 20.0, 0.06

SIZES = {"lg": 1000, "sm": 560}


# ----------------------------------------------------------------- easing
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def ramp(p, a, b):
    """0 before a, 1 after b, smoothstep between."""
    t = clamp((p - a) / (b - a)) if b > a else float(p >= b)
    return t * t * (3 - 2 * t)


def bump(p, a, peak, b):
    """Rises to 1 at `peak`, falls back to 0 by `b`."""
    return ramp(p, a, peak) * (1 - ramp(p, peak, b))


def ease_out(t):
    return 1 - (1 - clamp(t)) ** 3


# ------------------------------------------------------------ crema swirl
def swirl(patch, strength, twist=2.5, spread=0.42, samples=9):
    """Rotational motion blur about the centre with a radius-dependent twist.

    `patch` is a square RGB array whose inscribed circle is the liquid.
    strength 0 returns the patch untouched, so the real latte art re-forms.
    """
    if strength <= 0.004:
        return patch
    h, w = patch.shape[:2]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    R = min(cx, cy)
    # The centre of a cup turns faster than the edge, as a stirred liquid does.
    tw = twist * strength * np.clip(1.0 - r / R, 0.0, 1.0) ** 1.4

    acc = np.zeros((h, w, 3), np.float32)
    wsum = 0.0
    for k in range(samples):
        f = (k / (samples - 1)) - 0.5 if samples > 1 else 0.0
        ang = th + tw + strength * spread * f
        sx = np.clip(cx + r * np.cos(ang), 0, w - 1)
        sy = np.clip(cy + r * np.sin(ang), 0, h - 1)
        x0 = sx.astype(np.int32); y0 = sy.astype(np.int32)
        x1 = np.minimum(x0 + 1, w - 1); y1 = np.minimum(y0 + 1, h - 1)
        fx = (sx - x0)[..., None]; fy = (sy - y0)[..., None]
        top = patch[y0, x0] * (1 - fx) + patch[y0, x1] * fx
        bot = patch[y1, x0] * (1 - fx) + patch[y1, x1] * fx
        # Gaussian-ish weighting keeps the blur from looking like hard copies.
        wt = math.exp(-(f * 2.4) ** 2)
        acc += (top * (1 - fy) + bot * fy) * wt
        wsum += wt
    return acc / wsum


def radial_mask(size, feather):
    """Soft-edged disc, 1 in the middle, 0 outside."""
    h, w = size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot(xx - cx, yy - cy) / min(cx, cy)
    return np.clip((1.0 - r) / feather, 0.0, 1.0)[..., None]


# ---------------------------------------------------------------- overlays
def bean(size, angle, shade, softness):
    """One roasted bean. `softness` is the blur as a fraction of the bean's
    height, so a foreground bokeh bean can be very soft without dissolving.

    Colour and silhouette are built separately: blurring an RGBA layer directly
    bleeds its transparent black into the colour and flattens the alpha into a
    translucent rectangle, which is not a bean.
    """
    s = int(size)
    W_ = s * 2
    body = (shade[0], shade[1], shade[2])
    hi = (min(255, shade[0] + 46), min(255, shade[1] + 34), min(255, shade[2] + 24))

    # Colour fills the whole tile, brighter at the top-left where the light is.
    rgb = Image.new("RGB", (W_, W_), body)
    g = ImageDraw.Draw(rgb)
    g.ellipse([-s * .2, -s * .1, W_ * .78, W_ * .82], fill=hi)
    rgb = rgb.filter(ImageFilter.GaussianBlur(W_ * 0.16))
    # the roast crease, darker, down the long axis
    g = ImageDraw.Draw(rgb)
    g.line([(s * 0.52, s), (s * 1.48, s)],
           fill=(max(0, shade[0] - 38), max(0, shade[1] - 29), max(0, shade[2] - 23)),
           width=max(2, int(s * 0.16)))
    rgb = rgb.filter(ImageFilter.GaussianBlur(W_ * 0.03))

    mask = Image.new("L", (W_, W_), 0)
    pad = s * 0.18
    ImageDraw.Draw(mask).ellipse([pad, s * 0.54, W_ - pad, s * 1.46], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(1.0, s * 0.92 * softness)))

    im = Image.merge("RGBA", (*rgb.split(), mask))
    return im.rotate(angle, resample=Image.BICUBIC, expand=False)


def pour_layer(w, h, liq, alpha, wobble):
    """A soft falling stream plus the bright spot where it meets the crema."""
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if alpha <= 0.01:
        return lay
    # The jug sits outside the crop, so the stream enters from the upper left on
    # a slight arc. It is widest where it leaves the lip and narrows as it
    # accelerates, and the fast upper length carries more motion blur.
    x_top = liq["cx"] - w * 0.20 + wobble * 18
    x_hit = liq["cx"] - liq["rx"] * 0.06 + wobble * 6
    y_hit = liq["cy"] - liq["ry"] * 0.10
    far = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    near = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fd, nd = ImageDraw.Draw(far), ImageDraw.Draw(near)
    steps = 72
    for i in range(steps):
        t = i / (steps - 1)
        y = t * y_hit
        x = x_top + (x_hit - x_top) * (t ** 1.35)
        wid = (w * 0.0295) * (1.0 - 0.30 * t) * (0.62 + 0.38 * alpha)
        # a liquid column is not perfectly even
        wid *= 1.0 + 0.10 * math.sin(t * 9.0 + wobble * 3.0)
        a = int(202 * alpha * (0.30 + 0.70 * t))
        d_ = fd if t < 0.55 else nd
        d_.ellipse([x - wid, y - wid * 0.62, x + wid, y + wid * 0.62], fill=(228, 205, 173, a))
        d_.ellipse([x - wid * .40, y - wid * .38, x + wid * .10, y + wid * .38],
                   fill=(250, 240, 224, int(a * .62)))
    lay = Image.alpha_composite(
        far.filter(ImageFilter.GaussianBlur(w * 0.011)),
        near.filter(ImageFilter.GaussianBlur(w * 0.0075)))
    # impact bloom on the surface
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    rr = w * 0.082 * (0.7 + 0.3 * alpha)
    gd.ellipse([x_hit - rr, y_hit - rr * 0.40, x_hit + rr, y_hit + rr * 0.40],
               fill=(255, 245, 230, int(165 * alpha)))
    # a shallow crater rim where the stream displaces the crema
    gd.ellipse([x_hit - rr * 1.5, y_hit - rr * 0.62, x_hit + rr * 1.5, y_hit + rr * 0.62],
               outline=(120, 80, 48, int(70 * alpha)), width=max(2, int(w * 0.006)))
    g = g.filter(ImageFilter.GaussianBlur(w * 0.030))
    return Image.alpha_composite(lay, g)


def ripples(w, h, liq, amount, phase):
    """Faint concentric light rings spreading from the pour point."""
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if amount <= 0.01:
        return lay
    d = ImageDraw.Draw(lay)
    for i in range(3):
        t = (phase + i / 3.0) % 1.0
        sx = liq["rx"] * (0.18 + 0.82 * t)
        sy = liq["ry"] * (0.18 + 0.82 * t)
        a = int(105 * amount * (1 - t) ** 1.5)
        if a <= 1:
            continue
        d.ellipse([liq["cx"] - sx, liq["cy"] - sy, liq["cx"] + sx, liq["cy"] + sy],
                  outline=(255, 244, 226, a), width=max(2, int(w * 0.004)))
    return lay.filter(ImageFilter.GaussianBlur(w * 0.005))


def vignette(w, h, amount):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / (w - 1) - 0.5) * 2
    ny = (yy / (h - 1) - 0.5) * 2
    r = np.sqrt(nx ** 2 + ny ** 2) / math.sqrt(2)
    return (1.0 - amount * np.clip(r - 0.28, 0, 1) ** 1.6)[..., None]


# ------------------------------------------------------------------ render
def build(base, p):
    """One frame at scroll progress p."""
    W = H = base.shape[1]  # base is a square window already
    liq = LIQ_W

    # --- 1 · crema: swirl during the pour, resolve back into the art
    s = bump(p, 0.34, 0.56, 0.88) ** 0.85
    img = base.copy()
    if s > 0.004:
        pad = 1.06
        bx0 = int(liq["cx"] - liq["rx"] * pad); bx1 = int(liq["cx"] + liq["rx"] * pad)
        by0 = int(liq["cy"] - liq["ry"] * pad); by1 = int(liq["cy"] + liq["ry"] * pad)
        bx0, by0 = max(bx0, 0), max(by0, 0)
        bx1, by1 = min(bx1, W), min(by1, H)
        patch = img[by0:by1, bx0:bx1]
        ph, pw = patch.shape[:2]
        # circularise so the swirl follows the ellipse in perspective
        sq = np.asarray(Image.fromarray(patch.astype(np.uint8)).resize((pw, pw), Image.BILINEAR)).astype(np.float32)
        sw = swirl(sq, s)
        back = np.asarray(Image.fromarray(np.clip(sw, 0, 255).astype(np.uint8)).resize((pw, ph), Image.BILINEAR)).astype(np.float32)
        m = radial_mask((ph, pw), 0.16) * min(1.0, s * 1.6)
        img[by0:by1, bx0:bx1] = patch * (1 - m) + back * m

    frame = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    # --- 2 · focus pull: background softens as the cup resolves
    fp = ramp(p, 0.62, 1.0) * 0.85 + ramp(p, 0.0, 0.2) * 0.15
    if fp > 0.02:
        blurred = frame.filter(ImageFilter.GaussianBlur(W * 0.0085 * fp))
        keep = Image.new("L", (W, H), 0)
        ImageDraw.Draw(keep).ellipse(
            [liq["cx"] - liq["rx"] * 1.5, liq["cy"] - liq["ry"] * 2.3,
             liq["cx"] + liq["rx"] * 1.5, liq["cy"] + liq["ry"] * 3.1], fill=255)
        keep = keep.filter(ImageFilter.GaussianBlur(W * 0.05))
        frame = Image.composite(frame, blurred, keep)

    # --- 3 · beans drift into the foreground bokeh
    ba = bump(p, 0.12, 0.30, 0.52)
    if ba > 0.01:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        # Foreground bokeh only. Beans drawn small and sharp enough to "read"
        # sit on a photograph as smudges, because a real bean on that table
        # would carry its own shading, contact shadow and grain. Out-of-focus
        # foreground shapes are a genuine optical effect, so they composite
        # honestly: large, very soft, and cropped by the frame edge.
        spots = ((0.030, 0.885, 0.235, 38, (52, 31, 20), 0.70),
                 (0.155, 0.985, 0.190, -14, (44, 26, 17), 0.78),
                 (0.965, 0.930, 0.255, -8, (48, 28, 19), 0.72),
                 (0.845, 0.995, 0.170, 52, (40, 24, 15), 0.80))
        for fx, fy, fs, ang, shade, soft in spots:
            b = bean(W * fs, ang, shade, soft)
            op = ba * 0.72
            b.putalpha(b.getchannel("A").point(lambda v: int(v * op)))
            drift = int(W * -0.055 * (1 - ease_out(ramp(p, 0.12, 0.46))))
            lay.alpha_composite(b, (int(fx * W - b.width / 2), int(fy * H - b.height / 2) - drift))
        frame = Image.alpha_composite(frame, lay)

    # --- 4 · the pour and its ripples
    pa = bump(p, 0.30, 0.52, 0.74)
    if pa > 0.01:
        wob = math.sin(p * 26.0) * 0.5
        frame = Image.alpha_composite(frame, pour_layer(W, H, liq, pa, wob))
    ra = bump(p, 0.40, 0.62, 0.92)
    if ra > 0.01:
        frame = Image.alpha_composite(frame, ripples(W, H, liq, ra, (p - 0.40) * 2.6))

    # --- 5 · grade: warm tone, gentle vignette, a touch more bite at the end
    arr = np.asarray(frame.convert("RGB")).astype(np.float32)
    arr *= vignette(W, H, 0.34)
    warm = np.array([1.022, 1.000, 0.972], np.float32)
    arr *= warm
    k = 1.0 + 0.05 * ramp(p, 0.72, 1.0)
    arr = (arr - 128.0) * k + 128.0
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def liquid_in_window(box):
    """Re-express the liquid ellipse in the rendered window's pixel space."""
    k = WIN / (box[2] - box[0])          # the window is square, so one factor
    return dict(cx=(LIQ["cx"] - box[0]) * k, cy=(LIQ["cy"] - box[1]) * k,
                rx=LIQ["rx"] * k, ry=LIQ["ry"] * k)


def window_for(p, src):
    """Camera window: a slow push-in with a small settling drift."""
    scale = 1.0 + PUSH * ease_out(ramp(p, 0.0, 1.0))
    side = WIN / scale
    e = 1 - ease_out(ramp(p, 0.30, 1.0))
    cx = CENTER[0] + DRIFT * -0.55 * e
    cy = CENTER[1] + DRIFT * 0.85 * e
    x0, y0 = cx - side / 2, cy - side / 2
    x0 = clamp(x0, 0, src.width - side); y0 = clamp(y0, 0, src.height - side)
    return (x0, y0, x0 + side, y0 + side)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=56)
    ap.add_argument("--test", action="store_true", help="render six probe frames only")
    a = ap.parse_args()

    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    src = im.crop((round(DECHROME[0] * w), round(DECHROME[1] * h),
                   round(DECHROME[2] * w), round(DECHROME[3] * h)))

    global LIQ_W
    if a.test:
        os.makedirs("/tmp/hero-test", exist_ok=True)
        for i, p in enumerate((0.0, 0.22, 0.40, 0.56, 0.74, 1.0)):
            box = window_for(p, src)
            win = src.resize((WIN, WIN), Image.LANCZOS, box=box)
            LIQ_W = liquid_in_window(box)
            build(np.asarray(win).astype(np.float32), p).resize((760, 760), Image.LANCZOS).save(
                f"/tmp/hero-test/{i}-{p:.2f}.png")
        print("wrote 6 probe frames to /tmp/hero-test")
        return

    for tag, size in SIZES.items():
        d = os.path.join(OUT, tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
    total = 0
    for i in range(a.frames):
        p = i / (a.frames - 1)
        box = window_for(p, src)
        win = src.resize((WIN, WIN), Image.LANCZOS, box=box)
        LIQ_W = liquid_in_window(box)
        arr = np.asarray(win).astype(np.float32)
        full = build(arr, p)                      # render once, then downscale
        for tag, size in SIZES.items():
            f = full.resize((size, size), Image.LANCZOS)
            path = os.path.join(OUT, tag, f"{i:03d}.webp")
            f.save(path, "WEBP", quality=74 if tag == "lg" else 70, method=5)
            total += os.path.getsize(path)
        sys.stdout.write(f"\r  frame {i + 1}/{a.frames}")
        sys.stdout.flush()
    print(f"\nwrote {a.frames} frames x {len(SIZES)} sizes, {total / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
