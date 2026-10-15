# DAY3 Phase A 反映一覧(委任_H、2026-10-15)

管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01。到達Status: DAY3_PHASE_A_COMPLETE(文書反映のみ。盲検リプレイによる実運用有効性検証は未実施)。commit: (1/2) 286b71e9a、(2/2)=SSOT記録commit。

## 1. 反映一覧(決定との対応)
| 決定 | 反映先(ファイル:行) | 内容 |
|---|---|---|
| ② | docs/pm/PM_GOVERNANCE.md:2378-2388 (11-4) | 固定回数制限(自律3回・4回目以降毎回ユーザーGate・5回目以降継続)を撤廃。7観点・「委任回数が増えたことだけを理由にUSER_DECISION_REQUIREDへ移行しない」・既存Gate維持・「無制限のTrialや予算超過を許可するものではない」を逐語。11-6を正本。L3診断後Human Gate・構造的問題のSTOP条件は維持(U2-Q2 Deferred)を明記 |
| ② | PM_GOVERNANCE.md:2416(11-6 維持する境界)、:2424(11-6 他規定との関係) | 「11-4(自律3回…)現行どおり」「11-4のサイクルとして数える」を撤去し、11-4の固定回数撤廃・11-6正本・L3 Human Gate維持へ整合。サイクルはQDC記録に回数記録のみ |
| ② | docs/pm/PM_BRIEF.md:222 | 問題解決運用節に11-4回数撤廃の1項目を追記 |
| ③A | PM_GOVERNANCE.md:2445 (11-7) | 3状態の正式運用・疑いの段階で緩めない・調査中に有効化しない・確定時は直ちに廃止を追記(既存の3状態定義・潜在迂回路の扱いは弱めず維持) |
| ③B | PM_GOVERNANCE.md:3010 (15-9) | Production実経路の実費基準・Batch換算は参考・仮想経路を実費扱いしない・70円は目標でSTOP条件でない。既存「判定値」(U5-Q1)と矛盾なし。7-9はTTS算定記述なし=変更なし |
| ① | day3/BLIND_REPLAY_RUNBOOK_01.md:20-24 (§2) | 原則Fable自律起動・Opus独立採点・ユーザー操作は原則要求しない・事前確認7項目・代替方法調査 |
| 履歴 | PM_GOVERNANCE.md:3383 | 変更履歴1行 |
| SSOT | DECISION_LOG.md:27(索引)、:21116〜(本体)/OPEN_ITEMS.md OPEN-363,365,366/REGISTER #63,#65,#66,#71+追記集計/REPORT_LEDGER末尾 | ユーザー原文逐語+反映先+hash |

## 2. 旧回数基準の残存Grep
コマンド: `rg -n "3回|4回|回目|合計最大|初回\+|回数上限|最大3回|最大2回" CLAUDE.md .claude/agents docs/pm/templates docs/pm/PM_BRIEF.md` と `rg "自律3回|4回目以降|自律実施の上限" ...`。
- 11-4の旧回数基準を述べる箇所は、PM_BRIEF.md:222(撤廃済みの旨)、PM_GOVERNANCE.md:2383,2387(撤廃・改定履歴の説明)、:2424(撤廃済みの旨)、:3383(履歴)のみ。いずれも撤廃の記述で、有効な規則としての残存は0。CLAUDE.md・.claude/agents/*・docs/pm/templates/*に11-4旧基準の残存なし。
- 残した「回」(撤廃対象外): 11-3条件B「同じ問題へ2回修正しても再発→3回目パッチ前にOpus独立レビュー」(sandwich-pm.md:85, CLAUDE.md:98, PM_BRIEF.md:61。独立レビューGateでありユーザー判断回数ではない)/Opus利用枠(難問診断1回/管理ID・任意レビュー1日2回: sandwich-pm.md:68ほか, PM_BRIEF.md:67,222付近)/sandwich-pm.md:68「1受入あたり最大2回を目安とし回数到達だけでSTOPしない」/sonnet-worker.md:80「原因不明rc≠0が2回」・:83「有料run再起動は許可回数のみ」(26節の安全回数)/PM_BRIEF.md:267-269(過去事例の記述)。
- CLAUDE.md Charter原則4「安全上の回数上限と境界STOPは従来どおり(11-6)」: 11-6の維持する境界にOpus利用枠・26-2・L3後Human Gateが残るため、11-4改定後も意味が通る。変更不要。

## 3. Dangling Reference結果
`rg -n "11-4" PM_GOVERNANCE.md CLAUDE.md .claude docs/pm/PM_BRIEF.md docs/pm/templates`: PM_GOVERNANCE.md:2378(見出し),2397(11-5「別カウント」=記録のみ運用と整合),2416,2424(11-6),3383(履歴),PM_BRIEF.md:222。CLAUDE.md・.claude・templatesに11-4参照なし。11-4/11-6間の矛盾(「11-4現行維持」「11-4サイクルとして数える」)は撤去済み。11-4が参照する「Sonnet委任上限(初回+3)」の注記は11-4改定で削除(参照先は廃止済みだった)。dangling: 0。履歴文書(MODEL_ROUTING_TRIAL_LOG等)の旧記述は歴史的記録として改訂しない(OPEN-366付記どおり)。

## 4. 新セッション読込確認(A-3)
.claude/agents/sandwich-pm.md はgit tracked(git ls-files)、frontmatter先頭`---`〜`---`、`tools: Agent(sonnet-worker, opus-consultant, haiku-worker), Read, Grep, Glob`、`model: fable`を目視確認(本委任で未改変)。CLAUDE.mdもtracked。claude -pによる実読込は委任_Iの担当(未確認)。
