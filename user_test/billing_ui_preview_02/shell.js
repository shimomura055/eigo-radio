/* shell.js -- the state panel around the app frame (public membership UI preview). Display controls only; the app frame is the real built webapp + membership UI. */
(function () {
  'use strict';
  var PAGES_ROOT = 'https://shimomura055.github.io/eigo-radio/user_test/';
  var $ = function (id) { return document.getElementById(id); };
  var frame = $('app'), items = [], online = true;
  var qs = new URLSearchParams(location.search);
  function radio(name) { var r = document.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ''; }
  function setRadio(name, v) { var r = document.querySelector('input[name="' + name + '"][value="' + v + '"]'); if (r) r.checked = true; }
  function savedSel() { return [].map.call(document.querySelectorAll('#saved-list input:checked'), function (i) { return i.value; }); }
  function appUrl(hash) {
    var p = new URLSearchParams();
    p.set('scn', radio('scn')); p.set('day', $('s-day').value); if ($('s-pick').value) p.set('pick', $('s-pick').value);
    if ($('c-first').checked) p.set('first', '1');
    p.set('consent', radio('consent')); p.set('buy', $('s-buy').value); p.set('restore', $('s-restore').value);
    if ($('s-product').value === 'fail') p.set('product', 'fail');
    p.set('freemb', $('s-free').value);
    var sv = savedSel(); if (sv.length) p.set('saved', sv.join(','));
    if (!online) p.set('online', '0');
    p.set('_', String(Date.now()));
    return 'app/index.html?' + p.toString() + (hash || '#/home');
  }
  function start(hash) { frame.src = appUrl(hash); $('status').textContent = '起動: ' + radio('scn') + (radio('scn') === 'trial' ? '(' + $('s-day').value + '日目)' : ''); }
  function live(f) { try { return f(frame.contentWindow); } catch (e) { return null; } }
  function fill() {
    var d = $('s-day'); for (var i = 1; i <= 8; i++) { var o = document.createElement('option'); o.value = i; o.textContent = i + '日目'; d.appendChild(o); } d.value = '5';
    var pk = $('s-pick'), sl = $('saved-list'); pk.innerHTML = ''; sl.innerHTML = '';
    items.forEach(function (it, idx) {
      var o = document.createElement('option'); o.value = it.slug; o.textContent = it.title_ja || it.slug; pk.appendChild(o);
      var l = document.createElement('label'), c = document.createElement('input'); c.type = 'checkbox'; c.value = it.slug; c.checked = idx < 2; l.appendChild(c); l.appendChild(document.createTextNode(' ' + (it.title_ja || it.slug))); sl.appendChild(l);
    });
    var sc = qs.get('scn'); if (sc) setRadio('scn', sc);
    if (qs.get('day')) d.value = qs.get('day');
  }
  fetch(PAGES_ROOT + 'webapp_proto_01/data/catalog_auto.json').then(function (r) { return r.json(); }).then(function (c) { items = (c.items || []).slice(0, 12); }, function () { items = []; }).then(function () { fill(); start('#/home'); });
  $('b-apply').addEventListener('click', function () { start('#/home'); });
  $('b-day').addEventListener('click', function () { live(function (w) { w.__PV.advanceDay(); }); $('status').textContent = '日付を1日進めました(アプリは開いたまま)'; });
  $('b-off').addEventListener('click', function () { online = !online; live(function (w) { w.__PVHost.setOnline(online); }); $('status').textContent = online ? 'オンライン' : 'オフライン(通信なし)'; });
  $('s-free').addEventListener('change', function () { live(function (w) { w.__PVHost.setFree($('s-free').value); }); });
  ['s-buy', 's-restore', 's-product'].forEach(function (id) { $(id).addEventListener('change', function () { live(function (w) { w.__PV.set({ buy: $('s-buy').value, restore: $('s-restore').value, product: $('s-product').value }); }); }); });
  [].forEach.call(document.querySelectorAll('[data-go]'), function (b) { b.addEventListener('click', function () { live(function (w) { w.location.hash = b.getAttribute('data-go'); }); }); });
  $('w-phone').addEventListener('click', function () { $('phone').classList.remove('pc'); $('w-phone').classList.add('on'); $('w-pc').classList.remove('on'); });
  $('w-pc').addEventListener('click', function () { $('phone').classList.add('pc'); $('w-pc').classList.add('on'); $('w-phone').classList.remove('on'); });
})();
