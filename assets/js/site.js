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

  renderStatus();
  highlightToday();
  navToggle();
  menuTabs();
  setInterval(renderStatus, 60000);
})();
