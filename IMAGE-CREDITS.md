# Image credits and clearance status

Every photograph on the site came from the client as a phone screenshot. Each was cropped to
remove the status bar, app chrome and, where present, Google's "Images may be subject to
copyright" banner. Sources live outside the repo; `tools/make-photos.py` holds the crop box and
focus point for each, and regenerates `assets/photos/` on demand.

**Read this before launch.** Three groups below have different rights positions. Only the first is
safe to publish as-is.

## 🟢 The café's own material

Their own promotional artwork and product shots. Safe to use with the café's sign-off.

| Image | Used for | Source |
| --- | --- | --- |
| `logo-source.webp`, `logo*.webp`, `favicon*` | Header, footer, hero mark, favicon set | The client's own circular sign artwork, supplied directly — not a placeholder, and the only asset here with no rights question at all. `tools/make-logo.py` regenerates every derived size from it. |
| `beans-*` | Homepage hero, Our Coffee, beans menu item | Family Room Coffee retail packaging |
| `beef-burger-*` | Homepage card, menu | Product shot |
| `lamb-chops-*` | Homepage card, menu | Seaside Grill / Family Room story, 22 Dec 2020 |
| `chicken-burger-*` | Homepage card, menu | Seaside Grill / Family Room story, 18 Dec 2020 |
| `bolognese-*` | Gallery, menu | Seaside Grill promo card, 21 Mar 2020 |
| `thai-curry-*` | Gallery, menu | Seaside Grill promo card, 21 Mar 2020 |
| `chicken-wings-*` | Gallery, menu | Seaside Grill promo card, 21 Mar 2020 |
| `avocado-toast-*` | Homepage card, menu | @familyroomcoffee.mv post, 15 Dec 2020 |

Note: the Seaside Grill cards carry a "Served & Delivered by The Family Room" credit line. That is
why those dishes are now on the menu — see the note on `menu.html`.

## 🟡 Guest photos — permission needed

Taken by customers. The café does not own these, so **get written permission from each
photographer, or reshoot the dish**, before the site goes public.

| Image | Used for | Credited to |
| --- | --- | --- |
| `latte-blue-*` | Homepage card, Our Coffee, menu | @nishaaarl — reshared by the café 14 Sep 2020, which is a good sign but not a licence |
| `latte-donut-*` | Homepage card, gallery, menu | "Raya Ss", Google Maps |
| `chicken-rice-*` | Menu | "Hussain Shareef", Google Maps |
| `room-*` | Gallery | "Raya Ss", Google Maps |

`room-*` is cropped to exclude the customers visible in the background of the original. Keep it
that way, or get their consent.

## 🔴 Third-party brand material

| Image | Used for | Source |
| --- | --- | --- |
| `tea-jasmine-*` | Menu | Tea Drop supplier marketing image |
| `tea-fruits-*` | Menu | Tea Drop supplier marketing image |

Tea Drop is a tea supplier, not the café. These are cropped for composition, which drops their
logo from frame — so do not present them as the café's own. Stockists are often licensed to use
supplier images, but **confirm that with Tea Drop or the café**, and confirm the café still serves
these blends.

## The hero orbit

`assets/drinks/` holds five stills for the hero. Three (`cappuccino`, `jasmine`, `fruits-eden`) are
cut from photographs supplied directly for the hero, committed at `assets/drinks/sources/`; the
other two are cropped from photographs already listed above.

| Still | From | Rights group |
| --- | --- | --- |
| `cappuccino` | `sources/cappuccino-src.webp` | 🟡 supplied for this purpose; provenance not stated |
| `flat-white` | `latte-blue` | 🟡 guest photo |
| `jasmine` | `sources/jasmine-src.webp` | 🟡 supplied for this purpose; provenance not stated |
| `fruits-eden` | `sources/fruits-eden-src.webp` | 🟡 supplied for this purpose; provenance not stated |
| `single-origin` | `beans` | 🟢 café's own |

So **four of the five drinks in the hero still need clearance before launch**. The three supplied
directly for the hero read as professional studio photography — clean isolation, matched lighting,
no visible branding — which usually means either a paid shoot or stock/supplier imagery, but
nothing said which, so treat the rights as unconfirmed rather than assume either way. That is the
strongest argument for the shoot below: the hero is the first thing anyone sees.

The orbit has no espresso, americano, mocha or iced coffee because no photograph of those was
supplied. Each needs one photograph of the drink with the cup fully in frame (any aspect ratio —
`tools/make-drinks.py` cuts the cup out and trims to its own silhouette, not a fixed crop),
ideally on the café's own cups under the same light as the rest; drop it in with a crop box and it
joins the orbit.

## Replacing them

A single shoot solves all three groups at once. The audit asks for: hero 16:9 (4:5 crop for
mobile), food 1:1 or 4:5 shot slightly from above in natural light on the café's own tables,
interiors 3:2, and baristas at work. Drop new files into `assets/photos/` using the existing
names, or add them to `tools/make-photos.py` and re-run it.
