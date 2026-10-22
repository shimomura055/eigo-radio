FABLE-DELEGATION-MARKER: KPMG-CLOSEOUT-RECORD-委任_02-20261022

# 委任(FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_02: Fable独立評価・Trial Closeoutの記録のみ。API 0・JPY0・コード/Production無変更)

## 管理ID
FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_02(並行: `PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07`がOPEN-441行・REPORT_LEDGER末尾・UDR #142行を編集中。共有ファイル編集前に`git status`→該当行再Grep→自分の行だけ→即add+commit。`index.lock`は30秒待って再試行)。

## 性質/到達上限Status/禁止事項
- 記録のみ。到達Status: OPEN-446=`TRIAL1_VALIDATED_TRIAL2_REJECTED_PENDING_USER`(Fable分類)。Opus Gate: 非該当。費用/日次: JPY0。
- 禁止: コード・Excel・Trial成果物・Production・Promptの変更禁止(TRIAL_RESULT_02.md §7 Fable欄への追記のみ可)。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore(force-add禁止)。SSOT全文読込禁止。他agentの未commit差分を混ぜない。

## 前委任(委任_01)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_USER.md`): 「今回のゴールは、長く焦点のぼやけたKey Phraseを減らし、学習価値の高い表現を簡潔かつ汎用的な形で安定して提供できるかを判断すること。」Trial①=最小化Prompt×5モデル、Trial②=Luna選定結果への一般化工程分離Before/After。
- 最終成果物: `docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/{KP_PROMPT_MIN_GEN_COMPARISON_02.xlsx(6シート),TRIAL_RESULT_02.md,TRIAL_DESIGN_02.md}`、`er101_output/kp_prompt_min_gen_trial_02/`、`er101_kp_prompt_min_gen_trial_02_*.py`。commit ceb59ca21。
- 証拠: 本文sha 14/14一致、返却model ID 70/70一致、Prompt sha全件同一、技術的失敗1(ConnectTimeout、同一入力再試行で成功)、費用JPY188.278(選定43.806/一般化1.283/評価143.188、paid_calls.jsonl)、Prompt調整事後報告(①後置のみ、②文脈文を全件同一形式で付与+JSON出力指定)、評価方法変更点明示(G観点除外、C/U/S/X新設・旧出力は未採点)。
- 一致・不一致: §1〜§7要求=一致。限界開示(C/U/S/Xの旧出力同尺度比較なし、Trial②は文脈文なし条件と未比較、抽出の手動補正4件はモデル出力無改変)。
- 判定: ACCEPTED。判定整合: 重大NG=なし/主因=なし/是正対象=なし/STOP理由=なし/提示=ユーザー判断3件(A/B/C)。

## Fable独立評価・Closeout(TRIAL_RESULT_02.md §7へ逐語で追記)
### 7. Fable独立評価・Trial終了Status(2026-10-22)
- 分類: **Trial①=`VALIDATED`**(最小化Promptの有効性は確認。Production採用ではない)。**Trial②=`REJECTED`(今回構成=Claude Haiku 5.5+初期一般化Prompt)**。2工程方式という考え方自体は閉じない(下記C)。
- Trial①の根拠: 5モデルすべてで平均語数が短縮(Luna 3.61→3.14、Sonnet 3.89→2.87等)し、5語超0件・本文一致も維持(Luna 69/70、Haiku/Sonnet 70/70)。例示3件のうち`think up what happens next→think up`はLuna/Sonnetで達成、`formal agreements with their creators→through formal agreements`(Luna)は改善方向、`alone caused the different results`は期待形が本文に連続して存在しないため本文一致必須の条件下では原理的に不可能(Trial②/原形化の領域)。留意: Lunaの学習価値V(前回と同観点)は1.26→1.06へ低下しており、短縮と引き換えに価値がやや下がった可能性がある(評価者のぶれ[前回実測 平均絶対差0.11]の範囲内で断定不可)。
- Trial②の根拠: 変更16/70に対し原形化の適用漏れが17〜22/70(両評価者一致17)、過剰変更4、意味変化3、許容外の語の追加4(`materials`/`service`/`to`/`country-led`)。一般化の適切さ両者PASSは44/70(63%)。「変更すべきものを変え、不要なものを維持する」という要件を満たしていない。なお**原形化(canonicalization)は既存Production(DB hybrid方式)に既に工程として存在し**、今回の漏れの大半は既存工程が担っている種類の処理である。従って「新たに一般化LLMを1工程追加する」より、「最小化条件を既存のProduction経路(shortlist→選定→canonicalization)に入れて検証する」方が、既存仕様との整合・費用・リスクの面で合理的。
- 既存Productionとの比較の読み方: 今回Luna(厳格合格69/70、V/E/N 0.629、0.258円+一般化0.183円)と既存(47/70、0.550、1.828円)は方式が異なる(全文渡し vs DB hybrid+canonicalization)。既存の厳格合格の低さの大半は意図した原形化によるもの。費用差は方式差(shortlist・canonicalizationの呼出)を含む。
- Fable推奨(ユーザー判断A/B/Cは別件として整理):
  - **A(選定モデル変更)=現行gpt-6-luna維持を推奨。** Sonnet 5.5は最良だが費用約20倍。Claude Haiku 5.5は2回のTrialで一貫してLuna以上(遵守100%、最小化0.843 vs 0.766、価値0.669 vs 0.629)で費用もほぼ同等(0.335 vs 0.258円/セット)だが、差は評価者のぶれの範囲内で、かつProductionにAnthropic APIという新しいProvider依存を追加する実装・運用コストが発生する。品質差が実証されるまで切替は不要。
  - **B(選定・一般化の2工程方式の正式採用)=今回構成では不採用を推奨。** 適用漏れ・過剰変更が多く、原形化は既存工程で担える。
  - **C(次の一手)=「最小化条件(新Prompt第3条)を現行Production経路のPromptに組み込み、同一14本文・Lunaで現行方式と比較する小規模Trial」を推奨(見積は事前に算出、前回規模より小さい見込み)。** 採用判断はその結果で行う(Prompt変更はユーザー承認事項)。
- Closeout: Production/Prompt/Validator/モデル構成は無変更。再現情報=TRIAL_DESIGN_02.md+`er101_*`+paid_calls.jsonl。Opus条件Cレビューは採用提案時に実施。

## 更新箇所
- `docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/TRIAL_RESULT_02.md`: §7 Fable欄に上記を追記。§8(次に必要なユーザー判断)がSonnet記載なら「Fable整理: A/B/C(上記)」を1行追加。
- `OPEN_ITEMS.md`: Grep `OPEN-446` → Statusを`TRIAL1_VALIDATED_TRIAL2_REJECTED_PENDING_USER`(Fable分類2026-10-22、推奨A=Luna維持/B=今回構成不採用/C=Production経路Prompt Trial、UDR #146)へ。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#145` → 直後に `- #146(UDR・**回答待ち**・非blocking、FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02、OPEN-446) 件名=KP選定の(A)モデル変更/(B)選定・一般化2工程方式の採否/(C)最小化条件をProduction経路Promptへ入れる比較Trial GO。Trial①=VALIDATED(最小化有効)、Trial②=REJECTED(Haiku+初期Prompt、原形化漏れ17〜22/70)。Fable推奨=A:現行Luna維持/B:今回構成不採用/C:GO(小規模、見積は事前提示)。Excel=docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/KP_PROMPT_MIN_GEN_COMPARISON_02.xlsx。出典=TRIAL_RESULT_02.md §7。` を追加。#145行に「(関連#146。Trial②の結果でも推奨Luna維持は不変)」を1句追記。
- `DECISION_LOG.md`: 末尾に「FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_02 Fable分類(2026-10-22)」エントリ(上記分類・根拠・推奨。採用判断はユーザー、Production無変更)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行 `- 2026-10-22 | FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_02 | Fable分類 Trial①VALIDATED/Trial②REJECTED(今回構成)、推奨A Luna維持/B不採用/C Production経路Trial、UDR #146起票、記録のみ¥0。`
- `docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ(当日費用=2026-10-22 約670/1,000[出典 RESULT_PACKET_B3RD8 275.35+KP6M1 206.60+KPMG1 188.28]+Stage 2進行中)。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_委任_02.md`(Nは`FABLE-DELEGATION-MARKER: KPMG-CLOSEOUT-RECORD-委任_02-20261022`を含むAgent tool_useの通番、268前後。先頭行で一致確認)。

## Git
- 明示add: 上記5ファイル+delegation_log。commit: `KPMG 委任_02: Fable分類 Trial①VALIDATED(最小化Prompt有効)/Trial②REJECTED(今回構成)、推奨=Luna維持・2工程不採用・Production経路Prompt Trial提案、UDR #146、記録のみ¥0`。push→到達確認。

## 報告(RESULT_PACKET_KPMG2.md)
変更ファイル:行、commit hash、raw URL(TRIAL_RESULT_02.md)、RESULT_PACKET 4行。