# HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01 — Report

管理ID: HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01(**Trial扱い、Production配線
なし**)。実施者: Sonnet(sonnet-worker、Fable委任)。実施日: 2026-09-09。
同期実行のみ(バックグラウンド待機は、単一プロセスがBashツールの600秒
フォアグラウンド上限を超えた際にツール側が自動的に行ったもののみで、
複数プロセスの並行起動・二重起動は行っていない)。並列稼働中の他タスク領域
(`er011_output/discovery_stage4_cautionary_language_trial_10/`と同REPORT、
`er011_output/news_stage4_redesign_inventory_01/`)は読み取りのみで一切
編集していない。Production/Prompt/共有module/registry/SSOT/
`CURRENT_SPEC.md`編集・Git操作・旧artifact変更・代理承認は一切行っていない。

## 背景・目的

Household(Discovery/Why、Ledger v5)の最終版を一本化する。Primary=
Discovery Focus Module軽微改善(FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-
LANGUAGE-TRIAL-10の`cautionary_constrained`条件[Part B案1、未承認候補]、
保険文0/6を確認済み)を使い、A2/B1Bの記事→Support→Audio→試聴artifactまで
作り、Householdの最終候補としてユーザーへ提示する。

## 1. 事前確認

- Trial-10の`cautionary_constrained`条件(`CAUTIONARY_FOCUS_BLOCK`、Gate 4
  済み)を**無変更のままread-only importで再利用**(t10のOUT_DIR/REPORTへは
  一切書き込んでいない)。独自出力先(`er011_output/
  household_unified_final_candidate_01/audit/gate4_check.json`)で改めて
  静的確認(Production関数再定義なし、baseline↔cautionary差分は単一insert、
  Ledger v5マーカー確認、Point Overlap Loop Budget=2)を実施し**PASS**。
- Household既存完成版の構成(A2/B1B、Support=Preview/Comment/Key Phrase/
  日本語タイトル、SFX込みAssembly、player)を`er003_output/n3_01/household/`
  および`er011_output/open138_household_fact03_b1b_minimal_fix_03/`から確認
  し、同等の完成形になるよう手順を構成(Scaffold→Key Phrase→TTS→Assembly→
  Gate opt-in ONの順、既存Production関数のみ)。

## 2. 記事生成(`cautionary_constrained`条件、A2/B1B各1本)

既存経路のまま(Point Role Planning/Value QA/Point Overlap QA/Diagnostic
Full Retry[Loop Budget 2]/Fact Checker/Ledger Deviation Checker/Evidence
Compression/Directional Fact Precheck)。

| Level | 最終status | fact_verdict | ledger_status | Point Overlap記事全体retry | word_count | 保険文(regex) |
|---|---|---|---|---|---|---|
| A2 | **OK** | PASS | LEDGER_COMPLIANT(0件) | 1回(上限2、retry後解消) | 379 | 0件 |
| B1B | **OK** | PASS | LEDGER_COMPLIANT(0件) | 0回 | 399 | 0件 |

A2は1回目でPoint Overlap NG(lexical重複)を検知し、既存のDiagnostic Full
Retry機構(記事全体再生成、Loop Budget内)で2回目に解消。追加の自己判断
retryは行っていない(既定retryの範囲内)。両レベルとも自己判断による
再抽選(N追加)は行っていない。

## 3. Support(Preview/Comment/Key Phrase/日本語タイトル)

- A2/B1BともScaffold(Preview/Comment)は全項目OK。
- Key Phrase(Selection→Canonicalization→Redundancy QA): 両レベルとも
  `KEY_WORDS_STRUCTURE_PASS`→`CANONICALIZATION_PASS`→`REDUNDANCY_PASS`
  (1回で到達、追加retry不要)。
- **A2日本語タイトルgap**: `JAPANESE_TITLES`辞書に本Trial theme_id未登録
  (既存前例[FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01継続]と同一の既知
  gap)のため、既存Household完成版のタイトル「冷蔵庫の野菜室、2つの設定を
  使い分けると食品が長持ちする」をそのまま流用(新しい主張・数字は追加
  していない)。記録: `audit/a2_japanese_title_gap_note.json`。

## 4. Audio(TTS+ASR検証→Assembly+SFX→Gate opt-in ON)

| Level | TTS全segment | Assembly(Gate OFF) | Gate opt-in ON(OPEN-129) | duration | peak | clipping |
|---|---|---|---|---|---|---|
| A2 | 全14 segment+Key Phrase5件(EN/JA)OK | PASS | **PASS** | 330.0s | 0.98(headroom適用) | False |
| B1B | 全13 segment+Key Phrase5件(EN/JA)OK | PASS | **PASS** | 302.8s | 0.953 | False |

**HUMAN_REVIEW_REQUIRED/GATE_BLOCKEDの発動なし(Lock発動なし)**。両レベル
とも代理承認・独自回避は不要だった。

## 5. 試聴artifact

- `er011_output/household_unified_final_candidate_01/player.html`
  (file:///C:/Users/tensh/eigo-radio/er011_output/household_unified_final_candidate_01/player.html)。
  標準player規則(`audio_review_player.py`、Source列なし、audio
  min-width 360px)。A2/B1B両方の完成episode音声・segment一覧・記事全文・
  Support文を1ページに掲載。標準`SEEK_SCRIPT`は単一episode音声を前提と
  するため、1ページに2つの完成episode音声を並置する本ページでは、Seek対象
  をdata属性でscopeする専用JS(標準CSS/行/表テンプレートは無変更)に置き
  換えた(`build_player.py`内、audio_review_player.py自体は無変更)。
- 差分要約: `er011_output/household_unified_final_candidate_01/
  diff_vs_old_final_summary.md`(語数、保険文検出、Point切り口、FACT-03/04
  の扱いを新旧で比較)。

## 6. 費用

実測合計 **¥68.76**(上限¥300以内)。内訳: openai(Writer/QA系)¥19.62、
gemini(TTS)¥46.08、openai_asr(ASR検証)¥3.06。unpriced_records=0。
記録: `er011_output/household_unified_final_candidate_01/cost_summary.json`。

## Gate 1分類

**VALIDATED相当(Trial範囲)。到達Status: USER_FINAL_AUDIO_REVIEW_REQUIRED**。
A2/B1Bとも記事生成〜Audio Validation Gate opt-in ON経路まで完走し、
HUMAN_REVIEW_REQUIRED/GATE_BLOCKEDは発動しなかった。Production採用
(`APPROVED_FOR_PRODUCTION`)・旧完成版との差し替えは未承認のまま。

## 旧版との差分(要約)

詳細は`diff_vs_old_final_summary.md`参照。要点:
- 保険文検出(regex)は新旧とも0件(旧完成版は元々この問題の実例ではなかった
  ため、この指標だけでは新旧の優劣が示せない)。
- Point切り口は新候補の方が「診断的な質問→保管場所を先に決める」という
  順序をより明示的に強調。旧B1B(FIX-03)が使ったいちごの実例は新候補では
  使われていない。
- FACT-03/04整合は新旧とも矛盾なし(Ledger v5準拠、Ledger Deviation
  Checker 0件)。

## Supersession確認(PM_GOVERNANCE 2-3)

旧artifact(`er011_output/open138_household_fact03_b1b_minimal_fix_03/`、
既存Household完成版`er003_output/n3_01/household/`)は**一切変更していない**
(読み取りのみ)。新候補は独立した並置artifactであり、旧完成版を上書き・
置換していない。

## USER_DECISION_REQUIRED候補

1. Part B案1(cautionary_constrained)をProduction Discovery Focus Module
   へ正式採用するか(未承認候補のまま。Trial-10 REPORTはN=3・N=1の範囲での
   確認に留まる)。
2. 新候補(A2/B1B)を旧完成版の後継として採用するか、旧完成版を維持するか
   (両方をユーザーが試聴・比較したうえで判断)。
3. `editorial_mode="discovery_why"`の正式registry登録(採用する場合に
   必要、本Trialでは未登録の想定名のまま使用)。

## 成果物一覧

- `er011_household_unified_final_candidate_01_run.py`(root、新規、
  orchestrationのみ、既存Production関数を無変更で直接呼ぶ)
- `HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01_REPORT.md`(本ファイル)
- `er011_output/household_unified_final_candidate_01/`
  - `audit/gate4_check.json` / `audit/a2_japanese_title_gap_note.json`
  - `{a2,b1b}/article.md` / `run_summary.json` / `fact_qa.json` /
    `ledger_deviation.json` / `parts.json` /
    `{a2_support_texts,b1_support_texts}.json` / `key_phrases/` /
    `narration/` / `assembled/` / `audit/tts_generation_results.json` /
    `audit/timeline.json` / `run_summary_assemble.json` /
    `audit/assembly_and_gate_summary.json`
  - `build_player.py`(新規、試聴artifact生成)/ `player.html`
  - `diff_vs_old_final_summary.md`
  - `cost_summary.json` / `raw_usage_log.jsonl` / `e2e_run_summary_partial_*.json`
