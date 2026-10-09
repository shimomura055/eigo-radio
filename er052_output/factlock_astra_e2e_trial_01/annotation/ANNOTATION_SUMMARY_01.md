# ANNOTATION_SUMMARY_01(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_09)

日付 2026-10-09。注記A/Bの抽出->単独検査->統合->統合版検査。数値は annotation/check/, annotation/out/merged/, annotation/final/ の実測。
検査スクリプトは委任_09でバグ修正3件(P1台帳statusの読取り・P3段落区切り後の`- `・P4抽出時の末尾空行)を適用後の結果。修正前の結果は annotation/check_prefix/ に保存。詳細は `_09_result.md`。

## 1 テーマ別 検査結果(修正後)

| テーマ | 単独A | 単独B | 統合 | 事実数 | 中核/周辺 | cap_dropped | unmapped_claims(統合) | 分割一致率 | 中核Jaccard | 判定線(0.8/0.67) |
|---|---|---|---|---|---|---|---|---|---|---|
| byd_recall | PASS | PASS | PASS | 1 | 3/0 | 0 | - | 1.00 | 1.00 | 超え |
| central_bank_mortgage | PASS | PASS | PASS | 6 | 5/5 | 4 | - | 0.80 | 1.00 | 超え |
| hormuz | FAIL(d:sequence) | FAIL(d:sequence) | 未統合(単独PASSが2本揃わず) | - | - | - | - | - | - | - |
| inbound_tourism | FAIL(b:ledger_mapping,c:numbers) | FAIL(b:ledger_mapping,c:numbers) | 未統合(単独PASSが2本揃わず) | - | - | - | - | - | - | - |
| meta | PASS | PASS | PASS | 3 | 0/0 | 0 | - | 1.00 | n/a | 超え(中核0件記事のためJaccard算出不能) |
| openai_copyright | PASS | PASS | PASS | 1 | 3/0 | 0 | - | 1.00 | 1.00 | 超え |
| semiconductor_earnings | FAIL(b:ledger_mapping) | FAIL(b:ledger_mapping) | 未統合(単独PASSが2本揃わず) | - | - | - | - | - | - | - |
| small_bag | PASS | PASS | PASS | 3 | 1/0 | 0 | - | 1.00 | 1.00 | 超え |
| space_weapons | PASS | PASS | PASS | 5 | 1/0 | 0 | - | 1.00 | 1.00 | 超え |
| streaming_price | FAIL(b:ledger_mapping) | STOP | 未統合(単独PASSが2本揃わず) | - | - | - | - | - | - | - |

注: 単独FAILの理由。hormuz=B3 v1の Selected Facts 節が『Storyline:重複行+素材:段落』で【事実N】を付けられる箇条書き/段落が無く事実0件(仕様§2は素材行に付けない)。inbound_tourism=台帳ID F06(台帳status AMBIGUOUS)を注記者が参照->VERIFIED以外はFAIL(既存規則・非修正)に加え、概念統合の食い違い(`8月`と`2019年8月`が別概念)・分類漏れ(`01`,`02`,`03`,`06`)という注記者側の形式エラー。semiconductor_earnings=AMBIGUOUS台帳ID F1参照のみ(他は検査PASS)。streaming_price A=AMBIGUOUS台帳ID F07参照のみ、B=STOP(§4(ii))。

## 2 単独検査の詳細(事実数・unmapped_claims種類・cap_dropped)

| テーマ | 注記者 | 検査 | 事実数 | countable概念 | 中核(期待) | cap_dropped | unmapped_claims種類別 |
|---|---|---|---|---|---|---|---|
| byd_recall | A | PASS | 1 | 3 | 3 | 0 | - |
| byd_recall | B | PASS | 1 | 3 | 3 | 0 | - |
| central_bank_mortgage | A | PASS | 6 | 10 | 5 | 4 | - |
| central_bank_mortgage | B | PASS | 6 | 10 | 5 | 4 | - |
| hormuz | A | FAIL | 0 | 7 | 3 | 2 | {'new_number': 1} |
| hormuz | B | FAIL | 0 | 7 | 3 | 2 | {'new_number': 1} |
| inbound_tourism | A | FAIL | 4 | 14 | 6 | 6 | {'generalization': 1, 'qualifier': 1} |
| inbound_tourism | B | FAIL | 4 | 14 | 6 | 6 | {'qualifier': 1} |
| meta | A | PASS | 3 | 0 | 0 | 0 | - |
| meta | B | PASS | 3 | 0 | 0 | 0 | - |
| openai_copyright | A | PASS | 1 | 3 | 3 | 0 | - |
| openai_copyright | B | PASS | 1 | 3 | 3 | 0 | - |
| semiconductor_earnings | A | FAIL | 1 | 7 | 3 | 4 | {'generalization': 1, 'qualifier': 2} |
| semiconductor_earnings | B | FAIL | 1 | 7 | 3 | 4 | {'generalization': 1} |
| small_bag | A | PASS | 3 | 1 | 1 | 0 | - |
| small_bag | B | PASS | 3 | 1 | 1 | 0 | - |
| space_weapons | A | PASS | 5 | 1 | 1 | 0 | - |
| space_weapons | B | PASS | 5 | 1 | 1 | 0 | - |
| streaming_price | A | FAIL | 3 | 10 | 5 | 2 | - |
| streaming_price | B | STOP | - | - | - | - | - |

## 3 B3形式の観察(v1。全10テーマ)

| テーマ | Selected Facts形式 | 箇条書き行数 | 『・』行頭 | Storyline重複行 | 1事実あたり台帳ID数(統合 or A) |
|---|---|---|---|---|---|
| byd_recall | 段落 | 0 | 0 | 無 | [5] (統合) |
| central_bank_mortgage | 箇条書き | 5 | 0 | 無 | [1, 1, 1, 1, 1, 2] (統合) |
| hormuz | Storyline重複行+素材段落 | 0 | 0 | 有 | - (A) |
| inbound_tourism | 箇条書き | 5 | 5 | 無 | [1, 1, 1, 1] (A) |
| meta | 段落 | 0 | 0 | 無 | [1, 1, 1] (統合) |
| openai_copyright | 段落 | 0 | 0 | 有 | [6] (統合) |
| semiconductor_earnings | 段落 | 0 | 0 | 無 | [5] (A) |
| small_bag | 段落 | 0 | 0 | 有 | [1, 1, 3] (統合) |
| space_weapons | 箇条書き | 5 | 0 | 無 | [1, 1, 1, 1, 1] (統合) |
| streaming_price | 段落 | 0 | 0 | 無 | [4, 1, 1] (A) |

- 段落形式(箇条書き0行): byd_recall / openai_copyright / semiconductor_earnings / small_bag(+ streaming_price v1/v2)。これらは1段落に多数台帳IDが紐付き、事実数が少なく(1〜3)なる。
- 注記者は段落先頭に `- 【事実N】` を挿入した(仕様§1の定義済み挿入)。

## 4 B3 v2(hormuz・streaming_price。機械判定は annotation/b3_v2_judge.json)

| テーマ | 版 | 箇条書き行 | Storyline重複行 | 素材行 | 段落行 | 台帳外の数字 | 選択台帳ID数 |
|---|---|---|---|---|---|---|---|
| hormuz | v1 | 0 | 1 | 1 | 0 | ['25'] | 3 |
| hormuz | v2 | 4 | 0 | 0 | 0 | - | 4 |
| streaming_price | v1 | 0 | 0 | 0 | 1 | ['3'] | 6 |
| streaming_price | v2 | 0 | 0 | 0 | 1 | - | 6 |

## 5 transcript監査(annotation/audit/, annotation/AUDIT_SUMMARY.md)

| テーマ_注記者 | 既存strict | 既存base | 補助(許可=Read自分のプロンプト+Write自分のreply.md) | 使用ツール |
|---|---|---|---|---|
| byd_recall__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| byd_recall__B | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| central_bank_mortgage__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| central_bank_mortgage__B | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| hormuz__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| hormuz__B | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| inbound_tourism__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| inbound_tourism__B | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| meta__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| meta__B | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| openai_copyright__A | VIOLATION 4 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,Write,SubagentHandback |
| openai_copyright__B | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| semiconductor_earnings__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| semiconductor_earnings__B | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| small_bag__A | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| small_bag__B | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| space_weapons__A | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| space_weapons__B | VIOLATION 3 | rc=1 | DISALLOWED_TOOL_USE | Read,Bash,SubagentHandback |
| streaming_price__A | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
| streaming_price__B | VIOLATION 3 | rc=1 | PASS_ONLY_ALLOWED | Read,Write,SubagentHandback |
