(() => {
  const body = document.body;

  // スマホのメニュー開閉
  const toggle = document.querySelector('.menu-toggle');
  toggle?.addEventListener('click', () => {
    const open = body.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', open);
  });

  // 予約ボタンの店舗選択
  const rm = document.querySelector('.reserve-menu');
  rm?.querySelector('[data-reserve]').addEventListener('click', (e) => {
    e.preventDefault();
    rm.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (rm && !rm.contains(e.target)) rm.classList.remove('open');
  });

  // スライドショー
  document.querySelectorAll('.slides').forEach((box) => {
    const imgs = box.querySelectorAll('img');
    if (imgs.length < 2) return;
    let i = 0;
    setInterval(() => {
      imgs[i].classList.remove('on');
      i = (i + 1) % imgs.length;
      imgs[i].classList.add('on');
    }, 5500);
  });

  // スクロールでふわっと表示
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  // 店舗フィルター（スタッフ・お知らせ）
  document.querySelectorAll('.filters').forEach((bar) => {
    const targets = document.querySelectorAll(bar.dataset.filterFor);
    const keepAll = bar.dataset.keep; // お知らせでは「共通」を常に表示
    const apply = (f) => {
      bar.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.f === f));
      targets.forEach((t) => {
        const s = t.dataset.store;
        t.hidden = !(f === 'all' || s === f || (keepAll && s === keepAll));
        t.classList.add('in');
      });
    };
    bar.addEventListener('click', (e) => {
      const b = e.target.closest('button');
      if (!b) return;
      apply(b.dataset.f);
      history.replaceState(null, '', b.dataset.f === 'all' ? location.pathname : '#' + b.dataset.f);
    });
    const h = location.hash.slice(1);
    if (h === 'tsujido' || h === 'futamatagawa') apply(h);
  });

  // スタッフ詳細
  const dlg = document.querySelector('dialog.staff-modal');
  if (dlg && window.STAFF) {
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    document.querySelectorAll('.staff-card').forEach((card) => {
      card.addEventListener('click', () => {
        const p = window.STAFF[card.dataset.id];
        const msg = p.msg.map((m) => `<p>${esc(m)}</p>`).join('');
        const res = p.reserve ? `<a class="btn solid" href="${p.reserve}" target="_blank" rel="noopener">指名して予約する →</a>` : '';
        const cal = p.cal ? `<p class="small muted" style="margin:24px 0 0">出勤スケジュール</p><iframe src="${p.cal}" loading="lazy" title="${esc(p.name)}のスケジュール"></iframe>` : '';
        dlg.querySelector('.inner').innerHTML = `
          <img src="${p.photo}" alt="${esc(p.name)}">
          <div class="txt">
            <span class="tag">${p.storeLabel}</span>
            <p class="small" style="margin:14px 0 0;color:var(--accent);letter-spacing:.15em">${esc(p.role)}</p>
            <h3>${esc(p.name)}</h3>
            ${msg}
            <div class="btn-row" style="margin-top:20px">${res}</div>
            ${cal}
          </div>`;
        dlg.showModal();
      });
    });
    dlg.querySelector('.close').addEventListener('click', () => dlg.close());
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  }

  // 試作版の問い合わせフォーム
  document.getElementById('contact-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('試作版のため送信は行われません。入力チェックは正常に動作しています。');
  });
})();
