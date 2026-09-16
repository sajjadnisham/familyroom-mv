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

## Replacing them

A single shoot solves all three groups at once. The audit asks for: hero 16:9 (4:5 crop for
mobile), food 1:1 or 4:5 shot slightly from above in natural light on the café's own tables,
interiors 3:2, and baristas at work. Drop new files into `assets/photos/` using the existing
names, or add them to `tools/make-photos.py` and re-run it.
