# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: production asset(現行rev01-g。rev01-f・旧rev01-eは残置[rev01-e=藪の中のみ凍結])をDEVの『機械的派生』として作る(ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_02でrev01-fを追加)。

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
OUT_DIR = HERE / "rev01-g"
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
    # ---------------- rev01-f: 英語文と日本語訳の連動ハイライト(ENDUSER-EN-JA-LINKED-HIGHLIGHT-01。DEV rev01-eは不変、本番assetのみ) ----------------
    dict(id="J19", file="app.js", kind="ADD", why="rev01-f: 連動用の状態変数(jgEls=群id->JA要素, sidToG=文sid->群id, activeG=点灯中の群, jaHold=文と文の間も保持する群)",
         old="  var LEVEL_NAME = { std: 'Standard', adv: 'Advanced' };\n",
         new="  var LEVEL_NAME = { std: 'Standard', adv: 'Advanced' };\n  var jgEls = {}, sidToG = {}, activeG = null, jaHold = null;   // rev01-f: 英語文と日本語訳の連動(ja_align)\n"),
    dict(id="J20", file="app.js", kind="ADD", why="rev01-f: jaHtml()=日本語訳の群範囲(UTF-16 code unitオフセット)を<span class=jhl>で包む。訳本文は不変・ja_align無し/不正は従来表示。escは切り出し後",
         old="  function glossHtml(p) {",
         new=("  /* rev01-f: 英語文と日本語訳の連動。ja_align=[{g,sids,ja:[段落,開始,終了]|null}]。オフセットはJSのsubstringと同じUTF-16 code unit(正規化しない)。\n"
              "     訳本文は書き換えず、群の範囲を<span class=\"jhl\" data-jg>で包むだけ。ja_align無し/不正(範囲外・重なり)は従来どおりの素のテキスト。 */\n"
              "  function jaHtml(p, k, t) {\n"
              "    var al = p.ja_align;\n"
              "    if (!al || !al.length) return esc(t);\n"
              "    var gs = al.filter(function (g) { return g.ja && g.ja[0] === k && g.ja[1] >= 0 && g.ja[1] < g.ja[2] && g.ja[2] <= t.length; })\n"
              "      .sort(function (x, y) { return x.ja[1] - y.ja[1]; });\n"
              "    var out = '', pos = 0;\n"
              "    for (var i = 0; i < gs.length; i++) {\n"
              "      var a = gs[i].ja[1], b = gs[i].ja[2];\n"
              "      if (a < pos) return esc(t);\n"
              "      out += esc(t.substring(pos, a)) + '<span class=\"jhl\" data-jg=\"' + p.idx + ':' + gs[i].g + '\">' + esc(t.substring(a, b)) + '</span>';\n"
              "      pos = b;\n"
              "    }\n"
              "    return out + esc(t.substring(pos));\n"
              "  }\n"
              "  function glossHtml(p) {")),
    dict(id="J21", file="app.js", kind="ADD", why="rev01-f: 日本語訳の各段落をjaHtml()経由で出力(ja_align無しは従来出力と同一)",
         old="p.ja.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('')",
         new="p.ja.map(function (t, k) { return '<p>' + jaHtml(p, k, t) + '</p>'; }).join('')"),
    dict(id="J22", file="app.js", kind="ADD", why="rev01-f: render()末尾でjgEls/sidToGを構築(sentElsと同じ場所)。再構築時は点灯状態も初期化",
         old="    Array.prototype.forEach.call(document.querySelectorAll('[data-sid]'), function (e) { sentEls[e.dataset.sid] = e; });\n",
         new=("    Array.prototype.forEach.call(document.querySelectorAll('[data-sid]'), function (e) { sentEls[e.dataset.sid] = e; });\n"
              "    jgEls = {}; sidToG = {}; activeG = null; jaHold = null;\n"
              "    Array.prototype.forEach.call(document.querySelectorAll('.jhl'), function (e) { (jgEls[e.dataset.jg] = jgEls[e.dataset.jg] || []).push(e); });\n"
              "    parts.forEach(function (p) { (p.ja_align || []).forEach(function (g) { if (g.ja && jgEls[p.idx + ':' + g.g]) g.sids.forEach(function (s) { sidToG[s] = p.idx + ':' + g.g; }); }); });\n")),
    dict(id="J23", file="app.js", kind="ADD", why="rev01-f: highlight(sid)の先頭でjaLight(sid)を呼ぶ(連動の追加点はこの1箇所。nullグループのEN文はJAを点灯しない)",
         old="  function highlight(sid) {\n    if (sid === activeSid) return;\n",
         new=("  function jaLight(sid) {   // rev01-f: 英語文のon/offに連動して、対応する日本語群だけを点灯する\n"
              "    var g = sid ? (sidToG[sid] || null) : jaHold;   // 文と文の間: 同一群の前後の文に挟まれている間(jaHold)は消さない\n"
              "    if (g === activeG) return;\n"
              "    if (activeG && jgEls[activeG]) jgEls[activeG].forEach(function (e) { e.classList.remove('on'); });\n"
              "    activeG = g;\n"
              "    if (g && jgEls[g]) jgEls[g].forEach(function (e) { e.classList.add('on'); });\n"
              "  }\n"
              "  function gapGroup(g) {   // 文と文の間(2秒未満)で前後の文が同じ群なら、その群を返す\n"
              "    var lo = 0, hi = sync.length - 1, k = -1;\n"
              "    while (lo <= hi) { var m = (lo + hi) >> 1; if (sync[m].start <= g) { k = m; lo = m + 1; } else hi = m - 1; }\n"
              "    if (k < 0 || k + 1 >= sync.length) return null;\n"
              "    var a = sidToG[sync[k].sid], b = sidToG[sync[k + 1].sid];\n"
              "    return (a && a === b && sync[k + 1].start - sync[k].end < 2.0) ? a : null;\n"
              "  }\n"
              "  function highlight(sid) {\n    jaLight(sid);\n    if (sid === activeSid) return;\n")),
    dict(id="J24", file="app.js", kind="ADD", why="rev01-f: tick()で文と文の間の保持群(jaHold)を更新してからhighlight()を呼ぶ(再生・シーク・クリック・レベル切替は従来どおりtick/highlightに集約)",
         old="    if (sync.length) highlight(findActive(gt()));\n",
         new="    if (sync.length) { var ga = findActive(gt()); jaHold = ga ? null : gapGroup(gt()); highlight(ga); }\n"),
    dict(id="J25", file="app.js", kind="ADD", why="rev01-f: 検証用の状態__EUPに点灯中のJA群(jg)を追加",
         old="syncKind: syncKind, src: A.src };", new="syncKind: syncKind, src: A.src, jg: activeG };"),
    dict(id="C5", file="style.css", kind="ADD", why="rev01-f: 日本語訳の対応群の点灯(.sent.onと同じ変数・同じ見た目)",
         old=".kpitem .th2{margin-top:6px}\n",
         new=".kpitem .th2{margin-top:6px}\n.jhl{border-radius:4px;transition:background .12s}\n.jhl.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}\n"),
    # ---------------- rev01-g(ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B) ----------------
    dict(id="H4a", file="index.html", kind="ADD", why="rev01-g: キャッシュ更新用のbuild-id(rev01-e -> rev01-g。assetの更新が古いJSキャッシュで隠れない)",
         old='<meta name="build-id" content="rev01-e">', new='<meta name="build-id" content="rev01-g">'),
    dict(id="H4b", file="index.html", kind="ADD", why="rev01-g: style.cssのcache-bust",
         old='href="style.css?v=rev01-e"', new='href="style.css?v=rev01-g"'),
    dict(id="H4c", file="index.html", kind="ADD", why="rev01-g: body data-build",
         old='<body data-build="rev01-e">', new='<body data-build="rev01-g">'),
    dict(id="H4d", file="index.html", kind="ADD", why="rev01-g: app.jsのcache-bust",
         old='src="app.js?v=rev01-e"', new='src="app.js?v=rev01-g"'),
    dict(id="J26", file="app.js", kind="ADD", why="rev01-g: Previewカードにも日本語訳(trHtml)を出す(訳が無いPreviewは空文字=表示不変)。Adv Previewの生成訳の表示場所",
         old="      out += card('Preview', ja ? '<div class=\"jp\">' + sentHtml(p) + '</div>' : sentHtml(p), { part: p.idx, btn: btns(p) });",
         new="      out += card('Preview', (ja ? '<div class=\"jp\">' + sentHtml(p) + '</div>' : sentHtml(p)) + trHtml(p), { part: p.idx, btn: btns(p) });"),
    dict(id="J27", file="app.js", kind="ADD", why="rev01-g: Vocabulary単体音声の状態(mode='vocab'・vocabI=再生中の項目・resumeAt=再生前の通し位置)",
         old="var mode = 'full', curIdx = null, kpEnd = null;   // 'full'(全体音声) / 'kp'(Key Phrase英語区間のみ)",
         new="var mode = 'full', curIdx = null, kpEnd = null, vocabI = null, resumeAt = null;   // 'full'(全体音声) / 'kp'(Key Phrase英語区間のみ) / 'vocab'(Vocabulary項目の単体音声)"),
    dict(id="J28", file="app.js", kind="ADD", why="rev01-g: Vocabulary & Expressionsの各項目(summary内=閉じていても押せる)に英語音声の再生ボタン(article.jsonのvocab[i].audioがある項目)",
         old="'><summary><b class=\"vh\">' + esc(it.heading) + '</b><span class=\"vm\">' + mean + '</span></summary><dl>' +",
         new="'><summary><b class=\"vh\">' + esc(it.heading) + '</b><span class=\"vm\">' + mean + '</span>' + (it.audio ? '<button type=\"button\" class=\"seek part vplay\" data-act=\"vocab\" data-i=\"' + vi + '\" aria-label=\"' + esc(it.heading) + ' の英語音声を再生\">▶ 英語音声</button>' : '') + '</summary><dl>' +"),
    dict(id="J29", file="app.js", kind="ADD", why="rev01-g: playVocab/endVocab(単体mp3を共有プレーヤで再生。終端で通し再生の状態へ戻す=再生前の位置・自動再生なし)",
         old="  function endKp() {",
         new=("  function playVocab(vi) {   // rev01-g: Vocabulary項目の英語音声(KPと同じ契約の単体mp3。区間指定なし)\n"
              "    var it = L.vocab && L.vocab[vi], au = it && it.audio; if (!au) return;\n"
              "    if (mode !== 'vocab') resumeAt = mode === 'full' ? (A.currentTime || 0) : (mode === 'kp' && curIdx != null ? parts[curIdx].start : null);\n"
              "    mode = 'vocab'; vocabI = vi; curIdx = null; kpEnd = null;\n"
              "    ensureSrc(new URL(au.file, location.href).href);\n"
              "    withMeta(function () { A.currentTime = 0; playNow(); }); labels();\n"
              "  }\n"
              "  function endVocab() {   // 単体音声の終端: 停止して通し再生の状態へ戻す(自動再生しない)\n"
              "    var at = resumeAt; A.pause(); mode = 'full'; vocabI = null; resumeAt = null;\n"
              "    ensureSrc(audioUrl(L.main)); withMeta(function () { A.currentTime = at || 0; tick(); });\n"
              "  }\n"
              "  function endKp() {")),
    dict(id="J30", file="app.js", kind="ADD", why="rev01-g: vocabモードの長さ(単体mp3のdur)",
         old="var d = mode === 'kp' && curIdx != null ? parts[curIdx].dur : L.total_sec;",
         new="var d = mode === 'vocab' && vocabI != null ? L.vocab[vocabI].audio.dur : (mode === 'kp' && curIdx != null ? parts[curIdx].dur : L.total_sec);"),
    dict(id="J31", file="app.js", kind="ADD", why="rev01-g: vocabモードは全編のどの部分でもない(通し再生のpart強調・文ハイライトを出さない)",
         old="    if (mode === 'kp') return curIdx;\n",
         new="    if (mode === 'vocab') return null;\n    if (mode === 'kp') return curIdx;\n"),
    dict(id="J32", file="app.js", kind="ADD", why="rev01-g: nowLabelにvocab項目名",
         old="$('nowLabel').textContent = (mode === 'kp' && curIdx != null) ?",
         new="$('nowLabel').textContent = (mode === 'vocab' && vocabI != null) ? ('英語音声: ' + L.vocab[vocabI].heading) : (mode === 'kp' && curIdx != null) ?"),
    dict(id="J33", file="app.js", kind="ADD", why="rev01-g: vocabモード中はtickが文ハイライト(英語・日本語)を更新しない(単体音声の秒を全編の秒と取り違えない)",
         old="    if (sync.length) { var ga = findActive(gt()); jaHold = ga ? null : gapGroup(gt()); highlight(ga); }\n",
         new="    if (sync.length) { var ga = mode === 'vocab' ? null : findActive(gt()); jaHold = (ga || mode === 'vocab') ? null : gapGroup(gt()); highlight(ga); }\n"),
    dict(id="J34", file="app.js", kind="ADD", why="rev01-g: Vocabulary再生ボタンのclick(summary内のためdetailsの開閉を抑止)",
         old="    if (b.dataset.act === 'stop') { A.pause(); tick(); return; }",
         new="    if (b.dataset.act === 'vocab') { e.preventDefault(); playVocab(Number(b.dataset.i)); return; }\n    if (b.dataset.act === 'stop') { A.pause(); tick(); return; }"),
    dict(id="J35", file="app.js", kind="ADD", why="rev01-g: 単体音声の終端でendVocab()",
         old="A.addEventListener('ended', function () { tick(); });",
         new="A.addEventListener('ended', function () { if (mode === 'vocab') endVocab(); else tick(); });"),
    dict(id="J36", file="app.js", kind="ADD", why="rev01-g: 検証用の状態__EUPにvocab項目(vi)を追加",
         old="src: A.src, jg: activeG };", new="src: A.src, jg: activeG, vi: vocabI };"),
    dict(id="C6", file="style.css", kind="ADD", why="rev01-g: Vocabulary再生ボタンのレイアウト(PC=右横、mobile=意味の下)",
         old=".jhl.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}\n",
         new=".jhl.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}\ndetails.vi summary .vplay{margin-left:12px;vertical-align:middle;font-size:13px}\n@media(max-width:640px){details.vi summary .vplay{display:block;margin:6px 0 4px 0}}\n"),
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
        man = {"asset_build": "rev01-g", "derived_from": "DEV rev01-e + EDITS(機械的派生。許可リスト=derive_assets_01.py EDITS。rev01-fは連動ハイライトJ19-J25/C5、rev01-gはPreview訳J26・Vocabulary音声J27-J36/C6・build-id H4を追加)", "files": shas,
               "edits": [{"id": e["id"], "file": e["file"], "kind": e["kind"], "why": e["why"]} for e in EDITS]}
        (OUT_DIR / "ASSET_SHA256.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        lines = ["# production asset 差分一覧(DEV rev01-e -> production rev01-g)", "", "許可リスト(EDITS)に載った変更のみ。REMOVE=DEV専用機能の除去 / ADD=本番に必要な最小追加。", "",
                 "| id | file | 種別 | 内容 |", "|---|---|---|---|"]
        lines += [f"| {e['id']} | {e['file']} | {e['kind']} | {e['why']} |" for e in EDITS]
        lines += ["", "sha256:", ""] + [f"- {n}: `{s}`" for n, s in shas.items()]
        (HERE / "ASSET_DIFF_01.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(shas, indent=1))


if __name__ == "__main__":
    main()
