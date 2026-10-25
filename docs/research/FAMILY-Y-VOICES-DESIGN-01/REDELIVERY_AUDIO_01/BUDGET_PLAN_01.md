# BUDGET_PLAN_01 (委任_27 Phase 0: 工程別見積と本日(JST)累計。API 0)

作成: 2026-10-25 11:10頃(JST)。

## 1. 本日(2026-10-25 JST)の累計(実測)
- 集計: `py docs/pm/tools/daily_dev_cost_01.py --date 2026-10-25 --repo-root . --ledger docs/pm/REPORT_LEDGER.md`(raw usage log全件、換算USD/JPY=160、unpriced 0)。
  - 11:00頃: **721.68円**(記録442件) / 11:10頃: **735.47円**(443件)。並行agent(FX-CORE-NUMERIC・FZ-NARRATION-CHUNK・FZ-SOURCE-ESSENCE・FAMILY-Z-STUDY-TEXT)の進行で増加中。
  - 日次上限1,000円まで: **残約264円**(11:10時点)。
- 本件の見積(下表)の上限Cap=55円を足すと、790.5円(並行agentの追加見込み約30〜50円を加えても約840円以下)で**1,000円を超えない**。

## 2. 工程別見積(円)
実測の基準: Y Trial 01の英語化は1候補0.83〜1.85円、scaffoldは1.26〜1.45円(EN_COMPARISON_01、`raw_usage_log_en_*`/`_sc_*`の再集計)、Y音声Trial 1候補(Std+Adv)=14.4〜14.7円(OPEN-463 委任_05)、Tension+Closing・リードは各1 call(gpt-6.1-sol high、入力約1.5k token)。単価は`er005_output/cost_baseline_01/pricing_snapshot.json`。
| 工程 | 内容 | 想定call | 見積(円) | retry/再生成の予備 | 最大(円) |
|---|---|---|---|---|---|
| 1 リード生成 | gpt-6.1-sol high 1 call(+規則違反で再生成1) | 1〜2 | 0.8 | +0.8 | 1.6 |
| 1 Tension+Closing生成 | 同 1 call(+再生成1) | 1〜2 | 1.2 | +1.2 | 2.4 |
| 1 Tension Leakage Gate | gpt-6-luna high 1判定(局所書き換え時+sol medium 1+再判定1、上限3判定) | 1〜5 | 0.3 | +2.5 | 2.8 |
| 2 忠実英訳+In One Line+A2簡易化 | Family X承認方式(Adv/Std) | 約5 | 1.5 | +1.5(段落数retry1) | 3.0 |
| 2 監視Leakage(Adv・Std英語、記録のみ) | luna high 2 call | 2 | 0.6 | — | 0.6 |
| 3 scaffold(Comment1〜3×2レベル、Preview×2、KP選定・canonicalization・gloss×2、日本語タイトル) | 既存cmd_scaffold | 約20 | 3.0(KP gloss新段を含め余裕を見込む) | +2 | 5.0 |
| 4 TTS+ASR(Adv・Std。本文5seg・Comment・Preview・KP・In One Line・共有narration再利用) | Flash-Lite TTS+ASR(統一ASR) | clip約60/level | 15.0 | retry/局所Rewrite/fallback +10(既存上限内) | 25.0 |
| 5 組立・ページ・QA集計 | ffmpeg/numpy、API 0 | 0 | 0 | — | 0 |
| **合計** | | | **約22.4円** | | **約40.4円** |

- 案件Cap(承認ファイル `cap_jpy`): **55円**(テキスト系 `TEXT_CAP_JPY`=20円[工程1〜3の合算保険]、音声 `--budget-jpy`=35円)。最大見積40.4円に約36%の余裕。案件見積300円以下(7-7)・日次1,000円内(上記)を満たす。
- RF(Risk Flagger)は今回実行しない(約1.7円×2の節約)。意見ベースで検証済み事実台帳が存在せず、Yは「未定」(CURRENT_SPEC.md:1684表)。
- 超過見込み(テキスト20円・音声35円の各Cap、または案件55円)で停止してFableへ報告。作業の分割や日付分割はしない。

## 3. 量産単価への示唆(記録用の枠)
- 本Trialの実費を工程別に`BUDGET_LOG_01.md`へ記録し、日本語R0(委任_25=25.3円)+補完(リード・Tension)+英訳+scaffold+音声を足した1セット総額を量産単価の目安とする(目標70円/セット。測定値であり確定値ではない)。
