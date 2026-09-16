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
assets/js/site.js       open-now logic, nav toggle, menu tab tracking
assets/img/*.svg        15 generated placeholders, each labelled on the image itself
seo/schema.jsonld       CafeOrCoffeeShop schema, not yet embedded (see below)
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

**Every unverified claim is tagged** in the markup with `<span class="tag tag-tbc">`, so the gaps
are visible in the demo instead of hidden. Prices read `MVR —`. Items only evidenced in 2019 or
earlier are marked as possibly discontinued.

## Before this becomes a live site

The audit lists four blockers, all of which need the café's input:

1. **Logo and brand colours** — the demo's palette is a proposal.
2. **Current menu and prices** — the only price found online was a single 2019 figure.
3. **Hours, WhatsApp number and the exact map pin** — hours come from Tripadvisor only, and two
   different addresses circulate (Lot 20018 Beach Road / Phase 2 vs 10033 Nirolhu Magu).
4. **Photo rights and sign-off on claims** — the Coffee Lab wording, halal, vegan and award
   claims, and naming anyone personally.

Then, in the code:

- Remove the `.demo-bar` banner and the `<meta name="robots" content="noindex,nofollow">` on all
  five pages.
- Fill in `seo/schema.jsonld` (every `CONFIRM` value) and embed it as
  `<script type="application/ld+json">` on each page.
- Replace `assets/img/*.svg` with café-owned photography: hero 16:9 (4:5 crop on mobile), food
  1:1 or 4:5, interiors 3:2. Guest photos on Instagram and Tripadvisor belong to the guests.
- Swap the two placeholder quote cards on the homepage for owner-approved quotes, credited.
- Point the map embed at the confirmed pin, and add the WhatsApp click-to-chat link where the
  Visit page currently says "not published".

Two off-site wins worth doing at the same time: repoint the Google Business Profile's website
field (it currently sends people to a retired Facebook page), and start replying to reviews —
Tripadvisor shows no owner replies at all.

Note the name clash: `familyroomcoffee.com` and `@familyroomcoffee` belong to an unrelated US
business. Page titles and the domain need "Maldives" or "Hulhumalé" in them, which is why every
`<title>` here does.
