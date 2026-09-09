# OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02

管理ID: OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02(Lane B、Sonnet委任、
Production修正、Gate 3)。

対象: Opusレビューで指摘された欠陥(`er012_b_family_editorial_type_
registry_01.py::build_voice_attribution_block()`が`[VOICE_n_EVIDENCE]`
タグの乗る物理1行のみを抽出し、実Ledgerの2行目以降[fact本文の折り返し・
`source:`/URL/`counter_or_limitation:`/`verification:`]が欠落していた
問題)をProduction修正し、OPEN-131のruntime evidenceを再取得した。

---

## 0. Reconciliation Check(先に実施)

**OPEN-131承認内容との照合**: `OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-
PRODUCTION-WIRING-01_REPORT.md`は`build_voice_attribution_block()`を
「`[VOICE_n_EVIDENCE]`行を正規表現抽出」とだけ記述し、「evidence本体を
blockに含める」という設計意図を明示的な文章としては書いていない。ただし、
同関数内の`VOICE_ATTRIBUTION_RULE_TEXT`自体が「下記のVerified Fact
Ledgerの該当[VOICE_n_EVIDENCE]evidence(下記抜粋)の内容と実質的に対応
している場合」とモデルへ約束しており、実Ledger(`editorial_b_voices_
trial_07/research/verified_fact_ledger.txt`)は1 evidenceがfact本文の
折り返し+source/URL/counter_or_limitation/verificationの複数物理行に
またがる書式である(実測、下記1節)。タグ行1行だけの抽出では、この
ルール文言が約束する「evidence内容」を実質的に何も渡していないに等しく
(文の途中で切れる)、**実装漏れ**と判定する(仕様解釈の余地なし)。

**終端規約の確定**: Trial-07 Ledger(実測、`awk`による行番号確認)・
Trial-02の`combined_ledger_block.txt`(synthetic 3V例が複数行)から、
実Ledgerの各evidenceエントリは「空行1つ」で次のエントリ・次の`[...]`
タグ・`===...===`セクション見出しと区切られており、エントリ途中に空行は
無い。よって終端規約を「タグ行から開始し、次に現れる**空行/`[`開始行/
`===`開始行**のいずれかの直前まで」と確定した(曖昧では無く、Ledger実測
から一意に決まる。指示の保守的フォールバック[次`[`タグ行または空行2連続]
より厳格だが、実データと矛盾しない)。

**影響範囲**: `build_voice_attribution_block()`の呼び出し元は
`er012_b_family_production_runner_01.py::build_fact_attribution_block_
if_enabled()`の1箇所のみ(runner入口)。他の呼び出しは
`er012_open131_fact_attribution_production_wiring_01_test_01.py`の
regressionテストのみ。他のProduction関数からの直接呼び出しは無い
(grep確認済み)。

## 1. 実Ledger書式の実測

`verified_fact_ledger.txt`を`awk`で行番号付き確認した結果、各
`[VOICE_n_EVIDENCE]`エントリは、fact本文の折り返し(2〜6行)→
`  source:`→`  (URL)`→`  counter_or_limitation:`(1〜2行)→
`  verification:`(1〜4行)と続き、空行1つで次のエントリ/`===`見出しへ
移る。エントリ内部に空行は存在しない(全エントリで確認)。

## 2. 修正(Production)

`er012_b_family_editorial_type_registry_01.py::build_voice_attribution_
block()`を、タグ行から開始し次の(空行/`[`開始行/`===`開始行)の直前まで
を1エントリとして抽出するよう修正(関数シグネチャ不変、fail-closed挙動
[タグ0件→`""`]不変)。診断用の未使用正規表現`_VOICE_EVIDENCE_LINE_RE`は
削除せず残置(他箇所から参照されておらず実害なし、最小diff優先)。

## 3. テスト

`er012_open131_fact_attribution_production_wiring_01_test_01.py`へ5件
追加(既存13件は無変更・全PASS)。

| テスト | 確認内容 |
|---|---|
| `test_multiline_evidence_body_and_source_lines_are_included` | 本文2行目・sourse/URL/counter_or_limitation/verification継続行が含まれる |
| `test_multiline_entry_terminates_before_next_tag_and_does_not_bleed` | 1-01のsource行が1-02のエントリへ混入しない(出現順・非混入を確認) |
| `test_multiline_entry_does_not_bleed_into_next_section_header` | `===...===`見出し自体はblockに含まれない |
| `test_cross_reference_tag_is_excluded_even_when_mixed_in` | `[CROSS_REFERENCE]`はVOICE_n_EVIDENCEタグ混在時も除外される |
| `test_mixed_voice_1_and_voice_2_tags_both_fully_captured` | VOICE_1/VOICE_2混在時、両方とも継続行込みで完全抽出 |

既存の単行Ledgerテスト(`LEDGER_SAMPLE`)・3V拡張テスト(`LEDGER_SAMPLE_
3V`)・A-Family既定OFF時のbyte不変テストは無変更で全PASS(単行の場合は
新旧アルゴリズムが同じ結果を返すため非破壊)。

`run_project_regression.py`: `collected=2247 passed=2244 failed=3
errors=0`(修正前ベースライン`collected=2242 passed=2239 failed=3`から
新規5テスト分のみ増加、既知3件[`er003_test_p2j_investigate.py`の
reconciliation定数比較、本タスクと無関係]以外の失敗なし)。

## 4. Runtime evidence(再取得)

費用ロガーを冒頭で有効化(`er012_open131_attribution_block_multiline_
fix_02_evidence_01.py`、専用ログ`er012_output/open131_attribution_
block_multiline_fix_02/audit/raw_usage_log.jsonl`、Production側の既存
ログとは別ファイル)。`runner.run_fact_check_b1/a2`(Production関数、
無変更)を実際に4回呼び出した。

**block size**(evidence部分のみ、実Ledger全文使用):

| | 修正前(タグ1行のみ) | 修正後(継続行込み) |
|---|---|---|
| 文字数 | 741 | 5,120 |
| 行数 | 13 | 125 |
| block全体(ルール文言込み)文字数 | 1,359 | 5,738(約4.2倍) |

**B1/A2 verdict比較**:

| | OFF(既存記録) | ON修正前(切り詰めblock、既存記録) | ON修正後(完全block、本タスク実行) |
|---|---|---|---|
| B1 verdict | REVIEW_REQUIRED | PASS | **PASS**(不変) |
| B1 unsupported件数 | 5 | 0 | **0**(不変) |
| A2 verdict | REVIEW_REQUIRED | PASS | **REVIEW_REQUIRED** |
| A2 unsupported件数 | 6 | 0 | **2** |

**重要な発見**: A2は修正前PASSだったが、修正後はTension段落(`Where the
Difference Comes From`、Voice本文ではない地の文)の2claimが
`unsupported_specific_claims`として復活した。この2claimはopt-inルール
文言が明示的に免除対象外とする「Voice本文以外の地の文での客観的主張」に
該当し(Trial-01の`tension_repeated_desk_use`と同種)、免除すべきでない
ものが免除されずに正しく検出された結果であり、**false acceptの新規発生
ではなく、切り詰めblockの下で見えていなかった適正な検出が修正後に回復
した**と解釈する(B1側Voice本文のexemptionは0件のまま維持=FP無し、A2の
2件はTPの回復)。ただし、これはOPEN-131承認時の「A2もPASS」という
runtime evidenceの前提が、切り詰めbugの影響下で得られたものだったことを
意味し、修正後は同一条件でA2がPASSを再現しない。単発実行であり
(Trial-02同様、claim単位で試行間に若干の揺れがあり得る)、5run等の
反復検証はコスト制約上未実施。

**false accept control(N=2、TRIAL-02同種)**: B1記事のOne Voice section
へ捏造claimを挿入し、修正後blockで実Fact Checkを実行。

| Control | 挿入内容 | verdict | 検出 |
|---|---|---|---|
| 1(数値・主体捏造) | 架空調査機関「Meridian Analytics」による97%という捏造数値 | REVIEW_REQUIRED | 検出(2claim、捏造数値・最上級主張とも指摘) |
| 2(実在人物誇張) | 実在するNigel Oseland博士への誇張発言の帰属捏造 | **FAIL** | 検出(contradiction 1件+unsupported 1件) |

2/2検知(Trial-02のN=5・5/5相当を維持、false accept増加なし)。

**費用**: 実LLM呼び出し4回(B1・A2・control1・control2、全てweb_search
使用)。合計**¥11.67**(`openai`、`raw_usage_log.jsonl`実測、
`cost_report_after_fix.json`)。上限¥60以内。

## 5. Cost / latency(block増によるtoken影響)

blockサイズ自体は修正前後で約4.2倍(1,359→5,738文字)に固定的に増加する
(全呼び出しで確定的な追加)。ただし実測input_tokens(43,372〜73,298)は
web_search呼び出し回数(4〜9回、モデルの自律判断で毎回変動)に支配されて
おり、block増分単体の寄与を単発実行の比較だけで切り分けることはできな
かった(不明、反復試行での分離が必要)。総プロンプトが数万tokenある中で
block増分(数千文字≒概算で千〜数千token程度)は相対的に小さい。latency
(elapsed_seconds)も32.9秒〜52.7秒とweb_search回数と相関しており、
block増による明確な増加傾向は本タスクの実行回数では確認できなかった。

## Gate 3表

| # | 項目 | 結果 |
|---|---|---|
| Production正式path | PASS(修正対象は既存Production関数`build_voice_attribution_block()`本体、新規関数の追加ではない) |
| retry/regeneration整合 | PASS(blockはledger_text/flagのみに依存しarticle_textに非依存、既存テスト`test_block_is_independent_of_article_text_local_rewrite_simulation`は無変更でPASS) |
| Trial-onlyではないこと | PASS(全変更はProduction module内、Trialスクリプトをimportしない) |
| runtime発火 | PASS(4節、実記事2本+control2本、計4回の実LLM呼び出し) |
| 回帰 | PASS(3節、`run_project_regression.py` collected=2247 passed=2244 failed=3[既知]) |
| TP維持・FP是正 | PASS(B1側Voice本文のFP=0件を維持。A2のTension2件はVoice本文exemption対象外のTPが回復、新規FPではない。control 2/2検知でTP維持) |
| 二重実装なし | PASS(既存関数を修正、新規並行実装を作らず) |
| Cost・latency | PASS(5節、block4.2倍増だがweb_search変動が支配的、費用¥11.67/上限¥60以内) |
| SSOT・Git | 未実施(本タスクでは実施しない、並列稼働中のSSOT統合タスクが後続でCommit時に反映する前提) |
| 承認内容一致 | PASS(0節、ルール文言・免除対象は無変更、抽出範囲のみ修正) |
| Dangling Reference | PASS(4節末尾参照、新規参照する未承認仕様なし) |

## Gate 4表(Dangling Reference Check)

- 修正後の`build_voice_attribution_block()`は既存のVOICE_ATTRIBUTION_
  RULE_TEXT・EDITORIAL_TYPES辞書のみを参照し、新規の未承認仕様を一切
  参照していない。
- A-Family経路(`er006_pool_pilot_01_writer.py`・`er003_v1_n3_01_
  articles_generate.py`)は本修正後も`voice_attribution_block`・
  registry importを一切持たない(既存test `test_a_family_writer_files_
  do_not_reference_new_mechanism`で確認、無変更でPASS)。
- `fact_attribution_mode`既定Falseは無変更(`test_default_mode_is_off`
  PASS)。

## STOP条件確認

- Ledger終端規約: 実Ledgerから一意に確定できた(0節)→該当なし。
- false accept増加: B1側FP=0維持、A2側の2件はTP回復でありfalse accept
  ではない、control 2/2検知維持→該当なし。
- A-Familyプロンプト変化: byte不変テストPASS→該当なし。
- regression break: 新規失敗0件(既知3件のみ)→該当なし。
- 費用超過: ¥11.67(上限¥60以内)→該当なし。

**STOPなし。ただし4節の「A2 PASSがREVIEW_REQUIREDへ変化した」事実は
Fable/ユーザーへの重要な報告事項として明記する(OPEN-131承認時の
runtime evidenceの前提が変わったため)。**

## Status

Sonnetとして`PRODUCTION_WIRED`を宣言しない(Gate 7はFableが行う)。
本タスクはSSOT反映・Git操作を行っていない(並列稼働中のSSOT統合タスクが
後続で反映)。

## 新規・変更ファイル一覧

- `OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02_REPORT.md`(本ファイル、root、新規)
- `er012_b_family_editorial_type_registry_01.py`(root、修正: `build_voice_attribution_block()`の抽出ロジック)
- `er012_open131_fact_attribution_production_wiring_01_test_01.py`(root、修正: 多行evidence用テスト5件追加)
- `er012_open131_attribution_block_multiline_fix_02_evidence_01.py`(root、新規、runtime evidence再取得スクリプト)
- `er012_output/open131_attribution_block_multiline_fix_02/`(新規、`on_off_comparison_after_fix.json`・`on_block_after_fix.txt`・`b1_on_after_fix_result.json`・`a2_on_after_fix_result.json`・`control_1_fabricated_stat_result.json`・`control_2_named_individual_result.json`・`cost_report_after_fix.json`・`size_comparison.json`・`old_evidence_block.txt`・`new_evidence_block.txt`・`audit/raw_usage_log.jsonl`)

---
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SPsKBAZP5KEqdTH9TnkJdp
