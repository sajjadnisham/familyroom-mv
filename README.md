# Family Room Coffee — website concept demo

A four-page demo website for **Family Room Coffee**, a beachfront specialty-coffee café in
Hulhumalé, Maldives. Built from the *Family Room Coffee website opportunity audit*, which
concluded: **build the demo prototype, not the production site yet.** This repository is that
prototype.

> **This is an unofficial design proposal.** It is not affiliated with, commissioned by, or
> endorsed by Family Room Coffee or Coffee Lab Maldives. Every page says so in a banner at the
> top. All imagery is a labelled placeholder, and menu, prices, hours and policies are drawn from
> public listings and reviews rather than from the café.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Homepage — hero, live "today" strip, counter highlights, reasons to return, gallery, ratings, visit block, final CTA |
| `menu.html` | Sample menu with sticky category tabs; doubles as the in-store QR menu |
| `our-coffee.html` | The Coffee Lab roaster story, brew methods, the people, the living-room idea |
| `visit.html` | Hours (incl. the Friday prayer break), map, contact, and the FAQ that answers the review complaints |
| `pitch.html` | Not part of the café's site — the sales screen comparing today's Google result with one that has a website |

Hosting: `.github/workflows/pages.yml` publishes to **GitHub Pages** — needs Settings → Pages →
Source → "GitHub Actions", and a public repo unless the account has GitHub Pro.
`.github/workflows/deploy-pages.yml` publishes to **Cloudflare Pages** instead;
[`DEPLOY.md`](DEPLOY.md) covers that route and `familyroom.mv`, including the `noindex` removal
step that has to happen before the site can ever be indexed.

## Running it

Static HTML, CSS and vanilla JS. No build step and no dependencies.

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Open `index.html` directly in a browser if you prefer; only the Google Maps embed and the
Google Fonts stylesheet need a network connection.

## How it is built

```
index.html  menu.html  our-coffee.html  visit.html  pitch.html
assets/css/site.css     one stylesheet, design tokens on :root
assets/js/hero.js       hero frame scrubbing and steam
assets/js/site.js       open-now logic, nav toggle, menu tab tracking
assets/drinks/*.webp    5 drink stills for the hero orbit
tools/make-drinks.py    crops, grades and regenerates them
assets/photos/*.jpg     30 renditions of the 15 client-supplied photographs
tools/make-photos.py    crops and regenerates them from the originals
tools/make-hero-frames.py  superseded brew-sequence hero, kept to regenerate
assets/img/*.svg        20 vector illustrations, kept as a rights fallback
tools/make-art.py       regenerates the illustration set
IMAGE-CREDITS.md        per-image provenance and clearance status
seo/schema.jsonld       CafeOrCoffeeShop schema, not yet embedded (see below)
_headers                Cloudflare Pages caching and security headers
DEPLOY.md               Cloudflare Pages + familyroom.mv runbook
.github/workflows/      deploy to Cloudflare Pages on push to main
```

**Design tokens** follow the audit's proposed palette — Espresso `#2B1F1A`, Sand `#FAF7F2`,
Crema `#E8D9C6`, Lagoon `#1C7C7A` (buttons and links), Terracotta `#D9785B` (the open-now dot and
tags only), Driftwood `#6E625A`. Type is Fraunces for headings and Public Sans for body and
prices, with tabular numerals on prices. **The palette is a proposal, not the café's brand** —
sample the real colours from their logo and swap the `--espresso` / primary slot first.

**The open-now indicator** (`assets/js/site.js`) evaluates hours in Maldives time (UTC+5) so it is
correct for a visitor in any time zone. Hours are stored as minutes from midnight, with an end
past `1440` for the 01:30 close; the check looks at both today's and yesterday's intervals so the
after-midnight session resolves correctly. Friday carries two intervals for the 11:30–13:30 prayer
break. Edit the `HOURS` table in one place to change all of it.

**Mobile** gets a hamburger nav and a sticky Menu · Directions · Call bar. Hover zoom and
scroll-smoothing back off under `prefers-reduced-motion`.

**The hero's vertical fit is measured, not guessed.** The sticky stage sits below the site header
(`top: var(--head)`), and `hero.js` sets its height from the *measured* header-plus-notice height
— the only value that fits both states, since before the stage sticks it already begins below
both. The hero section also has its block padding zeroed, because the generic `section` rule would
otherwise push the track 84px down and make the stage overhang the fold. The orbit's horizontal
radius is clamped against the widest satellite, so the page never scrolls sideways. Verified at
eleven viewports, at rest and while stuck.

**The hero is a scroll-driven orbit of the drinks the café pours.** Five drinks travel one
elliptical path; scroll position sets the orbit's rotation, so the visitor turns it rather than
watching it spin. Whichever drink reaches the front is drawn into the middle, scaled up, sharpened
and named.

The depth is real rather than implied. Each node's position on the ellipse gives a signed depth,
and that single number drives scale, opacity, blur, tilt and stacking order together — front
drinks are larger, sharper and brighter; back drinks are smaller, softer and dimmer. The featured
bell is deliberately wide enough that hand-overs overlap: the outgoing drink is still being
released as the next is drawn in, so it reads as an orbital pass rather than a slide change.

`assets/js/hero.js` writes only transforms, opacity and filter per frame — never layout. Scroll
sets a target and a frame-rate-independent lerp walks the rendered value toward it, so a 120 Hz
and a 60 Hz screen travel at the same speed. Steam is drawn on its own canvas over the featured
cup and keeps drifting while the page is still; it is the one movement not driven by scroll, and
it is weighted per drink, so the bag of beans does not steam. The rAF loop runs only while the
hero intersects the viewport.

**Only drinks that were actually photographed appear.** There is no espresso, americano, mocha or
iced coffee in the orbit, because no photograph of those was supplied — and darkening the
cappuccino to stand in for them would put fabricated menu items in front of the café. Two real
photographs would add each one; see `tools/make-drinks.py`.

The stills are 5 × ~22 KB. `tools/make-drinks.py` bakes a per-drink vignette so every photograph
dissolves into the hero's darkness at the same rate, whatever its own background — the bean bags
were shot against a pale wall and need the most.

Under `prefers-reduced-motion` the track collapses to normal flow, the nodes lay out as a static
line-up with the first drink featured, the steam is hidden, and the rAF loop never starts.

**Photography is client-supplied, and its rights are not uniform.** Every photo came from the
client as a phone screenshot; `tools/make-photos.py` holds the crop box and focus point for each
and regenerates `assets/photos/`. Some are the café's own promotional artwork, some are guest
photos from Google Maps, and two are a tea supplier's marketing images — **read
[`IMAGE-CREDITS.md`](IMAGE-CREDITS.md) before publishing**, because the guest photos need the
photographer's permission.

**The illustration set is kept as a fallback.** `tools/make-art.py` generates 20 vector
illustrations in `assets/img/`, now unreferenced except the favicon. If any photo's rights don't
clear, the matching illustration drops straight in. Delete both once every photo is cleared.

**Prices are illustrative, and labelled as such.** No real price was available. They are anchored
to the single figure in the audit — a Nov 2019 review paid MVR 163 for pancakes, avocado toast and
two donuts, implying roughly MVR 60/63/20 each — scaled about 1.7× for 2026 so the demo reads
plausibly. The café replaces every number before launch.

**Every unverified claim is tagged** in the markup with `<span class="tag tag-tbc">`, so the gaps
are visible in the demo instead of hidden. Items only evidenced in 2019 or earlier are marked as
possibly discontinued.

## Before this becomes a live site

The audit lists four blockers, all of which need the café's input:

1. **Logo and brand colours** — the demo's palette is a proposal.
2. **Current menu and prices** — every price on the site is an illustrative sample.
3. **Hours, WhatsApp number and the exact map pin** — hours come from Tripadvisor only, and two
   different addresses circulate (Lot 20018 Beach Road / Phase 2 vs 10033 Nirolhu Magu).
4. **Photo rights and sign-off on claims** — the Coffee Lab wording, halal, vegan and award
   claims, and naming anyone personally.

Then, in the code:

- Remove the `.demo-bar` banner and the `<meta name="robots" content="noindex,nofollow">` on all
  five pages.
- Fill in `seo/schema.jsonld` (every `CONFIRM` value) and embed it as
  `<script type="application/ld+json">` on each page.
- Clear or replace every photo marked 🟡 or 🔴 in [`IMAGE-CREDITS.md`](IMAGE-CREDITS.md). One
  shoot covers all of them: hero 16:9 (4:5 crop on mobile), food 1:1 or 4:5, interiors 3:2.
- Replace every sample price with the café's real menu, and drop the "sample" labels.
- Verify the three bean origins on `our-coffee.html` — the names, producers, varietals and
  altitudes were transcribed from a photograph of the bags.
- Swap the two placeholder quote cards on the homepage for owner-approved quotes, credited.
- Swap the `.map-card` link-out block on `index.html` and `visit.html` for a real interactive
  embed once the pin is confirmed. It deliberately links out rather than framing Google Maps:
  the address is one of the unconfirmed items above, and sandboxed viewers block third-party
  frames.
- Add the WhatsApp click-to-chat link where the Visit page currently says "not published".

Two off-site wins worth doing at the same time: repoint the Google Business Profile's website
field (it currently sends people to a retired Facebook page), and start replying to reviews —
Tripadvisor shows no owner replies at all.

Note the name clash: `familyroomcoffee.com` and `@familyroomcoffee` belong to an unrelated US
business. Page titles and the domain need "Maldives" or "Hulhumalé" in them, which is why every
`<title>` here does.
