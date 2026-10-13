# plan_01: 有料run計画・見積・判定規則の事前登録 (委任_01では実行しない。Fable/ユーザーが上限と受入条件を確認後、委任_02で実行)
管理ID: FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 / 2026-10-13 / Trial専用 / 採用判断なし
事前登録時点: 有料call 0件(この文書の確定前に処置armを1件も実行していない)。対照値は既存runの再解析のみ(`control_baseline_01.json`)。

## 1. 比較設計
- 対照(M2P0): Round 1 の既存run。shortlist(M2)・Prompt(P0)の sha は現行構築と**全6セルで一致**(`offline_check_01.json prompt.cells[*].control`, `test_control_runs_reusable_by_sha`)。→ 対照の再実行不要。
- 処置(M2P0X): M2 shortlistとP0に追加1段落のみ(`design_diff_01.md`)。モデル gpt-6-luna(Round1/2と同一=比較可能性の例外。最新世代最上位系での検証ではない)。reasoning effort等はProduction既定(`prod.SELECTOR_REASONING_EFFORT`)でRound1と同一経路(`er064_kp_int_01_run.job`再利用)。
- 対照のn: coffee_std 3 / coffee_adv 3 / meta_std 2 / meta_adv 2 / hormuz_std 2 / hormuz_adv 2。処置nは下表。nの不揃いは比率とCI併記で扱い、n=2-3のセルは「方向性のみ」と明記する。
- オプション(推奨度中): meta_adv の対照を n=2→5 に揃える追加3 job(M2P0、中央JPY2.4/保守3.6)。付けない場合は meta_adv の対照は 2/2 裸 + M0P0(Phase2 C0) 3/3 + M2P3 2/2 の同型事実で補強(`DIAG_01.md` 2-(iii))。

## 2. job計画 (`er064_kp_noway_01_run.py` の `STAGE_PLAN`)
| Stage | セル | 処置n | 対照n(既存) | 目的 |
|---|---|---|---|---|
| 1 | meta_adv | 5 | 2 | 主目的: `no way` 単独の解消(再現確認) |
| 2 | coffee_std | 3 | 3 | 回帰 |
| 2 | coffee_adv | 3 | 3 | 回帰 |
| 2 | meta_std | 3 | 2 | 回帰 |
| 2 | hormuz_std | 3 | 2 | 回帰 |
| 2 | hormuz_adv | 3 | 2 | 回帰 |
合計 20 job(Stage 1: 5、Stage 2: 15)。6並列(Round 1〜3と同じ)。Stage 1 → Go判定 → Stage 2 の2段(直列の理由: 前工程出力依存。Stage 1が明確に失敗なら回帰15 job=約JPY14〜18を使わない。Stage 1は1バッチ約90秒)。各Stageは1回だけ手動起動、自動retry・監督ループ・別名ラッパなし、外部停止後の再起動禁止。

## 3. 見積 (`cost_01.json`。出典: Round1 M2P0実績14 job平均JPY0.9132/最大1.1869、M2P5実績10 job、委任文の保守値1.185)
| 区分 | job | 中央値(M2P0実績×n+追加入力0.0025/job) | P5並み推論+10〜12%の場合 | 保守(1.185/job) |
|---|---|---|---|---|
| Stage 1 meta_adv n=5 | 5 | 4.1 | 約4.4 | 5.93 |
| Stage 2 回帰 | 15 | 14.1 | 約16.0 | 17.78 |
| **合計(必須)** | **20** | **18.2** | **20.4** | **23.7** |
| (任意)meta_adv対照+3 | 3 | +2.4 | | +3.6 |
| 合計(任意込み) | 23 | 20.6 | | 27.25 |
- 推奨費用上限: **JPY30**(job上限2.5/job、ハードストップ30、見積保守27.25に余裕)。本Trial累計は102.46/300(Round3時点、`cost_r3.json`) + 本件最大30 = 132.5以内。委任_01の実支出は **JPY0**。
- 時間見込み: Stage 1 約1.5分、Stage 2 約5分(15 job / 6並列 × 約85秒)。合計約7分。解析は¥0(`er064_kp_noway_01_analyze.py`)。
- 注: Opus/他モデル費用なし。TTS/ASRなし。

## 4. 判定規則(事前登録、数値化)
用語: **bare** = 最終5件(canonicalized key_phrase)に`no way`単独。**A** = `no way`を含む語句なし。**B** = `no way`を含み3語以上。**B-valid** = Bで、選定gate PASS・有限助動詞なし・本文語幹許容逐語・canonicalization key_phrase==display_phrase(または canon PASS)・Redundancy PASS。
### 4-1. 主判定 (Stage 1, meta_adv n=5)
- **P1(必須)**: bare **0/5**。かつ B のrunは全て B-valid。
- **P2**: merged_overall_status PASS **≥4/5**(対照2/2)。選定gateが有限助動詞で INVALID になった run **0**(`have no way to know`型の誘発を検出)。contract_violation 0。
- **P3(良い選定の維持)**: `behind the scenes`・`unintentionally`・`concierge`・`contract worker(s)` の各採用が **≥4/5**(対照は各2/2)。
- 統計の限界(明記): n=5で0/5でもbare率の片側95%上限は約45%(Clopper-Pearson)。対照の裸率は2/2(M0P0 3/3、M2P3 2/2も同型)。「効果の存在を示す」ではなく「現行の2/2と比べて再現的に消えるか」の確認。
- **Stage 1 → Stage 2のGo規則**: bareが **≤2/5** かつ 選定INVALID(有限助動詞) ≤1/5 ならStage 2へ。bare ≥3/5 または INVALID ≥2/5 なら**Stage 2を実行せずSTOPして報告**(P0Xは効かない/有害。供給側補欠案は新規委任の判断事項)。
### 4-2. 回帰判定 (Stage 2, 対照=既存M2P0。n=3のため絶対差でなく許容幅を事前に置く)
- **R1 アンカー維持**(Coffee Std/Adv): 対照が3/3のアンカー(`pump one's fist`, `time lag`, `show up`, `come down`, `push prices up`)は処置 **≥2/3**。対照が2/3以下のアンカーは処置 ≥ 対照−1。
- **R2 スコア**: Coffee平均スコア(`EV.run_score`)が対照±5以内(Std 33.3、Adv 38.0; Round3の「同等幅±5」を流用)。
- **R3 低優先枠**: 低優先アンカー(rank9-12)枠/run が 対照+0.5以下(Std 1.67、Adv 0.67)。
- **R4 gate PASS率**: 回帰5セル(Coffee Std/Adv, Meta Std, Hormuz Std/Adv)の merged PASS が **≥12/15**(対照 10/12=83%。1 job分の許容)。
- **R5 meta concierge**: Meta Std+Adv(処置n=8)で `concierge` 採用 **≥5/8**(対照M2P0 3/4=75%)。
- **R6 過剰拡張**: 表示語数−候補語数 ≥2 の項目数/run が 対照+0.25以下(対照は全セル0)。新規INVALID(有限助動詞/語数)0。
- **R7 逐語**: 語幹許容の逐語率 ≥ 対照−5pt(対照 62/70=88.6%。irregular動詞は許容しない解析器のため相対比較)。
- **R8 費用**: 平均JPY/job ≤ 対照平均×1.15(0.913→1.05)。上限超過のjobは即STOP(job上限2.5)。
### 4-3. 総合区分(採用判断ではない。Trialステータスのみ)
- 改善確認(Trial): P1・P2・P3 全て満たし、かつ R1〜R8 の不合格が0。
- 部分的: P1・P2を満たし、R1〜R8の不合格が1〜2項目(どの項目かを必ず併記)。
- 不成立: P1不合格、またはR1〜R8の不合格が3以上、またはP2の有限助動詞INVALIDが発生。→ 同じ問題への修正1回目として記録。**2回修正して再発したら3回目パッチ前にOpus独立レビュー(PM_GOVERNANCE 11-3 条件B)**。
- 本件(1段落のPrompt追加)は新構造の設計ではなく条件A非該当と判断するが、最終判断はFable。有効でもProduction採用は人間ユーザーの承認が必要(Prompt変更・Validator `have` 扱いは本Trialの外)。

## 5. 実行手順(委任_02向け。委任_01では実行しない)
1. 事前確認: STOP/STOP_ALL/KP用STOP_NOTICE不在、`git status`でProduction state変更なし、`prep_run_01.json`再生成でsha一致。
2. 環境変数 `KP_NOWAY_PAID_RUN_AUTHORIZED=30` を設定して `PYTHONPATH=. PYTHONUTF8=1 .venv/Scripts/python.exe er064_kp_noway_01_run.py --mode run --stage 1 --budget-cap-jpy 30`。
3. `er064_kp_noway_01_analyze.py --glob "er064_output/kp_no_way_fix_01/runs/meta_adv_*_M2P0X_run*/job_result.json" --label treat_stage1 --out .../analysis_stage1_02.json` で4-1を判定、Go規則を適用。
4. Goなら `--stage 2`(同上)→ 解析 → 4-2/4-3 → `RESULT`は`ER`系の既存報告形式(`NOWAY_REPORT_02.md`を本ディレクトリに)。
5. 結果はTrialステータスで報告。SSOT(DECISION_LOG/OPEN_ITEMS)追記は有料run後にまとめる。

## 6. 既知のリスク・注意(事前明示)
- 追加段落が `have no way to know` を誘発して選定INVALIDになる可能性(Validatorの`have`扱い)。段落内で明示して回避を試みるが、効かなければP2で検出される(INVALIDはProductionのretry/fallbackに流れる性質のため、Trialではretryなしで記録のみ)。
- 拡張の副作用: `show up`→`show up in prices`のような過剰拡張でRedundancyや評価アンカーが崩れる可能性(R1/R6で検出)。
- n小(Stage 1 n=5、回帰n=3): 偶然の変動を排除できない。結果は方向性として扱う。
- Redundancy QA・canonicalization LLMの挙動はオフラインで予測不能(有料runで初観測)。
