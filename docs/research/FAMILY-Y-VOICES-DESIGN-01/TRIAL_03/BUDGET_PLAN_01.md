# BUDGET_PLAN_01: Family Y Trial_03(委任_09B、案(d)+世界設定先行)の費用計画と実績追記

> **[2026-10-24 注記 PM-FAMILY-Y-BUDGET-CONSOLIDATION-01]** 本書内の「Family Y累計上限(600円/650円等)」は作成当時の枠。同日ユーザー決定で撤廃済み(以後は日次1,000円で一元管理、PM_GOVERNANCE 7-9)。本書の委任単位上限(run単位Cap)は歴史的記録として維持。

Status: DEV/Trial。Production変更0。作成=開始前(T-0)。各段階後に「実績追記」節へ累計を追記する。

## 前提(ユーザー原文 USER_04 §1/§5)
**【追補】作業完了時点で `USER_04_ADDENDUM_BUDGET.md`(同日受領)により上限が Family Y Trial累計 600円 / 当日 1,400円 / Y残予算 334.25円 に再修正されていた(Fable注記)。本計画・実績は作業開始時点の旧上限(400円/1,200円/134.25円)基準で作成・監視し、実費は新旧どちらの上限内でもある(実績は末尾)。**
- Family Y Trial累計上限 400円。既使用 265.75円 → **Y残予算 134.25円(明示上限。無断超過禁止)**。
- 当日(2026-10-23 JST)開発費上限 1,200円(他案件を含む全体上限、Yの400円とは別管理)。
- 開始時 `daily_dev_cost_01.py` adopted = **632.59円**(うち前回Phase B含む) → 当日上限までの差 = **567.41円**(他agent並走分で変動するため、各段階後に再取得)。
- 報告トリガ: Y累計(本委任分)が **120円** に達した時点、または完成までの見込みが残予算134.25円を超えると判明した時点で、停止する前にFableへ報告。
- Charter: 本委任は承認済みScope内。見積合計が134.25円以内なら少額ごとの承認は求めない(7-7)。

## 見積(円。上限見込み側で記載)
| 工程 | 内容 | 見積(円) | 根拠 |
|---|---|---|---|
| T-1 | Web検索(日本の学校のスマホ預かり実態・定時制の扱い。既存Researchで足りない部分のみ)Perplexity sonar-pro 最大2 call | 〜8(上限10) | PPLX2実測 sonar 1 call 0.8円。sonar-proは数倍見込み。Ledger内根拠を最優先 |
| T-2 | 日本語修正稿のGate(Voice Leakage 3本+Tension)・見出し(LLM低価格) | 〜3 | it2 Gate等の実績(ゲート各0.2〜0.5円級)。Writer(high effort)は**呼ばない**(本文は手修正) |
| T-2 | 英訳(Adv忠実英訳+In One Line+Std簡易化)、1回、必要ならmust_fix付き再1回 | 〜3 | it2英語 1.11円 |
| T-2 | scaffold(Comment 1/2・Preview・Key Phrases)×2レベル | 〜4 | it2 scaffold 2.74円 |
| T-2 | RF(Risk Flagger) | 〜3 | it2 RF 2.06円 |
| T-3 | TTS音声 Adv(Gemini batch+ASR+Azure STT) 初回 | 〜12 | Phase B Adv 14.71円(V1の再試行含む) |
| T-3 | TTS音声 Std 初回(comment_1の日本語読み方確認は**回避**: Comment 1に英字略語・数字・外来語を入れない) | 〜12 | Phase B Std 27.13円のうち22.8円はcomment_1読み方確認(web検索3回)。除外すると約4.3円/途中まで→全編で約10〜12円 |
| T-3 | Repetition QA等の再生成余裕(V1〜V3・Tension、最大各2回) | 〜25 | OPEN-469偽陽性。原稿段階で語反復を避けて発生を抑える |
| T-3 | 発音確認(ASR・必要時) | 〜3 | |
| 予備 | 修正稿の再英訳/再Gateの余裕 | 〜15 | |
| **合計(上限見込み)** | | **〜88**(残予算134.25円の約66%) | |
- 計画上の内訳は「平常想定 約45円」「上限見込み 約88円」。**上限見込みが残予算を超えないため、作業を開始する**。
- 既存音声の再利用: 修正稿と本文が一致するclip(=KP等の再利用可能なもの)のみ。本文Voice等は修正稿で変わるため再生成が前提。
- 当日1,200円との差: 開始時567.41円。本委任の上限見込み88円は当日枠内。

## 実績追記
### 段階1(T-1 世界設定+T-2 テキスト一式)完了時点(JST 19:2x)
| 段 | 円 | 出典 |
|---|---|---|
| T-1 Web検索 1 call(Perplexity sonar-pro、q1のみ。q2[定時制]は埼玉県調査の実数で足りたため実施せず) | 1.32 | world_search/q1.json usage.cost.total_cost=$0.00849 |
| T-2 Gate(Voice+Tension、各初回PASS)+見出し(it2再利用でLLM 0) | 0.17 | it3/raw_usage_log.jsonl |
| T-2 英訳(Adv+In One Line+Std簡易化、+監視Leakage) | 1.02 | it3/raw_usage_log_en.jsonl |
| T-2 scaffold(Comment/Preview/KP×2レベル) | 2.14〜3.6(ログ合算) | it3/raw_usage_log_sc.jsonl |
| T-2 RF | 1.73 | it3/raw_usage_log_rf.jsonl |
| **段階1合計** | **約6.95**(it3 raw_usage_log合算5.63+検索1.32) | `cost03` 集計 |
- Y累計(本委任分)=約6.95円 / 残予算134.25円 → 残り約127.3円。120円トリガ(本委任分)に対して約5.8%。
- 当日累計: 開始時632.59円(`daily_dev_cost_01`) + 本委任約7円(他agent並走分は再取得で反映) → 1,200円まで十分余裕。
- 見積(平常45/上限88円)に対し、Writer(high effort)を呼ばず手修正としたためテキスト段は見積(〜3+3+4+3=〜13円)より約6円低い。

### 段階2(T-3 音声TTS、JST 19:23-19:56、再起動なし)完了時点
| 段 | 円 | 出典 |
|---|---|---|
| 音声 Adv(Gemini 12.21+OpenAI ASR 2.55+Azure 2.60+OpenAI 0.62) | 17.97 | runner `[cost] so far` after y persona tts b1b |
| 音声 Std(同) | 25.15(累計43.12-17.97) | runner `[cost] so far` after y persona tts a2 |
| 評価補助(E1/E2/E13、gpt-6-luna) | 0.23 | it3/raw_usage_log_eval.jsonl |
| 段階1(テキスト一式+検索) | 6.95(gate 0.17+英訳1.02+scaffold 2.40+RF 1.69+検索1.32、集計式差で±0.2) | 上記 |
| **本委任の累計(実費)** | **約50.0円** | `xr.compute_cost_jpy_so_far`(各raw_usage_log)+Perplexity |
- Y累計 = 265.75 + 約50.0 = **約315.7円 / 旧上限400円 -> 追補後上限600円**。**Y残予算 約84.3円(旧基準)/約284.3円(追補後基準)**(旧明示上限134.25円に対し使用約37%)。
- 120円トリガ(本委任分)未到達。完成見込み=V1のみ再生成(両level、約4〜12円)で、残予算内。
- 当日: `daily_dev_cost_01` adopted = **824.93円**(開始時632.59円。他agent分を含む増分約192円のうち本委任約50円) -> 旧上限1,200円まで約375円、追補後上限1,400円まで約575円の余裕。
- 見積(平常45/上限88円)に対する実績: 約50円(見積内)。超過要因: V1の再試行(Adv3+Std3=計6 TTS call)、Std Tension 2・V2 2・Adv V3 2試行。
- 事前見積外の費用: なし。Comment 1の日本語読み方確認(web検索付き)は、英字略語・数字を含めず発火回避(Latin token検出0を事前に確認)。
