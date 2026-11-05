/* Nebe Peklo Ráj – drobné vylepšení stránek. Bez závislostí.
   Web funguje i bez JavaScriptu: menu je pak rovnou vidět a záložky Žebříčku jsou pod sebou. */
(function () {
  'use strict';

  /* 1. Mobilní menu ------------------------------------------------------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = toggle && document.getElementById(toggle.getAttribute('aria-controls'));
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      nav.classList.toggle('is-open', open);
    };
    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    // Při přechodu na desktop menu zavřít, aby po zúžení okna nezůstalo otevřené
    var mq = window.matchMedia('(min-width: 60em)');
    var onChange = function () { if (mq.matches) setOpen(false); };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
  }

  /* 2. Postranní obsah – zvýraznění aktuální sekce ------------------------ */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('[data-scrollspy] a[href^="#"]'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var targets = tocLinks
      .map(function (a) { return document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))); })
      .filter(Boolean);
    var visible = new Set();
    var mark = function () {
      var current = null;
      for (var i = 0; i < targets.length; i++) {
        if (visible.has(targets[i])) { current = targets[i]; break; }
      }
      if (!current) return;
      tocLinks.forEach(function (a) {
        if (a.getAttribute('href') === '#' + current.id) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) visible.add(en.target); else visible.delete(en.target);
      });
      mark();
    }, { rootMargin: '-10% 0px -55% 0px' });
    targets.forEach(function (t) { io.observe(t); });
    // Na mobilu zavřít rozbalený obsah po výběru položky
    tocLinks.forEach(function (a) {
      a.addEventListener('click', function () {
        var d = a.closest('details');
        if (d && !window.matchMedia('(min-width: 60em)').matches) d.open = false;
      });
    });
  }
  // Na desktopu je postranní obsah vždy rozbalený
  var tocDetails = document.querySelectorAll('details.toc');
  if (tocDetails.length) {
    var desk = window.matchMedia('(min-width: 60em)');
    var syncToc = function () {
      tocDetails.forEach(function (d) { d.open = desk.matches; });
    };
    syncToc();
    if (desk.addEventListener) desk.addEventListener('change', syncToc);
  }

  /* 3. Záložky (Žebříček) -------------------------------------------------- */
  // Bez JS jsou záložky obyčejné odkazy na kotvy a panely jsou pod sebou.
  document.querySelectorAll('[data-tabs]').forEach(function (root) {
    var list = root.querySelector('.tabs__list');
    var tabs = Array.prototype.slice.call(root.querySelectorAll('.tabs__tab'));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('href').slice(1)); });
    if (!list || panels.indexOf(null) !== -1) return;
    list.setAttribute('role', 'tablist');
    tabs.forEach(function (t, i) {
      var id = t.id || (panels[i].id + '-tab');
      t.id = id;
      t.parentNode.setAttribute('role', 'presentation');
      t.setAttribute('role', 'tab');
      t.setAttribute('aria-controls', panels[i].id);
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].setAttribute('aria-labelledby', id);
      panels[i].tabIndex = 0;
    });
    var select = function (i, focus) {
      tabs.forEach(function (t, j) {
        var on = i === j;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        panels[j].hidden = !on;
      });
      if (focus) tabs[i].focus();
    };
    // Z odkazů (bez JS) uděláme tlačítka záložek
    tabs.forEach(function (t, i) {
      t.removeAttribute('href');
      t.addEventListener('click', function (e) { e.preventDefault(); select(i, false); });
      t.addEventListener('keydown', function (e) {
        var n = tabs.length, k = null;
        if (e.key === 'ArrowRight') k = (i + 1) % n;
        else if (e.key === 'ArrowLeft') k = (i - 1 + n) % n;
        else if (e.key === 'Home') k = 0;
        else if (e.key === 'End') k = n - 1;
        else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(i, false); return; }
        if (k !== null) { e.preventDefault(); select(k, true); }
      });
    });
    var start = tabs.findIndex(function (t) { return '#' + t.getAttribute('aria-controls') === location.hash; });
    select(start >= 0 ? start : 0, false);
  });
})();
