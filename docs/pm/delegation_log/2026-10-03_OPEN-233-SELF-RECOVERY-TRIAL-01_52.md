## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_52)。並行タスク: 委任_51(ユーザー決定のSSOT記録・線引き・再分類。**SSOTを編集するのは委任_51だけ**)、委任_53(説明文混入12件の対策、runner編集+有料)。本委任は**read-only調査+新規doc 1点のみ**。runner・Production code・SSOTを編集しない。git操作もしない(commitはFableが後で別委任で行う)。

## 性質/到達上限Status/禁止事項

- 性質: (A)末尾句読点差対策(Trial runnerの`VS_MATCH_EXT`のL5)を**Production正式経路へ反映するための準備**(反映先の特定・計画・Gate追跡の設計。実装はしない)、(B)日本語本文を直さないことで後続処理に実害があるかの整理(具体的なProduction経路つき)。
- 到達上限Status: なし。Production code変更なし。`PRODUCTION_WIRED`判断はしない。
- 禁止事項: すべてのコード・Prompt・テスト・SSOT・既存docの編集禁止。LLM/API呼び出し禁止(¥0)。`git add`/`commit`/`push`禁止。
- 費用上限: ¥0(T-3対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 本委任は準備・調査のみで非該当。ただし反映計画の中で「Production反映の実装前に条件C(Production採用候補の最終レビュー)に該当するか」を判定して記載する。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する。
T-2: TTSを伴う委任はSTANDARD明示。(本委任はTTSを伴わない。)

(注: 本ファイルは委任文の要点を含む保存版。ユーザー指示原文・作業A(A-1〜A-5)・作業B(B-1〜B-4)・事前指定Read/Grep一覧・報告項目は受領した委任文のとおり。新規docは`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`。)

## ユーザー指示(原文要点、2026-10-03)

3. 日本語本文は原則修正しない: LedgerとのDeviationが英語側にあるなら英語だけ修正する。英語のDeviation修正のために日本語本文へ遡らない/日本語側の対応箇所を推測して同時Rewriteしない/日英整合のためだけに処理を複雑化しない。日本語タイトルは英語本文の最小修正で変更する前提にしない(タイトル変更なし前提)。確認すべきは「日本語本文を直さないことで後続処理に実害があるか」だけ。実害があれば具体的なProduction経路を示す。単に整合を保ちたいだけなら対策不要。

4-1. 末尾の句読点差22件: 既存346件で再生・22件解消・悪化0。ユーザーとして正式採用してよい意向。Trial/DEV専用に残さずProduction正式経路への反映対象として追跡する。`PRODUCTION_WIRED`と判断するのは既存Gateどおり、Production初回経路への実装・retry/fallback/regenerationとの整合・runtime evidence・必要test PASS・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Git反映まで完了してから。「Trialでは直っていたがProductionへ入れ忘れた」状態を禁止する。

## 作業A / 作業B / 報告

(受領した委任文のとおり。報告は最終メッセージ。RESULT_PACKETは書かない。)
