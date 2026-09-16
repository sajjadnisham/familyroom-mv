/* Family Room Coffee — hero: a scroll-driven orbit of the drinks we pour.
 *
 * Five drinks travel a single elliptical path. Scroll position sets the orbit's
 * rotation, so the visitor turns the carousel of the café's collection by
 * scrolling rather than watching it spin. Whichever drink reaches the front of
 * the ellipse is drawn into the middle, scaled up, sharpened and named.
 *
 * Depth is real, not implied: each node's position on the ellipse gives a
 * signed depth, and that one number drives scale, opacity, blur, tilt and
 * stacking order together. Only transforms, opacity and filter are written per
 * frame — no layout properties — and the loop runs solely while the hero is on
 * screen.
 *
 * Every still is a photograph of a drink the café actually serves. There is no
 * espresso, americano, mocha or iced coffee here because no photograph of
 * those was supplied; see tools/make-drinks.py.
 */
(function () {
  'use strict';

  var DRINKS = [
    { slug: 'cappuccino',    name: 'Cappuccino',
      desc: 'Rich espresso under a deep cap of velvety foam.',            steam: 1.00 },
    { slug: 'jasmine',       name: 'Oriental Jasmine',
      desc: 'Loose-leaf jasmine green tea, light and floral.',            steam: 0.80 },
    { slug: 'flat-white',    name: 'Flat White',
      desc: 'House roast under a thin, glossy layer of steamed milk.',    steam: 0.95 },
    { slug: 'fruits-eden',   name: 'Fruits of Eden',
      desc: 'Hibiscus and dried fruit, steeped deep red.',                steam: 0.75 },
    { slug: 'single-origin', name: 'Single Origin',
      desc: 'Kagunyu, Kenya — berries, citrus and plum, roasted locally.', steam: 0.00 }
  ];

  var N = DRINKS.length;
  var TAU = Math.PI * 2;

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  function init() {
    var root = document.querySelector('[data-orb]');
    if (!root) return;
    var track = root.querySelector('.orb-track');
    var scene = root.querySelector('[data-orb-scene]');
    var steamCv = root.querySelector('.orb-steam');
    var nameEl = root.querySelector('[data-orb-name]');
    var descEl = root.querySelector('[data-orb-desc]');
    var dots = [].slice.call(root.querySelectorAll('.orb-dot'));
    if (!track || !scene) return;

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* Build the nodes. */
    var nodes = DRINKS.map(function (d, i) {
      var el = document.createElement('div');
      el.className = 'orb-node';
      el.setAttribute('data-slug', d.slug);
      var im = document.createElement('img');
      im.src = 'assets/drinks/' + d.slug + '.webp';
      im.width = 760; im.height = 760;
      im.alt = d.name + ' at Family Room Coffee';
      im.loading = i === 0 ? 'eager' : 'lazy';
      if (i === 0) im.setAttribute('fetchpriority', 'high');
      el.appendChild(im);
      scene.appendChild(el);
      return el;
    });

    /* Geometry, recomputed on resize only. */
    var A = 0, B = 0, base = 0, FEAT = 2.35;

    /* The sticky stage sticks below the site header, but before it sticks it
       already begins below the demo notice *and* the header. Sizing it against
       the larger of the two offsets is the only value that fits in both
       states: exactly the viewport at rest, and a little short once stuck. */
    function stageHeight() {
      var bar = document.querySelector('.demo-bar');
      var head = document.querySelector('.site-head');
      var off = (bar ? bar.offsetHeight : 0) + (head ? head.offsetHeight : 0);
      root.style.setProperty('--orb-h', (window.innerHeight - off) + 'px');
    }

    function measure() {
      stageHeight();
      var r = scene.getBoundingClientRect();
      base = Math.round(Math.min(r.height * 0.36, r.width * 0.22));
      // Keep the widest satellite inside the scene, so the page never scrolls
      // sideways however narrow the viewport gets.
      var maxHalf = base * 0.5 * 0.95;
      A = Math.min(r.width * 0.36, r.width / 2 - maxHalf - 6);
      B = r.height * 0.255;
      nodes.forEach(function (el) { el.style.width = el.style.height = base + 'px'; });
      if (steamCv) {
        var s = steamCv.getBoundingClientRect();
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        steamCv.width = Math.max(1, Math.round(s.width * dpr));
        steamCv.height = Math.max(1, Math.round(s.height * dpr));
      }
    }

    var featured = -1;

    /* Restart the entrance animation by class, not by timer, so scrolling fast
       through several drinks cannot leave the text mid-fade. */
    function swap(el, text) {
      if (!el) return;
      el.classList.remove('is-in');
      void el.offsetWidth;          // once per drink change, not per frame
      el.textContent = text;
      el.classList.add('is-in');
    }

    function layout(p) {
      // Node i is dead-centre at p = i/(N-1), so the first is featured at the
      // top of the hero and the last as the hero ends.
      var rot = p * TAU * (N - 1) / N;
      var best = 0, bestW = -1;

      for (var i = 0; i < N; i++) {
        var th = (i / N) * TAU - rot;
        var d = Math.cos(th);                 // +1 nearest the viewer, -1 far
        var f = (d + 1) / 2;                  // 0..1 front-ness
        // A bell at the front of the ellipse. Wide enough that the hand-over
        // overlaps -- the outgoing drink is still being released as the next is
        // drawn in -- but not so wide that two read as featured at once.
        var w = Math.pow(Math.max(0, d), 4);
        var rf = 1 - 0.84 * w;                // drawn in toward the middle
        var x = A * Math.sin(th) * rf;
        var y = B * d * rf;
        var sc = (0.64 + 0.31 * f) * (1 + (FEAT - 1) * w);
        var op = clamp(0.34 + 0.54 * f + 0.20 * w, 0, 1);
        var bl = 5.5 * (1 - f) * (1 - w);
        var tz = -7 * Math.sin(th) * (1 - w);

        var el = nodes[i];
        el.style.transform = 'translate3d(' + x.toFixed(2) + 'px,' + y.toFixed(2) +
          'px,0) rotate(' + tz.toFixed(2) + 'deg) scale(' + sc.toFixed(4) + ')';
        el.style.opacity = op.toFixed(3);
        el.style.filter = bl > 0.15 ? 'blur(' + bl.toFixed(2) + 'px)' : 'none';
        el.style.zIndex = String(50 + Math.round(d * 40) + Math.round(w * 60));
        el.classList.toggle('is-featured', w > 0.5);

        if (w > bestW) { bestW = w; best = i; }
      }

      if (best !== featured) {
        featured = best;
        var d2 = DRINKS[best];
        swap(nameEl, d2.name);
        swap(descEl, d2.desc);
        dots.forEach(function (el, j) { el.classList.toggle('is-on', j === best); });
        root.style.setProperty('--orb-steam', String(d2.steam));
      }
      return bestW;
    }

    /* Steam over the featured cup. Continues while the page is still: it is the
       one movement not driven by scroll. */
    var puffs = [];
    for (var i = 0; i < 14; i++) {
      puffs.push({ t: Math.random(), sp: 0.15 + Math.random() * 0.18,
                   x: 0.34 + Math.random() * 0.32, r: 0.05 + Math.random() * 0.07,
                   ph: Math.random() * TAU, sw: 0.5 + Math.random() });
    }
    function drawSteam(time, strength) {
      if (!steamCv) return;
      var ctx = steamCv.getContext('2d');
      var w = steamCv.width, h = steamCv.height;
      ctx.clearRect(0, 0, w, h);
      if (strength <= 0.01) return;
      for (var i = 0; i < puffs.length; i++) {
        var q = puffs[i];
        var t = reduce ? (0.28 + (i % 5) * 0.15) : (q.t + time * q.sp) % 1;
        var y = h * (0.92 - t * 0.9);
        var x = w * q.x + Math.sin(t * 3.0 + q.ph) * w * 0.05 * q.sw;
        var rad = w * q.r * (0.5 + t * 1.2);
        var a = strength * 0.2 * Math.sin(Math.PI * clamp(t, 0, 1)) * (reduce ? 0.6 : 1);
        if (a <= 0.002) continue;
        var g = ctx.createRadialGradient(x, y, 0, x, y, rad);
        g.addColorStop(0, 'rgba(255,248,238,' + a.toFixed(3) + ')');
        g.addColorStop(1, 'rgba(255,248,238,0)');
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(x, y, rad, 0, TAU); ctx.fill();
      }
    }

    function targetP() {
      var r = track.getBoundingClientRect();
      var span = r.height - window.innerHeight;
      return span > 0 ? clamp(-r.top / span, 0, 1) : 0;
    }

    if (reduce) {
      // No scroll linkage at all: the first drink is featured, the rest sit
      // where CSS puts them, and the steam is painted once.
      measure();
      layout(0);
      drawSteam(0, DRINKS[0].steam);
      window.addEventListener('resize', function () { measure(); layout(0); });
      return;
    }

    var cur = 0, tgt = 0, visible = true, running = false, t0 = performance.now();

    function frame(now) {
      var dt = Math.min((now - t0) / 1000, 0.05); t0 = now;
      // Frame-rate independent approach, so a 120Hz screen and a 60Hz screen
      // travel at the same speed and the orbit never snaps.
      cur += (tgt - cur) * (1 - Math.pow(0.0018, dt));
      var w = layout(cur);
      var strength = (DRINKS[featured] ? DRINKS[featured].steam : 0) * clamp(w * 1.6, 0, 1);
      drawSteam(now / 1000, strength);
      if (visible) requestAnimationFrame(frame);
      else running = false;
    }
    function start() { if (!running && visible) { running = true; t0 = performance.now(); requestAnimationFrame(frame); } }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        visible = es[0].isIntersecting;
        if (visible) start();
      }, { rootMargin: '140px' }).observe(root);
    }
    window.addEventListener('scroll', function () { tgt = targetP(); start(); }, { passive: true });
    window.addEventListener('resize', function () { measure(); tgt = targetP(); start(); });

    measure();
    tgt = cur = targetP();
    layout(cur);
    start();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
