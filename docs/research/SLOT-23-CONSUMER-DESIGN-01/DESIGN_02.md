> 【失効】本書はDESIGN_03.mdに置換された(Opus条件A所見反映)。参照しないこと。
# DESIGN_02 学習項目①②③の表示仕様(DESIGN_01を置換する正本)
ユーザー正式決定(2026-10-27、`APPROVED_FOR_PRODUCTION`、到達目標`PRODUCTION_WIRED`、X/Y/Z×Std/Adv全6経路)を反映。read-only設計(コード編集0・API 0)。到達上限=DESIGN_READY(Opus条件Aレビュー→実装)。
DESIGN_01の(a)案A/B/C選択・(b)`<mark>`方式・(f)G3「chunk境界を跨がない」「文内に2回=BLOCK」は本書で**撤回**(理由は各節に明記)。USER_DECISION_DRAFT_01(Q1-Q3)は決定済みのため失効。
原文=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`(以下USER.md)。矛盾の全リスト=`SPEC_CONFLICT_02.md`。

## 0. 用語・前提・解釈(判断候補の扱い)
- **Part 1**=学習テキスト「Vocabulary & Expressions」(既存、`er003_kp_general_explanation_01.py`)。表示項目=英語表現/本文中の意味(確定gloss)/本文の英文/日本語訳(T1)/解説(`assemble_part1`=`er003…:364-400`、`render_html_block`=`:475-497`)。
- **解釈(判断候補#1、分類B=承認範囲内で自己解決)**: USER.mdの「英語解説」は、既存仕様の語法どおり**Part 1の解説=英語表現についての解説**(解説文は既存Prompt通り日本語の説明文、`PROMPT_HEAD`:39-44「…下の英語表現それぞれの『一般的な解説』を日本語で書いて」)。「Std向けの適切な難易度」=**Prompt中の学習者像とやさしさの指示のみ**を調整する(USER.md:95「項目構成は既存Adv側を踏襲しStdに必要な難易度調整のみ」、:97「新しい説明方式を追加しない」)。解説本文の言語を英語へ変えるのは「新しい説明方式」に当たるため採らない。万一ユーザー意図が「解説本文を英語で書く」なら項目構成の変更になり、新たな判断(D)になる。Fableが報告9項目の3で「Std②=Adv同型(日本語解説・Std向け難易度)」と明記して拾う。
- Std ②の件数: ①3+②2=5(AI島。フォーム上限は①+②=5)。Part 1の最大件数は`MAX_PHRASES=5`(`er003…:68`)で足りる。

## A. Std Part 1(区分②)= 既存Adv Part 1生成工程の`level`引数化
### A-1 入力(ユーザー確定の保持)
- 入力=確定レコード①+②(`vocab_confirmed.json`相当。Std ①3+②2=5件、順序は①→②のai_rank順=`build_items``er128:252-260`)。Advと同一の単一アクセサ`rv.part1_items(kp_dir)`(`er119:1135-`)+`load_verified_items(which="part1")`(`er128:1258-`)を使い、a2でも`kp_dir`=`<run>/a2/key_phrases`。ユーザー確定の英語・gloss・順序は後続工程で書換えない(KCP G1が`verify_items_against_record`で守る=Advと同一機構)。
- 生成Promptへ送るのは従来どおり`used_form`のみ(`strict_phrases`、本文・gloss・引用文は送らない=`CURRENT_SPEC.md:2086`)。ユーザー確定の「英語表現・日本語訳」は**表示時**に確定値をそのまま使う(`meaning_in_text_ja`=確定gloss、`assemble_part1`:`gloss`)。

### A-2 level引数化(Adv出力はバイト同一)
- `er003_kp_general_explanation_01.py`: `PROMPT_HEAD`を`PROMPT_HEADS={"b1b": 現行そのまま, "a2": Std版}`に。`PROMPT_BODY`・出力形式・構造検査は共通のまま。`PROMPT_TEMPLATE_SHA256`(b1b)は現行値を維持し、a2は`PROMPT_TEMPLATE_SHA256_A2`を追加。Std版Headは現行Headの**学習者像の1文**(「B1〜B2相当」→「A2〜B1相当(Standard)」)と、難易度指示を**1項目**(「やさしい語で書き、専門用語・文法用語を使う場合は短く言い換える。解説の観点・項目・分量の考え方は変えない」)のみ追加する(Opus条件Aレビュー対象の唯一のPrompt差分)。
- `build_prompt(phrases, level="b1b")`、`phrases_signature(items, model=None, level="b1b")`: payloadへ`"level"`を**a2のときだけ**追加(b1bのsignature不変→既存Adv成果物はstaleにならない)。`generate_*`/`resolve_*`/`require_fresh_*`に`level`を通し、保存docへ`level`を記録(a2 docをAdvが誤って使わない)。
- `write_study_text(..., level="b1b")`: 保存`level`値を`"Advanced"|"Standard"`に。`study_html_for_audio_dir(audio_dir, items=None, level="b1b")`: `b = f"{audio_dir}/{level}"`。既定=従来バイト同一。
- `er003_kp_source_sentence_ja_01.py`(T1訳): Promptは**変更しない**(翻訳はレベル非依存。学習者像`B1〜B2`は現行のまま共通=Advバイト同一・Stdにも同一Promptを使用。署名・ファイル名は`level`のdir分離のみ)。
- 品質検査(USER.md:90,:157-159): **既存Adv検査を同一適用**=①`validate_phrases`/`check_prompt_isolation`(課金前)②`parse_response`構造検査(見出し数・番号・正規化見出し一致・日本語本文≥`MIN_BODY_CHARS`=30字・`PAGE_FORBIDDEN_RE`)③`assemble_part1`(gloss HR/未評価/空→STOP、引用英文の本文逐語実在、signature最新)④応答model_id一致(不一致はretryなしSTOP)⑤ページ側`study_html_for_audio_dir`の現在値照合。Std固有の追加検査・独自品質基準は**追加しない**(USER.md:97)。
- retry/fallback/resume: 既存のまま(技術retry 1回→fail-closed、旧方式fallbackなし)。resume時は`ensure_stage`/signatureでreuse(API 0)、確定itemsはsignature(expression列)に含まれ、KCP G4相当(`verify_items_against_record`)が再開時の確定保持を検査。

### A-3 Std生成のFamily別配線(stage名・path)
| Family | 生成点(現行はb1bのみ) | 新(両level) |
|---|---|---|
| X | scaffold内`generate_part1_all_for_b1b`(`er019:904-921`)+`--stage study_text` | `generate_part1_all(level)`(関数名`_for_b1b`は互換別名を残さず置換)。a2もKP PASS後・TTS前。`_part1_explanations_path(out_dir, level)`は既にlevel引数あり(:430) |
| Z | `stage_kp`内`kp_part1_b1b`/`kp_part1_ja_b1b`(`er026:2196-2199`) | `kp_part1_{lv}`/`kp_part1_ja_{lv}`。`E2E_KP_EXTRA_REGEN_NAMES`(:1135)へ`_a2`追加。path`key_phrases/{lv}/` |
| Y | `kp` stage内`PART1_STAGE`(`er121:321,669-671`) | `PART1_STAGES={lv:…}` |
- 失敗時: Adv同様、Part 1失敗はTTS前STOP(KP確定は保持)。Stdの失敗がAdvの進行を止めないか: Std/Advは別level dir・別stageなので相互独立。ただし「どちらかのlevelのPart 1がNG→そのlevelのTTS前STOP」は従来のAdv規則をStdへ同型適用。

### A-4 記録・マーク(遡及なしの技術的根拠。§F)
- `kp_human_review.json`に`std_part1: true`(新規review作成時に付与。b1bは不問)。`vocab`許可/必須判定は`vocab_enabled(level, review) = level=="b1b" or review.get("std_part1")`の1関数に集約(S1-S8,S9,S11)。

## B. 本文ハイライト(二重下線方式。USER.md:96-115)
### B-1 表示仕様(決定どおり)
| 区分 | 要素 | 書式 |
|---|---|---|
| ① | `<strong class="lk1">` | 太字+二重下線 |
| ② | `<strong class="lk2">` | 太字+通常下線 |
| ③ | `<span class="lk3">` | 通常下線のみ(太字なし) |
- CSS(`HIGHLIGHT_CSS`、単一定数。`font-size:inherit;color:inherit;background:none`):
  `.lk1{font-weight:700;text-decoration-line:underline;text-decoration-style:double;-webkit-text-decoration-style:double;text-underline-offset:3px;text-decoration-thickness:from-font}`
  `.lk2{font-weight:700;text-decoration:underline;text-underline-offset:2px}` / `.lk3{font-weight:inherit;text-decoration:underline;text-underline-offset:2px}`
  背景マーカー・色なし。二重下線の見え方は実ブラウザ(PC幅+スマホ幅375/390px・DPR2/3)で撮影確認(IMPL_PLAN F、受入条件の4)。thicknessは実測で調整(間隔が潰れるスマホ幅で2本に見えない場合のみ`1.5px`等へ)=ユーザー承認見た目(AI島Std/Advのモック確認済みB案)からの逸脱をしない範囲。
- **コピー/読み上げ**: 記号・疑似要素(`::before/after`)・絵文字を一切追加しない。装飾はCSSのみ=`textContent`は本文と同一。`aria-label`/`title`でテキストを足さない(③の訳は後述の独立要素)。開発用`⏸`は`audience="dev"`のみ(§C)。
- **凡例**(任意・1行): 節先頭または`intro_html`に「本文の下線: 太字+二重下線=Key Phrase/太字+下線=追加解説/下線のみ=意味表示(下の一覧)」。スマホで区分が分かる補助(決定「スマホでも区分の違いが分かる」)。台本表の外(`div.script`の外)に置くため`check_page`のscript判定に触れない。判断区分B(表示補助、承認見た目の文言追加のみ)。
- **③の短い日本語訳**: 当該Partの台本セル(`<td>`)の`div.script`群の直後に`<ul class="hl-meaning">`(各`<li><b>英語(本文表層形)</b> = 日本語訳</li>`)。日本語訳=確定`japanese_gloss`(ユーザー確定の公式訳、`ja_gloss_status=official`のみ=`cmd_from_form`が保証)。JS不要・スマホで常時可視。補助として`<span class="lk3" title="訳">`のtitle属性を付けてよい(PCホバーのみ。主表示ではない)。①②には出さない(①=KP行、②=Part 1「本文中の意味」が選定区分の表示。USER.md:117「日本語訳の表示は選定区分の仕様に従う」)。`<ul>`は`div.script`・`table`・`h2`の外=`check_page`(`er_user_listening_page_common_01.py`のtable/h2/script判定)に触れない。
- 本文テキスト・改行・段落・句読点・TTS・Chunk・ポーズ: 不変。ハイライトは`esc()`済み本文を**同一文字列のまま**タグで包むだけ(包む前後で`html.unescape(strip_tags(x)) == text`をassert=不変性の実行時検証)。

### B-2 `script_block`拡張(共通builder、単一の描画入口)
```python
# er_user_listening_page_common_01.py
def script_block(text, chunk_texts=None, audience="public", warnings=None, highlights=None) -> str
# highlights=None/[] → 現行とバイト同一(既定)。list[dict]: {"kind":1|2|3,"start":int,"end":int,"candidate_id":str}
def render_script_html(text, chunk_texts, audience, highlights, warnings=None) -> str   # 内部。位置の併合描画
def script_blocks_for_part(texts, highlights_for_part, chunk_texts_list, audience) -> list[str]  # Zのクリップ連結用
def meaning_list_html(items) -> str   # ③の「英語=訳」ul(空なら"")
HIGHLIGHT_CSS: str   # CSS.の末尾へ連結する単一定数(Y/Z共通CSS・X player CSS・X公開ページCSSが同じ定数を使う)
```
- 併合描画: 文字位置の境界集合 = {各highlightのstart,end} ∪ {dev時の各Chunk境界位置}。昇順に区切り、各片を`esc`。highlight内の片は開きタグで包み、**Chunk境界の`⏸`マーカーspanはハイライトの外**に出す(highlightタグを一度閉じて`⏸`を置き、再度開く)。→`audience="dev"`でも装飾が`⏸`に掛からず、`public`は従来どおり`⏸`0個(`count_chunk_markers`不変)。
- Chunk境界跨ぎ(DESIGN_01の「跨がない」条件を**撤回**): 理由=Chunk境界は音声合成単位で表示のみの`⏸`と無関係、ハイライトは表示専用でTTS/Chunk/ポーズを変えない(USER.md:106-107)。跨いでも誤表示は生じず、過剰制約で制作を止めない(USER.md:138)。ZのようにChunkごとに別`div.script`になる場合は、跨ぐ範囲を**片ごとに同種のタグへ分割**して描画(各片の連結文字列=元の表層形)。
- 同一位置の入れ子は禁止(下記B-4)。タグは平坦(strongの中に別タグを入れない)。

### B-3 確定情報の取得(単一アクセサ)と照合アルゴリズム
**取得**: `er128.load_verified_items(kp_dir, level=, which="highlight")`(新which)。内部で`rv.require_final_consistent`(G1)→確定レコード(`display_spec`マーク付きのみ。無し→`[]`=従来描画)→itemsの①(category1,slot=kp)・②(category2,slot=vocab)と`unconsumed[]`のうち`category==3`を結合し、**候補doc**(`kp_candidates.json`、`candidates_sha256`がレコードの`origin.candidates_sha256`と一致することを確認)の`candidate_id`で`item.source_span`・`source_sentence`・`source_sentence_id`・`occurrence_sentence_ids`・`selection_resolution_method`を付与して返す。件数・ID集合はレコードから読む(定数決め打ちなし)。③のreasonは新規`CATEGORY3_HIGHLIGHT`(旧`CATEGORY3_NO_CONSUMER`は読取互換のみ)。

**照合アルゴリズム**(純関数。新module `er_learning_highlight_01.py`。既存の本文一致規約を**再利用**し新方式を作らない): 入力=spec(上記)・`article_text`(`<run>/<lv>/article.md`、候補生成時と同一の文分割に使う)・display_units(表示順の台本テキスト群: X=`parts.json`のfull_story_part1-3、Y=`parts["segments"]`、Z=`g["script"]`のクリップ群をPart単位に連結。各unitに元ブロックのオフセット表)。
1. **文の特定**(候補データ優先、USER.md:126): 候補生成と同じ`er028…build_sentence_units(article.md)`で`source_sentence_id`(`S{i+1}`)の文`units[i].raw_text`を得る。これが`source_sentence`と等しいことを確認(不一致=候補docと本文の不整合→fail-closed)。
2. **語形の特定**: その文内で`er105_kp_fulltext_selector_01._phrase_pattern(source_span)`(語境界・アポストロフ/ダッシュ許容・大小無視。選定時と同一規約)の最初の一致を取る。`carry over`→本文表層形`carried over`は候補が`source_span="carried over"`を保持しているため、原形(`used_form`)の再活用推定は**行わない**(`take a detour`→`taken a detour`、`look at separately`→`looked at separately`、`erase`→`erased`も同様に`source_span`が正本)。選定時の`locate_phrase`が`hits[0]`を採る規約(`first_of_N`)と同一の「最初の一致」を使うので、候補生成が選んだ出現と一致する。
3. **複数出現**(USER.md:130-132): 本文に複数回出ても`source_sentence_id`が出現を特定する(`occurrence_count>1`は`fulltext_exact_first_of_N`として許容。AI島実データ: Std`Strategy`=S2・3回、Adv`technique`=S25・3回、いずれも`source_sentence_id`で1箇所に特定可)。**ハイライトは特定した1出現のみ**(KP音声・Part 1の引用文と同じ出現。他の出現は装飾しない)。同一文内に2回以上一致する場合も最初の出現(選定規約と同じ)。不一致を「複数出現=不合格」にしない。
4. **表示本文への写像**: 特定した文を表示本文(display_units)で`_norm_match`相当(NFKC・引用符統一・空白畳み)で探し、文内の`source_span`位置を表示文字オフセットへ写像(表示本文が正規化前の生文字列のまま、Unicode/引用符差はオフセット対応表で戻す)。Local Rewrite後の表示本文で文が見つからない(文が書き換わった)場合は**fail-closed**(誤箇所に出さない)。
5. **fail-closed**: 上記いずれかで特定不能→`ISSUE`(`raise_issue`同型。rc=4待機ではなく**ページ生成前STOP**、item・原因コード・sentence_id・span・本文断片・修正案を`confirmed_content_issue.json`へ記録。原因調査はUSER.md:134の要求どおりレポートに残す)。原因コード: `HL_SENTENCE_ID_UNKNOWN`/`HL_SENTENCE_MISMATCH`/`HL_SPAN_NOT_IN_SENTENCE`/`HL_SENTENCE_NOT_IN_DISPLAY(LR等で書換え)`/`HL_OVERLAP_PARTIAL`。部分適用・黙って落とすことをしない。
6. 事前検査(早期検出): `confirm --from-form`時にも同じ解決(article.md基準)を実行し、特定不能は確定前に`ISSUE`(候補doc側の欠陥はここで判明=TTS費用前)。表示本文基準(LR後)の最終検査はG3。

### B-4 重なり・部分一致(USER.md:136。KCP Gateと整合)
- KCP側: ①②は`validate()`のRedundancy QAで意味重複をユーザー選定時に排除済み(`er119:531-551`)。③はQA対象外→③と①②・③同士の文字範囲重複は表示層で扱う。
- 優先度: ①>②>③。
  - 完全一致/低優先が高優先に**完全に包含**される(例:②`attention`が①`worth paying attention to`内、同一span): 低優先は**装飾しない**(包含先の装飾が適用済み)。③の訳リストには残す(訳を見る手段を失わない)。→`NOTICE`(記録のみ、**停止しない**=過剰制約回避)。
  - **部分的に交差**(どちらの区間にも他方の外側がある): 表示不能(入れ子禁止)→ISSUE`HL_OVERLAP_PARTIAL`+修正案(どちらかを別表現にする)。発生はごく稀(連続語句の端点交差)。
  - 同優先同士の包含(③⊂③)も包含ルール(広い方のみ装飾)。
- 隣接(間に空白1つのみ)は別要素として個別に装飾(連結しない)。

### B-5 開発専用Chunkマーカーとの共存(USER.md:115)
`audience="public"`(既定)の出力に`⏸`/`chunk-mark`が0個であること(既存`check_page(audience="public")`+`count_chunk_markers`)。ハイライト導入でこの検査を弱めない。`audience="dev"`では§B-2のとおり`⏸`はハイライトの外・1境界1個。

## C. X/Y/Z 配線点(file:line、全6経路)
| Family | 本文を描く箇所(現行) | ハイライトの入口 | Part 1/Std Part 1 |
|---|---|---|---|
| **Z** | `er063_family_z_audio_01.py:2528`(Full Story各クリップ`uc.script_block(g["script"], chunk_texts, audience)`)・`:2554`(その他は`script_block(r["script"])`=非対象)。`build_pages`:`:2557-2610` | `_user_page_rows`→`build_page_rows`でPart単位に`g["script"]`群を`script_blocks_for_part`へ渡す。`build_pages(…, highlights_by_level=None)`新引数(None=従来バイト同一)。runnerの`stage_pages`(`er026:2476-2495`)が`load_verified_items(which="highlight")`→解決→渡す | `study_html_by_level["a2"]`にもPart 1(`stage_pages`:2484-2491) |
| **Y** | `er121_family_y_audio_01.py:1467`(`cp.script_block(parts["segments"][sid], chunk_texts, audience)`)、`:1418`(`_script`はFull Story以外=非対象) | `build_page_rows(…, highlights=…)`でsid単位に渡す。`stage_pages`(`er121_family_y_runner_01.py:1192-1215`)が解決 | `study_html`のstd側(:1208)をPart 1込みへ |
| **X(Production player)** | `er019_family_x_audio_production_runner_01.py:3017-`の`_build_level_table`(`info["text"]`を`player_common.render_timeline_row`へ。dev時のみ`script_html_with_chunk_markers`で上書き=:3056-3058)。`build_player_html`:3086-3150(CSS=`player_common.PLAYER_STANDARD_CSS`) | Full Story Part行の`info["text"]`を共通`render_script_html`に置換。`HIGHLIGHT_CSS`を`PLAYER_STANDARD_CSS`に連結。`--stage player`が解決 | `player`(:3725-3749)のa2側に`part1_study_html_for_player(level="a2")` |
| **X(公開ページ)** | 個別`er019_*_page_*.py`は`pp.seg_html`でテキストを組み、共通builderを使わない。AI島=`tools/build_aif3_listening_page_01.py`(Script行: `blocks=[f"<div class='script'>{esc(info['text'])}</div>"]`)(`blocks=[f"<div class='script'>{esc(info['text'])}</div>"]`)。最新generic=`er019_nws2_final_page_01.py`(Part 1は`study_html_for_audio_dir(pp.RUN)`のb1b固定、Part 2・Stdなし) | **新規 `er019_family_x_listening_page_01.py`**: `tools/build_aif3…`を`--slug --run-name --web`引数のProduction標準builderへ昇格(共通`render_standard_page`+`script_block(highlights=…)`+`public_study_html`)。AI島はこれで再ビルド。旧per-article script(`er019_nws2…`等)は**遡及なしのため未改修**(新規記事はこの標準builderを使うと`er019_nws2_final_page_01.py`の先頭docstringに明記し、旧scriptが確定レコード付きrunで呼ばれたら`display_spec`検出でSTOP=旧経路を新規記事で使えない) | `public_study_html`(`er120:512-531`)がa2でもPart 1 |
- 共通化の原則: 本文のハイライト描画は`render_script_html`1箇所、解決は`er_learning_highlight_01.resolve_highlights`1箇所、確定情報取得は`load_verified_items(which="highlight")`1箇所(R-1/R-2同型の「描画は1関数」)。
- `audience=dev`マーカーとの併用はB-2/B-5のとおり。

## D. KCP G3拡張(検査項目。`er128.verify_outputs`と同型・fail-closed)
`verify_highlight_outputs(kp_dir, level, page_texts, display_units)`(新、`er128_kp_highlight_01.py`に置き、`verify_outputs`から1行委譲)。`display_spec`マーク付きレコードのみ検査(無し=何もしない)。
1. **網羅**: 確定レコードの①②③の全itemが、ページHTMLに期待どおりの区分クラス(lk1/lk2/lk3)で**ちょうど1回**出現(包含で省略されたものは`NOTICE`記録と照合)。欠落・余剰・区分違い=BLOCK(rc=3 INTEGRITY)。
2. **一致**: 各装飾要素のtextContentが解決結果の表層形(`source_span`の本文実表記)と一致。
3. **本文不変**: ページから装飾タグを剥がしたScript文字列が元の台本テキストと完全一致(本文を変えていない)。
4. **③訳**: `ul.hl-meaning`の各訳が確定`japanese_gloss`と完全一致、全③を網羅。
5. **public混入**: `⏸`/`chunk-mark`が0(既存)。装飾タグ以外の追加テキスト・記号が`div.script`に増えていない。
6. **Std Part 1**(Std新規): `vocab_page_paths`に対し、確定レコードの各itemの`japanese_gloss`がPart 1行に表示(現行`er128:818-`のb1b限定を両level化)、`study_text`の`meaning_in_text_ja`==確定gloss。
7. **LR整合**: LR(`note_lr_fired`/`confirmed_kp_lr_overlap.json`)で書換えられた範囲と重なる項目は、ハイライト解決が失敗した時点でISSUEに既存の`lr_overlap`記録を添付(原因調査)。
8. **G1(record↔artifact)**: `_artifact_diffs`のvocab突合をStd新規へ(S11)。`PROTECTED_ITEM_FIELDS`・`content_sha256`定義は不変。

## E. Std節の構成順(GPGとの配置)
Std節: 全編通し再生 → 台本表(ハイライト+③訳リスト) → **Part 1「Vocabulary & Expressions」**(新) → **Part 2「Grammar & Sentence Structure」**(Top1/0件固定文面)。Advと同じ`compose_page_html(part1_html, result)`(`er120_part2_wiring_01.py:507`)で、Part 1が先・Part 2が後。GPGの文法選定・事前生成・凍結(`er120_part2_grammar_production_01.py`、`er128`のgrammar系)には触れない。AI島は文法0件=Part 2に固定文面(既存挙動)。

## F. 遡及なし・既存ページ・AI島(USER.md:53-60,:140-155)
- **マーク方式**(feature flagではない=承認済み仕様。環境変数・設定dictで切替不可): review`std_part1:true`、確定レコード`display_spec:"LEARNING_ITEMS_123_V1"`。新規作成経路(`new_review`/`_new_record`)が常に付与。マーク無し=従来描画(ハイライトなし・Std Part 1なし)、`display_spec`はハッシュ対象外(`content_sha256`/`PROTECTED_ITEM_FIELDS`は不変。`record_sha256`は全体ハッシュなのでmigration時に再計算)。
- **既存公開ページ**: 再ビルド・差替えなし。旧runで`pages`段を再実行してもマーク無し→従来バイト同一(test)。個別承認された再ビルドは、`reconsume`コマンドを個別に実行することで可能(妨げない)。
- **AI島(X)のmigration**: 新コマンド`py er128_kp_confirmed_content_01.py reconsume --run <run> --level a2|b1b --by <名> --user-ref <USER.md/委任文path>`(`confirm-revise`同型のレコード版数+1)。処理: (1)Std: `unconsumed[]`のSTD_CATEGORY2_NO_SLOT 2件を`items`(category2,slot=vocab)へ移し、`build_items`で再構築、reviewへ`std_part1:true`と`selection.vocab=①+②`、`vocab_confirmed.json`書出し、(2)Std/Adv共通: ③の`reason`を`CATEGORY3_HIGHLIGHT`へ、`display_spec`付与、(3)履歴`event="reconsumed"`・`user_ref`にUSER.md、`content_sha256`再計算(itemsが変わるのはStdのみ)。ユーザー選定(①②③の候補ID・区分・件数)は**一切変更しない**(再選定不要、USER.md:140-142)。同一入力の再実行は冪等。実行前に確定レコードのhash chain(`_problems_self`)を検証。
- 音声・本文再利用: 音声は不変。HTML再ビルド(API 0)+Std Part 1生成のみ(約¥0.16)。AI島のassemble停止(d05729316、M3 Style Gate)の解消は別Agent担当=依存(IMPL_PLAN_02)。

## G. 既定動作・安全性(CLAUDE.md「Production安全性」との整合)
- 本機能は**APPROVED_FOR_PRODUCTION**(ユーザー正式決定2026-10-27、USER.md:1-10)のため未承認機能の隔離flagは不要。「確定レコード(`display_spec`付き)がある記事で自動有効、無し=従来どおり」。Grep確認項目: 既定値(`display_spec`/`std_part1`の付与箇所が新規作成経路のみ・環境変数で変更不可)。
- 既存retry/fallback/regeneration/resume・KCP G0〜G4・STOP/Gateは迂回しない。fail-closedは新規ISSUEとして既存`raise_issue`系に追加。
- DEV/Trial経路にだけ実装してProductionへ未接続にしない(受入条件7): 全てX/Y/Z正式runner・page builderの入口に配線(§C)。

## H. 未決・Opus依頼事項(`OPUS_REVIEW_REQUEST_02.md`)
照合の正確性・多重出現、Std Part 1 level化がAdv品質を変えないこと、旧経路撤去漏れ、KCP整合(`display_spec`/`std_part1`マークとhash)、X/Y/Z差異(特にXの二系統page、Zのクリップ連結)、既存ページ回帰、費用。
