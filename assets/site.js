// The working preview in the hero: the Bucksley Mac window with made-up sample data. Switch views,
// pick an account or a range, hover the net worth chart, ask a question, and change the theme and
// appearance. Further down, the iPhone review inbox works, and the agent session switches between
// "View only" and "Can make changes". No network calls; every name and number is invented.
(function () {
  var gw = document.querySelector('.gw');
  if (gw) preview(gw);
  review(document.querySelector('[data-review]'));
  agentSession();
  looks(gw);

  function money(n, cents) {
    var s = Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: cents ? 2 : 0, maximumFractionDigits: cents ? 2 : 0 });
    return (n < 0 ? '−$' : '$') + s;
  }
  function short(n) { return '$' + (Math.abs(n) >= 1000 ? (Math.abs(n) / 1000).toFixed(1) + 'k' : Math.round(Math.abs(n))); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  function preview(gw) {
    var DAYS = 730;
    var seed = 20261125;
    function random() { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; }

    // Sample accounts: [id, name, kind, final balance, color class, start fraction, volatility]
    var ACCOUNTS = [
      ['checking', 'Everyday Checking', 'cash', 4812.37, 'c3', 0.9, 0.18],
      ['savings', 'High-Yield Savings', 'cash', 28450.12, 'c3', 0.62, 0.004],
      ['card', 'Rewards Card', 'debt', -1236.48, 'c5', 0.8, 0.35],
      ['brokerage', 'Brokerage', 'investments', 142381.06, 'c1', 0.71, 0.009],
      ['crypto', 'Crypto', 'crypto', 9640.05, 'c2', 0.48, 0.035]
    ];
    var series = {};
    ACCOUNTS.forEach(function (a) {
      var v = [], x = a[5];
      for (var d = 0; d < DAYS; d++) {
        var drift = (1 - a[5]) / DAYS;
        x = x + drift + (random() - 0.5) * a[6] * (a[2] === 'cash' && a[0] === 'checking' ? 1 : x);
        if (a[0] === 'checking' && d % 14 === 0) x += 0.25; // paydays
        x = Math.max(a[2] === 'debt' ? 0.15 : 0.05, x);
        v.push(x);
      }
      var scale = a[3] / v[DAYS - 1];
      series[a[0]] = v.map(function (y) { return y * scale; });
    });
    var LAYERS = [['investments', 'Investments', 'c1'], ['cash', 'Cash', 'c3'], ['crypto', 'Crypto', 'c2']];

    var today = new Date();
    function dayDate(i) { var d = new Date(today); d.setDate(d.getDate() - (DAYS - 1 - i)); return d; }
    function label(d, withYear) { return d.toLocaleDateString('en-US', withYear ? { month: 'short', year: 'numeric' } : { month: 'short', day: 'numeric' }); }
    var MONTH = today.toLocaleDateString('en-US', { month: 'long' });
    var dayOfMonth = today.getDate();
    var monthDays = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();

    // Sample transactions: [days ago, merchant, initials, category, class, amount, account]
    var TXS = [
      [0, 'Corner Market', 'CM', 'Groceries', 'c1', -84.27, 'card'],
      [0, 'Northside Fuel', 'NF', 'Gas', 'c4', -52.10, 'card'],
      [1, 'StreamBox', 'SB', 'Subscriptions', 'c5', -17.99, 'card'],
      [1, 'Dividend', 'DV', 'Income', 'c6', 212.40, 'brokerage'],
      [2, 'Hardware Barn', 'HB', 'Home', 'c3', -146.83, 'checking'],
      [3, 'Leaf & Bowl', 'LB', 'Dining', 'c2', -16.45, 'card'],
      [4, 'Payroll deposit', 'PD', 'Income', 'c6', 3420, 'checking'],
      [4, 'Staking reward', 'SR', 'Income', 'c6', 3.21, 'crypto'],
      [5, 'Bean There', 'BT', 'Dining', 'c2', -6.75, 'card'],
      [6, 'Transfer to savings', 'TR', 'Transfer', 'c6', -500, 'checking'],
      [6, 'Transfer from checking', 'TR', 'Transfer', 'c6', 500, 'savings'],
      [8, 'Card payment', 'CP', 'Transfer', 'c6', -1180.22, 'checking'],
      [8, 'Card payment', 'CP', 'Transfer', 'c6', 1180.22, 'card'],
      [9, 'Interest', 'IN', 'Income', 'c6', 98.12, 'savings'],
      [12, 'Index fund purchase', 'IF', 'Investments', 'c1', 400, 'brokerage'],
      [15, 'Coin purchase', 'CO', 'Investments', 'c1', 250, 'crypto']
    ];
    var SPEND = [['Groceries', 'c1', 486], ['Dining', 'c2', 312], ['Home', 'c3', 241], ['Other', 'c6', 189], ['Gas', 'c4', 148], ['Subscriptions', 'c5', 64]];
    var BUDGETS = [['Groceries', 'c1', 486, 600], ['Dining', 'c2', 312, 300], ['Gas', 'c4', 148, 200], ['Subscriptions', 'c5', 64, 80], ['Home', 'c3', 241, 300], ['Fun', 'c2', 92, 150]];
    var ANSWERS = {
      dining: 'You’ve spent <b>$312</b> on dining in ' + MONTH + ', <b>$12 over</b> your $300 budget. Most of it went to Leaf &amp; Bowl ($98) and Bean There ($61).',
      subs: 'Two went up this year: <b>StreamBox</b> from $15.49 to $17.99 a month, and <b>Cloud Locker</b> from $2.99 to $3.99. Together that’s <b>$42 more a year</b>.',
      budget: '<b>5 of 6</b> budgets are on pace. Dining is <b>$12 over</b>, and Groceries is at 81% with ' + (monthDays - dayOfMonth) + ' days to go.'
    };

    var state = { view: 'home', acct: 'all', range: 365 };
    var svg = gw.querySelector('.nw-chart svg');
    var readout = gw.querySelector('.readout');
    var W = 640, H = 200, PAD = { l: 0, r: 8, t: 12, b: 22 };
    function q(k) { return gw.querySelector('[data-k="' + k + '"]'); }

    function valueOn(id, i) { return series[id][i]; }
    function layersOn(i) {
      if (state.acct !== 'all') { var v = Math.abs(valueOn(state.acct, i)); return [v]; }
      var out = { investments: 0, cash: 0, crypto: 0 };
      ACCOUNTS.forEach(function (a) { if (a[2] !== 'debt') out[a[2]] += valueOn(a[0], i); });
      return LAYERS.map(function (l) { return out[l[0]]; });
    }
    function netOn(i) {
      if (state.acct !== 'all') return valueOn(state.acct, i);
      return ACCOUNTS.reduce(function (s, a) { return s + valueOn(a[0], i); }, 0);
    }
    function niceMax(v) { var p = Math.pow(10, Math.floor(Math.log10(v))); var m = v / p; return (m <= 1.5 ? 1.5 : m <= 2 ? 2 : m <= 3 ? 3 : m <= 5 ? 5 : 10) * p; }
    function account(id) { return ACCOUNTS.filter(function (a) { return a[0] === id; })[0]; }

    function sparks() {
      gw.querySelectorAll('.acct[data-acct]').forEach(function (b) {
        var id = b.getAttribute('data-acct');
        var box = b.querySelector('.spark');
        if (!box || id === 'all') return;
        var v = series[id], bars = '', lo = Infinity, hi = -Infinity, pts = [];
        for (var k = 0; k < 8; k++) { var y = Math.abs(v[DAYS - 1 - (7 - k) * 30]); pts.push(y); lo = Math.min(lo, y); hi = Math.max(hi, y); }
        pts.forEach(function (y) { bars += '<i></i>'; });
        box.innerHTML = bars;
        box.querySelectorAll('i').forEach(function (bar, j) { bar.style.height = Math.round(25 + 75 * (pts[j] - lo) / ((hi - lo) || 1)) + '%'; });
      });
      q('nw-side').textContent = money(Math.round(ACCOUNTS.reduce(function (s, a) { return s + series[a[0]][DAYS - 1]; }, 0)));
    }

    function home() {
      var n = state.range, start = DAYS - n;
      var a = state.acct === 'all' ? null : account(state.acct);
      var now = netOn(DAYS - 1), then = netOn(start);
      var whole = Math.trunc(now), cents = Math.abs(Math.round((now - whole) * 100)).toString().padStart(2, '0');
      q('nw-label').textContent = a ? a[1] : 'Net worth';
      q('nw').innerHTML = esc(money(whole)) + '<small>.' + cents + '</small>';
      var pct = then ? (now - then) / Math.abs(then) * 100 : 0;
      var good = a && a[2] === 'debt' ? pct <= 0 : pct >= 0;
      var chip = q('nw-chip');
      chip.className = 'chip fig' + (good ? '' : ' down');
      chip.textContent = (now - then >= 0 ? '+' : '−') + Math.abs(pct).toFixed(1) + '% ' + { 30: '1M', 90: '3M', 365: '1Y', 730: 'All' }[n];
      var layers = a ? [[a[0], a[1], a[4]]] : LAYERS;
      var last = layersOn(DAYS - 1);
      q('keys').innerHTML = layers.map(function (l, i) { return '<span class="' + l[2] + '"><i></i>' + esc(l[1]) + ' <b class="fig">' + short(last[i]) + '</b></span>'; }).join('') +
        (a ? '' : '<span class="c5"><i></i>Debt <b class="fig">−' + short(series.card[DAYS - 1]) + '</b></span>');

      // Chart
      W = Math.max(280, Math.round(svg.getBoundingClientRect().width) || 640);
      H = W < 520 ? 170 : 220;
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      var step = Math.max(1, Math.ceil(n / 160)), idx = [];
      for (var i = start; i < DAYS; i += step) idx.push(i);
      if (idx[idx.length - 1] !== DAYS - 1) idx.push(DAYS - 1);
      var stacks = idx.map(function (i) { var ls = layersOn(i), acc = 0; return ls.map(function (v) { acc += v; return acc; }); });
      var max = niceMax(Math.max.apply(null, stacks.map(function (s) { return s[s.length - 1]; })) * 1.04);
      var iw = W - PAD.l - PAD.r, ih = H - PAD.t - PAD.b;
      function X(k) { return PAD.l + (idx[k] - start) / (n - 1) * iw; }
      function Y(v) { return PAD.t + ih - v / max * ih; }
      var out = '';
      for (var L = layers.length - 1; L >= 0; L--) {
        var top = idx.map(function (_, k) { return (k ? 'L' : 'M') + X(k).toFixed(1) + ' ' + Y(stacks[k][L]).toFixed(1); }).join('');
        var bottom = '';
        for (var k = idx.length - 1; k >= 0; k--) bottom += 'L' + X(k).toFixed(1) + ' ' + Y(L ? stacks[k][L - 1] : 0).toFixed(1);
        out += '<path class="area ' + layers[L][2] + '" d="' + top + bottom + 'Z"/>';
        if (L < layers.length - 1) out += '<path class="edge" d="' + top + '"/>';
      }
      out += '<g class="grid">';
      [0.25, 0.5, 0.75].forEach(function (f) { out += '<line x1="' + PAD.l + '" x2="' + (W - PAD.r) + '" y1="' + Y(max * f).toFixed(1) + '" y2="' + Y(max * f).toFixed(1) + '"/>'; });
      out += '</g><g class="axis">';
      [0.25, 0.5].forEach(function (f) { out += '<text class="on" x="' + (PAD.l + 6) + '" y="' + (Y(max * f) - 4).toFixed(1) + '">' + short(max * f).replace('.0k', 'k') + '</text>'; });
      var ticks = W < 520 ? 2 : 4;
      for (var t = 0; t <= ticks; t++) {
        var di = start + Math.round(t / ticks * (n - 1));
        var anchor = t === 0 ? 'start' : t === ticks ? 'end' : 'middle';
        out += '<text x="' + (PAD.l + (di - start) / (n - 1) * iw).toFixed(1) + '" y="' + (H - 5) + '" text-anchor="' + anchor + '">' + (t === ticks ? 'Today' : label(dayDate(di), n > 120)) + '</text>';
      }
      out += '</g><line class="hover-line" x1="0" x2="0" y1="' + PAD.t + '" y2="' + (H - PAD.b) + '" visibility="hidden"/><circle class="hover-dot" r="5" cx="0" cy="0" visibility="hidden"/>';
      svg.innerHTML = out;
      state.chart = { start: start, n: n, iw: iw, X: function (i) { return PAD.l + (i - start) / (n - 1) * iw; }, Y: Y };
      showDay(null);

      // Recent activity for the chosen account
      var list = TXS.filter(function (t) { return state.acct === 'all' ? t[3] !== 'Transfer' : t[6] === state.acct; }).slice(0, 5);
      q('tx-scope').textContent = a ? a[1] : 'All accounts';
      q('txs').innerHTML = list.map(function (t) {
        var d = new Date(today); d.setDate(d.getDate() - t[0]);
        return '<li><span class="dt fig">' + label(d) + '</span><i class="av ' + t[4] + '">' + t[2] + '</i><span class="m">' + esc(t[1]) + '</span><span class="tag ' + t[4] + '">' + t[3] + '</span><span class="amt fig' + (t[5] > 0 ? ' pos' : '') + '">' + (t[5] > 0 ? '+' : '') + money(t[5], true) + '</span></li>';
      }).join('');
    }

    function showDay(i) {
      var c = state.chart, line = svg.querySelector('.hover-line'), dot = svg.querySelector('.hover-dot');
      if (i === null) {
        readout.textContent = 'Hover the chart to see any day.';
        line.setAttribute('visibility', 'hidden'); dot.setAttribute('visibility', 'hidden');
        return;
      }
      var ls = layersOn(i), total = ls.reduce(function (s, v) { return s + v; }, 0);
      var parts = state.acct === 'all' ? ' · ' + LAYERS.map(function (l, k) { return l[1] + ' ' + short(ls[k]); }).join(' · ') : '';
      readout.textContent = label(dayDate(i)) + ' · ' + money(Math.round(netOn(i))) + parts;
      var x = c.X(i).toFixed(1);
      line.setAttribute('x1', x); line.setAttribute('x2', x); line.setAttribute('visibility', 'visible');
      dot.setAttribute('cx', x); dot.setAttribute('cy', c.Y(total).toFixed(1)); dot.setAttribute('visibility', 'visible');
    }

    function spending() {
      var total = SPEND.reduce(function (s, c) { return s + c[2]; }, 0), off = 0, gap = 0.6, rings = '';
      SPEND.forEach(function (c, i) {
        var pct = c[2] / total * 100;
        rings += '<circle class="' + c[1] + '" data-i="' + i + '" cx="21" cy="21" r="15.9155" fill="none" stroke="var(--k)" stroke-width="6" pathLength="100" stroke-dasharray="' + Math.max(0.1, pct - gap).toFixed(2) + ' ' + (100 - pct + gap).toFixed(2) + '" stroke-dashoffset="' + (-off).toFixed(2) + '"/>';
        off += pct;
      });
      var dsvg = gw.querySelector('.donut svg');
      dsvg.innerHTML = '<g transform="rotate(-90 21 21)">' + rings + '</g>';
      q('spend-total').textContent = money(total);
      q('spend-label').textContent = MONTH;
      q('legend').innerHTML = SPEND.map(function (c, i) {
        return '<li class="' + c[1] + '" data-i="' + i + '" tabindex="0"><i></i><span>' + c[0] + '</span><em class="fig">' + Math.round(c[2] / total * 100) + '%</em><b class="fig">' + money(c[2]) + '</b></li>';
      }).join('');
    }
    function focusSlice(i) {
      var dsvg = gw.querySelector('.donut svg');
      dsvg.classList.toggle('focus', i !== null);
      dsvg.querySelectorAll('circle').forEach(function (c) { c.classList.toggle('on', c.getAttribute('data-i') === String(i)); });
      gw.querySelectorAll('.legend li').forEach(function (l) { l.classList.toggle('on', l.getAttribute('data-i') === String(i)); });
      var c = i === null ? null : SPEND[i];
      q('spend-total').textContent = money(c ? c[2] : SPEND.reduce(function (s, x) { return s + x[2]; }, 0));
      q('spend-label').textContent = c ? c[0] : MONTH;
    }

    function budgets() {
      q('pace').textContent = 'Day ' + dayOfMonth + ' of ' + monthDays;
      q('rings').innerHTML = BUDGETS.map(function (b) {
        var pct = Math.round(b[2] / b[3] * 100), over = pct > 100;
        return '<li class="' + b[1] + '"><div class="rg"><svg viewBox="0 0 36 36" aria-hidden="true"><circle class="track" cx="18" cy="18" r="14.5" fill="none" stroke-width="4"/>' +
          '<circle class="val' + (over ? ' over' : '') + '" cx="18" cy="18" r="14.5" fill="none" stroke-width="4" stroke-linecap="round" pathLength="100" stroke-dasharray="' + Math.min(pct, 100) + ' 100" transform="rotate(-90 18 18)"/></svg>' +
          '<b class="fig' + (over ? ' neg' : '') + '">' + pct + '%</b></div><span>' + b[0] + '</span><em class="fig">' + money(b[2]) + ' / ' + money(b[3]) + '</em></li>';
      }).join('');
    }

    function render() {
      gw.querySelectorAll('[data-view]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === state.view)); });
      gw.querySelectorAll('[data-pane]').forEach(function (p) { p.hidden = p.getAttribute('data-pane') !== state.view; });
      gw.querySelectorAll('.acct').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-acct') === state.acct)); });
      gw.querySelectorAll('[data-range]').forEach(function (b) { b.setAttribute('aria-pressed', String(+b.getAttribute('data-range') === state.range)); });
      if (state.view === 'home') home();
    }

    svg.addEventListener('pointermove', function (e) {
      var c = state.chart, box = svg.getBoundingClientRect();
      var x = (e.clientX - box.left) / box.width * W;
      var i = c.start + Math.round((x - PAD.l) / c.iw * (c.n - 1));
      showDay(Math.max(c.start, Math.min(DAYS - 1, i)));
    });
    svg.addEventListener('pointerleave', function () { showDay(null); });
    gw.querySelector('.legend').addEventListener('pointerover', function (e) { var li = e.target.closest('li'); if (li) focusSlice(+li.getAttribute('data-i')); });
    gw.querySelector('.legend').addEventListener('focusin', function (e) { var li = e.target.closest('li'); if (li) focusSlice(+li.getAttribute('data-i')); });
    gw.querySelector('.legend').addEventListener('pointerleave', function () { focusSlice(null); });
    gw.querySelector('.legend').addEventListener('focusout', function () { focusSlice(null); });
    gw.addEventListener('click', function (e) {
      var v = e.target.closest('[data-view]'), a = e.target.closest('.acct'), r = e.target.closest('[data-range]');
      if (v) state.view = v.getAttribute('data-view');
      if (a) { state.acct = a.getAttribute('data-acct'); state.view = 'home'; }
      if (r) state.range = +r.getAttribute('data-range');
      if (v || a || r) render();
    });
    q('ask').addEventListener('submit', function (e) {
      e.preventDefault();
      var box = q('answer');
      box.innerHTML = ANSWERS[q('ask-q').value] + '<small>Answered on your Mac by Apple’s on-device model · sample data</small>';
      box.hidden = false;
    });
    var resizeTimer;
    window.addEventListener('resize', function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(function () { if (state.view === 'home') home(); }, 120); });

    sparks(); spending(); budgets(); render();
  }

  function review(screen) {
    if (!screen) return;
    // Sample review queue: [initials, class, category, merchant, amount, date, account, note]
    var QUEUE = [
      ['HB', 'c3', 'Home', 'Hardware Barn', '−$146.83', 'Sun, Nov 22', 'Everyday Checking', 'About $60 more than your usual Hardware Barn visit.'],
      ['SB', 'c5', 'Subscriptions', 'StreamBox', '−$17.99', 'Sat, Nov 21', 'Rewards Card', 'Up from $15.49. The price changed this month.'],
      ['LB', 'c2', 'Dining', 'Leaf & Bowl', '−$16.45', 'Fri, Nov 20', 'Rewards Card', 'Your third visit this week.'],
      ['NF', 'c4', 'Gas', 'Northside Fuel', '−$52.10', 'Fri, Nov 20', 'Rewards Card', 'Filed by your rule for Northside Fuel.'],
      ['PD', 'c6', 'Income', 'Payroll deposit', '+$3,420.00', 'Thu, Nov 19', 'Everyday Checking', 'Same as last paycheck.']
    ];
    var CATS = [['Home', 'c3'], ['Groceries', 'c1'], ['Shopping', 'c4'], ['Gifts', 'c5'], ['Dining', 'c2']];
    var pos = 0, card = screen.querySelector('.dcard');
    function k(name) { return screen.querySelector('[data-k="' + name + '"]'); }
    function show() {
      var done = pos >= QUEUE.length;
      k('count').textContent = done ? 'Done' : (pos + 1) + ' of ' + QUEUE.length;
      screen.querySelector('[data-act="category"]').hidden = done;
      screen.querySelector('[data-act="reviewed"]').textContent = done ? 'Start over' : 'Reviewed';
      if (done) {
        k('av').className = 'av c2'; k('av').textContent = '✓';
        k('cat').className = 'tag c2'; k('cat').textContent = 'Inbox zero';
        k('merchant').textContent = 'All caught up';
        k('amount').textContent = QUEUE.length + ' reviewed';
        k('date').textContent = 'Just now'; k('acct').textContent = 'Synced to your Mac';
        k('note').textContent = 'Everything you marked here is already on your Mac, through your iCloud.';
        upNext();
        return;
      }
      var t = QUEUE[pos];
      k('av').className = 'av ' + t[1]; k('av').textContent = t[0];
      k('cat').className = 'tag ' + t[1]; k('cat').textContent = t[2];
      k('merchant').textContent = t[3]; k('amount').textContent = t[4];
      k('amount').classList.toggle('pos', t[4].charAt(0) === '+');
      k('date').textContent = t[5]; k('acct').textContent = t[6]; k('note').textContent = t[7];
      upNext();
    }
    function upNext() {
      var list = k('next');
      list.innerHTML = '';
      QUEUE.slice(pos + 1, pos + 3).forEach(function (t) {
        var li = document.createElement('li');
        li.innerHTML = '<i class="av ' + t[1] + '">' + t[0] + '</i><span><b></b><small>' + t[2] + '</small></span><span class="fig"></span>';
        li.querySelector('b').textContent = t[3];
        li.querySelector('.fig').textContent = t[4];
        list.appendChild(li);
      });
      screen.querySelector('.up').hidden = !list.children.length;
    }
    screen.addEventListener('click', function (e) {
      var act = e.target.closest('[data-act]');
      if (!act) return;
      if (act.getAttribute('data-act') === 'category') {
        var cur = k('cat').textContent, i = 0;
        CATS.forEach(function (c, j) { if (c[0] === cur) i = j + 1; });
        var next = CATS[i % CATS.length];
        k('cat').className = 'tag ' + next[1]; k('cat').textContent = next[0];
        k('av').className = 'av ' + next[1];
        k('hint').textContent = 'Category changed. It syncs back to your Mac.';
        return;
      }
      if (pos >= QUEUE.length) { pos = 0; show(); return; }
      card.classList.add('out');
      setTimeout(function () { pos += 1; show(); card.classList.remove('out'); }, 220);
      k('hint').textContent = 'Marked reviewed. Synced back to your Mac through iCloud.';
    });
    show();
  }

  function looks(gw) {
    var lookButtons = document.querySelectorAll('[data-look]'), themeButtons = document.querySelectorAll('[data-theme-to]');
    if (!gw) return;
    var phoneScreen = document.querySelector('[data-review]');
    lookButtons.forEach(function (b) { b.addEventListener('click', function () { setLook(b.getAttribute('data-look')); }); });
    themeButtons.forEach(function (b) { b.addEventListener('click', function () { setTheme(b.getAttribute('data-theme-to')); }); });
    function setLook(look) {
      gw.setAttribute('data-appearance', look);
      lookButtons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-look') === look)); });
    }
    function setTheme(theme) {
      gw.setAttribute('data-theme', theme);
      if (phoneScreen) phoneScreen.setAttribute('data-theme', theme);
      themeButtons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-theme-to') === theme)); });
    }
  }

  function agentSession() {
    var session = document.querySelector('.session');
    if (!session) return;
    session.querySelectorAll('[data-mode-to]').forEach(function (b) {
      b.addEventListener('click', function () {
        var mode = b.getAttribute('data-mode-to');
        session.setAttribute('data-mode', mode);
        session.querySelectorAll('[data-mode-to]').forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
      });
    });
  }
})();
