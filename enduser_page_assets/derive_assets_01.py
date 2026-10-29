# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: production asset(rev01-e)をDEV rev01-eの『機械的派生』として作る。

 - 入力 : DEV rev01-e(`user_test/dev_enduser_page_01/{index.html,app.js,style.css}`。**読み取りのみ・DEVは不変**)
 - 出力 : `enduser_page_assets/rev01-e/{index.html,app.js,style.css,ASSET_SHA256.json}` と `ASSET_DIFF_01.md`(許可リスト=EDITSの一覧)
 - 派生規則 : 下の `EDITS`(許可リスト)だけ。各editは旧文字列が**ちょうど1回**現れることを要求(0/2回以上はエラー)。許可リスト外の差分は生じない。
   REMOVE=DEV専用機能の除去(記事切替・DEV注記・ダミー同期・`Q.get('a')`・仮データ表示・DEV訳表示)、ADD=本番で必要な最小追加(Voice説明文・KP 3列目)。
 - testは本scriptの `derive()` を呼び、assetが『DEV + EDITSのみ』と一致すること(T-ASSET-DIFF)を検査する。
実行: .venv\\Scripts\\python.exe enduser_page_assets\\derive_assets_01.py [--write]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEV_DIR = ROOT / "user_test" / "dev_enduser_page_01"
OUT_DIR = HERE / "rev01-e"
FILES = ("index.html", "app.js", "style.css")


EDITS = [
    # ---------------- index.html ----------------
    dict(id="H1", file="index.html", kind="REMOVE", why="DEV表記のtitle",
         old='<title>[DEV] English Your Way · 記事視聴ページ</title>', new='<title>English Your Way · 記事視聴ページ</title>'),
    dict(id="H2", file="index.html", kind="REMOVE", why="ダミー同期の状態表示(確認用)",
         old='<span id="syncState" hidden></span>\n', new=''),
    dict(id="H3", file="index.html", kind="ADD", why="承認済みVoice説明文(Family Y。CURRENT_SPEC:3202-3206)の表示場所=hero直下",
         old='<div class="top">', new='<div class="notice" id="notice" hidden></div>\n <div class="top">'),
    # ---------------- app.js ----------------
    dict(id="J1", file="app.js", kind="REMOVE", why="DEV試作の説明コメント(DEV path・dummy同期の記述)",
         old=("/* END-USER-LISTENING-PAGE-PROTOTYPE-01 DEV試作(静的・外部ライブラリなし)。\n"
              "   データ: data/<article>.json (docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/tools/build_data_01.py が公開済み/候補ページから生成)。\n"
              "   音声: 既存mp3を相対パスで参照(コピー・再生成なし)。\n"
              "   文単位ハイライトのフック: 各文は <span class=\"sent\" data-sid=\"...\">、同期データ(sentences:[{sid,start,end}], 全編内の秒)を\n"
              "   data/sync_index.json 経由(または ?sync=dummy の確認用ダミー)で読み込む。 */\n"),
         new=("/* English Your Way 記事視聴ページ(End User向け。静的・外部ライブラリなし)。\n"
              "   データ: data/article.json と data/sync_<level>.json(er135_enduser_page_01.pyが公開dirの最終dev index.htmlから生成)。\n"
              "   音声: 既存mp3を相対パス(../)で参照(コピー・再生成なし)。\n"
              "   文単位ハイライト: 各文は <span class=\"sent\" data-sid=\"...\">、同期データ(sentences:[{sid,start,end}], 全編内の秒)で点灯する。 */\n")),
    dict(id="J2", file="app.js", kind="REMOVE", why="sync_index(複数記事の同期索引)の変数",
         old="var raf = 0, lastUserScroll = 0, syncIndex = null;", new="var raf = 0, lastUserScroll = 0;"),
    dict(id="J3", file="app.js", kind="REMOVE", why="DEV訳(未承認)の判定変数とコメント",
         old="function trHtml(p) {   // 英語本文の直後に日本語訳(承認済み日本語原稿の対応段落 / DEV訳(未承認))\n    if (!p.ja || !p.ja.length) return '';\n    var dev = p.ja_source === 'dev_translation_unapproved';\n",
         new="function trHtml(p) {   // 英語本文の直後に日本語訳(承認済み日本語原稿の対応段落のみ。無いブロックは出さない)\n    if (!p.ja || !p.ja.length) return '';\n"),
    dict(id="J4", file="app.js", kind="REMOVE", why="DEV訳(未承認)の表示タグ",
         old="<span class=\"trtag\">日本語訳' + (dev ? '<em>(DEV訳・未承認)</em>' : '') + '</span>' +",
         new="<span class=\"trtag\">日本語訳</span>' +"),
    dict(id="J5", file="app.js", kind="ADD", why="Key Phrase表の3列目(Z Advanced: 英語での説明)を意味の下に表示(2列のKPは不変)",
         old="'<div class=\"def\"><span class=\"th\">' + esc(hdr[1] || '') + '</span>' + esc(k.text) + '</div>' +",
         new="'<div class=\"def\"><span class=\"th\">' + esc(hdr[1] || '') + '</span>' + esc(k.text) + (k.text2 ? '<span class=\"th th2\">' + esc(hdr[2] || '') + '</span>' + esc(k.text2) : '') + '</div>' +"),
    dict(id="J6", file="app.js", kind="REMOVE", why="文法の仮データ表示(placeholder)の判定",
         old="      var ph = L.grammar_source === 'placeholder_for_layout_check';   // rev01-c: 表示確認用の仮データ(DEVページのみ・本文と内容は無関係)\n", new=""),
    dict(id="J7", file="app.js", kind="REMOVE", why="文法の仮データ注記",
         old="out += card('Grammar & Sentence Structure', (ph ? '<div class=\"phnote\" data-grammar-source=\"placeholder_for_layout_check\">【仮データ・表示確認用】他記事(月のしわ Advanced)の文法解説を流用しています。記事本文とは内容が対応しません。レイアウト・文字サイズ確認専用で、正式な文法解説ではありません。</div>' : '') + L.grammar.map(",
         new="out += card('Grammar & Sentence Structure', L.grammar.map("),
    dict(id="J8", file="app.js", kind="REMOVE", why="文法ラベルの仮表示",
         old="{ label: ph ? 'GRAMMAR(仮)' : 'GRAMMAR', id: 'grammar', cls: 'blk-grammar' }", new="{ label: 'GRAMMAR', id: 'grammar', cls: 'blk-grammar' }"),
    dict(id="J9", file="app.js", kind="REMOVE", why="ニュアンスの仮データ判定とコメント",
         old="    if (L.nuance && L.nuance.length) {   // rev01-d: ニュアンス解説(DEV仮表示。採用0件ならコーナーごと非表示)\n      var nph = L.nuance_source === 'placeholder_for_layout_check';\n",
         new="    if (L.nuance && L.nuance.length) {   // ニュアンス解説(採用0件ならコーナーごと非表示)\n"),
    dict(id="J10", file="app.js", kind="REMOVE", why="ニュアンスの仮データ注記",
         old="out += card('ニュアンス解説', (nph ? '<div class=\"phnote\" data-nuance-source=\"placeholder_for_layout_check\">【仮データ・表示確認用】他記事のニュアンス解説を流用。記事本文とは内容が対応しません。</div>' : '') + L.nuance.map(",
         new="out += card('ニュアンス解説', L.nuance.map("),
    dict(id="J11", file="app.js", kind="REMOVE", why="ニュアンスラベルの仮表示",
         old="{ label: nph ? 'NUANCE(仮)' : 'NUANCE', id: 'nuance', cls: 'blk-nuance' }", new="{ label: 'NUANCE', id: 'nuance', cls: 'blk-nuance' }"),
    dict(id="J12", file="app.js", kind="REMOVE", why="同期データ読込: ?sync=dummy|off分岐・sync_index経由(複数記事)・状態表示を除き、data/sync_<lv>.jsonだけを読む",
         between=("  function loadSync() {", "  /* ---------- レベル切替・初期化 ---------- */"),
         new=("  function loadSync() {\n"
              "    sync = []; syncKind = 'none'; highlight(null);\n"
              "    var done = function () { tick(); };\n"
              "    return fetchJson('data/sync_' + lv + '.json').then(function (j) { sync = norm(j); syncKind = 'real'; done(); }).catch(function (e) { console.warn(e); done(); });\n"
              "  }\n\n")),
    dict(id="J13", file="app.js", kind="REMOVE", why="document.titleの[DEV]接頭辞",
         old="document.title = '[DEV] ' + art.title_ja + '｜' + LEVEL_NAME[lv];", new="document.title = art.title_ja + '｜' + LEVEL_NAME[lv];"),
    dict(id="J14", file="app.js", kind="REMOVE", why="URL queryの記事id(a=)。記事切替UIは無く1ページ=1記事",
         old="u.searchParams.set('a', art.id); u.searchParams.set('lv', lv);", new="u.searchParams.set('lv', lv);"),
    dict(id="J15", file="app.js", kind="REMOVE", why="記事id引数・記事別data path(data/<id>.json)を固定のdata/article.jsonへ",
         old="  function init(aid) {\n    fetchJson('data/' + aid + '.json').then(function (j) {\n      art = j;\n",
         new="  function init() {\n    fetchJson('data/article.json').then(function (j) {\n      art = j;\n"),
    dict(id="J16", file="app.js", kind="ADD", why="承認済みVoice説明文(Y)をhero直下へ表示(notice無しなら非表示のまま)",
         old="      $('jaTitle').textContent = art.title_ja; $('enTitle').textContent = art.topic_en;\n",
         new="      $('jaTitle').textContent = art.title_ja; $('enTitle').textContent = art.topic_en;\n      if (art.notice) { $('notice').textContent = art.notice; $('notice').hidden = false; }\n"),
    dict(id="J17", file="app.js", kind="REMOVE", why="記事切替の入口(Q.get('a'))",
         old="  init(Q.get('a') === 'moon' ? 'moon' : 'ai_island');", new="  init();"),
    dict(id="J18", file="app.js", kind="ADD", why="不具合是正: 不規則動詞(hold/give等)の3単現・ing形(holds/giving等)を太字対象に含める(DEVはholds heat inのholdを取りこぼした。月Standardで検出)",
         old="    if (IRR[w]) return IRR[w];\n",
         new=("    if (IRR[w]) {   // 不規則動詞: 原形・過去形・過去分詞に加え、3単現(-s/-es)・-ing形(語尾e脱落・子音重ね)も候補にする\n"
              "      var ex = IRR[w].slice();\n"
              "      IRR[w].forEach(function (x) {\n"
              "        ex.push(x + 's', x + 'es', x + 'ing');\n"
              "        if (/e$/.test(x)) ex.push(x.slice(0, -1) + 'ing');\n"
              "        if (!/[aeiou]$/.test(x) && x.length < 6) ex.push(x + x.slice(-1) + 'ing');\n"
              "      });\n"
              "      return ex;\n"
              "    }\n")),
    # ---------------- style.css ----------------
    dict(id="C1", file="style.css", kind="REMOVE", why="DEV試作の説明コメント",
         old=("/* END-USER-LISTENING-PAGE-PROTOTYPE-01 DEV試作。旧 user_test/unified.html の配色・カード構成・用語を継承。\n"
              "   本文下線(lk1-3)は最新の承認済み表示(family_x_ai_island_form_01)のものをそのまま使う。 */\n"),
         new="/* English Your Way 記事視聴ページ(End User向け)。本文下線(lk1-3)は承認済み表示と同一。 */\n"),
    dict(id="C2", file="style.css", kind="REMOVE", why="DEV訳(未承認)タグのスタイル",
         old=".trtag em{font-style:normal;font-weight:400;color:#b54708;margin-left:6px}\n", new=""),
    dict(id="C3", file="style.css", kind="REMOVE", why="仮データ注記(phnote)のスタイル",
         old=".phnote{margin:0 0 12px;padding:10px 14px;background:#fff4e5;border:2px dashed #e08a00;border-radius:8px;color:#7a4300;font-size:14px;font-weight:700;line-height:1.7}\n", new=""),
    dict(id="C4", file="style.css", kind="ADD", why="Voice説明文(hero直下)とKP 3列目のスタイル",
         old="@media(prefers-reduced-motion:reduce){*{transition:none!important}}\n",
         new=("@media(prefers-reduced-motion:reduce){*{transition:none!important}}\n"
              ".notice{margin:0 0 12px;padding:10px 14px;background:#f2f4f7;border:1px solid var(--line);border-radius:10px;color:#344054;font-size:13.5px;line-height:1.7}\n"
              ".notice[hidden]{display:none}\n"
              ".kpitem .th2{margin-top:6px}\n")),
]


def _apply(text: str, e: dict) -> str:
    if "between" in e:
        a, b = e["between"]
        if text.count(a) != 1 or text.count(b) != 1:
            raise SystemExit(f"edit {e['id']}: marker count != 1 (start={text.count(a)}, end={text.count(b)})")
        i, j = text.index(a), text.index(b)
        if i >= j:
            raise SystemExit(f"edit {e['id']}: marker order")
        return text[:i] + e["new"] + text[j:]
    if text.count(e["old"]) != 1:
        raise SystemExit(f"edit {e['id']}: 旧文字列の出現回数={text.count(e['old'])}(ちょうど1回が必要)")
    return text.replace(e["old"], e["new"])


def derive(dev_dir: Path = DEV_DIR) -> dict:
    out = {}
    for name in FILES:
        t = (Path(dev_dir) / name).read_text(encoding="utf-8")
        for e in EDITS:
            if e["file"] == name:
                t = _apply(t, e)
        out[name] = t
    return out


def main():
    res = derive()
    shas = {n: hashlib.sha256(t.encode("utf-8")).hexdigest() for n, t in res.items()}
    if "--write" in sys.argv:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for n, t in res.items():
            (OUT_DIR / n).write_bytes(t.encode("utf-8"))
        man = {"asset_build": "rev01-e", "derived_from": "DEV rev01-e(機械的派生。許可リスト=derive_assets_01.py EDITS)", "files": shas,
               "edits": [{"id": e["id"], "file": e["file"], "kind": e["kind"], "why": e["why"]} for e in EDITS]}
        (OUT_DIR / "ASSET_SHA256.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        lines = ["# production asset 差分一覧(DEV rev01-e -> production rev01-e)", "", "許可リスト(EDITS)に載った変更のみ。REMOVE=DEV専用機能の除去 / ADD=本番に必要な最小追加。", "",
                 "| id | file | 種別 | 内容 |", "|---|---|---|---|"]
        lines += [f"| {e['id']} | {e['file']} | {e['kind']} | {e['why']} |" for e in EDITS]
        lines += ["", "sha256:", ""] + [f"- {n}: `{s}`" for n, s in shas.items()]
        (HERE / "ASSET_DIFF_01.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(shas, indent=1))


if __name__ == "__main__":
    main()
