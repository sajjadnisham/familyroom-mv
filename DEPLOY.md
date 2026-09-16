# Deploying to Cloudflare Pages on familyroom.mv

The repo carries everything needed. What is left are the steps that require your
Cloudflare account and the domain registrar — neither can be automated from here.

> **Read this first.** Pointing `familyroom.mv` at this demo makes an unofficial
> page reachable at the café's own brand name. The demo banner and `noindex` keep
> it from reading or ranking as the real thing, but a domain matching their brand
> is a different situation from a private link: get Family Room Coffee's go-ahead
> before you put it there, and register the domain with the intention of handing
> it to them. If you only need something to show on a phone, the private Claude
> artifact link does that with none of this.

## 1 · Register familyroom.mv

**Cloudflare cannot register `.mv`** — Cloudflare Registrar only handles a fixed
list of TLDs and `.mv` is not on it. You register elsewhere and point DNS at
Cloudflare.

`.mv` is administered by **Dhiraagu** (dhiraagu.com.mv). Two things to confirm with
them directly, because both can stop you:

- **Availability.** Unverified — this session could not resolve DNS or reach the
  registry, and the original audit never checked it either.
- **Eligibility.** `.mv` registration has historically expected a Maldives
  presence or local business registration. If that applies, the café registers it
  (which is the right outcome anyway) and you administer it for them.

If `.mv` turns out to be blocked or slow, `familyroomcoffee.mv` and
`familyroom.coffee` are fallbacks. Note `familyroomcoffee.com` is taken by an
unrelated US bakery — see the name clash in `README.md`.

## 2 · Add the domain to Cloudflare

1. Create a Cloudflare account, then **Add a site** → `familyroom.mv`, Free plan.
2. Cloudflare gives you two nameservers. Set them at Dhiraagu, replacing the
   existing ones.
3. Wait for the zone to go **Active** (usually minutes, up to 24h).

## 3 · Create the Pages project

The repo is private, so pick one:

**Option A — deploy from GitHub Actions (what this repo is set up for).**
No Cloudflare access to your source code.

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Use direct upload**, and name the project exactly `familyroom-mv`
   (`.github/workflows/deploy-pages.yml` passes that name).
2. **My Profile** → **API Tokens** → **Create Token** → Custom token with
   permission **Account · Cloudflare Pages · Edit**.
3. Copy your **Account ID** from the Workers & Pages sidebar.
4. In GitHub: repo → **Settings** → **Secrets and variables** → **Actions**, add
   `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.
5. Push to `main`, or run the workflow manually from the **Actions** tab.

**Option B — Cloudflare's Git integration.** Workers & Pages → Create → Pages →
**Connect to Git**, install the Cloudflare GitHub App on `familyroom-mv`, and set
build command: *(none)*, output directory: `/`. Simpler to click, but it grants
Cloudflare read access to the repo and publishes `README.md`, `DEPLOY.md` and
`seo/` alongside the site. Option A stages only the 24 site files.

## 4 · Attach the domain

1. Pages project → **Custom domains** → **Set up a custom domain** →
   `familyroom.mv`. With the zone in the same account, Cloudflare creates the DNS
   record itself — apex works via CNAME flattening, no A record needed.
2. Add `www.familyroom.mv` too, then a **Redirect Rule** sending `www` → apex
   (301) so the site has one canonical address.
3. TLS is automatic. Turn on **Always Use HTTPS** under SSL/TLS → Edge
   Certificates.

## 5 · When it stops being a demo

Once the café has signed off and supplied real content, in this order:

1. Delete the `.demo-bar` block from all five pages.
2. Remove `<meta name="robots" content="noindex,nofollow">` from all five pages —
   **until you do this, Google will not index the site at all.** That is deliberate
   while it is unofficial, and it is the single easiest thing to forget.
3. Fill in `seo/schema.jsonld` and embed it (see `README.md`).
4. Delete `pitch.html` — it is your internal sales screen, not theirs.
5. Repoint the Google Business Profile website field at `https://familyroom.mv`.

## Notes

- **Caching.** `_headers` keeps HTML revalidating every request and caps assets at
  one hour, because asset filenames are not content-hashed. If you later add
  hashes (`site.abc123.css`), raise `/assets/*` to
  `public, max-age=31536000, immutable`.
- **Clean URLs.** Pages serves `/menu` for `menu.html` and 301s `/menu.html` to
  `/menu`. Internal links deliberately keep the `.html` so the site also works
  over `file://` and `python3 -m http.server`; the cost is one redirect hop.
- **Rollback.** Pages keeps every deployment. Project → Deployments → **Rollback**
  on the previous one.
