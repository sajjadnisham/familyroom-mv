#!/usr/bin/env python3
"""Generates the site's illustration set into assets/img/.

These are drawn vector illustrations, NOT photographs. They exist so the demo
looks designed without reusing the cafe's or its guests' copyrighted photos.
Swap them for real photography once the cafe supplies images it owns.

Run:  python3 tools/make-art.py
"""
import os, xml.dom.minidom, glob

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")
os.makedirs(OUT, exist_ok=True)

# Brand tokens, mirrored from assets/css/site.css
ESPRESSO, LAGOON, CREMA, SAND = "#2B1F1A", "#1C7C7A", "#E8D9C6", "#FAF7F2"
TERRA, DRIFT = "#D9785B", "#6E625A"
MILK, ROAST, ROAST_D = "#F6EDE2", "#8A4726", "#5C2F19"
GREEN, GOLD, SALMON = "#7C9A58", "#D9A94E", "#E2856B"


def svg(w, h, body, label, bg=CREMA):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{label}">\n'
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>\n{body}</svg>\n'
    )


def sun(cx, cy, r, fill, op=1.0):
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" opacity="{op}"/>\n'


def steam(x, y, scale=1.0, colour=ESPRESSO, op=0.28):
    """Three rising wisps."""
    out = ""
    for i, dx in enumerate((-26, 0, 26)):
        h = 46 + (i % 2) * 16
        out += (
            f'  <path d="M{x + dx * scale} {y} c -9 -{13 * scale} 9 -{18 * scale} 0 -{h * scale}" '
            f'fill="none" stroke="{colour}" stroke-width="{5 * scale:.1f}" stroke-linecap="round" opacity="{op}"/>\n'
        )
    return out


def saucer(cx, y, rw, fill=MILK, shade="#E4D6C6"):
    return (
        f'  <ellipse cx="{cx}" cy="{y + 8}" rx="{rw}" ry="{rw * 0.17}" fill="{shade}"/>\n'
        f'  <ellipse cx="{cx}" cy="{y}" rx="{rw}" ry="{rw * 0.17}" fill="{fill}"/>\n'
    )


# ---------------------------------------------------------------- drink cups
def cup(w, h, liquid, label, bg, iced=False, tall=False, handle=True, art=None, topping=None,
        demitasse=False):
    cx, base = w / 2, h * 0.74
    rw = w * (0.155 if demitasse else 0.20 if tall else 0.25)
    ch = h * (0.20 if demitasse else 0.40 if tall else 0.28)
    top = base - ch
    body = ""
    body += sun(cx, h * 0.36, w * 0.30, "#FFFFFF", 0.22)
    body += saucer(cx, base + ch * 0.10, rw * 1.52)
    if handle:
        body += (
            f'  <path d="M{cx + rw - 4} {top + ch * 0.32} c {rw * 0.75} -6 {rw * 0.8} {ch * 0.62} 0 {ch * 0.52}" '
            f'fill="none" stroke="{MILK}" stroke-width="{w * 0.045:.1f}" stroke-linecap="round"/>\n'
        )
    # tapered cup wall
    body += (
        f'  <path d="M{cx - rw} {top} L{cx + rw} {top} L{cx + rw * 0.78} {base} '
        f'Q{cx} {base + ch * 0.16} {cx - rw * 0.78} {base} Z" fill="{MILK}"/>\n'
    )
    # liquid surface
    body += f'  <ellipse cx="{cx}" cy="{top + 6}" rx="{rw - 5}" ry="{(rw - 5) * 0.26}" fill="{liquid}"/>\n'
    if iced:
        u = rw * 0.42
        for dx, dy, sc, rot in ((-0.42, 0.10, 1.0, -14), (0.34, 0.04, 1.15, 9),
                                (-0.08, 0.34, 0.9, 22), (0.46, 0.44, 0.78, -6)):
            sz = u * sc
            body += (
                f'  <rect x="{cx + rw * dx - sz / 2}" y="{top + ch * dy}" width="{sz}" height="{sz}" rx="{sz * 0.22}" '
                f'fill="#EAF6F5" opacity="0.82" stroke="#FFFFFF" stroke-width="2" '
                f'transform="rotate({rot} {cx + rw * dx} {top + ch * dy + sz / 2})"/>\n'
            )
    if demitasse:
        body += f'  <ellipse cx="{cx}" cy="{top + 6}" rx="{rw - 9}" ry="{(rw - 9) * 0.26}" fill="#C08A52"/>\n'
        body += f'  <ellipse cx="{cx}" cy="{top + 6}" rx="{(rw - 9) * 0.55}" ry="{(rw - 9) * 0.15}" fill="#8A5A30"/>\n'
    if art == "rosetta":
        body += f'  <ellipse cx="{cx}" cy="{top + 6}" rx="{(rw - 5) * 0.56}" ry="{(rw - 5) * 0.15}" fill="{MILK}" opacity="0.95"/>\n'
        for i in range(5):
            yy = top + 1 + i * 3.6
            ww = (rw - 9) * (0.50 - i * 0.075)
            body += f'  <ellipse cx="{cx}" cy="{yy}" rx="{ww}" ry="{ww * 0.30}" fill="{MILK}" opacity="0.9"/>\n'
        body += f'  <path d="M{cx} {top - 2} L{cx} {top + 16}" stroke="{ROAST}" stroke-width="2" opacity="0.5"/>\n'
    if topping == "orange":
        body += f'  <circle cx="{cx + rw * 0.42}" cy="{top + 2}" r="{rw * 0.30}" fill="{GOLD}"/>\n'
        body += f'  <circle cx="{cx + rw * 0.42}" cy="{top + 2}" r="{rw * 0.30}" fill="none" stroke="#B9812F" stroke-width="2"/>\n'
        for a in range(6):
            import math
            ang = a * math.pi / 3
            body += (f'  <path d="M{cx + rw * 0.42} {top + 2} l{math.cos(ang) * rw * 0.26:.1f} '
                     f'{math.sin(ang) * rw * 0.26:.1f}" stroke="#B9812F" stroke-width="1.4" opacity="0.7"/>\n')
    if not iced:
        body += steam(cx, top - 14, w / 340)
    return svg(w, h, body, label, bg)


# ---------------------------------------------------------------- food plates
def plate(w, h, label, bg, inner):
    cx, cy = w / 2, h * 0.56
    r = w * 0.27
    body = sun(cx, h * 0.34, w * 0.30, "#FFFFFF", 0.22)
    body += f'  <ellipse cx="{cx}" cy="{cy + 10}" rx="{r * 1.1}" ry="{r * 0.36}" fill="#E4D6C6"/>\n'
    body += f'  <ellipse cx="{cx}" cy="{cy}" rx="{r * 1.1}" ry="{r * 0.36}" fill="{MILK}"/>\n'
    body += f'  <ellipse cx="{cx}" cy="{cy}" rx="{r * 0.82}" ry="{r * 0.27}" fill="#EFE4D6"/>\n'
    body += inner(cx, cy, r)
    return svg(w, h, body, label, bg)


def _toast(cx, cy, r):
    out = (f'  <rect x="{cx - r * 0.62}" y="{cy - r * 0.42}" width="{r * 1.24}" height="{r * 0.46}" rx="7" fill="#D7A866"/>\n'
           f'  <rect x="{cx - r * 0.56}" y="{cy - r * 0.46}" width="{r * 1.12}" height="{r * 0.40}" rx="6" fill="{GREEN}"/>\n')
    for dx, dy in ((-0.34, -0.30), (-0.05, -0.34), (0.26, -0.29)):
        out += f'  <ellipse cx="{cx + r * dx}" cy="{cy + r * dy}" rx="{r * 0.16}" ry="{r * 0.10}" fill="#8FAE68"/>\n'
    out += (f'  <circle cx="{cx + r * 0.30}" cy="{cy - r * 0.14}" r="{r * 0.20}" fill="#FBF3E4"/>\n'
            f'  <circle cx="{cx + r * 0.30}" cy="{cy - r * 0.14}" r="{r * 0.10}" fill="{GOLD}"/>\n')
    return out


def _sandwich(cx, cy, r):
    out = ""
    for i, (fill, dy) in enumerate(((("#D7A866"), 0.02), (("#FBF3E4"), -0.10), ((GREEN), -0.17), (("#D7A866"), -0.30))):
        out += (f'  <rect x="{cx - r * 0.60}" y="{cy + r * dy}" width="{r * 1.20}" height="{r * 0.17}" '
                f'rx="6" fill="{fill}"/>\n')
    out += f'  <path d="M{cx - r * 0.60} {cy + r * 0.02} l{r * 1.20} 0" stroke="#C0954F" stroke-width="2" opacity="0.5"/>\n'
    return out


def _burger(cx, cy, r):
    return (
        f'  <path d="M{cx - r * 0.58} {cy - r * 0.16} a {r * 0.58} {r * 0.46} 0 0 1 {r * 1.16} 0 Z" fill="#D79A53"/>\n'
        f'  <rect x="{cx - r * 0.58}" y="{cy - r * 0.16}" width="{r * 1.16}" height="{r * 0.11}" rx="4" fill="{GREEN}"/>\n'
        f'  <rect x="{cx - r * 0.60}" y="{cy - r * 0.05}" width="{r * 1.20}" height="{r * 0.16}" rx="6" fill="{ROAST_D}"/>\n'
        f'  <rect x="{cx - r * 0.56}" y="{cy + r * 0.11}" width="{r * 1.12}" height="{r * 0.09}" rx="4" fill="{GOLD}"/>\n'
        f'  <path d="M{cx - r * 0.56} {cy + r * 0.20} a {r * 0.56} {r * 0.30} 0 0 0 {r * 1.12} 0 Z" fill="#C98C46"/>\n'
        + "".join(f'  <circle cx="{cx + r * dx}" cy="{cy - r * 0.42}" r="2.6" fill="#FBF3E4"/>\n'
                  for dx in (-0.28, -0.08, 0.14, 0.32))
    )


def _cake(cx, cy, r):
    """A wedge seen from the side: biscuit base, filling, glaze, berry."""
    w_, top_, bot_ = r * 0.72, cy - r * 0.62, cy + r * 0.12
    return (
        f'  <path d="M{cx - w_} {bot_} L{cx + w_} {bot_} L{cx + w_ * 0.62} {top_} L{cx - w_ * 0.62} {top_} Z" '
        f'fill="#FBF0DC"/>\n'
        f'  <path d="M{cx - w_ * 0.62} {top_} L{cx + w_ * 0.62} {top_} L{cx + w_ * 0.66} {top_ + r * 0.13} '
        f'L{cx - w_ * 0.66} {top_ + r * 0.13} Z" fill="#F6E3C4"/>\n'
        f'  <path d="M{cx - w_ * 0.66} {top_ + r * 0.13} q {w_ * 0.5} {r * 0.10} {w_ * 1.32} 0 '
        f'l0 {r * 0.07} q -{w_ * 0.82} {r * 0.10} -{w_ * 1.32} 0 Z" fill="{TERRA}" opacity="0.75"/>\n'
        f'  <path d="M{cx - w_} {bot_} L{cx + w_} {bot_} L{cx + w_ * 0.90} {bot_ - r * 0.17} '
        f'L{cx - w_ * 0.90} {bot_ - r * 0.17} Z" fill="#C79A63"/>\n'
        f'  <circle cx="{cx + w_ * 0.20}" cy="{top_ - r * 0.09}" r="{r * 0.11}" fill="{TERRA}"/>\n'
        f'  <path d="M{cx + w_ * 0.20} {top_ - r * 0.19} q {r * 0.08} -{r * 0.07} {r * 0.14} -{r * 0.02}" '
        f'fill="none" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/>\n'
    )


# ---------------------------------------------------------------- scenes
def scene(w, h, label, body, bg):
    return svg(w, h, body, label, bg)


def scene_terrace(w, h):
    hz = h * 0.52
    b = f'  <rect width="{w}" height="{hz}" fill="#BFE3E0"/>\n'
    b += sun(w * 0.76, hz * 0.34, w * 0.09, "#FFE2B8")
    b += f'  <rect y="{hz}" width="{w}" height="{h * 0.14}" fill="{LAGOON}"/>\n'
    for i in range(4):
        yy = hz + 8 + i * 13
        b += (f'  <path d="M0 {yy} q {w * 0.12} -7 {w * 0.25} 0 t {w * 0.25} 0 t {w * 0.25} 0 t {w * 0.25} 0" '
              f'fill="none" stroke="#FFFFFF" stroke-width="2.5" opacity="{0.45 - i * 0.08:.2f}"/>\n')
    b += f'  <rect y="{h * 0.66}" width="{w}" height="{h * 0.34}" fill="#EFE0CB"/>\n'
    # table + two chairs + cup
    tx, ty = w * 0.34, h * 0.78
    b += f'  <ellipse cx="{tx}" cy="{ty}" rx="{w * 0.17}" ry="{w * 0.055}" fill="{MILK}"/>\n'
    b += f'  <rect x="{tx - 4}" y="{ty}" width="8" height="{h * 0.13}" fill="{ROAST}"/>\n'
    b += f'  <ellipse cx="{tx}" cy="{ty + h * 0.13}" rx="{w * 0.06}" ry="{w * 0.018}" fill="{ROAST_D}"/>\n'
    for sx in (tx - w * 0.23, tx + w * 0.23):
        b += (f'  <rect x="{sx - w * 0.045}" y="{ty - h * 0.02}" width="{w * 0.09}" height="{h * 0.05}" rx="5" fill="{ROAST}"/>\n'
              f'  <rect x="{sx - w * 0.045}" y="{ty - h * 0.14}" width="{w * 0.09}" height="{h * 0.12}" rx="6" fill="{ROAST_D}"/>\n')
    b += f'  <rect x="{tx - 10}" y="{ty - 16}" width="20" height="15" rx="3" fill="{MILK}"/>\n'
    b += f'  <ellipse cx="{tx}" cy="{ty - 16}" rx="10" ry="3" fill="{ROAST_D}"/>\n'
    b += steam(tx, ty - 26, 0.34)
    # parasol
    px = w * 0.76
    b += f'  <path d="M{px - w * 0.14} {h * 0.62} a {w * 0.14} {w * 0.10} 0 0 1 {w * 0.28} 0 Z" fill="{TERRA}"/>\n'
    b += f'  <rect x="{px - 3}" y="{h * 0.62}" width="6" height="{h * 0.26}" fill="{ROAST}"/>\n'
    return scene(w, h, "Illustration: the terrace by the sea", b, "#BFE3E0")


def scene_interior(w, h):
    b = f'  <rect width="{w}" height="{h}" fill="#F0E2CE"/>\n'
    b += f'  <rect y="{h * 0.72}" width="{w}" height="{h * 0.28}" fill="#DFCDB4"/>\n'
    # window
    b += (f'  <rect x="{w * 0.06}" y="{h * 0.14}" width="{w * 0.30}" height="{h * 0.36}" rx="8" fill="#BFE3E0" '
          f'stroke="{MILK}" stroke-width="7"/>\n'
          f'  <path d="M{w * 0.21} {h * 0.14} L{w * 0.21} {h * 0.50}" stroke="{MILK}" stroke-width="6"/>\n')
    # shelf with books
    b += f'  <rect x="{w * 0.56}" y="{h * 0.22}" width="{w * 0.36}" height="9" rx="4" fill="{ROAST}"/>\n'
    for i, c in enumerate((TERRA, LAGOON, GOLD, ROAST_D, GREEN, TERRA)):
        b += (f'  <rect x="{w * 0.58 + i * w * 0.055}" y="{h * 0.22 - h * 0.11}" width="{w * 0.040}" '
              f'height="{h * 0.11}" rx="2" fill="{c}"/>\n')
    # banquette + table
    b += f'  <rect x="{w * 0.08}" y="{h * 0.56}" width="{w * 0.34}" height="{h * 0.20}" rx="10" fill="{ROAST}"/>\n'
    b += f'  <rect x="{w * 0.08}" y="{h * 0.52}" width="{w * 0.34}" height="{h * 0.08}" rx="8" fill="{ROAST_D}"/>\n'
    b += f'  <rect x="{w * 0.50}" y="{h * 0.60}" width="{w * 0.34}" height="10" rx="5" fill="{MILK}"/>\n'
    b += f'  <rect x="{w * 0.65}" y="{h * 0.60}" width="8" height="{h * 0.16}" fill="{ROAST_D}"/>\n'
    b += f'  <rect x="{w * 0.56}" y="{h * 0.545}" width="22" height="16" rx="3" fill="{MILK}"/>\n'
    b += f'  <ellipse cx="{w * 0.56 + 11}" cy="{h * 0.545}" rx="11" ry="3.4" fill="{ROAST_D}"/>\n'
    b += f'  <rect x="{w * 0.72}" y="{h * 0.565}" width="30" height="7" rx="2" fill="{GOLD}"/>\n'
    # pendant lamps
    for lx in (w * 0.48, w * 0.70):
        b += (f'  <path d="M{lx} 0 L{lx} {h * 0.14}" stroke="{ESPRESSO}" stroke-width="2.5"/>\n'
              f'  <path d="M{lx - 22} {h * 0.20} a 22 22 0 0 1 44 0 Z" fill="{ESPRESSO}"/>\n'
              f'  <ellipse cx="{lx}" cy="{h * 0.205}" rx="13" ry="4" fill="{GOLD}"/>\n')
    return scene(w, h, "Illustration: inside the room", b, "#F0E2CE")


def scene_barista(w, h):
    b = f'  <rect width="{w}" height="{h}" fill="#E7D6C0"/>\n'
    b += f'  <rect y="{h * 0.70}" width="{w}" height="{h * 0.30}" fill="{ROAST}"/>\n'
    b += f'  <rect y="{h * 0.66}" width="{w}" height="{h * 0.06}" fill="#3C2A20"/>\n'
    # machine
    mx = w * 0.56
    b += f'  <rect x="{mx}" y="{h * 0.30}" width="{w * 0.36}" height="{h * 0.36}" rx="10" fill="#9AA3A6"/>\n'
    b += f'  <rect x="{mx + w * 0.03}" y="{h * 0.34}" width="{w * 0.30}" height="{h * 0.10}" rx="6" fill="#6E787C"/>\n'
    for i in range(3):
        b += f'  <circle cx="{mx + w * 0.07 + i * w * 0.10}" cy="{h * 0.39}" r="{w * 0.022}" fill="{CREMA}"/>\n'
    b += f'  <rect x="{mx + w * 0.10}" y="{h * 0.50}" width="{w * 0.09}" height="{h * 0.05}" rx="4" fill="#5C666A"/>\n'
    b += f'  <rect x="{mx + w * 0.125}" y="{h * 0.55}" width="{w * 0.04}" height="{h * 0.06}" rx="3" fill="{MILK}"/>\n'
    for i in range(2):
        b += (f'  <path d="M{mx + w * 0.135 + i * 7} {h * 0.61} L{mx + w * 0.135 + i * 7} {h * 0.645}" '
              f'stroke="{ROAST_D}" stroke-width="2.4" opacity="0.8"/>\n')
    # barista
    px = w * 0.28
    b += f'  <circle cx="{px}" cy="{h * 0.30}" r="{w * 0.072}" fill="#C98F63"/>\n'
    b += f'  <path d="M{px - w * 0.075} {h * 0.275} a {w * 0.075} {w * 0.062} 0 0 1 {w * 0.15} 0 Z" fill="{ESPRESSO}"/>\n'
    b += (f'  <path d="M{px - w * 0.11} {h * 0.70} L{px - w * 0.085} {h * 0.40} '
          f'Q{px} {h * 0.355} {px + w * 0.085} {h * 0.40} L{px + w * 0.11} {h * 0.70} Z" fill="{LAGOON}"/>\n')
    b += f'  <path d="M{px + w * 0.07} {h * 0.44} Q{px + w * 0.20} {h * 0.50} {mx + w * 0.10} {h * 0.55}" fill="none" stroke="#C98F63" stroke-width="{w * 0.035}" stroke-linecap="round"/>\n'
    b += f'  <rect x="{px - w * 0.065}" y="{h * 0.52}" width="{w * 0.13}" height="{h * 0.18}" rx="4" fill="{MILK}" opacity="0.85"/>\n'
    return scene(w, h, "Illustration: a barista at the machine", b, "#E7D6C0")


def scene_shelf(w, h):
    b = f'  <rect width="{w}" height="{h}" fill="#EFE1CC"/>\n'
    rows = 3
    for r in range(rows):
        sy = h * (0.26 + r * 0.24)
        b += f'  <rect x="{w * 0.10}" y="{sy}" width="{w * 0.80}" height="9" rx="4" fill="{ROAST}"/>\n'
        cols = (TERRA, LAGOON, GOLD, ROAST_D, GREEN, TERRA, LAGOON)
        x = w * 0.13
        for i in range(6):
            bw = w * (0.035 + (i % 3) * 0.012)
            bh = h * (0.14 + (i % 2) * 0.03)
            b += f'  <rect x="{x}" y="{sy - bh}" width="{bw}" height="{bh}" rx="2" fill="{cols[(i + r) % 7]}"/>\n'
            x += bw + w * 0.012
        if r == 1:  # a board game box leaning at the end
            b += (f'  <rect x="{x + w * 0.02}" y="{sy - h * 0.10}" width="{w * 0.16}" height="{h * 0.10}" rx="3" '
                  f'fill="{MILK}" stroke="{ROAST_D}" stroke-width="2"/>\n')
            for i in range(9):
                b += (f'  <rect x="{x + w * 0.035 + (i % 3) * w * 0.035}" y="{sy - h * 0.085 + (i // 3) * h * 0.026}" '
                      f'width="{w * 0.024}" height="{h * 0.018}" rx="1.5" fill="{TERRA if i % 2 else LAGOON}"/>\n')
    return scene(w, h, "Illustration: books and board games", b, "#EFE1CC")


def scene_roastery(w, h):
    b = f'  <rect width="{w}" height="{h}" fill="#E2CDB4"/>\n'
    b += f'  <rect y="{h * 0.74}" width="{w}" height="{h * 0.26}" fill="{ROAST_D}"/>\n'
    cx, cy = w * 0.44, h * 0.44
    b += f'  <rect x="{cx - w * 0.19}" y="{cy - h * 0.20}" width="{w * 0.38}" height="{h * 0.40}" rx="16" fill="#8E9599"/>\n'
    b += f'  <circle cx="{cx}" cy="{cy}" r="{h * 0.145}" fill="#5C666A"/>\n'
    b += f'  <circle cx="{cx}" cy="{cy}" r="{h * 0.105}" fill="{ROAST_D}"/>\n'
    for a, dx, dy in ((0, -0.03, -0.02), (1, 0.04, 0.01), (2, -0.01, 0.05), (3, 0.02, -0.06)):
        b += f'  <ellipse cx="{cx + w * dx}" cy="{cy + h * dy}" rx="{w * 0.018}" ry="{w * 0.013}" fill="{ROAST}"/>\n'
    b += f'  <path d="M{cx + w * 0.19} {cy - h * 0.10} l{w * 0.10} 0 l0 {h * 0.22} l{w * 0.07} 0" fill="none" stroke="#6E787C" stroke-width="9"/>\n'
    b += f'  <rect x="{cx - w * 0.26}" y="{cy - h * 0.30}" width="{w * 0.13}" height="{h * 0.16}" rx="6" fill="#6E787C"/>\n'
    for i in range(3):
        b += f'  <circle cx="{cx - w * 0.235 + i * w * 0.035}" cy="{cy - h * 0.22}" r="{w * 0.011}" fill="{TERRA}"/>\n'
    # sacks of beans
    for sx, s in ((w * 0.78, 1.0), (w * 0.90, 0.78)):
        b += (f'  <path d="M{sx - 26 * s} {h * 0.74} q 0 -{40 * s} {26 * s} -{44 * s} q {26 * s} 4 {26 * s} {44 * s} Z" '
              f'fill="#C9B18E"/>\n'
              f'  <ellipse cx="{sx}" cy="{h * 0.74 - 44 * s}" rx="{16 * s}" ry="{5 * s}" fill="{ROAST}"/>\n')
    b += steam(cx, cy - h * 0.34, 0.5, ESPRESSO, 0.18)
    return scene(w, h, "Illustration: the micro-roastery", b, "#E2CDB4")


def scene_brewbar(w, h):
    b = f'  <rect width="{w}" height="{h}" fill="#DCE9E6"/>\n'
    b += f'  <rect y="{h * 0.72}" width="{w}" height="{h * 0.28}" fill="{ROAST}"/>\n'
    b += f'  <rect y="{h * 0.70}" width="{w}" height="{h * 0.04}" fill="#3C2A20"/>\n'
    # V60 cone + carafe
    cx = w * 0.36
    b += (f'  <path d="M{cx - w * 0.10} {h * 0.34} L{cx + w * 0.10} {h * 0.34} L{cx + w * 0.022} {h * 0.50} '
          f'L{cx - w * 0.022} {h * 0.50} Z" fill="{LAGOON}"/>\n')
    b += f'  <ellipse cx="{cx}" cy="{h * 0.34}" rx="{w * 0.10}" ry="{w * 0.026}" fill="#166663"/>\n'
    b += f'  <ellipse cx="{cx}" cy="{h * 0.345}" rx="{w * 0.082}" ry="{w * 0.020}" fill="{ROAST_D}"/>\n'
    b += (f'  <path d="M{cx - w * 0.075} {h * 0.52} L{cx + w * 0.075} {h * 0.52} L{cx + w * 0.062} {h * 0.70} '
          f'L{cx - w * 0.062} {h * 0.70} Z" fill="{MILK}" opacity="0.92"/>\n')
    b += f'  <rect x="{cx - w * 0.070}" y="{h * 0.60}" width="{w * 0.140}" height="{h * 0.10}" fill="{ROAST}" opacity="0.85"/>\n'
    b += f'  <path d="M{cx} {h * 0.50} L{cx} {h * 0.60}" stroke="{ROAST_D}" stroke-width="2.5" opacity="0.7"/>\n'
    # gooseneck kettle
    kx = w * 0.68
    b += f'  <path d="M{kx - w * 0.075} {h * 0.70} L{kx - w * 0.065} {h * 0.46} L{kx + w * 0.065} {h * 0.46} L{kx + w * 0.075} {h * 0.70} Z" fill="#8E9599"/>\n'
    b += f'  <ellipse cx="{kx}" cy="{h * 0.46}" rx="{w * 0.065}" ry="{w * 0.018}" fill="#6E787C"/>\n'
    b += (f'  <path d="M{kx - w * 0.065} {h * 0.52} q -{w * 0.11} -{h * 0.02} -{w * 0.115} -{h * 0.16}" '
          f'fill="none" stroke="#8E9599" stroke-width="7" stroke-linecap="round"/>\n')
    b += f'  <path d="M{kx + w * 0.070} {h * 0.50} q {w * 0.06} {h * 0.06} 0 {h * 0.12}" fill="none" stroke="#6E787C" stroke-width="7" stroke-linecap="round"/>\n'
    # scale
    b += f'  <rect x="{w * 0.12}" y="{h * 0.655}" width="{w * 0.13}" height="{h * 0.045}" rx="5" fill="{ESPRESSO}"/>\n'
    b += f'  <rect x="{w * 0.155}" y="{h * 0.668}" width="{w * 0.06}" height="{h * 0.020}" rx="2" fill="{LAGOON}"/>\n'
    b += steam(cx, h * 0.28, 0.55, ESPRESSO, 0.2)
    return scene(w, h, "Illustration: the brew bar", b, "#DCE9E6")


def scene_breakfast(w, h):
    b = f'  <rect width="{w}" height="{h}" fill="#F2E4CE"/>\n'
    b += f'  <rect y="{h * 0.62}" width="{w}" height="{h * 0.38}" fill="#D9C3A4"/>\n'
    b += f'  <ellipse cx="{w * 0.42}" cy="{h * 0.56}" rx="{w * 0.30}" ry="{w * 0.105}" fill="#E4D6C6"/>\n'
    b += f'  <ellipse cx="{w * 0.42}" cy="{h * 0.54}" rx="{w * 0.30}" ry="{w * 0.105}" fill="{MILK}"/>\n'
    b += _toast(w * 0.42, h * 0.52, w * 0.30)
    b += f'  <ellipse cx="{w * 0.80}" cy="{h * 0.44}" rx="{w * 0.12}" ry="{w * 0.042}" fill="{MILK}"/>\n'
    b += f'  <rect x="{w * 0.755}" y="{h * 0.33}" width="{w * 0.09}" height="{h * 0.11}" rx="4" fill="{MILK}"/>\n'
    b += f'  <ellipse cx="{w * 0.80}" cy="{h * 0.33}" rx="{w * 0.045}" ry="{w * 0.014}" fill="{ROAST_D}"/>\n'
    b += steam(w * 0.80, h * 0.29, 0.30)
    b += f'  <rect x="{w * 0.12}" y="{h * 0.40}" width="{w * 0.05}" height="{h * 0.16}" rx="3" fill="#F6D98E"/>\n'
    b += f'  <ellipse cx="{w * 0.145}" cy="{h * 0.40}" rx="{w * 0.025}" ry="{w * 0.009}" fill="#E9C46A"/>\n'
    return scene(w, h, "Illustration: a breakfast plate", b, "#F2E4CE")


def hero_scene(w, h):
    """Wide beach-terrace scene used behind the hero."""
    hz = h * 0.56
    b = f'  <rect width="{w}" height="{hz}" fill="#4E3A2E"/>\n'
    b += (f'  <defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="#3A2A22"/><stop offset="1" stop-color="#9C5F36"/></linearGradient>'
          f'<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="#1E6F6C"/><stop offset="1" stop-color="#12504E"/></linearGradient></defs>\n')
    b += f'  <rect width="{w}" height="{hz}" fill="url(#sky)"/>\n'
    b += sun(w * 0.70, hz * 0.70, w * 0.085, "#F7C789", 0.95)
    b += sun(w * 0.70, hz * 0.70, w * 0.135, "#F0B073", 0.16)
    b += f'  <rect y="{hz}" width="{w}" height="{h - hz}" fill="url(#sea)"/>\n'
    for i in range(7):
        yy = hz + 10 + i * 26
        b += (f'  <path d="M0 {yy} q {w * 0.09} -9 {w * 0.18} 0 t {w * 0.18} 0 t {w * 0.18} 0 t {w * 0.18} 0 '
              f't {w * 0.18} 0 t {w * 0.18} 0" fill="none" stroke="#7FC2BD" stroke-width="3" '
              f'opacity="{0.34 - i * 0.04:.2f}"/>\n')
    b += f'  <ellipse cx="{w * 0.70}" cy="{hz + 6}" rx="{w * 0.05}" ry="{h * 0.14}" fill="#F0B073" opacity="0.28"/>\n'
    # silhouetted railing and two chairs, foreground left
    # Terrace deck, railing and two chair silhouettes in the foreground.
    b += f'  <rect y="{h * 0.88}" width="{w}" height="{h * 0.12}" fill="#241A15"/>\n'
    b += f'  <rect y="{h * 0.855}" width="{w}" height="{h * 0.03}" fill="#2F221B"/>\n'
    b += f'  <rect x="0" y="{h * 0.775}" width="{w}" height="6" fill="#241A15" opacity="0.95"/>\n'
    for i in range(14):
        b += f'  <rect x="{w * 0.02 + i * w * 0.072}" y="{h * 0.775}" width="5" height="{h * 0.085}" fill="#241A15" opacity="0.95"/>\n'
    for cxx, sc in ((w * 0.13, 1.0), (w * 0.30, 0.92)):
        b += (f'  <rect x="{cxx - 46 * sc}" y="{h * 0.80}" width="{92 * sc}" height="{9 * sc}" rx="4" fill="#241A15"/>\n'
              f'  <rect x="{cxx - 46 * sc}" y="{h * 0.70}" width="{12 * sc}" height="{h * 0.10}" rx="4" fill="#241A15"/>\n'
              f'  <rect x="{cxx - 46 * sc}" y="{h * 0.695}" width="{92 * sc}" height="{10 * sc}" rx="5" fill="#241A15"/>\n')
    b += f'  <ellipse cx="{w * 0.215}" cy="{h * 0.795}" rx="{w * 0.035}" ry="{w * 0.011}" fill="#241A15"/>\n'
    b += f'  <rect x="{w * 0.213}" y="{h * 0.795}" width="5" height="{h * 0.06}" fill="#241A15"/>\n'
    return svg(w, h, b, "Illustration: the beach terrace at golden hour", "#3A2A22")


# ---------------------------------------------------------------- build
BUILD = {
    "hero-terrace":      lambda: hero_scene(1600, 900),
    "counter-espresso":  lambda: cup(800, 600, ROAST_D, "Illustration: an espresso", "#EADBC6", demitasse=True),
    "counter-filter":    lambda: cup(800, 600, "#7A4526", "Illustration: hand-brewed filter coffee", "#E7DCC9", handle=False, tall=True),
    "counter-avocado":   lambda: plate(800, 600, "Illustration: avocado toast with eggs", "#E6E3CE", _toast),
    "counter-chicken":   lambda: plate(800, 600, "Illustration: a grilled chicken sandwich", "#EEE0C8", _sandwich),
    "counter-burger":    lambda: plate(800, 600, "Illustration: a beef burger", "#EDDCC4", _burger),
    "counter-cheesecake":lambda: plate(800, 600, "Illustration: a slice of cheesecake", "#F0E4D2", _cake),
    "room-terrace":      lambda: scene_terrace(800, 800),
    "room-interior":     lambda: scene_interior(800, 800),
    "room-latteart":     lambda: cup(800, 800, ROAST_D, "Illustration: latte art", "#E9DAC5", art="rosetta"),
    "room-breakfast":    lambda: scene_breakfast(800, 800),
    "room-barista":      lambda: scene_barista(800, 800),
    "room-bookshelf":    lambda: scene_shelf(800, 800),
    "story-roastery":    lambda: scene_roastery(1200, 800),
    "story-brewbar":     lambda: scene_brewbar(1200, 800),
    # signature drinks, also used as standalone illustrations
    "drink-orangepresso":lambda: cup(600, 600, "#8A3F16", "Illustration: Orangepresso", "#F2E0C4", topping="orange", tall=True, handle=False),
    "drink-flatwhite":   lambda: cup(600, 600, "#A97449", "Illustration: flat white", "#EADBC6", art="rosetta"),
    "drink-filter":      lambda: cup(600, 600, "#7A4526", "Illustration: hand-brewed filter", "#E7DCC9", handle=False, tall=True),
    "drink-icedmocha":   lambda: cup(600, 600, "#6B3B22", "Illustration: iced mocha", "#DFE9E4", iced=True, handle=False, tall=True),
    "drink-espresso":    lambda: cup(600, 600, ROAST_D, "Illustration: espresso", "#EADBC6", demitasse=True),
}

for name, fn in BUILD.items():
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(fn())

for p in sorted(glob.glob(os.path.join(OUT, "*.svg"))):
    xml.dom.minidom.parse(p)          # malformed XML fails silently in browsers
print(f"wrote {len(BUILD)} illustrations; all {len(glob.glob(os.path.join(OUT, '*.svg')))} svg files parse")

# NOTE: real client photography now fills every slot these illustrations used to
# occupy, so assets/img/*.svg is currently unreferenced except favicon.svg. The
# set is kept on purpose: IMAGE-CREDITS.md flags several photos as needing the
# photographer's permission, and if any of those are refused, the matching
# illustration is the drop-in replacement. Delete this file and assets/img/ once
# every photo is cleared.
