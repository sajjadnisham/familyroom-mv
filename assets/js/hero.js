/* Family Room Coffee — scroll-driven hero.
 *
 * The coffee is a photographic image sequence (see tools/make-hero-frames.py),
 * scrubbed on a canvas by scroll position. Two reasons for a sequence rather
 * than CSS on layered artwork: the frames are derived from a real photograph,
 * so the crema, ceramic and bokeh are genuinely photographic; and drawImage of
 * an already-decoded frame is cheap and steady, where filtering a large image
 * per frame in CSS is not.
 *
 * Scroll sets a target; a spring-ish lerp walks the rendered value toward it,
 * so the brew eases rather than snapping, in both directions. Steam is drawn
 * separately and keeps drifting while the page is still, which is the only
 * motion not tied to scroll. Under prefers-reduced-motion nothing animates:
 * one finished frame is drawn and the loop never starts.
 */
(function () {
  'use strict';

  var FRAMES = 56;
  var SETS = { lg: { dir: 'assets/hero/lg/', size: 1000 }, sm: { dir: 'assets/hero/sm/', size: 560 } };
  var STAGES = [0, 0.22, 0.44, 0.72];

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function smooth(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }

  function init() {
    var root = document.querySelector('[data-hero]');
    if (!root) return;

    var track = root.querySelector('.hx-track');
    var cv = root.querySelector('.hx-canvas');
    var steamCv = root.querySelector('.hx-steam');
    var bar = root.querySelector('[data-hx-bar]');
    var steps = [].slice.call(root.querySelectorAll('.hx-step'));
    if (!track || !cv) return;

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var set = (window.innerWidth < 760 || (window.devicePixelRatio || 1) < 1.5) && window.innerWidth < 1100
      ? SETS.sm : SETS.lg;

    var ctx = cv.getContext('2d', { alpha: false });
    var sctx = steamCv ? steamCv.getContext('2d') : null;
    var imgs = new Array(FRAMES);
    var ready = new Array(FRAMES);
    var readyCount = 0;

    /* ---------------------------------------------------------- sizing */
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      [cv, steamCv].forEach(function (c) {
        if (!c) return;
        var r = c.getBoundingClientRect();
        c.width = Math.max(1, Math.round(r.width * dpr));
        c.height = Math.max(1, Math.round(r.height * dpr));
      });
      draw(shown, true);
    }

    /* --------------------------------------------------------- loading */
    function load(i) {
      return new Promise(function (res) {
        var im = new Image();
        im.decoding = 'async';
        im.onload = function () {
          imgs[i] = im; ready[i] = true; readyCount++;
          if (i === 0) draw(0, true);
          res();
        };
        im.onerror = function () { ready[i] = false; res(); };
        im.src = set.dir + String(i).padStart(3, '0') + '.webp';
      });
    }

    // First frame first so the hero is never blank, then the rest in order at
    // a small concurrency so the network is not flooded on a phone.
    load(0).then(function () {
      var next = 1, inflight = 0, LIMIT = 6;
      (function pump() {
        while (inflight < LIMIT && next < FRAMES) {
          inflight++;
          load(next++).then(function () { inflight--; pump(); });
        }
      })();
    });

    /* ---------------------------------------------------------- drawing */
    var shown = -1;
    function nearestReady(idx) {
      if (ready[idx]) return idx;
      for (var d = 1; d < FRAMES; d++) {
        if (ready[idx - d]) return idx - d;
        if (ready[idx + d]) return idx + d;
      }
      return -1;
    }

    function draw(p, force) {
      var idx = clamp(Math.round(p * (FRAMES - 1)), 0, FRAMES - 1);
      var use = nearestReady(idx);
      if (use < 0) return;
      if (use === shown && !force) return;
      shown = use;
      var im = imgs[use];
      // cover-fit the square frame into the canvas box
      var cw = cv.width, ch = cv.height;
      var s = Math.max(cw / im.width, ch / im.height);
      var w = im.width * s, h = im.height * s;
      ctx.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h);
    }

    /* ------------------------------------------------------------ steam */
    var puffs = [];
    for (var i = 0; i < 16; i++) {
      puffs.push({ t: Math.random(), sp: 0.16 + Math.random() * 0.2, x: 0.30 + Math.random() * 0.42,
                   r: 0.05 + Math.random() * 0.075, ph: Math.random() * 6.283, sw: 0.5 + Math.random() });
    }
    function drawSteam(p, time) {
      if (!sctx) return;
      var w = steamCv.width, h = steamCv.height;
      sctx.clearRect(0, 0, w, h);
      // More visible once the visitor starts scrolling, per the brief.
      var vis = 0.42 + 0.58 * smooth((p - 0.04) / 0.34);
      vis *= 1 - 0.45 * smooth((p - 0.80) / 0.20);   // settles as the cup does
      for (var i = 0; i < puffs.length; i++) {
        var q = puffs[i];
        var t = reduce ? (0.25 + (i % 5) * 0.16) : (q.t + time * q.sp) % 1;
        var y = h * (0.88 - t * 0.86);
        var x = w * q.x + Math.sin(t * 3.1 + q.ph) * w * 0.055 * q.sw;
        var rad = w * q.r * (0.55 + t * 1.15);
        var a = vis * 0.22 * Math.sin(Math.PI * clamp(t, 0, 1)) * (reduce ? 0.7 : 1);
        if (a <= 0.002) continue;
        var g = sctx.createRadialGradient(x, y, 0, x, y, rad);
        g.addColorStop(0, 'rgba(255,248,238,' + a.toFixed(3) + ')');
        g.addColorStop(1, 'rgba(255,248,238,0)');
        sctx.fillStyle = g;
        sctx.beginPath(); sctx.arc(x, y, rad, 0, 6.2832); sctx.fill();
      }
    }

    /* -------------------------------------------------------- progress */
    function targetP() {
      var r = track.getBoundingClientRect();
      var span = r.height - window.innerHeight;
      return span > 0 ? clamp(-r.top / span, 0, 1) : 0;
    }

    function setStage(p) {
      if (bar) bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      var active = 0;
      for (var i = 0; i < STAGES.length; i++) if (p >= STAGES[i]) active = i;
      for (var j = 0; j < steps.length; j++) steps[j].classList.toggle('is-on', j === active);
    }

    if (reduce) {
      // Finished cup, no loop, no scroll listener.
      var wait = setInterval(function () {
        if (readyCount > 0) { clearInterval(wait); resize(); draw(1, true); drawSteam(1, 0); }
      }, 60);
      setStage(1);
      window.addEventListener('resize', resize);
      return;
    }

    var cur = 0, tgt = 0, running = false, visible = true, t0 = performance.now();

    function frame(now) {
      var dt = Math.min((now - t0) / 1000, 0.05); t0 = now;
      // Critically-damped-ish approach: fast enough to track a flick, slow
      // enough that the pour never snaps.
      cur += (tgt - cur) * (1 - Math.pow(0.0015, dt));
      draw(cur);
      drawSteam(cur, now / 1000);
      setStage(cur);
      // The loop continues for as long as the hero is on screen, because the
      // steam drifts even when the page is still. It stops entirely once the
      // hero scrolls away, so no work happens further down the page.
      if (visible) requestAnimationFrame(frame);
      else running = false;
    }
    function start() {
      if (running || !visible) return;
      running = true; t0 = performance.now();
      requestAnimationFrame(frame);
    }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        visible = es[0].isIntersecting;
        if (visible) start();
      }, { rootMargin: '120px' }).observe(root);
    }

    window.addEventListener('scroll', function () { tgt = targetP(); start(); }, { passive: true });
    window.addEventListener('resize', function () { resize(); tgt = targetP(); start(); });

    resize();
    tgt = cur = targetP();
    start();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
