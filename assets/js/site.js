/* Family Room Coffee — concept demo
   Opening hours are from Tripadvisor only and are marked "to be confirmed"
   throughout the demo. Times are evaluated in Maldives time (UTC+5, no DST)
   so the indicator is correct for visitors in any time zone. */

(function () {
  'use strict';

  var MVT_OFFSET_MIN = 5 * 60;

  // Minutes from midnight. An end past 1440 means the day closes after midnight.
  // 0=Sun … 6=Sat. Friday (5) has the prayer break.
  var HOURS = {
    0: [[540, 1530]],            // 09:00 – 01:30
    1: [[540, 1530]],
    2: [[540, 1530]],
    3: [[540, 1530]],
    4: [[540, 1530]],
    5: [[480, 690], [810, 1530]], // 08:00 – 11:30, 13:30 – 01:30
    6: [[540, 1530]]
  };

  var DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function maldivesNow() {
    var now = new Date();
    return new Date(now.getTime() + (now.getTimezoneOffset() + MVT_OFFSET_MIN) * 60000);
  }

  function fmt(mins) {
    var m = ((mins % 1440) + 1440) % 1440;
    var h = Math.floor(m / 60);
    return (h < 10 ? '0' : '') + h + ':' + (m % 60 < 10 ? '0' : '') + (m % 60);
  }

  /* Returns { open, until } where `until` is the closing time when open,
     or the next opening time when closed. Yesterday's late-night session is
     checked by shifting its interval back a day. */
  function state(d) {
    var day = d.getDay();
    var mins = d.getHours() * 60 + d.getMinutes();
    var yday = (day + 6) % 7;
    var i, iv;

    for (i = 0; i < HOURS[yday].length; i++) {
      iv = HOURS[yday][i];
      if (iv[1] > 1440 && mins < iv[1] - 1440) {
        return { open: true, until: fmt(iv[1]) };
      }
    }
    for (i = 0; i < HOURS[day].length; i++) {
      iv = HOURS[day][i];
      if (mins >= iv[0] && mins < iv[1]) {
        return { open: true, until: fmt(iv[1]) };
      }
    }
    for (i = 0; i < HOURS[day].length; i++) {
      if (mins < HOURS[day][i][0]) {
        return { open: false, until: fmt(HOURS[day][i][0]), sameDay: true };
      }
    }
    var next = (day + 1) % 7;
    return { open: false, until: fmt(HOURS[next][0][0]), sameDay: false };
  }

  function renderStatus() {
    var dot = document.querySelector('[data-open-dot]');
    var text = document.querySelector('[data-open-text]');
    if (!dot && !text) return;

    var d = maldivesNow();
    var s = state(d);

    if (dot) {
      dot.classList.toggle('is-open', s.open);
      dot.classList.toggle('is-closed', !s.open);
    }
    if (text) {
      text.textContent = s.open
        ? 'Open now · closes ' + s.until
        : 'Closed · opens ' + s.until + (s.sameDay ? ' today' : ' tomorrow');
      text.setAttribute('title', DAYS[d.getDay()] + ' in Maldives time (UTC+5)');
    }
  }

  function highlightToday() {
    var rows = document.querySelectorAll('.hours tr[data-day]');
    if (!rows.length) return;
    var today = maldivesNow().getDay();
    Array.prototype.forEach.call(rows, function (row) {
      if (Number(row.getAttribute('data-day')) === today) row.classList.add('is-today');
    });
  }

  function navToggle() {
    var btn = document.querySelector('.nav-toggle');
    var nav = document.getElementById('site-nav');
    if (!btn || !nav) return;
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function menuTabs() {
    var tabs = document.querySelectorAll('.menu-tabs a');
    var groups = document.querySelectorAll('.menu-group[id]');
    if (!tabs.length || !groups.length || !('IntersectionObserver' in window)) return;

    var byId = {};
    Array.prototype.forEach.call(tabs, function (t) {
      byId[t.getAttribute('href').slice(1)] = t;
    });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        Array.prototype.forEach.call(tabs, function (t) { t.classList.remove('active'); });
        var tab = byId[entry.target.id];
        if (tab) tab.classList.add('active');
      });
    }, { rootMargin: '-140px 0px -70% 0px' });

    Array.prototype.forEach.call(groups, function (g) { io.observe(g); });
  }

  /* ----------------------------------------------------------------- hero
     Signature-coffee selector. Tabs follow the ARIA tabs pattern: arrow keys
     move between drinks, Home/End jump to the ends, and the cup itself
     advances to the next drink so tapping the artwork does something. */
  var DRINKS = {
    flatwhite:    { name: 'Flat White',         price: '65', note: 'Coffee Lab\u2019s house roast under a thin, glossy layer of steamed milk.' },
    orangepresso: { name: 'Orangepresso',       price: '80', note: 'The house signature: espresso over orange, served long and cold.' },
    filter:       { name: 'Hand-brewed Filter', price: '85', note: 'A single origin, ground and poured to order. Ask what\u2019s on the bar.' },
    icedmocha:    { name: 'Iced Mocha',         price: '80', note: 'Espresso, chocolate and cold milk over ice for the walk back.' }
  };

  function signature() {
    var root = document.querySelector('[data-signature]');
    if (!root) return;
    var tabs = Array.prototype.slice.call(root.querySelectorAll('.sig-tab'));
    var cups = Array.prototype.slice.call(root.querySelectorAll('.sig-cup'));
    var nameEl = root.querySelector('[data-sig-name]');
    var noteEl = root.querySelector('[data-sig-note]');
    var priceEl = root.querySelector('[data-sig-price]');
    if (!tabs.length || !cups.length) return;

    var current = 0;

    function select(i, focus) {
      current = (i + tabs.length) % tabs.length;
      var id = tabs[current].getAttribute('data-tab');
      var d = DRINKS[id];

      tabs.forEach(function (t, n) {
        var on = n === current;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
      });
      cups.forEach(function (c) {
        c.classList.toggle('is-active', c.getAttribute('data-drink') === id);
      });
      if (d) {
        nameEl.textContent = d.name;
        noteEl.textContent = d.note;
        priceEl.innerHTML = 'MVR ' + d.price + ' <span class="tbc">sample</span>';
      }
      if (focus) tabs[current].focus();
    }

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i); });
      t.addEventListener('keydown', function (e) {
        var k = e.key;
        if (k === 'ArrowRight' || k === 'ArrowDown') { e.preventDefault(); select(current + 1, true); }
        else if (k === 'ArrowLeft' || k === 'ArrowUp') { e.preventDefault(); select(current - 1, true); }
        else if (k === 'Home') { e.preventDefault(); select(0, true); }
        else if (k === 'End') { e.preventDefault(); select(tabs.length - 1, true); }
      });
    });

    cups.forEach(function (c) {
      c.addEventListener('click', function () { select(current + 1); });
    });

    select(0);
  }

  /* ------------------------------------------------------------ brewing
     One pour-over, driven by how far the visitor has scrolled through the
     tall track rather than by a timer, so the brew tracks the scrollbar in
     both directions. Under prefers-reduced-motion the track collapses (CSS)
     and we render the finished brew once instead of following scroll. */
  var STAGES = [0, 0.18, 0.40, 0.62, 0.86];

  function lerp(p, a, b) { return p <= a ? 0 : p >= b ? 1 : (p - a) / (b - a); }

  function brewing() {
    var sec = document.querySelector('[data-brew]');
    if (!sec) return;
    var track = sec.querySelector('.brew-track');
    var svg = sec.querySelector('[data-brew-svg]');
    var bar = sec.querySelector('[data-brew-bar]');
    var steps = Array.prototype.slice.call(sec.querySelectorAll('.brew-steps li'));
    if (!track || !svg) return;

    var el = {};
    Array.prototype.forEach.call(svg.querySelectorAll('[data-el]'), function (n) {
      el[n.getAttribute('data-el')] = n;
    });

    var CARAFE_TOP = 296, CARAFE_BOTTOM = 396;

    function render(p) {
      // 1 · grind: beans fall in, then the bed appears
      var grind = lerp(p, 0, 0.16);
      el.beans.setAttribute('opacity', String(Math.max(0, 1 - lerp(p, 0.10, 0.20))));
      el.beans.setAttribute('transform', 'translate(0 ' + (grind * 110).toFixed(1) + ')');
      el.bed.setAttribute('opacity', String(lerp(p, 0.10, 0.20)));

      // 2 · bloom: kettle tips, first water hits, bed swells and gasses off
      var pourOn = lerp(p, 0.18, 0.26) - lerp(p, 0.66, 0.74);
      el.kettle.setAttribute('transform', 'rotate(' + (-15 * Math.max(0, pourOn)).toFixed(1) + ' 186 46)');
      el.stream.setAttribute('opacity', String(Math.max(0, pourOn)));
      var bloom = lerp(p, 0.20, 0.34) - lerp(p, 0.42, 0.56);
      el.bubbles.setAttribute('opacity', String(Math.max(0, bloom) * 0.9));
      el.bed.setAttribute('ry', String(14 + Math.max(0, bloom) * 5));

      // 3 · pour: water pools above the bed, then drains away
      var pooled = lerp(p, 0.30, 0.56) - lerp(p, 0.62, 0.82);
      el.water.setAttribute('opacity', String(Math.max(0, pooled) * 0.92));
      el.water.setAttribute('ry', String(4 + Math.max(0, pooled) * 13));

      // 4 · drawdown: drips, and the carafe fills
      el.drips.setAttribute('opacity', String(lerp(p, 0.34, 0.44) - lerp(p, 0.84, 0.92)));
      var fill = lerp(p, 0.34, 0.88) * (CARAFE_BOTTOM - CARAFE_TOP) * 0.82;
      el.carafe.setAttribute('y', String(CARAFE_BOTTOM - fill));
      el.carafe.setAttribute('height', String(fill));

      // 5 · serve
      el.served.setAttribute('opacity', String(lerp(p, 0.86, 0.97)));

      if (bar) bar.style.width = (p * 100).toFixed(1) + '%';
      var active = 0;
      for (var i = 0; i < STAGES.length; i++) if (p >= STAGES[i]) active = i;
      steps.forEach(function (li, i) { li.classList.toggle('is-on', i === active); });
    }

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { render(1); return; }

    var queued = false;
    function onScroll() {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(function () {
        queued = false;
        var r = track.getBoundingClientRect();
        var span = r.height - window.innerHeight;
        var p = span > 0 ? (-r.top) / span : 0;
        render(Math.min(1, Math.max(0, p)));
      });
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();
  }

  renderStatus();
  highlightToday();
  navToggle();
  menuTabs();
  signature();
  brewing();
  setInterval(renderStatus, 60000);
})();
