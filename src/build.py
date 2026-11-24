"""HONDA AVEDA 試作サイトの生成スクリプト。

  python3 src/build.py

原稿フォルダ（../HONDA AVEDA サイト原稿）の文章と画像から site/ フォルダに静的HTMLを作ります。
"""
import html, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_DOC = os.path.join(os.path.dirname(ROOT), "HONDA AVEDA サイト原稿")
SRC_IMG = os.path.join(SRC_DOC, "images")
OUT = os.path.join(ROOT, "site")
sys.path.insert(0, HERE)
from menus import TSUJIDO, FUTAMATAGAWA  # noqa: E402

E = html.escape
EMBEDS = json.load(open(os.path.join(HERE, "embeds.json"), encoding="utf-8"))
used_images = set()


def img(rel):
    """原稿/images からの相対パス → サイト内パス（コピー対象に登録）"""
    rel = rel.removeprefix("images/") if rel.startswith("images/media/") or rel.startswith("images/images/") else rel
    used_images.add(rel)
    return "img/" + rel


STORES = {
    "tsujido": dict(
        key="tsujido", label="辻堂店", en="Tsujido", name="HONDA AVEDA hair&spa 辻堂店",
        tag="HONDA AVEDA", tel="0120-68-2410",
        addr="神奈川県藤沢市辻堂神台1-3-1 テラスモール湘南1F",
        hours="10:00〜21:00 年中無休", last="カット 18:00 / カットカラー 17:00",
        reserve="https://my.saloon.to/?g=10560&m=0008&introduction_clear=1",
        gmap="https://g.page/HondaAveda?share",
        shop="https://www.aveda.jp/locator/get_the_facts.tmpl?vanity=1&SalonID=57406&utm_medium=referral&utm_source=aveda-salon&utm_campaign=acom_site-traffic&utm_content=honda_fs&utm_keyword=online",
        insta="https://www.instagram.com/honda.aveda",
        kv=[f"images/hondaaveda/img-kv-0{i}.jpg" for i in range(1, 5)],
        card="images/img-top-hondaaveda.jpg",
        feat=["images/hondaaveda/img-top-hairmenu.jpg", "images/hondaaveda/img-top-relaxation.jpg",
              "images/hondaaveda/img-top-team02.jpg"],
        menu=TSUJIDO, page="tsujido.html", menupage="tsujido-menu.html",
    ),
    "futamatagawa": dict(
        key="futamatagawa", label="二俣川店", en="Futamatagawa", name="HONDA AVEDA 二俣川店",
        tag="AVEDA 二俣川", tel="0120-72-5538",
        addr="神奈川県横浜市旭区二俣川2-91-7 ジョイナステラス2 4F",
        hours="10:00〜19:00",
        last="日〜木 カット 18:00 / カットカラー 17:00<br>金・土 カット 19:00 / カットカラー 18:00",
        reserve="https://my.saloon.to/?g=10560&m=0010&introduction_clear=1",
        gmap="https://goo.gl/maps/vhuf3P9Ckd1PRbYP9",
        shop="https://www.aveda.jp/locator/get_the_facts.tmpl?vanity=1&SalonID=58621&utm_medium=referral&utm_source=aveda-salon&utm_campaign=acom_site-traffic&utm_content=honda_fs&utm_keyword=online",
        insta="https://www.instagram.com/honda_aveda_joinusterrace/",
        kv=[f"images/hutamatagawa/img-kv-0{i}.jpg" for i in range(1, 5)],
        card="images/img-top-hutamatagawa.jpg",
        feat=["images/hutamatagawa/img-top-hairmenu.jpg", "images/hutamatagawa/img-top-relaxation.jpg",
              "images/hutamatagawa/img-top-team.jpg"],
        menu=FUTAMATAGAWA, page="futamatagawa.html", menupage="futamatagawa-menu.html",
    ),
}
TAG_TO_STORE = {"HONDA AVEDA": "tsujido", "AVEDA 二俣川": "futamatagawa", "共通": "all"}
STORE_LABEL = {"tsujido": "辻堂店", "futamatagawa": "二俣川店", "all": "共通"}


# ---------------------------------------------------------------- 原稿の読み込み
def blocks(fname):
    text = open(os.path.join(SRC_DOC, fname), encoding="utf-8").read()
    for b in text.split("\n---\n")[1:]:
        m = re.search(r"- 元URL: (\S+)", b)
        if m:
            yield m.group(1), b


def inline(s):
    s = E(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1).strip()}</a>', s)
    return s


def load_news():
    items = []
    for url, b in blocks("07_お知らせ全記事.md"):
        nid = url.rsplit("/", 1)[1]
        lines = b.split("\n")
        di = next(i for i, l in enumerate(lines) if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", l.strip()))
        date = lines[di].strip()
        rest = [l for l in lines[di + 1:]]
        tag = next(l.strip() for l in rest if l.strip())
        ti = next(i for i, l in enumerate(rest) if l.startswith("##"))
        title = rest[ti].lstrip("#").strip()
        body = rest[ti + 1:]
        imgs, paras = [], []
        for l in body:
            l = l.strip()
            if not l:
                continue
            m = re.fullmatch(r"!\[[^\]]*\]\(([^)]+)\)", l)
            if m:
                imgs.append(img(m.group(1)))
                continue
            paras.append(l)
        if nid == "295":  # 元サイトではタイトル欄に本文の書き出しが入っていたため補う
            if title:
                paras.insert(0, title)
            title = "改装工事に伴う休業のお知らせ"
        # 削除済みの記事への旧リンクを修正
        paras = [p.replace("https://www.honda-aveda.com/topics/view/69", "news/212.html") for p in paras]
        items.append(dict(id=nid, date=date, store=TAG_TO_STORE.get(tag, "all"), title=title, imgs=imgs, paras=paras))
    items.sort(key=lambda x: (x["date"], int(x["id"])), reverse=True)
    return items


ROLES = ("ディレクター", "プロデューサー", "マネージャー", "店長", "副店長", "主任", "セラピスト")


def load_staff():
    text = open(os.path.join(SRC_DOC, "05_スタッフ.md"), encoding="utf-8").read()
    order = list(dict.fromkeys(re.findall(r"staff/view/(\d+)", text)))
    futa_list = text.split("staff/index/4\n", 1)[1].split("\n---\n", 1)[0]
    futa_ids = set(re.findall(r"staff/view/(\d+)", futa_list))
    staff = {}
    for url, b in blocks("05_スタッフ.md"):
        if "/staff/view/" not in url:
            continue
        sid = url.rsplit("/", 1)[1]
        lines = [l.strip() for l in b.split("\n")]
        hi = next(i for i, l in enumerate(lines) if l.startswith("##  "))
        full = lines[hi][4:].strip()
        parts = full.split("　", 1)
        role, name = (parts[0], parts[1]) if len(parts) == 2 and parts[0] in ROLES else ("", full)
        photo = next((img(re.search(r"\(([^)]+)\)", l).group(1)) for l in lines if l.startswith("![")), "")
        msg = []
        for l in lines[hi + 1:]:
            if l.startswith("[ Reservation") or l.startswith("####"):
                break
            if l:
                msg.append(l)
        rm = re.search(r"\]\((https://my\.saloon\.to/staffs/[^)]+)\)", b)
        staff[sid] = dict(id=sid, role=role, name=name, photo=photo, msg=msg,
                          reserve=rm.group(1) if rm else "",
                          store="futamatagawa" if sid in futa_ids else "tsujido",
                          cal=EMBEDS["calendar"].get(sid, ""))
    return [staff[i] for i in order if i in staff]


def load_policy():
    text = open(os.path.join(SRC_DOC, "06_会社案内_お問い合わせ_サイトマップ.md"), encoding="utf-8").read()
    seg = text.split("#### 個人情報の取扱いについて", 1)[1].split("\n---\n", 1)[0]
    seg = "#### 個人情報の取扱いについて" + seg
    out, ul = [], False
    for l in seg.split("\n"):
        l = l.strip()
        if not l or "入力内容を確認" in l or l.startswith("["):
            continue
        if l.startswith("- "):
            if not ul:
                out.append("<ul>"); ul = True
            out.append(f"<li>{inline(l[2:])}</li>")
            continue
        if ul:
            out.append("</ul>"); ul = False
        if l.startswith("####"):
            out.append(f"<h4>{E(l.lstrip('#').strip())}</h4>")
        else:
            out.append(f"<p>{inline(l)}</p>")
    if ul:
        out.append("</ul>")
    return "\n".join(out)


# ---------------------------------------------------------------- レイアウト
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Shippori+Mincho:wght@500&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">')


def layout(title, body, active="", root="", desc="神奈川県藤沢市・横浜市のアヴェダ ヘアサロン＆スパ。HONDA AVEDA 辻堂店（テラスモール湘南）・二俣川店（ジョイナステラス）。"):
    def nav(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{root}{href}"{cur}>{label}</a>'
    t = STORES["tsujido"]; f = STORES["futamatagawa"]
    full_title = f"{title} | HONDA AVEDA hair&spa" if title else "HONDA AVEDA hair&spa｜辻堂・二俣川のアヴェダ ヘアサロン"
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="noindex">
{FONTS}
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{root}index.html"><img src="{root}img/images/logo-aveda.svg" alt="HONDA AVEDA hair&amp;spa"></a>
    <button class="menu-toggle" aria-label="メニュー" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="gnav">
      {nav(t['page'], '辻堂店', 'tsujido')}
      {nav(f['page'], '二俣川店', 'futamatagawa')}
      {nav('staff.html', 'スタッフ', 'staff')}
      {nav('news.html', 'お知らせ', 'news')}
      {nav('company.html', '会社案内', 'company')}
      <div class="reserve-menu">
        <a href="#" class="btn-reserve" data-reserve>ご予約</a>
        <div class="pop">
          <a href="{t['reserve']}" target="_blank" rel="noopener">辻堂店を予約<small>テラスモール湘南 1F</small></a>
          <a href="{f['reserve']}" target="_blank" rel="noopener">二俣川店を予約<small>ジョイナステラス 4F</small></a>
        </div>
      </div>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <img class="logo-f" src="{root}img/images/logo-aveda.svg" alt="HONDA AVEDA hair&amp;spa">
        <p>ピュアな花と植物エッセンスから生まれた美と科学を、湘南と横浜で。</p>
        <div class="sns">
          <a href="https://www.instagram.com/honda.aveda" target="_blank" rel="noopener">Instagram</a>
          <a href="https://www.facebook.com/HondaAveda" target="_blank" rel="noopener">Facebook</a>
          <a href="https://www.youtube.com/channel/UCcFp3PpFNmaf0vyyh29mtSA" target="_blank" rel="noopener">YouTube</a>
        </div>
      </div>
      <div>
        <h4>Tsujido</h4>
        <p>{t['addr']}</p>
        <p>Tel. <a href="tel:{t['tel']}">{t['tel']}</a></p>
        <p>{t['hours']}</p>
      </div>
      <div>
        <h4>Futamatagawa</h4>
        <p>{f['addr']}</p>
        <p>Tel. <a href="tel:{f['tel']}">{f['tel']}</a></p>
        <p>{f['hours']}</p>
      </div>
    </div>
    <div class="links">
      <a href="{root}index.html">トップ</a><a href="{root}news.html">お知らせ</a><a href="{root}staff.html">スタッフ</a>
      <a href="{root}company.html">会社案内</a><a href="{root}contact.html">お問い合わせ</a>
      <a href="https://honda-phi.com/" target="_blank" rel="noopener">HONDA GROUP</a>
    </div>
    <p class="copy">© 2026 HONDA PREMIER WORKS / HONDA AVEDA hair&amp;spa</p>
  </div>
</footer>
<script src="{root}main.js"></script>
</body>
</html>
"""


def arrow():
    return '<span class="arrow">→</span>'


def topic_cards(items, root=""):
    out = []
    for n in items:
        ph = f'<img src="{root}{n["imgs"][0]}" alt="" loading="lazy">' if n["imgs"] else '<span class="noimg">News</span>'
        out.append(f"""<a class="topic-card reveal" href="{root}news/{n['id']}.html">
  <div class="ph">{ph}</div>
  <div class="meta"><time>{n['date']}</time><span class="tag">{STORE_LABEL[n['store']]}</span></div>
  <h3>{E(n['title'])}</h3>
</a>""")
    return '<div class="topics">' + "\n".join(out) + "</div>"


def cta(store=None):
    if store:
        s = STORES[store]
        btns = f'<a class="btn" href="{s["reserve"]}" target="_blank" rel="noopener">{s["label"]}をWEB予約 {arrow()}</a><a class="btn" href="tel:{s["tel"]}">Tel. {s["tel"]}</a>'
    else:
        btns = "".join(f'<a class="btn" href="{s["reserve"]}" target="_blank" rel="noopener">{s["label"]}を予約 {arrow()}</a>' for s in STORES.values())
    return f"""<section class="cta"><div class="wrap">
  <span class="en">Reservation</span>
  <p>ご予約はWEBで24時間受け付けています。</p>
  <div class="btn-row center">{btns}</div>
</div></section>"""


def store_bar(s, root=""):
    return f"""<div class="store-bar"><div class="wrap">
  <div class="name">{s['en']}<small>{s['name']}</small></div>
  <nav>
    <a href="{root}{s['page']}">店舗トップ</a>
    <a href="{root}{s['menupage']}">メニュー</a>
    <a href="{root}staff.html#{s['key']}">スタッフ</a>
    <a href="{root}news.html#{s['key']}">お知らせ</a>
    <a href="{root}{s['page']}#access">アクセス</a>
    <a href="{s['shop']}" target="_blank" rel="noopener">公式オンラインショップ</a>
  </nav>
  <a class="tel" href="tel:{s['tel']}">Tel. {s['tel']}</a>
</div></div>"""


def slides(paths, cls="hero", copy=""):
    imgs = "".join(f'<img src="{img(p)}" alt=""{" class=\"on\"" if i == 0 else ""}>' for i, p in enumerate(paths))
    return f'<section class="{cls}"><div class="slides">{imgs}</div>{copy}</section>'


# ---------------------------------------------------------------- 各ページ
def page_index(news):
    copy = """<div class="hero-copy"><div class="wrap">
  <div class="en">Pure flower &amp; plant essences</div>
  <h1><span class="ib">ピュアな花と植物エッセンスから</span><span class="ib">生まれた美と科学</span></h1>
  <div class="sub">HONDA AVEDA hair &amp; spa — 辻堂 / 二俣川</div>
</div></div>"""
    salons = []
    for s in STORES.values():
        salons.append(f"""<article class="salon-card reveal">
  <a class="ph" href="{s['page']}"><img src="{img(s['card'])}" alt="{s['name']}"></a>
  <div class="body">
    <h3>{s['en']}<small>{s['name']}</small></h3>
    <dl class="info">
      <div><dt>住所</dt><dd style="margin:0">{s['addr']}</dd></div>
      <div><dt>営業時間</dt><dd style="margin:0">{s['hours']}</dd></div>
      <div><dt>電話</dt><dd style="margin:0"><a href="tel:{s['tel']}">{s['tel']}</a></dd></div>
    </dl>
    <div class="btn-row">
      <a class="btn" href="{s['page']}">店舗を見る {arrow()}</a>
      <a class="btn solid" href="{s['reserve']}" target="_blank" rel="noopener">予約する</a>
    </div>
  </div>
</article>""")
    gallery = "".join(f'<img class="reveal" src="{img(f"images/img-gallery-0{i}.jpg")}" alt="" loading="lazy">' for i in range(1, 7))
    body = f"""{slides(["images/mv-01.jpg", "images/mv-02.jpg", "images/mv-03.jpg"], copy=copy)}
<section class="block"><div class="narrow center reveal">
  <div class="sec-head"><span class="en">Concept</span><span class="ja">コンセプト</span></div>
  <p class="lead">「ピュアな花と植物エッセンスから生まれた美と科学」<br>を実践するアヴェダ。</p>
  <p>植物が持つ溢れるほどの生命力を科学的に研究してその高い効果に着目し、「あなたのためのケア」をご提案します。<br>
  アヴェダのヘアケア、スキンケア、ライフスタイルなどの製品は、高い効果だけでなく、地球環境にも深く配慮しています。</p>
</div></section>
<section class="block sand"><div class="wrap">
  <div class="sec-head"><span class="en">Salon</span><span class="ja">店舗のご案内</span></div>
  <div class="salons">{''.join(salons)}</div>
</div></section>
<section class="block"><div class="wrap">
  <div class="sec-head"><span class="en">Topics</span><span class="ja">お知らせ</span></div>
  {topic_cards(news[:3])}
  <div class="btn-row center" style="margin-top:40px"><a class="btn" href="news.html">お知らせ一覧 {arrow()}</a></div>
</div></section>
<section class="block alt"><div class="wrap">
  <div class="sec-head"><span class="en">Salon Gallery</span><span class="ja">ギャラリー</span></div>
  <p class="center" style="max-width:640px;margin:0 auto 40px">ショップ、サロン、スパの3つの空間ではピュアな花と植物成分による製品とアロマが織りなす豊かな時間の中、リラックスしてお過ごしいただけます。</p>
  <div class="gallery">{gallery}</div>
</div></section>
{cta()}"""
    return layout("", body, "home")


FEAT_TEXT = [
    ("Hair Menu", "ヘアメニュー", "お客様一人一人のお悩みや理想のスタイルをカウンセリングして、より素敵なあなただけのスタイルを提案させていただきます。アヴェダならではのヘアカラーは、髪へのダメージを抑えるだけではなく、環境にも配慮しております。", "{menu}", "メニューを見る"),
    ("Relaxation", "ヘッドスパ・トリートメント", "アヴェダ独自の先進技術による植物成分を短期間で髪の奥まで浸透させるヘアトリートメントや、ヒーリング効果の高いヘッドスパをご提供いたします。", "{menu}#spa", "スパメニューを見る"),
    ("Project Team", "スタッフ", "お客様一人一人のお悩みや理想のスタイルをカウンセリングして、より素敵なあなただけのスタイルを提案させていただきます。", "staff.html#{key}", "スタッフを見る"),
]


def page_store(s, news):
    feats = []
    for (en, ja, txt, href, btn), ph in zip(FEAT_TEXT, s["feat"]):
        href = href.format(menu=s["menupage"], key=s["key"])
        feats.append(f"""<div class="feature reveal">
  <div class="ph"><img src="{img(ph)}" alt="{en}" loading="lazy"></div>
  <div><h3>{en}</h3><span class="ja">{ja}</span><p>{txt}</p>
  <a class="btn" href="{href}">{btn} {arrow()}</a></div>
</div>""")
    snews = [n for n in news if n["store"] in (s["key"], "all")][:3]
    copy = f"""<div class="hero-copy"><div class="wrap">
  <div class="en">HONDA AVEDA hair &amp; spa</div><h1>{s['label']}</h1>
</div></div>"""
    body = f"""{slides(s['kv'], 'hero short', copy)}
{store_bar(s)}
<section class="block"><div class="wrap">
  <div class="sec-head"><span class="en">Topics</span><span class="ja">{s['label']}からのお知らせ</span></div>
  {topic_cards(snews)}
  <div class="btn-row center" style="margin-top:40px"><a class="btn" href="news.html#{s['key']}">一覧を見る {arrow()}</a></div>
</div></section>
<section class="block alt"><div class="wrap">{''.join(feats)}</div></section>
<section class="block" id="access"><div class="wrap">
  <div class="sec-head"><span class="en">Access</span><span class="ja">アクセス</span></div>
  <div class="access reveal">
    <div>
      <table>
        <tr><th>店名</th><td>{s['name']}</td></tr>
        <tr><th>住所</th><td>{s['addr']}</td></tr>
        <tr><th>電話</th><td><a href="tel:{s['tel']}">{s['tel']}</a></td></tr>
        <tr><th>営業時間</th><td>{s['hours']}</td></tr>
        <tr><th>最終受付</th><td>{s['last']}</td></tr>
      </table>
      <div class="btn-row" style="margin-top:24px">
        <a class="btn" href="{s['gmap']}" target="_blank" rel="noopener">Google Map {arrow()}</a>
        <a class="btn solid" href="{s['reserve']}" target="_blank" rel="noopener">WEB予約</a>
      </div>
    </div>
    <iframe src="{EMBEDS['map'][s['key']]}" loading="lazy" title="{s['name']}の地図" referrerpolicy="no-referrer-when-downgrade"></iframe>
  </div>
</div></section>
{cta(s['key'])}"""
    return layout(s["label"], body, s["key"])


def menu_cat(c):
    groups = []
    for g in c["groups"]:
        lis = []
        for nm, pr, ds in g["items"]:
            d = f'<div class="ds">{E(ds)}</div>' if ds else ""
            lis.append(f'<li><div class="row"><span class="nm">{E(nm)}</span><span class="dots"></span><span class="pr">{E(pr)}</span></div>{d}</li>')
        if len(g["items"]) > 1 and all(len(nm) <= 5 and not ds for nm, pr, ds in g["items"]):
            lis = [f'<li><span class="nm">{E(nm)}</span><span class="pr">{E(pr)}</span></li>' for nm, pr, ds in g["items"]]
            ul = f'<ul class="price-grid">{"".join(lis)}</ul>'
        else:
            ul = f'<ul class="price-list">{"".join(lis)}</ul>'
        h = f"<h4>{E(g['title'])}</h4>" if g["title"] else ""
        dsc = f'<p class="gdesc">{E(g["desc"])}</p>' if g["desc"] else ""
        groups.append(f'<div class="menu-group">{h}{dsc}{ul}</div>')
    notes = "".join(f'<p class="note">{E(n)}</p>' for n in c.get("notes", []))
    text = f'<div class="body-text">{c["text"]}</div>' if c.get("text") else ""
    foot = f'<p class="note">{E(c["foot"])}</p>' if c.get("foot") else ""
    return f"""<article class="menu-cat reveal" id="{c['id']}">
  <div class="menu-cat-head"><div><h3>{c['en']}</h3><span class="ja">{c['ja']}</span>{notes}</div>
  <img src="{img(c['img'])}" alt="" loading="lazy"></div>
  {text}{''.join(groups)}{foot}
</article>"""


def page_menu(s):
    side, cats = [], []
    for sec, items in s["menu"].items():
        sid = "hairmenu" if sec == "Hair Menu" else "relaxation"
        side.append(f'<p>{sec}</p><ul>' + "".join(f'<li><a href="#{c["id"]}">{c["en"]}</a></li>' for c in items) + "</ul>")
        cats.append(f'<h2 class="cat-title" id="{sid}">{sec}</h2>' + "".join(menu_cat(c) for c in items))
    body = f"""{slides(s['kv'][:1], 'hero short', f'<div class="hero-copy"><div class="wrap"><div class="en">Menu</div><h1>{s["label"]} メニュー</h1></div></div>')}
{store_bar(s)}
<section class="block"><div class="wrap menu-layout">
  <aside class="menu-side">{''.join(side)}</aside>
  <div>{''.join(cats)}
    <p class="menu-foot">※表示価格はすべて税込み価格となっております。</p>
    <div class="btn-row center" style="margin-top:28px"><a class="btn solid" href="{s['reserve']}" target="_blank" rel="noopener">{s['label']}をWEB予約 {arrow()}</a></div>
  </div>
</div></section>"""
    return layout(f"メニュー｜{s['label']}", body, s["key"])


def page_staff(staff):
    cards = []
    for p in staff:
        cards.append(f"""<button class="staff-card reveal" data-id="{p['id']}" data-store="{p['store']}">
  <div class="ph"><img src="{p['photo']}" alt="{E(p['name'])}" loading="lazy"></div>
  <span class="role">{E(p['role']) or '&nbsp;'}</span><span class="nm">{E(p['name'])}</span><span class="st">{STORE_LABEL[p['store']]}</span>
</button>""")
    data = json.dumps({p["id"]: dict(p, storeLabel=STORE_LABEL[p["store"]]) for p in staff}, ensure_ascii=False)
    body = f"""<div class="page-head"><span class="en">Project Team</span><span class="ja">スタッフ紹介</span></div>
<section class="block" style="padding-top:0"><div class="wrap">
  <div class="filters" data-filter-for=".staff-card">
    <button class="on" data-f="all">全員</button><button data-f="tsujido">辻堂店</button><button data-f="futamatagawa">二俣川店</button>
  </div>
  <div class="staff-grid">{''.join(cards)}</div>
</div></section>
<dialog class="staff-modal"><button class="close" aria-label="閉じる">×</button><div class="inner"></div></dialog>
<script>window.STAFF = {data};</script>
{cta()}"""
    return layout("スタッフ紹介", body, "staff")


def news_row(n, root=""):
    th = f'<img src="{root}{n["imgs"][0]}" alt="" loading="lazy">' if n["imgs"] else ""
    return f"""<a href="{root}news/{n['id']}.html" data-store="{n['store']}">
  <div class="th">{th}</div>
  <div><div class="meta"><time>{n['date']}</time><span class="tag">{STORE_LABEL[n['store']]}</span></div><h3>{E(n['title'])}</h3></div>
</a>"""


def page_news(news):
    body = f"""<div class="page-head"><span class="en">Topics</span><span class="ja">お知らせ</span></div>
<section class="block" style="padding-top:0"><div class="narrow">
  <div class="filters" data-filter-for=".news-list a" data-keep="all">
    <button class="on" data-f="all">すべて</button><button data-f="tsujido">辻堂店</button><button data-f="futamatagawa">二俣川店</button>
  </div>
  <div class="news-list">{''.join(news_row(n) for n in news)}</div>
</div></section>"""
    return layout("お知らせ", body, "news")


def page_article(n, prev, nxt):
    r = "../"
    imgs = ""
    if n["imgs"]:
        cls = "multi" if len(n["imgs"]) > 1 else "single"
        imgs = f'<div class="imgs {cls}">' + "".join(f'<img src="{r}{p}" alt="">' for p in n["imgs"]) + "</div>"
    content = "\n".join(f"<p>{inline(p)}</p>" for p in n["paras"]).replace('href="news/', f'href="{r}news/')
    pv = f'<a href="{prev["id"]}.html">← {E(prev["title"])}</a>' if prev else "<span></span>"
    nx = f'<a href="{nxt["id"]}.html" style="text-align:right">{E(nxt["title"])} →</a>' if nxt else "<span></span>"
    body = f"""<div class="narrow crumb"><a href="{r}index.html">トップ</a> / <a href="{r}news.html">お知らせ</a></div>
<section class="block" style="padding-top:8px"><div class="narrow">
  <article class="article">
    <div class="meta" style="margin:0"><time>{n['date']}</time><span class="tag">{STORE_LABEL[n['store']]}</span></div>
    <h1>{E(n['title'])}</h1>
    {imgs}
    <div class="content">{content}</div>
  </article>
  <div class="pager">{pv}{nx}</div>
  <div class="btn-row center" style="margin-top:40px"><a class="btn" href="{r}news.html">一覧に戻る</a></div>
</div></section>"""
    return layout(n["title"], body, "news", root=r)


def page_company():
    gallery = "".join(f'<img class="reveal" src="{img(f"images/img-gallery-0{i}.jpg")}" alt="" loading="lazy">' for i in (1, 3, 5))
    body = f"""<div class="page-head"><span class="en">Company</span><span class="ja">会社案内</span></div>
<section class="block" style="padding-top:0"><div class="narrow">
  <div class="article reveal">
  <table class="company-table">
    <tr><th>会社名</th><td>有限会社 HONDA PREMIER WORKS</td></tr>
    <tr><th>代表取締役</th><td>本田 真一 / Masa Honda</td></tr>
    <tr><th>設立</th><td>2011年10月</td></tr>
    <tr><th>本社</th><td>〒242-0029 神奈川県大和市上草柳二丁目1番15号</td></tr>
    <tr><th>TEL / FAX</th><td>0466-38-2410 / 0466-38-2411</td></tr>
    <tr><th>事業内容</th><td>理美容に関する一般業務<br>業界誌及び一般誌の撮影<br>テレビ・CM・ポスターなどのヘア&amp;メイク<br>ニューヨーク、ロンドン、パリなどのコレクション・全国ヘアショー出演及び全国講習活動</td></tr>
    <tr><th>店舗</th><td><a href="tsujido.html">HONDA AVEDA hair&amp;spa 辻堂店</a><br><a href="futamatagawa.html">HONDA AVEDA 二俣川店</a></td></tr>
  </table>
  </div>
</div></section>
<section class="block alt" style="padding-top:0;padding-bottom:0"><div class="gallery">{gallery}</div></section>"""
    return layout("会社案内", body, "company")


PREFS = "北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県".split()


def page_contact(policy):
    req = '<span class="req">必須</span>'
    opts = "".join(f"<option>{p}</option>" for p in PREFS)

    def f(label, inp, r=True):
        return f'<div class="field"><label>{label}{req if r else ""}</label><div>{inp}</div></div>'
    body = f"""<div class="page-head"><span class="en">Contact</span><span class="ja">お問い合わせ</span></div>
<section class="block" style="padding-top:0"><div class="narrow">
  <p>内容を確認次第、担当者よりご連絡させていただきます。お客さまからいただいたメールアドレスが違っていたり、システム障害などによりお返事できない場合がございます。返答のない場合は、お電話でその旨お問い合わせください。<br>
  お問い合わせ内容は、フォームにご記入頂きましたメールアドレス宛にも自動返送されます。</p>
  <p class="small muted">ご予約・ご予約の変更は、各店舗のWEB予約またはお電話でお願いいたします。</p>
  <form class="form" id="contact-form">
    <div class="proto-note">試作版のため、このフォームは送信されません。公開時にフォームの送信先を設定します。</div>
    {f('お名前', '<input name="name" required autocomplete="name">')}
    {f('ふりがな', '<input name="kana" required>')}
    {f('メールアドレス', '<input type="email" name="email" required autocomplete="email">')}
    {f('電話番号', '<input type="tel" name="tel" autocomplete="tel">', False)}
    {f('郵便番号', '<input name="zip" required autocomplete="postal-code" placeholder="例）251-0041" style="max-width:220px">')}
    {f('ご住所', f'<div class="sub-fields"><span>都道府県</span><select name="pref" required><option value="">選択してください</option>{opts}</select><span>市区町村・番地</span><input name="addr1" required><span>建物名など</span><input name="addr2"></div>')}
    {f('お問い合わせ内容', '<textarea name="body" required></textarea>')}
    <div class="policy"><strong>個人情報取り扱い（プライバシー・ポリシー）について</strong>{policy}</div>
    <div class="center"><button class="btn solid" type="submit">個人情報保護方針に同意の上、入力内容を確認する</button></div>
  </form>
</div></section>"""
    return layout("お問い合わせ", body, "contact")


# ---------------------------------------------------------------- 書き出し
def write(path, s):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    news, staff = load_news(), load_staff()
    write("index.html", page_index(news))
    for s in STORES.values():
        write(s["page"], page_store(s, news))
        write(s["menupage"], page_menu(s))
    write("staff.html", page_staff(staff))
    write("news.html", page_news(news))
    for i, n in enumerate(news):
        nxt = news[i - 1] if i > 0 else None
        prev = news[i + 1] if i + 1 < len(news) else None
        write(f"news/{n['id']}.html", page_article(n, prev, nxt))
    write("company.html", page_company())
    write("contact.html", page_contact(load_policy()))
    shutil.copy(os.path.join(HERE, "style.css"), os.path.join(OUT, "style.css"))
    shutil.copy(os.path.join(HERE, "main.js"), os.path.join(OUT, "main.js"))
    used_images.add("images/logo-aveda.svg")
    missing = []
    for rel in sorted(used_images):
        src = os.path.join(SRC_IMG, rel)
        if not os.path.exists(src):
            missing.append(rel); continue
        dst = os.path.join(OUT, "img", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
    print(f"pages: {6 + len(news) + 2}, news: {len(news)}, staff: {len(staff)}, images: {len(used_images)}")
    if missing:
        print("MISSING:", missing)


if __name__ == "__main__":
    main()
