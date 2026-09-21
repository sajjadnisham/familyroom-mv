# Family Room Coffee — website concept demo

A six-page demo website for **Family Room Coffee**, a beachfront specialty-coffee café in
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
| `index.html` | Homepage — hero, live "today" strip, a one-row taste of the menu, reasons to return, gallery, ratings, visit block, final CTA |
| `menu.html` | Sample menu with sticky category tabs; doubles as the in-store QR menu |
| `combos.html` | Six coffee-and-food pairings suggested from the real menu, at an illustrative combo price |
| `our-coffee.html` | The Coffee Lab roaster story, brew methods, the people, the living-room idea |
| `visit.html` | Hours (incl. the Friday prayer break), an embedded map, contact, and the FAQ that answers the review complaints |
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

**Regenerating images needs Python packages the site itself does not.** `tools/make-drinks.py`
segments each drink with `rembg` (`pip install rembg onnxruntime scipy pillow numpy`); the u2net
weights (176 MB) download once on first run and cache in `~/.rembg`. `tools/make-photos.py`,
`tools/make-logo.py` and `tools/make-art.py` need only Pillow and numpy. None of this touches the
deployed site, which is static files with zero dependencies.

## How it is built

```
index.html  menu.html  combos.html  our-coffee.html  visit.html  pitch.html
assets/css/site.css     one stylesheet, design tokens on :root
assets/js/hero.js       the scroll-driven orbit: four beats, depth and steam
assets/js/site.js       open-now logic, nav toggle, menu tab tracking
assets/drinks/*.webp    5 cut-out drink stills for the hero orbit
tools/make-drinks.py    segments, grades and regenerates them
assets/photos/*.jpg     30 renditions of the 15 client-supplied photographs
tools/make-photos.py    crops and regenerates them from the originals
tools/make-hero-frames.py  superseded brew-sequence hero, kept to regenerate
assets/img/logo*.webp   the client's own sign artwork, trimmed
assets/img/favicon*.png, favicon.ico, apple-touch-icon.png  the sign's emblem, baked down
tools/make-logo.py      regenerates the logo and favicon set from the source art
assets/img/*.svg        20 vector illustrations, kept as a rights fallback
tools/make-art.py       regenerates the illustration set
IMAGE-CREDITS.md        per-image provenance and clearance status
seo/schema.jsonld       CafeOrCoffeeShop schema, not yet embedded (see below)
_headers                Cloudflare Pages caching and security headers
DEPLOY.md               Cloudflare Pages + familyroom.mv runbook
.github/workflows/      deploy to GitHub Pages and to Cloudflare Pages on push to main
```

**Design tokens** are a restrained coffee palette — Espresso `#2B1F1A`, Sand `#FAF7F2`,
Crema `#E8D9C6`, Brass `#7A4F1E` (buttons and links, 7.08:1 on white), Terracotta `#D9785B` (the
open-now dot and tags only), Driftwood `#6E625A`. The teal accent an earlier pass used was the
only colour on the page that had nothing to do with coffee, and it has been replaced. Type is
Cormorant Garamond for headings — an editorial serif, set large — and Inter for body and prices,
with tabular numerals on prices. **The palette is still a proposal, not sampled from the café's
brand** — the header mark and favicon now use the client's real sign artwork
(`assets/img/logo-source.webp`), but the page colours were not drawn from it; sample the real
colours from the sign's brass ring and swap the `--espresso` / primary slot first.

**The logo is the client's own**, not a placeholder initial. `tools/make-logo.py` trims the full
disc for the header, footer and hero mark, and separately crops just the emblem — house, lamp,
cup, burger, palm, sunset — clear of the sign's brass ring and its three lines of small type, which
does not survive down to a 16px favicon. That emblem, composited onto a solid espresso backing,
is the favicon and apple-touch-icon set. The header mark is sized up from the 36px text badge it
replaced and carries a warm ring so it reads on both the pale header and the hero's dark field.

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

**The hero is a scroll-driven orbit of the drinks the café pours, cut out rather than framed.**
Five drinks travel one elliptical path; scroll position sets the orbit's rotation, so the visitor
turns it rather than watching it spin. Whichever drink reaches the front is drawn into the middle,
scaled up, sharpened and named. Each still is the drink's own silhouette -- no disc, no circular
mask, no vignette -- so the cup reads as floating in the hero's dark field rather than a photo in
a window.

**The scroll is choreographed in four beats, not linear**, because a constant rotation reads as a
machine rather than an experience:

| beat | scroll | what happens |
| --- | --- | --- |
| Still | 0.00–0.13 | one cup, centred, alone. Only the steam moves. |
| Wake | 0.11–0.26 | the rest of the collection emerges from the dark, nearest first, as the headline eases back. |
| Orbit | 0.26–0.90 | the collection turns. Rotation is eased *per segment*, so each drink dwells at the centre and the travel between them accelerates and settles. |
| Hand off | 0.90–1.00 | the satellites recede and dim, the featured cup settles, and the scene releases into the page. |

The per-segment easing is the part that matters: the path is divided into one segment per
hand-over and each is run through a quintic ease, which produces a rest at every drink instead of
a conveyor belt. `--orb-p`, `--orb-intro`, `--orb-read` and `--orb-out` are written to the hero
element each frame, so CSS — not JavaScript — decides what the copy, the read-out and the hairline
do with each beat.

The depth is real rather than implied. Each node's position on the ellipse gives a signed depth,
and that single number drives scale, opacity, blur, tilt and stacking order together — front
drinks are larger, sharper and brighter; back drinks are smaller, softer and dimmer. The featured
bell is deliberately wide enough that hand-overs overlap: the outgoing drink is still being
released as the next is drawn in, so it reads as an orbital pass rather than a slide change.

`assets/js/hero.js` writes only transforms, opacity and filter per frame — never layout. Scroll
sets a target and a frame-rate-independent lerp walks the rendered value toward it, so a 120 Hz
and a 60 Hz screen travel at the same speed. **Every motion in the scene, including the steam,
flows only while the visitor is scrolling.** The steam's own phase only advances while the orbit
is still easing toward its target; the instant it settles, steam and orbit both hold still, and
the rAF loop stops rather than idling on a wall clock -- it wakes again on the next scroll event.
Steam is weighted per drink, so the bag of beans does not steam. The rAF loop otherwise runs only
while the hero intersects the viewport.

**Only drinks that were actually photographed appear.** There is no espresso, americano, mocha or
iced coffee in the orbit, because no photograph of those was supplied — and darkening the
cappuccino to stand in for them would put fabricated menu items in front of the café. Two real
photographs would add each one; see `tools/make-drinks.py`.

The stills are 5 × ~52 KB. `tools/make-drinks.py` segments each photograph locally with
`rembg`/u2net -- no hosted background-removal API, no account, run entirely on this machine's CPU
-- keeps only the largest connected blob (so a stray fleck of reflection or text does not survive
as its own island), feathers the edge by a couple of pixels, and trims the result to the cutout's
own bounding box, so the exported image's aspect ratio is the cup's, not the square the source
photo happened to be cropped to. It also applies one restrained grade across the set, on the RGB
channels only: the photographs are of bright ceramic — teal, cobalt, red — on orange wood, and at
full saturation five of them floating together read as a colour wheel rather than a coffee bar, so
the saturation comes down to 0.66 and what is left is tilted warm. A CSS `drop-shadow` (not baked
into the image) grounds each cup in the scene.

**The hero does not end at a section boundary.** A `.bridge` section carries the scene's dark
field down through a gradient into the page's sand, and holds the "Our coffee" heading inside the
dark part — the dissolve is deliberately held back until the copy has finished, and lands on the
today strip's own colour, so there is no seam and no warm-grey text on a warm-grey background. The
navigation floats transparently over that whole dark run (the scene's field is carried up behind
the header by `.orb::before`, so the nav reads as sitting *inside* the hero) and only turns solid
when the pale page actually reaches it — not on a scroll threshold, which fires far too early.

Under `prefers-reduced-motion` the track collapses to normal flow, the nodes lay out as a static
line-up with the first drink featured and the other four smaller beside it, the steam is hidden,
and the rAF loop never starts. The scroll-linked custom properties are neutralised there, and
`hero.js` skips its inline node sizing so CSS can set that line-up.

**Photography is client-supplied, and its rights are not uniform.** Every photo came from the
client as a phone screenshot; `tools/make-photos.py` holds the crop box and focus point for each
and regenerates `assets/photos/`. Some are the café's own promotional artwork, some are guest
photos from Google Maps, and two are a tea supplier's marketing images — **read
[`IMAGE-CREDITS.md`](IMAGE-CREDITS.md) before publishing**, because the guest photos need the
photographer's permission.

**The illustration set is kept as a fallback.** `tools/make-art.py` generates 20 vector
illustrations in `assets/img/`, now fully unreferenced (the favicon moved to the real logo). If
any photo's rights don't clear, the matching illustration drops straight in. Delete both once
every photo is cleared.

**The homepage's menu preview is a taste, not a second copy of the menu.** Six round thumbnails in
one row — image, name, price, nothing else — link out to `menu.html` for the description and the
rest of the list. It replaced a two-row, six-card grid with full photos and copy, at roughly 40%
of that grid's height; the level of counter detail belongs on the menu page, not repeated on the
homepage.

**The map is a real embed, not a link-out card.** `#visit` and `visit.html` both carry a
`<iframe>` onto `?q=...&output=embed` — no API key needed, since it searches the café by name
rather than pinning an address. A link-out card was the right call inside the sandboxed Claude
artifact preview, which blocks framed content; on the actual deployed site there is no such
restriction, and a link-out under-delivers what a map section is for. The "Open in Google Maps ↗"
link stays underneath for turning the search into directions.

**Combos are a suggestion, not a menu item.** `combos.html` pairs six real drinks with six real
dishes already on the menu, at an illustrative combined price a little under ordering both apart.
The page says plainly that the pairing and the discount are this page's proposal, not something
the café currently offers.

**Prices are illustrative, and labelled as such.** No real price was available. They are anchored
to the single figure in the audit — a Nov 2019 review paid MVR 163 for pancakes, avocado toast and
two donuts, implying roughly MVR 60/63/20 each — scaled about 1.7× for 2026 so the demo reads
plausibly. The café replaces every number before launch.

**Every unverified claim is tagged** in the markup with `<span class="tag tag-tbc">`, so the gaps
are visible in the demo instead of hidden. Items only evidenced in 2019 or earlier are marked as
possibly discontinued.

## Before this becomes a live site

The audit lists four blockers, all of which need the café's input. The logo is now the real one
(the client supplied it); brand *colours* are still a proposal, not sampled from it:

1. **Brand colours** — the demo's palette is a proposal; the logo itself is now the client's own.
2. **Current menu and prices** — every price on the site is an illustrative sample, combos
   included.
3. **Hours, WhatsApp number and the exact map pin** — hours come from Tripadvisor only, and two
   different addresses circulate (Lot 20018 Beach Road / Phase 2 vs 10033 Nirolhu Magu).
4. **Photo rights and sign-off on claims** — the Coffee Lab wording, halal, vegan and award
   claims, and naming anyone personally.

Then, in the code:

- Remove the `.demo-bar` banner and the `<meta name="robots" content="noindex,nofollow">` on all
  six pages.
- Fill in `seo/schema.jsonld` (every `CONFIRM` value) and embed it as
  `<script type="application/ld+json">` on each page.
- Clear or replace every photo marked 🟡 or 🔴 in [`IMAGE-CREDITS.md`](IMAGE-CREDITS.md). One
  shoot covers all of them: hero 16:9 (4:5 crop on mobile), food 1:1 or 4:5, interiors 3:2.
- Replace every sample price with the café's real menu, and drop the "sample" labels.
- Verify the three bean origins on `our-coffee.html` — the names, producers, varietals and
  altitudes were transcribed from a photograph of the bags.
- Swap the two placeholder quote cards on the homepage for owner-approved quotes, credited.
- Swap the `?q=...` search embed on `index.html` and `visit.html` for a pinned one
  (`?q=<lat>,<lng>` or a Place ID) once the café confirms which of the two addresses is real —
  right now it searches the café by name, which is why it does not need either address to work
  today.
- Add the WhatsApp click-to-chat link where the Visit page currently says "not published".

Two off-site wins worth doing at the same time: repoint the Google Business Profile's website
field (it currently sends people to a retired Facebook page), and start replying to reviews —
Tripadvisor shows no owner replies at all.

Note the name clash: `familyroomcoffee.com` and `@familyroomcoffee` belong to an unrelated US
business. Page titles and the domain need "Maldives" or "Hulhumalé" in them, which is why every
`<title>` here does.
