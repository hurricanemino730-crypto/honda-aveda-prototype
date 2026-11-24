# HONDA AVEDA 試作サイト

「HONDA AVEDA サイト原稿」の文章と画像を使って作った、新しいサイトの試作版です。

## 中身

- `site/` … 完成したサイト（そのまま公開できる HTML 一式）
- `src/` … サイトを作るための元ファイル
  - `menus.py` … メニュー料金表（料金を変えるときはここを直す）
  - `style.css` … デザイン（色・文字・配置）
  - `main.js` … 動き（スライドショー、スマホメニュー、スタッフ詳細、絞り込み）
  - `build.py` … 原稿フォルダとこれらから `site/` を作り直すスクリプト
  - `embeds.json` … スタッフ予定表（Googleカレンダー）と地図の埋め込みURL

## 作り直し方

```
python3 src/build.py
```

お知らせ・スタッフの文章は `../HONDA AVEDA サイト原稿/` の 05・07 番ファイルから読み込みます。

## ページ

| ページ | ファイル | 旧サイトのURL |
|---|---|---|
| トップ | index.html | /index.html |
| 辻堂店 | tsujido.html | /aveda.html |
| 辻堂店メニュー | tsujido-menu.html | /avedamenu.html |
| 二俣川店 | futamatagawa.html | /hutamatagawa.html |
| 二俣川店メニュー | futamatagawa-menu.html | /hutamatagawamenu.html |
| スタッフ | staff.html | /staff.html, /staff/index/4, /staff/view/* |
| お知らせ一覧 | news.html | /topics.html |
| お知らせ記事 | news/番号.html | /topics/view/番号（番号は同じ） |
| 会社案内 | company.html | /company.html |
| お問い合わせ | contact.html | /contact.html |

## 試作版で未対応のもの

- 問い合わせフォームは送信されない（公開時に送信先サービスを設定する）
- 検索エンジンに載らない設定（noindex）にしてある。公開時に外す
- 二俣川店の住所は店舗ページの表記「ジョイナステラス2 4F」に統一した（正しい表記を要確認）
- 2026.10.05 のお知らせにはタイトルがなかったため「改装工事に伴う休業のお知らせ」を仮で付けた

## GitHub Pages での公開

`main` ブランチに push すると、GitHub Actions（`.github/workflows/pages.yml`）が `site/` フォルダを GitHub Pages に公開します。

1. リポジトリの Settings → Pages → Source を「GitHub Actions」にする（初回のみ）
2. 料金や文章を直したら `python3 src/build.py` で `site/` を作り直し、commit して push する

お知らせ・スタッフの文章は原稿フォルダ（このリポジトリの外）から読み込むため、`site/` は作り直した状態で commit してください。
