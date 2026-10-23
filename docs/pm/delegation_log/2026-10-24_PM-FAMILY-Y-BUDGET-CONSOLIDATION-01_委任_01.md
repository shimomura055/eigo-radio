MARKER: PM-FAMILY-Y-BUDGET-CONSOLIDATION-01 委任_01 (2026-10-24, Fable→sonnet-worker)

# 管理ID: PM-FAMILY-Y-BUDGET-CONSOLIDATION-01 委任_01(ユーザー決定「Family Y固有の累計予算上限の撤廃・日次1,000円一元管理」の管理文書反映。API 0・Production変更0)

## ユーザー決定(2026-10-24、原文は末尾§Zに逐語。**最初に** `docs/pm/delegation_log/2026-10-24_PM-FAMILY-Y-BUDGET-CONSOLIDATION-01_USER.md` として逐語保存)
- Family Y固有の累計開発予算上限(600円/650円等)を撤廃。以後はプロジェクト共通の日次1,000円(JST)で管理(他Family・並行タスク含む全体上限)。費用はタスク別記録を継続。日付変更での不要な分割・延期禁止。
- 上限接近時の事前報告(使用額・残額・継続見込み費用・作業状況と残工程・追加予算要否)。少額ごとの承認は求めない。**追加承認なく日次1,000円を超過しない。**
- Family Y Persona改善Trialは継続。UDR #176の予算上限変更判断は本決定で解消(ただし旧題材再現検証・6段階iterationなど承認範囲を超える選択肢は従来どおり判断Gate)。
- 本変更は他タスクの個別承認条件(例: KP案件の7-7枠等)を撤廃する根拠にしない。

## 作業
1. `docs/pm/PM_GOVERNANCE.md`: 7-9(日次上限)・7-7(案件枠)付近に「Family Y固有の累計上限は2026-10-24に撤廃、日次1,000円で一元管理。上限接近時の事前報告義務。他タスクの個別承認条件は不変」を既存書式で最小追記(新規節は作らない。該当節番号はGrepで特定)。
2. `OPEN_ITEMS.md` OPEN-463: 「Y累計上限600円→撤廃(2026-10-24ユーザー決定)、以後日次1,000円で管理。UDR #176の予算判断は解消」を1行追記(他agent[FAMILY-Y 委任_20]がOPEN-463へ並行追記中の可能性: commit前に `git diff -- OPEN_ITEMS.md` で自分以外のhunkを確認、含まれる場合は数分待って再確認、残る場合は報告に明記)。
3. `DECISION_LOG.md`: ユーザー決定1件。
4. `docs/pm/USER_DECISION_REGISTER_01.md` #176: 「予算上限変更の部分は本決定で解消(判断済み2026-10-24)。選択肢(A)旧題材再現検証/(B)/(C)6段階iterationの実施可否は未回答のまま維持(Scope判断として残る)」に更新。
5. **実行制御・STOP判定の残存確認**: `er110_*` runner・`docs/research/FAMILY-Y-VOICES-DESIGN-01/**/BUDGET_PLAN*.md`・`ACTIVE_TASK.md` のY行で、「Y累計600/650円」を上限として参照している定数・文言・STOP条件をGrepで列挙し、実行制御に効くもの(例: 累計をチェックして停止するコード)があれば日次1,000円参照または撤去に修正(per-run cap `TREE_CAP_JPY` 等の**run単位**の歯止めは残す。これはY累計上限ではない旨をコメント)。文書上の「Y累計上限」記載は「撤廃(2026-10-24)」注記に。結果を `docs/research/FAMILY-Y-VOICES-DESIGN-01/BUDGET_POLICY_CHANGE_01.md` に表で記録。
6. `docs/pm/ACTIVE_TASK.md`: 固定ヘッダの予算行(日次上限・Y累計)を本決定に合わせて更新(Y累計の「上限」表記を削除し実績のみ残す)。本管理ID行を新設。
7. 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_PM-FAMILY-Y-BUDGET-CONSOLIDATION-01_委任_01.md`(先頭MARKER一致、0始まり)。commit前に `git status` でindex確認→`git commit --only -- <paths>`(`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。
8. 報告 `docs/pm/RESULT_PACKET_PMYB1.md`: 更新箇所、残存確認表(実行制御に効いていたものの有無)、commit hash、4行、判定整合行。

## §Z ユーザー指示原文(逐語)
# 追加指示｜Family Y予算管理方式の変更

## 1. ユーザー決定（正式承認）

**Family Y固有の累計開発予算上限（600円／650円等）を撤廃する。**

今後、Family YのTrial・原因究明・改善検証については、プロジェクト共通の**日次開発費上限1,000円（JST）**で管理する。

- Family Y固有の累計予算によるSTOPは廃止。
- 日次1,000円はFamily Y専用ではなく、他Family・並行タスクを含むプロジェクト全体の上限。
- 費用は引き続きタスク別に記録し、QCDと量産単価を管理する。
- 日付変更を理由に作業を不必要に分割・延期しない。

## 2. 予算上限接近時の事前報告

**当日の累計開発費が1,000円に近づき、進行中の作業で上限到達が見込まれる場合、余裕を持ってユーザーへ事前報告すること。**

報告内容：
- 当日の使用額・残額
- 継続に必要な費用見込み
- 作業状況と残工程
- 追加予算が必要な場合の金額と理由

上限に達してから初めて報告する運用は避ける。

一方、残予算内で完了可能な作業について、少額費用ごとに承認を求めない。

**ユーザーの追加承認なく日次1,000円を超過しないこと。**

## 3. Family Y Trialの継続

前回指示の予算制約部分を本決定で置き換える。

- Family YのPersona改善Trialを継続する。
- UDR #176の予算上限変更判断は、本決定に基づき解消する。
- 承認済み改善方針の範囲で、原因究明→対策→Trial→評価の自己ループを自律的に進める。
- 品質を維持しながら、不要なTrial・待機・費用を削減する。

ただし、**予算上限の撤廃は、未承認の新仕様・新Trial範囲・Production採用を自由に認めるものではない。**

UDR #176に含まれる旧題材での再現検証や6段階方式の追加iterationなど、今回の承認済み範囲を超える選択肢は、従来どおり適切な判断Gateで扱う。

## 4. 管理文書の更新

PM_GOVERNANCE、OPEN_ITEMS、DECISION_LOG、関連するFamily Yの予算管理記録を更新する。

旧600円／650円上限が実行制御やSTOP判定に残らないよう整合を確認すること。

本変更を他タスクの個別承認条件まで無断で撤廃する根拠にはしない。

**最優先原則：品質を守りながら最速で完成させる。開発費は日次1,000円で一元管理し、上限接近時のみ前広に報告する。**