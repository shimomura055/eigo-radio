## 管理ID

GPT6-MODEL-COMPARISON-TRIAL-01(Closeout=正式価格の一次ソース確認・84 call 実測コスト再計算・Trial Status 分類の SSOT 反映、委任 _04)。一時ファイル `docs/pm/ACTIVE_TASK_G6D.md` / `docs/pm/RESULT_PACKET_G6D.md`(commitしない)。並行: 別 Sonnet 1 件(OPEN-233 再設計案 v0.2、出力先 `docs/pm/design_checker_redesign_v02_01.md`・`OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`)→ これらに触れない。**SSOT 4 点(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)+REPORT_LEDGER は本タスクが編集権を持つ(直列化)**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキー本文を表示・log・commit・報告に書かない**。Production code・Prompt・Checker・routing・schema の変更禁止。**API 呼び出し(有料)禁止、Sol/Astra の追加 call 禁止**(¥0)。Opus 起動禁止。

## ユーザー決定(2026-09-29、逐語厳守)

- `gpt-6-luna` は「Checker の正式採用候補として次工程へ進める」。ただし「Trial 結果を踏まえた有力候補/Production routing 変更前」であり **`APPROVED_FOR_PRODUCTION` にはしない**。
- `gpt-6-sol` の本比較は **保留**(probe 結果は Evidence 保持、追加 Trial・大量 call 禁止)。Astra 対象外。
- OPEN-233 を deferred から **再開**(REOPENED)。OPEN-234 は引き続き後回し。
- 「単価未確認のままにしない。OpenAI 公式の最新 Pricing / API documentation を確認。第三者情報・推測は禁止」。

## A. 正式価格の確認(一次ソースのみ)

対象: `gpt-5.6-luna` / `gpt-6-luna` / `gpt-6-sol`。項目: input / 1M tokens、cached input / 1M tokens、output / 1M tokens、reasoning token の課金方法(output に含まれるか等)。
取得手段(順に試行、成功したものを記録): (1) `curl -sL -A "Mozilla/5.0" https://openai.com/api/pricing/`、(2) `curl -sL -A "Mozilla/5.0" https://platform.openai.com/docs/pricing`、(3) headless Chrome `chrome.exe --headless=new --dump-dom <URL>`(Pages 確認で使用済みの手段)、(4) `https://platform.openai.com/docs/models/<model_id>`(モデルページに価格が併記される場合)。**取得した DOM/HTML から該当行を逐語抜粋し、URL・取得日時(UTC/JST)・抜粋を REPORT に記録**。3 モデルのいずれかが取得不能なら、その model のみ「公式ソースで確認不能(取得試行の URL・HTTP status・日時)」と明記し、**推測値を書かない**。

## B. 84 call 実測コスト再計算

`er050_output/gpt6_checker_comparison_trial_01/**/run_*.json`(step1/step1_er009_changed_actor_n5/step2/step3、84 call)+`er050_output/gpt6_sol_probe_result.json`(参考、Trial 外)から、model 別に input / cached_input / output / reasoning tokens・call 数を集計(集計スクリプトは scratchpad、repo に追加しない。集計結果 json は `er050_output/gpt6_checker_comparison_trial_01/cost_recalc_01.json` として保存可)。
- 正式単価 × token で GPT-5.6 Luna / GPT-6 Luna それぞれ: 総 USD、1 call 平均、1 call 中央値、記事換算(4 Checker call)。cached input は cached 単価で計算(cached 単価が公式にあれば)。reasoning token は公式の課金方法に従う(output に含むなら二重計上しない。現行 log の `output_tokens` に reasoning が含まれるかを `usage` 構造から確認して明記)。
- 差分: %、USD、JPY 参考換算(為替レートは一次ソース[例: 日本銀行 or 公表レート API]から取得し、レート・取得日時を明記。取得不能なら「換算なし」)。
- **過去値との整合**: 「現行 Checker ≈ ¥0.90/call(`NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01` n=12)」と今回実測(harness の `ref_cost_jpy` に用いた単価・レートを Grep で特定)を突合し、差があれば原因(単価版・レート・token 量の違い)を記述。
- 単価が確認不能な model は token 集計のみ提示し USD を出さない。

## C. Trial Closeout の SSOT 反映

- **Trial Status 分類(Fable 判定)**: `VALIDATED`(Checker 採用候補として次工程へ進めることをユーザーが決定。**`APPROVED_FOR_PRODUCTION` ではない**、Production routing 未変更)。根拠: 重大検出で優位(changed_actor 50% vs 0%、Meta 境界例検出)・新規重大見逃し 0・gold 一致率 90% vs 70%・token −7%/非改善: 不要 BLOCK 率 75%=75%・latency +34%・(単価は本委任で確定)。
- CURRENT_SPEC: 「Model Routing」関連小節に「Checker 採用候補 `gpt-6-luna`(VALIDATED、routing 未変更、正式採用は別途ユーザー判断)」「`gpt-6-sol` 互換性 probe SUCCESS・本比較保留」「`gpt-6-astra` 対象外」を追記(Contract は不変)。
- DECISION_LOG: 新エントリ(ユーザー判断逐語: Luna 候補化・Sol 保留・Astra 対象外・OPEN-233 再開・OPEN-234 後回し・価格精査必須/Fable の Trial 分類と根拠/価格・コスト再計算結果の要約)。
- OPEN_ITEMS: **OPEN-233 を `REOPENED (ACTIVE)`** へ変更し、再設計目的(逐語: 「必要なものは確実に止め、不要なものは止めず、しかも安定して判定する Checker へ再設計する」「過剰品質によって Production の生産性が失われることは許容しない」)、GPT-6 Trial の追加 Evidence(post-hoc 降格のみ非対称、changed_actor 現行 0/6・GPT-6 3/6、B-2 非決定性、B 群不要 BLOCK 率 75%=baseline、JA 段の揺れ)、並行の再設計管理ID `OPEN-233-CHECKER-REDESIGN-V02-01` へのポインタを追記。OPEN-234 は deferred 維持。
- REPORT_LEDGER: `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` を VALIDATED(採用候補、Production 採用ではない)で更新。
- REPORT `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` に §Closeout(正式価格表・84 call 再計算表・差分・過去値整合・Status 分類・Closeout 10 項目)。設計書 §10。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_04.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_04.md --json-out docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_04.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: API 支出なし。

## 事前指定Read一覧 / 事前指定Grep一覧

- `er050_gpt6_checker_comparison_trial_01.py`: Grep `ref_cost|USD_JPY|price|PRICE|per_million`(参考換算に使った単価・レート)、`NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01_REPORT.md` §0/§1(¥0.90 の算出根拠)、`er050_output/.../budget_state.json`、`CURRENT_SPEC.md` Grep `Model Routing|gpt-5.6|Approved Model`、`OPEN_ITEMS.md` Grep `OPEN-233|OPEN-234`、`DECISION_LOG.md` 先頭ヘッダーチェーン。
- 更新位置: REPORT、設計書、SSOT 3 点+REPORT_LEDGER、`cost_recalc_01.json`、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- 価格取得: 上記 (1)〜(4)
- 集計: `.venv\Scripts\python.exe <scratchpad>\recalc_cost.py`(自作、repo 外)

## Git

- commit 2 つ: (1) REPORT §Closeout+設計書+`cost_recalc_01.json`+delegation_log `GPT6-MODEL-COMPARISON-TRIAL-01: Closeout(公式価格一次確認、84 call実測コスト再計算、過去値整合、Status=VALIDATED[採用候補・Production採用ではない])`;(2) SSOT 3 点+REPORT_LEDGER `GPT6-MODEL-COMPARISON-TRIAL-01: SSOT反映(gpt-6-luna=Checker採用候補VALIDATED・routing未変更、Sol保留、Astra対象外、OPEN-233をREOPENEDへ、OPEN-234 deferred維持)`。trailer `Management-ID: GPT6-MODEL-COMPARISON-TRIAL-01`、path 指定 add、push。

## 報告(RESULT_PACKET_G6D + handback、目安35行)

【正式価格】(model 別、URL・日時・逐語抜粋、確認不能なら明記)【84 call 再計算】(model 別 総 USD・平均・中央値・記事換算、差分 %・USD・JPY[レート・日時])【過去値 ¥0.90 との整合】【SSOT 更新箇所】(OPEN-233 REOPENED、Trial VALIDATED、CURRENT_SPEC 追記)/commit hash 2 件・raw URL/STOP 有無。
