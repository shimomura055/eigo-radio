# FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09 実行報告

管理ID: `FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`(Lane A、N-4=(a))。
**Trial(Production実装ではない)**。Production/Prompt/共有module/SSOT編集・Git操作は一切行っていない。

## 0. 目的

Hanshin以外の新規News Ledgerを既存Research正式経路で作成し、そのLedgerでFocus Module+
Point Role hint条件でA2/B1B各N=3(予算超過のためN=2で確定)を実施した。目的は「News NG率50%
がHanshin固有か、仕組み側の一般問題か」の切り分けと、News Completion(theme→research→
Ledger→Writer→QA→artifact)の実走確認。

## 1. Step 0: テーマ選定(Reconciliation)

既存Research正式経路(`er003_v1_en_direct_vfl_01_generate.py`、通称vfl01。Hanshin/Health/
Household 3ジャンルへ横展開されたVerified Fact Ledgerパイプライン、根拠:
`ER-003-EN-DIRECT-VFL-01_REPORT.md`)のResearcher呼び出し構造を再現し、実Web検索で候補3件を
検索した(`er011_output/news_stage3_new_theme_ledger_trial_09/research/candidate_search.json`)。

CURRENT_SPEC.md「Editorial Type Routing(2軸判定)」と`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-
DESIGN-TRIAL-01_REPORT.md` §2.1 Gate 6項目で評価した結果(詳細:
`research/theme_selection_reconciliation.md`):

| 候補 | 分野 | 2軸判定 | 採否 |
|---|---|---|---|
| ケイティ・テイラー引退(2026-09-05) | sports | MAJOR_DAILY | 却下(Hanshinと同型の単一試合勝敗構造、切り分け目的に合わない) |
| **体内CAR-T免疫療法でMS等症状改善報告(2026-09-03、NEJM)** | science | MAJOR_DAILY | **採用** |
| アテネ動物園トラ幼獣健康診断(2026-09-08) | society | 形式上MAJOR_DAILY | 却下(Gate項目3[Ledger充足]リスク、題材が薄い) |

採用理由: Hanshin(単一試合スコアラインで数値密度が高い)と異なり、候補2は「mechanism(体内で
直接CAR-T誘導する新方式)」と「limitation/unconfirmed(小規模単群第1相、大規模検証が必要)」
という、語彙がFull Story/Pointへ自然に分かれやすい構造を持つ(News Focus Module/Point Role
hintが想定する役割候補[mechanism/beyond-headline/limitation]と直接対応)。既存DECIDED判定
(CURRENT_SPEC.md「Health(単一起点研究発表がある場合の扱い)」節、単一研究発表=MAJOR_DAILY)
とも整合する。

Verified Fact Ledgerは同経路(Researcher→独立Verification→CONFIRMED[VERIFIED]のみ採用、
AMBIGUOUS/REJECTEDは除外)で作成した: **14件CONFIRMED**(AMBIGUOUS 1件[99.7%の分母定義不明]
除外、REJECTED 0件)。手動Mode判定=`MAJOR_DAILY`(Gate 6項目全PASS、
`research/major_daily_gate_checklist.json`)。**費用: ¥57.89**(候補検索¥13.73+Ledger作成
¥44.16)。

## 2. Step 1: Focus Module+Point Role hint条件(text-only)

Trial-06のharness(`er011_point_role_planning_focus_connection_trial_03.run_one_pattern_
connected`、G1修正済みProduction、無変更import)を再利用し、focus_hint条件×A2/B1B×N=2
(予算超過見込みのためN=3からN=2へ縮小、run1完了時点でN=3見込み¥186.6>予算¥150のため)を
実施(`er011_news_stage3_new_theme_ledger_trial_09.py`)。**baselineは回していない**。

| run | level | 初期attempt flag | 最終retry回数 | 最終status | P1 overlap | P2 overlap | Value QA | Fact Checker | Ledger Deviation(最終) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | A2 | flag無し | 0 | OK | 0.179 | 0.324 | NG無し | REVIEW_REQUIRED | LEDGER_COMPLIANT(0) |
| 2 | A2 | lexical flag | 2 | OK | 0.211 | 0.306 | NG無し | REVIEW_REQUIRED | LEDGER_COMPLIANT(2 minor) |
| 1 | B1B | lexical flag | 2 | OK | 0.294 | 0.262 | NG無し | REVIEW_REQUIRED | 1 MAJOR→Local Rewrite 1cycleでLEDGER_COMPLIANT |
| 2 | B1B | flag無し | 0 | OK | 0.176 | 0.394 | NG無し | PASS | 2 minor/1 MAJOR→Local Rewrite 1cycleでLEDGER_COMPLIANT |

閾値0.40(既存Production既定、変更なし)。Directional Fact Precheck: 4本全てDIRECTION_
REVIEW_REQUIRED(advisory、blockingではない、他Trialでも頻出の既知挙動)。**費用: ¥142.50**
(N=2、4本合計)。

## 3. Hanshin/Theme2との比較

| 指標 | Hanshin Trial-06 baseline | Hanshin Trial-06 focus_hint | Theme2 Trial-05 baseline | **本Trial(新テーマ)focus_hint** |
|---|---|---|---|---|
| N | 6 | 6 | 4(A2×2+B1B×2) | 4(A2×2+B1B×2) |
| 最終NG率 | 100%(6/6) | 50%(3/6) | 50%(2/4) | **0%(0/4)** |
| retry平均 | 2.0 | 1.5 | 1.5 | 1.0 |
| P1 overlap平均 | 0.429 | 0.390 | (未集計) | 0.215 |
| P2 overlap平均 | 0.458 | 0.287 | (未集計) | 0.322 |

**題材依存の判定**: 本Trialの初期attempt flag率(2/4=50%)はHanshin/Theme2と同水準であり、
「Diagnostic Full Retryが発火する頻度」自体は題材によらず同程度と見られる。一方、**retry後の
最終解消率は本Trialで4/4(100%)、Hanshin focus_hintでは3/6(50%)しか解消していない**。これは
「retryが起きるかどうか」ではなく「retryで実際にPointの意味づけを分離できるかどうか」が題材
依存であることを示唆する。Step 0で選定理由に挙げた「mechanism/limitationへ自然に分かれる
Ledger構造」が、retry時のPoint再設計を実際に助けている可能性が高い。ただしN=4は小標本であり、
断定的な結論ではなく方向性の示唆にとどめる。

## 4. News Completion実走(B1B 1本、Production関数)

Step1のB1B run2(fact_verdict=PASS、point overlap NG無し)article.mdを入力に、Key Phrase
選定→TTS→Assembly→Audio Validation Gateまで既存Production関数(無変更)で通した
(`er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`)。

- Key Phrase: selection=PASS、canonicalization=PASS、redundancy_qa=**REDUNDANCY_PASS**
- TTS: 13segment中**12件RESOLVED(OK)**、1件(`full_story_part1`)が3回試行(既存retry上限)後も
  ASR検証NG(`TRUE_CONTENT_MISMATCH`、TTSが"published **a report on** a new gene treatment"の
  "a report on"を3回とも一貫して読み落とす)で**HUMAN_REVIEW_REQUIRED**へ遷移(既存Human
  Review Lock機構、独自回避せず)
- Assembly: **GATE_BLOCKED**(`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`、既存Audio Validation
  Gateが未検証segmentを検出して正しく停止)。player/完成episodeは生成していない(**STOP条件
  該当: Lock発動**)。

これは「theme→research→Ledger→Writer→QA→artifact」の実走がAssembly直前まで到達し、既存の
安全装置(Audio Validation Gate、Human Review Lock)が意図通り機能したことのevidenceである。
費用: **¥40.10**(作業中の誤操作で二重起動が発生し即座に強制終了、無駄になったScaffold呼び出し
分約¥2.56を含む。TTS/Assembly/Key Phraseは二重実行されていない[各出力ファイルのtimestampで
確認済み]。Scaffold出力[Preview/Comment本文json]はこの誤操作後の2回目生成で上書きされ、実際に
音声化された1回目の本文とはbyte一致しなくなった[記事本文自体には影響なし、Gate BLOCKEDのため
最終artifactは元々未生成])。

## 5. Gate 1分類・人手介在箇所

**Gate 1分類**: `VALIDATED(Trial)`止まり(Production採用は別途UDR、本Trial単体では判断しない)。
News Completionの人手介在箇所: (1)テーマ選定(候補検索結果からの手動2軸+Gate6判定)、(2)Mode
判定(手動MAJOR_DAILY判定)、(3)Ledger供給(手動でtopic文字列・Ledgerパスをharnessへ渡す)、
(4)B1B用日本語タイトルは本Trialでは不要(B1Bのみ実施のため未検証、A2 JAPANESE_TITLES登録は
既存gapのまま)。

## 6. USER_DECISION_REQUIRED候補

1. NG率0%(N=4)という結果は小標本であり、Production採用(Focus Module+hint配線)の可否判断
   には別途十分なNで再現性確認が必要(既存OPEN-135行の一般問題)。
2. 「retry発火率は題材によらないが、retry解消率は題材依存」という本Trialの新規知見をSSOTへ
   反映するかどうか。
3. `full_story_part1`のTTS content-dropping(“a report on”省略)は新しいfailure modeではなく
   既存TRUE_CONTENT_MISMATCH機構が正しく検知した通常のTTS変動と判断したが、パターンとして
   記録するかはユーザー判断。

## 7. 新規ファイル

- `er011_news_stage3_new_theme_ledger_trial_09.py`(root、新規)
- `er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`(root、新規)
- `er011_output/news_stage3_new_theme_ledger_trial_09/`(research/、a2/、b1b/、_combo_results/、
  all_results.json、run_config.json、run_metadata.json、gate4_g1_freshness_check.json、
  cost_summary.json、raw_usage_log.jsonl)
- `er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/`(b1b/、
  b1b_full_pipeline_summary.json、raw_usage_log.jsonl)

## 8. 費用合計

¥57.89(Step0)+¥142.50(Step1)+¥40.10(B1B full pipeline)=**¥240.49**(実測、各段階budget内)。
