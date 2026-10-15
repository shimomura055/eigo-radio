# 委任文(逐語保存) PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3〜4 委任_H(Phase A)

## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 = 委任_H(Phase A: ユーザー正式決定①〜③の規則・SSOT反映)。前提commit: F2 `a342f7b52`/F1 `71baeb78f`/F3 `a1118d9ec`/G `7997c894d`。**並行: KGCPW 委任_05がSSOT5本(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)+`CURRENT_SPEC.md`+`ACTIVE_TASK.md`を編集中。** 本委任は先に非SSOT(PM_GOVERNANCE/CLAUDE.md/Agent定義/テンプレ/運用資料)を仕上げ、**SSOT編集は`git log --oneline -5`に「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_05」のcommitが現れてから**行う(5分間隔で確認、最大45分。現れなければSSOT部分を未実施としてRESULT_PACKETに記録し、非SSOT部分のみcommit)。並行の委任_I(盲検リプレイ実動作確認)はRepo外`C:\Users\tensh\eigo-radio-replay\`と`day3/REPLAY_FEASIBILITY_01.md`のみ。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式承認済み決定の規則反映+SSOT記録(規則変更はユーザー承認範囲内のみ)。到達上限: `DAY3_PHASE_A_COMPLETE`。
- Opus独立技術レビューGate: 不要(ユーザー承認済み決定の文書反映。新構造なし)。
- 禁止: 決定①〜③の範囲を超える規則変更。**L3診断後のHuman Gate(U2-Q2 Deferred)、安全STOP(26節)、Opus利用枠(難問診断1回/管理ID・任意レビュー1日2回)、予算・仕様採用・Production採用・Human Review等の既存Gateは変更しない**(ユーザー原文「既存Gateは維持」「回数制限の撤廃は無制限のTrialや予算超過を許可するものではない」)。既存SSOTエントリの書換え(追記のみ)。コード変更なし。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。有料API 0。
- 時間見込み: 非SSOT 0.8h+SSOT 0.5h(待機含む)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する。保存先: `docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3H.md`(本委任文とユーザー指示原文を全文逐語保存。要旨化禁止)。
T-2: TTSなし。T-3: 費用0。

## ユーザー指示(原文・逐語)

# Claude Code／Fableへの回答・指示
## PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01
### Day 3〜4 ユーザー決定反映・盲検リプレイ実施

## 1. ユーザー正式決定

報告された判断事項①〜③について、以下のとおり正式決定する。

### 決定① 盲検リプレイ：Fableによる自律起動を原則とする

**承認。**

盲検リプレイは、原則としてFable自身が隔離環境から被験セッションを起動し、独立したOpusに採点させる。

役割分担：

- Fable：安全確認、被験セッションの起動・管理、結果収集、採点依頼、最終受入評価
- 被験セッション：新運営ルールに従い、与えられた課題へ対応
- Opus：独立した採点者として、事前定義済み基準に基づき評価

ユーザーによるPowerShell操作や新規セッション起動は、原則として要求しない。

ただし、まず以下を確認すること。

- `claude -p`等の実際の起動可否
- Fable／Sonnet／Opusの実際のモデル・ルーティング
- 課金経路と費用上限
- ツール権限・委任機能の動作
- 被験者と採点者の独立性
- 期待値・採点基準の漏洩がないこと
- 元のProduction Repoや秘密情報へアクセスできないこと

安全性が確保できる方法をFableが選択してよい。

`claude -p`で必要な検証委任ができない場合は、対話セッションの自律起動等、実運用に近い代替方法を検討する。

権限不足や環境制約を理由に、直ちにユーザーの手作業へ戻さず、まず自律的に解決可能な方法を調査すること。

ただし、既存の安全Gate・承認Gateを迂回してはならない。

### 決定② PM_GOVERNANCE 11-4：固定回数制限を撤廃

**正式承認。**

従来の「自律対応3回、4回目以降は毎回ユーザー判断」という回数基準は撤廃する。

今後は以下の観点で、自律対応の継続・再計画・Opus相談・STOPを判断する。

- 品質への影響
- 納期への影響
- 費用と残予算
- 問題解決の進捗
- 次の対応による改善見込み
- 同じ試行の無益な反復になっていないか
- 安全性・副作用・既存仕様との整合

**委任回数が増えたことだけを理由に、USER_DECISION_REQUIREDへ移行しない。**

11-4をこの方針へ変更し、既に改定した11-6と整合させること。

関連するAgent定義、Charter、テンプレート等に旧回数基準が残っていないか確認する。

一方、予算承認・仕様採用・Production採用・安全STOP・Human Review等の既存Gateは維持する。

回数制限の撤廃は、無制限のTrialや予算超過を許可するものではない。

### 決定③ SUSPENDED運用・Production TTS費用算定

**両方とも正式承認。**

**A. SUSPENDED運用**

未承認Trial機能の既定OFF例外について、状態を次のように運用する。

- ACTIVE：例外制度を利用可能
- SUSPENDED：違反の合理的な疑いがあり、一時停止・調査中
- REVOKED：違反確定により例外制度を廃止

違反の疑いが生じた場合、対象の利用を安全側に停止し、速やかに調査する。

違反確定時は、以前のユーザー決定どおり例外制度を直ちに廃止する。

疑いの段階で停止を緩めたり、調査中に未承認機能を有効化したりしてはならない。

**B. Production TTS費用算定**

量産原価目標70円／記事セットは、実際にProductionで利用する経路の費用を基準として評価する。

- 通常実行なら通常実行の実費
- 正式なBatch経路ならBatch実費
- Batch換算値は参考情報として区別して表示

未導入の割引や仮想的な経路の費用を、現在のProduction実費として扱わない。

70円は改善目標であり、それ自体を機械的なSTOP条件にはしない。

---

## 2. 今回実施する作業

### Phase A：決定事項の反映

上記①〜③を、既存の管理ID・OPEN-363〜367・Decision Register等との対応を確認したうえで正式記録する。

対象：

- PM_GOVERNANCE
- CLAUDE.md／Agent定義
- 関連テンプレート・運用資料
- CURRENT_SPEC（該当する場合）
- DECISION_LOG
- OPEN_ITEMS
- USER_DECISION_REGISTER
- REPORT_LEDGER

重複規則・矛盾・Dangling Referenceを確認する。

特に11-4と11-6の方針競合を解消すること。

改定後の規則が、実際に新しいFableセッションで読み込まれることも確認する。

### Phase B：盲検リプレイの実行

既存の`BLIND_REPLAY_RUNBOOK_01.md`を利用し、不要な新設計は行わない。

開始前に隔離・権限・課金経路を小規模に実動作確認する。

問題がなければ、次の検証を実行する。

1. 欠陥ケース：独立した新規セッション2回
2. 陰性対照：独立した新規セッション1回
3. 合成シナリオ：14件

独立実行が可能なシナリオは並列化してよい。ただし、各セッションの隔離・ログ分離・採点独立性を維持すること。

被験セッションには正解・欠陥の所在・採点基準を知らせない。

元Repoへの書込み、秘密情報へのアクセス、外部Productionへの影響が発生しないようにする。

安全確認に失敗した場合は被験実行を停止し、原因を確認する。

### Phase C：Opus独立評価

Opusは既存のR1〜R10基準を使用する。

ただし、陰性対照の採点では次を厳守すること。

**合理的な安全上の問題発見を、不必要な差戻しと同一視しない。**

例えば、実際の実装に潜在的な安全違反がある場合、その指摘自体を減点対象にしてはならない。

以下を区別する。

- 根拠のある安全上の指摘
- 適切なリスク報告・記録
- 不必要なProduction差戻し
- 承認済み仕様を理解せず行う誤判定

既存の採点基準と矛盾する場合は、採点基準の妥当性を独立確認する。

**実際の問題を正しく検出したセッションが、採点基準の欠陥によって不合格とならないこと。**

ただし、結果を良く見せるために採点基準を事後的に変更しない。

基準の欠陥が確認された場合は、元の採点結果と修正提案を分けて報告し、必要な承認Gateを適用する。

---

## 3. 受入条件

次の条件を満たした場合に限り、Day 3〜4の検証結果を受入候補とする。

- ユーザー正式決定①〜③がSSOTへ反映済み
- 11-4と11-6の競合が解消
- 被験Fableの実際の起動・行動ログがある
- actual model_id／routing／課金経路が確認済み
- セッションの隔離・権限制御が確認済み
- 欠陥ケース・陰性対照・合成シナリオの結果がある
- Opusの独立評価と根拠がある
- Fable自身が評価内容を独立照合済み
- 未解決事項・副作用・失敗ケースが隠されず記録されている

既定OFF例外のflag突合testや量産費用ベースラインなど、今回対象に含まれる未充足事項は、完了済みと誤認せずOpen Itemとして明示する。

---

## 4. STOP条件・今回の到達範囲

Fableは承認された範囲内で技術的問題を自律解決してよい。

ただし、以下の場合はSTOPする。

- 安全上の重大な問題
- Production Repoへの影響や秘密情報流出の懸念
- 必要な課金経路・予算を確認できない
- 新たなユーザー承認が必要な仕様変更
- 採点基準の重要な変更が必要
- 検証が無益な反復へ陥った
- 既存の正式STOP Gateに該当

Day 3〜4の検証結果が良好でも、**Day 5〜6へ自動移行しないこと。**

また、Trialの成功をProduction採用と混同しない。

Day 3〜4の検証と評価を報告したところでSTOPし、ユーザー判断を待つ。

---

## 5. 最終報告

非エンジニアPM向けに、次の順で報告すること。

1. Day 3〜4の総合判定
2. ユーザー正式決定①〜③の反映結果
3. Fable自律起動の実動作・課金・権限・安全性
4. 欠陥ケース／陰性対照／合成14件の結果
5. Opus独立評価とFable受入判定
6. 失敗ケースと原因
7. QDC上の効果と新しいリスク
8. 未完了・USER_DECISION_REQUIRED・deferred項目
9. Day 5〜6へ進めるかについての提案
10. commit／push／SSOT整合状況

**Day 3〜4のコード・文書実装と、実運用での有効性検証は明確に区別すること。**

今回の目的は、新しい運営ルールを文書化することではなく、**Fableがユーザーへの不要な判断依頼を減らし、品質・納期・費用を管理しながら、自律的かつ安全に問題を解決できることを実証すること**である。

(ユーザー指示原文ここまで。本委任はPhase Aのみ。Phase B/Cは別委任)

## KPI provenance欄 / Opus台帳更新

provenance: 該当なし。Opus台帳: 本体編集なし(OF-D3関連に変更なし)。

## 事前指定Read一覧

1. `docs/pm/PM_GOVERNANCE.md`: Grep `^### 11-4|^### 11-6|^### 11-7|^### 15-9|^### 7-9|11-4` → 11-4全文、11-6の「他規定との関係」(11-4 cycle countingへの言及)、11-7の状態定義、15-9・7-9のTTS費用算定記述、11-4を参照する他箇所一覧
2. `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/U2_AUTONOMOUS_RESOLUTION_RULE_DESIGN_01.md`: Grep `U2-Q1|11-4|案B` → 推奨Bの設計文(置換文案の土台)
3. `CLAUDE.md`、`.claude/agents/sandwich-pm.md`、`.claude/agents/sonnet-worker.md`、`.claude/agents/opus-consultant.md`、`.claude/agents/haiku-worker.md`、`docs/pm/templates/*.md`、`docs/pm/PM_BRIEF.md`: Grep `3回|4回|回目|合計最大|初回\+|回数上限|最大3回|最大2回` → 旧回数基準の残存一覧(Opus利用枠の「1回/管理ID」「1日2回」は撤廃対象外として区別)
4. `OPEN_ITEMS.md`: Grep `OPEN-363|OPEN-365|OPEN-366` / `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#63|#64|#65|#66|#7[0-9]` / `DECISION_LOG.md`: Grep `Day3〜4 ユーザー正式判断U1〜U6` → 既存記録位置(SSOT読取は待機後でよい)
5. `docs/pm/REPORT_LEDGER.md` 末尾5行

## 追記位置・更新位置の手順

### A-1 PM_GOVERNANCE(非SSOT、先行実施)
- 11-4を改定: 旧「自律対応3回・4回目以降毎回ユーザー判断」を撤廃し、ユーザー原文の7観点(品質/納期/費用と残予算/進捗/改善見込み/無益な反復/安全性・副作用・既存仕様整合)で継続・再計画・Opus相談・STOPを判断する旨へ置換。「委任回数が増えたことだけを理由にUSER_DECISION_REQUIREDへ移行しない」を逐語。「予算承認・仕様採用・Production採用・安全STOP・Human Review等の既存Gateは維持」「回数制限の撤廃は無制限のTrialや予算超過を許可するものではない」を逐語。11-4のL3診断後Human Gate・構造的問題のSTOP条件は現行維持(U2-Q2 Deferred)と明記。11-6との重複は11-6を正本にし11-4は参照に寄せる(重複規則を残さない)。改定日・管理ID・「ユーザー正式承認2026-10-15 決定②」を付記。
- 11-6「他規定との関係」の11-4 cycle counting記述を更新(競合解消)。
- 11-7: 決定③Aの3状態定義(ACTIVE/SUSPENDED/REVOKED)と「疑いの段階で停止を緩めない・調査中に未承認機能を有効化しない」「違反確定時は直ちに廃止」が既存文と一致するか確認し、不足分のみ逐語追記(既存記述を弱めない)。
- 15-9(および7-9/15-8の該当部): 決定③B「実際にProductionで利用する経路の費用を基準/通常実行なら通常実行の実費/正式Batch経路ならBatch実費/Batch換算値は参考情報として区別表示/未導入の割引や仮想経路の費用を現在のProduction実費として扱わない/70円は改善目標でありSTOP条件ではない」を逐語で反映(既存のU5-Q1実装と矛盾しないか確認)。
- 決定①(盲検リプレイのFable自律起動)はPM_GOVERNANCEの規則ではなく運用資料(`day3/BLIND_REPLAY_RUNBOOK_01.md` §2の「ユーザーまたはFableが実行」を「原則Fableが隔離環境から自律起動、Opus独立採点、ユーザー操作は原則要求しない。事前確認7項目」へ更新)へ反映。
### A-2 CLAUDE.md/Agent定義/テンプレ(非SSOT)
- Grep結果の旧回数基準を是正(Opus利用枠は維持)。CLAUDE.md Charter原則4の「安全上の回数上限と境界STOPは従来どおり(11-6)」は、11-4改定後も意味が通るか確認(Opus枠=安全上の回数上限として残る旨が11-6に書かれているなら不変で可)。
- Dangling Reference Check: 改定後に「11-4」「3回」「4回目」を参照する箇所を全Grepし一覧化(残る参照は意図的なものだけにする)。
### A-3 新セッション読込確認
- `claude -p`の実行は委任_Iの担当(本委任ではしない)。本委任では、改定ファイルがgit tracked・HEADに含まれ、`.claude/agents/sandwich-pm.md`のfrontmatterが壊れていないことを確認(YAML先頭`---`〜`---`、`tools:`行)。
### A-4 SSOT(委任_05 commit確認後)
- DECISION_LOG(索引1行+本体): 「PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3〜4 ユーザー正式決定①〜③(2026-10-15)」= 原文§1逐語+反映先(ファイル:節)+commit hash。
- OPEN_ITEMS: OPEN-363(未処理UDR U2-Q1→解決済み[決定②]、確認推奨#65/#66→承認済み[決定③]、Phase B/Cへ進行中)/OPEN-365(状態運用を決定③Aで正式化)/OPEN-366(算定基準を決定③Bで正式化)を追記更新。
- REGISTER: #63(U2-Q1)=決定済み(B採用)、#65=承認、#66=承認、新規#71「盲検リプレイ実施方法=Fable自律起動(決定①)」判断済み。集計更新。
- REPORT_LEDGER: 1行。
- `docs/pm/ACTIVE_TASK.md`: 委任_05が更新した新ヘッダを尊重し、ROLLOUT行のみ「Phase A完了・Phase B(委任_I実動作確認)進行中」へ更新。
- `day3/DAY3_PHASE_A_APPLIED_01.md`: 反映一覧(ファイル:行、決定①〜③との対応、旧回数基準の残存Grep結果、Dangling Reference結果)。

## 実行コマンド全文

- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3H.md --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3H_check.json`
- 旧回数基準Grep: `rg -n "3回|4回|回目|合計最大|初回\+|回数上限|最大3回" CLAUDE.md .claude/agents docs/pm/templates docs/pm/PM_BRIEF.md docs/pm/PM_GOVERNANCE.md`
- 委任_05待機: `git log --oneline -5`(「委任_05」を含む行の出現を5分間隔で確認)
- 既存test: `.venv\Scripts\python.exe -m pytest docs/pm/tools -q`(check_delegation_prompt関連testが存在する場合。無ければ省略)
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`
- git: `git status --porcelain`(add対象のみ)、`git log --oneline -3`

## SSOT追記文

上記A-4。ユーザー原文は逐語、事実はcommit hash付き。

## Git(明示add対象・コミットメッセージ・trailer)

2 commitに分ける: (1)非SSOT「PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase A 委任_H(1/2): ユーザー正式決定②③の規則反映(PM_GOVERNANCE 11-4回数制撤廃→QDC7観点・11-6整合・11-7 3状態・15-9 Production実経路基準)+決定①をRUNBOOKへ+Agent定義/テンプレの旧回数基準是正。SSOTは(2/2)」 (2)SSOT「…委任_H(2/2): SSOT記録(DECISION_LOG 決定①〜③原文、OPEN-363/365/366更新、REGISTER #63/#65/#66決定済み+#71、REPORT_LEDGER)。JPY0」。明示addのみ。push to origin/main。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_ROLL3H.md`へ: (1)T-0 (2)11-4改定前後の全文 (3)11-6/11-7/15-9の差分要旨 (4)旧回数基準の残存Grep結果と是正一覧(撤廃対象外として残したものとその理由) (5)Dangling Reference結果 (6)SSOT差分(ファイル:行) (7)委任_05待機の経過(確認時刻・commit hash) (8)commit hash×2・push・raw URL(PM_GOVERNANCE・DECISION_LOG) (9)確認できなかった事項・逸脱。

Fableは(2)(4)を照合する(受領≠受入)。
