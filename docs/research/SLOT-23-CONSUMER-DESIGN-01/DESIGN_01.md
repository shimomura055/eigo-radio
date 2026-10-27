# DESIGN_01 区分②(Std追加解説)/③(本文ハイライト・短い日本語意味)の消費者設計
到達上限=DESIGN_READY(ユーザー確認待ち→Opus条件A→実装)。コード編集なし。

## (a) 区分②
**Adv**: 既存Part 1(`vocab_confirmed.json`≤5件、KP⊂vocab)がそのまま②を消費する=追加実装なし。承認済み(CURRENT_SPEC.md:2086)の意味は変えない。
**Std**(現行はvocab不可。`er119…:524-525`)。確定レコード側は`slot=display_only`(DESIGN_02:23)で保持済みなので、消費側だけの選択:
- A: StdにPart 1様式の簡易ブロック(英語表現/本文中の意味[確定gloss]/本文引用英文)を文字のみ表示。LLMなし=0円。解説文・訳なし。承認仕様(Part 1はAdvのみ)の例外が1点要る。
- B: Std②は③と同じ扱い(ハイライト+短い日本語意味のみ)。0円・追加ブロックなし。承認仕様は不変。②と③の見た目の差は無くなる(区分差=件数枠だけ)。
- C: StdにAdv Part 1と同一Prompt・T1の完全版。約0.16円/記事、Part 1の「Advのみ」仕様を拡張=ユーザー承認+Std全経路のrunner/ページ検証(`_assert_study_ready`等)の変更が必要。重い。
- 推奨=**B**(ユーザー定義はラベル「追加解説」のみで、承認済みPart 1のAdv限定仕様を変えずに区分を消費できる最小案。Stdは英語学習者向けの基礎水準で、Adv級の英語解説はそもそも想定外=Std Part 1はAdv限定と決めた経緯と整合。ただしユーザーが「Stdでも②は解説文が出る」意図ならC)。

## (b) ③(および区分に応じた本文ハイライト)
- 本文(台本表の各Script欄)で確定itemの`source_span`(本文表層形)を`<mark class="hl hl3">…</mark>`でハイライト。短い日本語意味(確定gloss)は、当該Script欄直下の`<ul class="hl-meaning">`(英語=日本語)で表示。ホバー(title)はスマホで効かないため補助にとどめ、主表示は直下リスト(JS不要、標準適合checkのtable/h2判定に触れない)。
- 音声は変更しない。③は文字のみ。LR(本文書換え)後の本文に対して**ビルド時**に再突合するため、書面不変=影響なし(書換えでspanが消えたらBLOCK、下記)。
- 共通builder(`er_user_listening_page_common_01.py`): `script_block(text, chunk_texts=None, audience=…, highlights=None)`に任意引数を追加。`highlights=None`/空=従来とバイト同一(既定)。`_find_chunk`同様に区間を非重複で切り出し`esc`を各片へ適用(⏸マーカーと併用可: 区間を集合し昇順で重ならない前提)。
- 区分別スタイルの要否はユーザー確認(USER_DECISION_DRAFT Q2)。

## (c) 確定レコードとの接続
- `unconsumed[]`のうち、③(CATEGORY3_NO_CONSUMER)とStd②(STD_CATEGORY2_NO_SLOT)をレコード側で`display_only`系として`load_verified_items(which="highlight")`(新which)から取得(G1を通す=確定保護と同じ単一アクセサ)。`unconsumed[]`は互換のため保持(消費可能になった項目は理由コードを`CONSUMED_BY_…`に更新するか別フィールドで管理=実装時に確定レコードのhash互換性を確認)。
- 件数上限・ID集合はレコードから読む(定数決め打ちしない)。

## (d) Family差
- X: 記事別script(`er019_*_page_*.py`)→`er120_part2_wiring_01.public_study_html(level=)`と`script_block`の呼出側。**Xは共通ページbuilderがScriptを描く箇所が記事別scriptに分散**=highlightsを渡す入口を共通関数`highlights_for_page(audio_dir, level, segments)`として1つ用意し、各記事別scriptの`script_block`呼出に1引数追加(既存X公開記事の再ビルドは各scriptを再実行)。
- Y: `er121…:1418,1467`の`cp.script_block`へ。Z: `er063…:2528`の`uc.script_block`へ。
- Std/Adv共通(levelキー a2/b1b)。③ itemsはレベル別に確定(Std/Advで別選定)。

## (e) 既存公開記事
- 確定レコード(origin hash chain付き)のある記事のみ再ビルド(HTMLのみ、音声不変、API 0)。レコードの無い旧記事は`highlights=None`=不変(遡及しない、またはユーザー要望があれば選定後に適用)。

## (f) 検証(G3拡張)・test/evidence計画
- G3(ビルド時): 各item `source_span`が(1)`source_sentence`内に実在 (2)その文が対象levelの表示本文(Script欄)に**ちょうど1箇所**で実在 (3)span範囲が他itemと重ならない (4)chunk/clip境界(Z)を跨がない。1つでも不成立→BLOCK+修正案(「spanを〜に直す/本文の〜と照合」)。黙って落とさない、部分適用しない。
- 大文字小文字: 照合は文中の実体(原文の大小文字)と`source_span`の完全一致を第一、不一致時のみcase-insensitive一意一致を許容し、表示は本文の実表記のまま。タイトル/見出し行(`Strategy`等)はハイライト対象外=本文Scriptのみ(`source_sentence_id`で文を特定、同一語が他文にあっても別文は触れない)。
- 多重一致: `source_sentence_id`の文内の最初の一意出現。文内に2回出る場合は`occurrence_sentence_ids`と`source_span`位置情報で特定、特定不能=BLOCK。
- test(API 0): ①highlights未指定でバイト同一(DefaultOffIsolation型相当、6経路) ②span正常(大小文字・活用形・句読点隣接) ③多重/不一致/clip跨ぎ=BLOCK ④LR後本文でspan消失=BLOCK ⑤check_page(table/h2判定、`_RAW_ID_RE`)に違反しない ⑥X/Y/Z×Std/Advの6経路ページ生成smoke(既存fixtureで)。evidenceは既存`er0xx_output`構造へ。

## 主なリスク
1. ハイライトのspan/文照合が確定レコードのみで足りるか(文が複数Script行に跨る)。
2. 既存公開記事の再ビルドがビルド再現性(Z `assemble`等)に副作用を持たない確認。
3. B案ではStd②の「追加解説」に解説文が無い(ユーザー意図との差)。
