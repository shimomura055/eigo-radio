FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_31(Fableから): ユーザーがUDR #178を承認(KP案件累計上限300→500円、X2p'補強Trial実施、到達上限VALIDATED、Production配線は自動開始しない)。委任_30で準備済みの成果物(commit e7f4a75ee: TRIAL_DESIGN_07、HARDCORE_HELDOUT_02、`er112_kp_gm_trial_06.py`、fable_blind_06、BUDGET_PLAN_T6_01)を使い、重複準備なしで有料の補強検証を実行する。

## 0. 最初にやること(0円)
- ユーザー指示原文を逐語保存: `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_08.md`。原文は本委任文の末尾【ユーザー原文】ブロック(逐語、改変禁止)。
- `docs/pm/USER_DECISION_REGISTER_01.md` #178 を「判断済み(2026-10-24、承認A相当・上限500円)」に更新。KP案件の予算記録(BUDGET_LOG_01/BUDGET_PLAN_T6_01の該当欄)に上限500円・「使用目標ではなく停止防止の上限」を記録。DECISION_LOGに予算判断1エントリ。
- 日次確認: `daily_dev_cost_01.py`等で10-24(JST)の日次累計を確認(把握分約414円)。本Trial上限28円を足しても1,000円内であることを記録。KP案件累計(台帳全合算295.43円)+28円≤500円。

## 1. 実行構成(Fable決定)
- **P案(本番相当・full-level、見積20.99円)**、cap 28円(retry込み)。ユーザーが「本番と同じ構成」を最重視しているためQ案(段落上限5)ではなくPとする。R案は不採用。
- 手順は委任_30の次の一手どおり: `prodhash start` → (b)新hard-core 9KP `gen --set HC --siblings off --reps 1,2` → (b')元hard-core R集合の退行確認(約0.75円、実施する) → (c)Stage 2 `gen --set S2 --siblings on`(full-level) → `prodhash end`(start/end一致を記録)。
- arm: B0p(現行Production `ga.align_glosses`そのまま)とX2pp(X2p'、同level全KP 1 call、`rules_fulltext`、`prior`、retry上限2)。X2p' Promptは**変更しない**(TRIAL_DESIGN_07の「修正は1回のみ」は、問題が出た場合の自己ループにのみ使い、理由をPROMPT_DIFFとして記録)。
- 有料起動は上記の各genを1回ずつ。retryはharness内の上限2のみ。capに当たって止まった場合、残費用と残工程を記録してFableへ報告(自己判断で再起動しない)。
- 使用モデル: 現行Production glossと同一モデル(名称・最新かを記録。最新でなければ理由=本番同一条件)。

## 2. 記録するもの(ユーザー確認6項目に対応)
1. 本番構成(複数KP 1 call)での効果再現: Stage 2 54KP(評価KP)+sibling生成数、B0p vs X2pp の strict PASS/THIN/FAIL/FAIL_LIT 分布(ラベルはFable/Opusが付ける。agentは文字列収集・盲検表作成まで)。
2. 新難例9件(HC): B0p vs X2pp、rep 1,2。
3. 過剰解釈: 対照KP `sheltered from the rain` 等、字義が正解のKPで解釈訳化が起きたか(文字列を盲検表に含める)。
4. 通常KP品質維持: Stage 2の PASS→THIN/FAIL 件数(ラベル後に `agree` で再計算)。
5. 実測単価: call数・入力/出力トークン・reasoningトークン・円、KP単価と1記事セット換算(約10KP、sibling込み)、生成時間(call当たり・記事セット換算)、B0p比。
6. X/Y/Z適用可能性: Xは本Trialの主対象、ZはHCにZ小説5件を含むので別集計、Yは`er110`系の現行gloss経路の有無をGrepで確認し、Yへ適用する場合の経路(OPEN-484との関係)を事実として記す(実装しない)。
- 盲検表: `fable_blind_06.md`に今回出現した文字列を埋め(arm伏せ、既ラベル継承、key分離)、同じ内容をOpus評価用にも使えるよう`OPUS_EVAL_REQUEST_06.md`(評価基準の明示・armは伏せる・再照合対象`add up`/`reach for someone's wallet`を明示)を用意。Fable/Opusのラベル受領後に`er112_kp_gm_trial_06_blind.py agree --labels`で一致率とBefore/Afterを算出する前提で、集計コマンドと入力形式をhandbackに書く。
- 台帳: `TRIAL_06/BUDGET_LOG_T6_01.md`(call単位、stdout控え)、`TRIAL_06/METRICS_06.md`、`TRIAL_06/TRIAL_RESULT_06_DRAFT.md`(ラベル待ちの欄を空けておく)。

## 3. 自己ループの条件(ユーザー§3)
- 問題(cap停止、retry多発、JSON崩れ、持ち込み多発等)が出たら原因→修正→再検証を予算内で行うが、同じ方法を繰り返さない。Prompt修正は1回まで、追加検査callや工程追加は導入しない。承認範囲外の新仕様・新テーマは追加しない。
- 予算: KP累計500円・日次1,000円の両方。上限接近(KP累計450円/日次900円)見込みで事前報告。

## 4. Git/SSOT
- commit前に`git status`でindex確認、`git commit --only -- <paths>`(他agentの未commit差分を巻き込まない、必要なら一時index方式)。`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止。raw_usage_log・ACTIVE_TASK・RESULT_PACKETは追跡しない。OPEN-490自動書換えは復元・stageしない。secret grep 0件。`git push origin HEAD:main`。
- OPEN-474にTrial_06実行の1行、CURRENT_SPECは触らない(VALIDATED判定前)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_31.md`(Nは先頭「FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_31」を含むAgent呼出の0始まり通番、jsonl検索で特定。直近は452)。

## 5. handback
実行結果(各gen のcall数・費用・時間、prodhash一致)、盲検表のパスと行数、機械的に分かる事実(JSON失敗数、retry数、持ち込み検出record-onlyの件数、HCでの文字列の変化有無は述べてよいがPASS/FAIL判定はしない)、費用(本委任実績・KP累計・日次累計)、commit hash、raw URL、Fableが次にやること(ラベル付けの手順と`agree`コマンド)。

【ユーザー原文】
# 追加指示｜Key Phrase① 字義訳根本改善・補強Trial予算承認（UDR #178）

## 1. ユーザー決定

**UDR #178：補強Trialの実施を承認する。**

- Key Phrase案件の累計開発予算上限を **300円 → 500円** に引き上げる。
- X2p'の補強Trialを、報告済みの計画に基づいて実施する。
- 今回の補強Trialの想定費用は約20〜21円、retry込み上限約28円。
- Production採用は未承認。今回の到達上限はVALIDATED。

**重要：500円は使用目標ではなく、作業が途中で不要に停止することを防ぐための上限である。**

予算を使い切る必要は一切ない。必要十分な検証が完了した時点で終了すること。

## 2. 補強Trialの実施

既に準備済みの成果物（commit e7f4a75ee）を活用し、重複する設計・準備作業を行わず、速やかに検証する。

特に以下を確認する。

1. 本番と同じ、複数Key Phraseをまとめて意味生成する構成で改善効果が再現するか。
2. 事前固定した新規難例9件を使い、未知の表現でも効果があるか。
3. 本来字義どおりに訳すべき表現を、誤って比喩的に解釈する悪化がないか。
4. 通常Key Phraseの意味品質が維持されるか。
5. 実測の量産単価増加と、生成時間への影響。
6. Family X/Zおよび開発中のYへの適用可能性。

FableとOpusによる独立評価を行い、改善件数・残存NG・新規悪化を区別して報告する。

## 3. 自律的な問題解決

Trial中に問題が発生した場合は、承認済み範囲・予算内で、原因究明→修正→再検証の自己ループを行う。

- 失敗した方法を漫然と繰り返さない。
- 改善の見込みが低い場合は、原因やアプローチを再検討する。
- 追加検査callや工程の複雑化を安易に導入しない。
- 過去のTrial・正常な成果物・評価データを再利用する。
- 品質を守りながら、費用・時間を最小化する。
- 必要十分な品質に達したら、それ以上のTrialを行わず終了する。

今回承認した補強Trialの範囲を超える新仕様・新たな検証テーマは、予算が残っていても無断で追加しないこと。

## 4. 予算管理

- KP案件累計上限：500円
- プロジェクト全体の日次開発費上限：1,000円（JST）
- 両方の上限を遵守する。
- 上限への接近が予想される場合は、余裕を持って事前報告する。
- 少額費用ごとの承認確認は不要。
- 既存のSTOP条件、品質基準、承認範囲を維持する。

予算枠の増額を理由にTrial回数を増やさない。

## 5. Trial Closeoutと最終報告

以下を報告すること。

- X2p'の本番相当条件での検証結果
- Before／After、改善・残存NG・新規悪化
- Opus／Fableの独立評価
- Family X/Y/Zへの適用方針と例外の必要性
- 量産単価・生成時間への影響
- 実際の使用額・KP案件累計額
- Trial最終Status（REJECTED／VALIDATED／USER_DECISION_REQUIRED）

VALIDATEDでもProductionへの配線を自動開始しない。

正式採用については、ユーザーの明示判断を求める。

UDR #178の予算判断を記録し、関連するDECISION_LOG／OPEN_ITEMS／予算管理記録を更新する。

---

**最優先方針：字義訳の根本解決を、品質を守りながら最速・最小費用で実現する。500円を使い切ることではなく、必要な検証を途中停止なく完了することが目的である。**