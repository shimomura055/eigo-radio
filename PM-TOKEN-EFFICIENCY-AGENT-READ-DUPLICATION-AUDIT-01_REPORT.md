# PM-TOKEN-EFFICIENCY-AGENT-READ-DUPLICATION-AUDIT-01 (Phase 1: read-only実測監査)

## 要点(5行)
1. 実測できた転記(subagent JSONL 3件+Fable本体3セッション+Opus実転記2件、計615呼び出し、読込文字数835,677字≈概算38.0万token)では、**巨大SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)の全文Read(offset/limit省略)は0件**。全てGrepまたは行範囲指定Readで、T1のOPEN_ITEMS構造分割・「Opus入力限定」ルールが少なくともこのサンプルでは機能している形跡がある。
2. 一方、**同一管理ID内での同一ファイル再読込(重複)は読込文字数の37.8%(316,166字)**、うち**Agent間(Fable↔Sonnet↔Opus)の重複は7.0%(58,460字)**。再読込はSSOTよりも**REPORT/governanceファイル(PM_GOVERNANCE.md・PM_BRIEF.md・ACTIVE_TASK.md・個別*_REPORT.md)**に集中している(実例は4節)。
3. **Fable→Sonnet/Opus委任文(Agent tool)自体の文字量が744,841字**あり、これは実測した全Read/Grep/Bash読込合計(835,677字)に匹敵する規模。委任文1件平均3,124字(Sonnet)・2,860字(Opus)。**「何を読むか」より前に「委任文そのものが既に大きい」**ことが、少なくとも同等以上の削減余地として実測された。
4. Opus L2レビューの入力構成は実測できた2件で「REPORT本文(43%)+OPEN_ITEMS等SSOTのGrep結果(15%)+trial_output成果物(18%)+コード(13%)」であり、過去実測(3V Phase1、T3報告、コード全文379,435字+REPORT72,789字=45.2万字)とは異なるパターン(コード全文ダンプ型ではなく複数REPORT横断参照型)。Opus入力の重さは案件によって性質が異なる。
5. 代表タスク名(News Trial-14/15、Discovery Towels Trial-11 Audio/Standard Player、Voices 3V Phase1B等)の多くは、**Subagent自身の転記ファイルが保持期限切れ(rotation)で失われており**、Fable側の委任文サイズのみ実測可能だった(2節に制約明記)。

## 1. データ源と制約(実測できたもの/できなかったもの)

### 実測に使った転記(実ファイル、機械集計)
| 種別 | セッション/Agent | ファイル | サイズ | 備考 |
|---|---|---|---|---|
| Sonnet subagent転記 | 現セッション294958fe | `a070ee8cef0720d0d.output` | 670,870字 | PM-RECOVERY-AFTER-SHUTDOWN-2026-09-11-01ほか多数の管理IDを連続処理(同一subagentスレッドを使い回し) |
| Sonnet subagent転記 | 現セッション294958fe | `aea028056531cac60.output` | 567,368字 | PM-TOKEN-EFFICIENCY-T3ほか |
| Sonnet subagent転記 | 前セッションa146ec25 | `a142aac94ff8f6d1e.output` | 1,404,914字 | PM-FABLE-SONNET-REVIEW-LOOP-03、PM-CLOSEOUT-CONSOLIDATION-65〜69ほか多数 |
| Opus subagent転記(実転記) | 旧セッションeba13a8b | `a15dd268df8bc04e5.output` | 389,483字 | 管理ID `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`(opus-consultant) |
| Opus subagent転記(実転記) | 旧セッションeba13a8b | `a2cf98b0e56f13ba1.output` | 557,262字 | 管理ID `FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`(opus-consultant) |
| Fable本体 | 294958fe / a146ec25 / eba13a8b の3セッション`.jsonl` | `~/.claude/projects/.../<session>.jsonl` | 各2.4M〜5.9MB | isSidechain=falseの行のみ抽出(Fable自身のRead/Grep/Bash/Agent委任) |

パーサ: `er011_pm_agent_read_audit_01.py`(repo root、read-only、Production非関与)。出力: `er011_output/pm_agent_read_audit_01/{per_call.jsonl, per_agent_task_summary.json, summary.md}`。

### 制約・取れなかったもの(正直な限界)
- **`<TEMP>/claude/.../tasks/*.output`の大半(観測125件中48件が0バイト、他はJSONLではなく"cat -n"形式の生テキストblob)は転記そのものではない**。実際にJSONL会話ログとして解析できたのは17文字agentIdの`a*.output`5件のみ(Sonnet3件+Opus2件)。ユーザー例示タスク(News Trial-14/15、ASR Trial、Standard Player、Voices 3V Phase1B等)の**Sonnet/Opus側の生転記は保持期限切れで存在せず**、Fable側の委任文(Agent tool input)からのみ規模を実測した(3-3節)。
- 委任文からの管理ID自動抽出(正規表現)は198件の管理IDを検出したが、Fableが「管理ID:」を明示しなかった/文中で崩れた一部の呼び出しは`UNKNOWN_MGMT_ID`(253,210字、全体の30.3%)に集約されており、個別タスクへの帰属ができていない。
- Bashコマンド経由の読込(`cat`/`sed -n`/`grep`等)はコマンド文字列への正規表現マッチでファイル分類しており、完全なshell構文解析ではない(複数ファイルにまたがるコマンドは先頭一致ファイルに全文字数を帰属)。
- Haiku-workerの実転記は本監査の対象データ内に1件のみ(委任文676字、結果転記なし)。2026-09-10新設のため実績が薄く、本Phase 1では評価不能。
- Opus入力のうち「他Agentが既読の内容の割合」(指標I)は、**同一管理ID内でのFable→Opus直接引き継ぎ**は測定できたが(4節)、**Sonnetが別の関連管理IDで先に読んでいた同一コードをOpusが再読する**パターン(T3報告記載の3V Phase1実例)は本Phase 1のサンプルには含まれておらず、T3報告の実測値をそのまま「過去再掲」として使用した(1節の要点5)。

## 2. 現状のToken消費構造(実測)

全615呼び出し(読込374件+委任241件)、Model別内訳:

| Agent | 呼び出し(自ら読んだ) | 読込文字数 | 概算token(÷2.2) | 委任として送った文字数 | 概算token |
|---|---|---|---|---|---|
| Fable | 144 | 251,943 | 114,520 | 744,841(236件委任) | 338,564 |
| Sonnet | 179 | 362,424 | 164,738 | 0 | 0 |
| Opus | 49 | 218,025 | 99,102 | 0 | 0 |
| 合計 | 372 | 835,677(除く上記の重複調整前) | 379,853 | 744,841 | 338,564 |

**委任文自体(744,841字)がRead/Grep/Bash読込合計(835,677字)とほぼ同規模**。委任文はSonnet/Opus側では「毎回のinput token」として課金されるため、"何を読むか"を最適化する以前に"委任文自体の分量"が既に大きなコスト要因である。

## 3. Agent別読込量

### 3-1 カテゴリ別(全Read/Grep/Bash合算、委任文除く)
| カテゴリ | 文字数 | 割合 |
|---|---|---|
| REPORT(`*_REPORT.md`) | 284,558 | 34.0% |
| Trial出力(`er0*_output/`) | 113,745 | 13.6% |
| SSOT巨大(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS) | 106,877 | 12.8% |
| Production code(`er0*.py`) | 105,096 | 12.6% |
| governance(`docs/pm/*`) | 87,335 | 10.5% |
| その他(未分類Bash等) | 約99,000 | 11.8% |
| History(`*_HISTORY.md`) | 299 | 0.04% |

### 3-2 ツール別
Read 541,188字 / Bash 190,979字 / Grep 90,210字 / Glob 13,300字。**SSOT巨大3ファイルの読込106,877字は全件Grepまたは行範囲指定(offset/limit明示)であり、全文Read(offset/limit省略)は実測0件**。Historyファイルもほぼ読まれていない(299字)。少なくとも本サンプルでは「巨大SSOT全文再読」「History念のため全文読込」は再現しなかった(過去のT2/T3報告で懸念された挙動が、その後のルール運用で抑制されている可能性がある実測結果)。

### 3-3 代表タスク別(委任文サイズ実測、Subagent転記が失われているものはFable側のみ)
| 管理ID | Fable自身の読込 | 委任文サイズ | Subagent転記 |
|---|---|---|---|
| FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME | 0字 | 1,775字 | 転記なし(rotation) |
| FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-STANDARD-PLAYER-01 | 0字 | 1,897字 | 転記なし |
| JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 | 0字 | 2,449字 | 転記なし |
| FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14 | 787字(governance Grep) | 3,474字 | 転記なし |
| FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15 | 4,306字 | 6,948字 | 転記なし |
| EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-02-BUDGET-GUARD-AND-COMMENT3-01 | 0字 | 1,992字 | 転記なし |
| PM-CLOSEOUT-CONSOLIDATION-72(SSOT編集) | 8,901字+9,240字(2セッション) | 4,168字 | 転記なし |
| FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01(Opus L2実転記あり) | 0字 | 2,764字 | **135,397字**(Read119,838/Grep15,451) |
| FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01(Opus L2実転記あり) | 1,319字 | 5,838字 | **82,628字**(Read72,933/Grep7,301) |
| PM-RECOVERY-AFTER-SHUTDOWN-2026-09-11-01(Sonnet実転記あり) | 14,680字 | 5,081字 | **112,314字**(うちBash95,661字) |
| PM-TOKEN-EFFICIENCY-T3-CLAUDE-DEV-TOKEN-REASSESSMENT-01(Sonnet実転記あり) | 0字 | 1,688字 | **55,729字** |

## 4. Agent間重複(実測)

- 同一管理ID内の同一ファイル再読込(全Agent合算): **316,166字/835,677字 = 37.8%**
- うちAgent種別をまたぐ重複(Fable↔Sonnet↔Opus): **58,460字 = 全体の7.0%**
- 具体例(上位、実測):
  - `docs/pm/PM_BRIEF.md`: 4回読込、重複12,711字、**全て異なるAgent種別**(fable×2セッション+subagent×1+fable現セッション×1) — Agent間重複率100%
  - `docs/pm/ACTIVE_TASK.md`: 5回読込、重複8,637字、Agent間重複8,637字(100%) — Fableが新セッション開始のたびに読み、subagentも独自に読む
  - `docs/pm/PM_GOVERNANCE.md`: 6回読込、重複12,724字、Agent間重複7,467字(59%)
  - `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-01-OPUS-L2-REVIEW-01_REPORT.md`(管理ID PM-RECOVERY-AFTER-SHUTDOWN-2026-09-11-01): Fableが読んだ後、同一管理ID内でSonnet subagentも同じREPORTを読み直し、重複7,395字(**Fable→Sonnet引き継ぎ時にREPORT要約を渡さず、Sonnetが自分でも全文を読み直す**パターン、実測)
  - `FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`内で`OPEN_ITEMS.md`をOpusが6回個別Grep、重複34,846字(**同一Agent内での多段Grep**、Agent間重複ではないがOpus単体の非効率)

## 5. 最大の無駄(上位5、根拠付き)

1. **委任文(Agent tool input)自体の規模(744,841字)** — 読込量そのものと同等規模。個別の委任文は最大で数千字級(平均3,124字/Sonnet、2,860字/Opus)だが236件という頻度が支配的。根拠: `per_call.jsonl`内`category=="task_delegation_prompt"`集計。
2. **PM_GOVERNANCE.md/PM_BRIEF.md/ACTIVE_TASK.mdのAgent間重複読込(合計28,815字、Agent間重複率59〜100%)** — Fableとsubagentが同じgovernanceファイルをそれぞれ独自に読んでいる。根拠: 4節の実例。
3. **Opus単体の多段Grep(OPEN_ITEMS.mdに34,846字)** — 1件のOpusレビュー内で同一ファイルへの類似検索が繰り返され、累積コストになっている。根拠: `top_reread_files`実測。
4. **REPORT間の階層的引き継ぎ未整理(実測、`PM-CLOSEOUT-CONSOLIDATION-69`で`PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`を同一タスク内でFableが4回読込、重複15,631字)** — 同一SSOT編集タスクの作業中に同じREPORTを何度も参照し直している(T3報告2-5節で指摘された「後続タスクがどの段階を読むべきか判断できない」問題の別実例)。
5. **Opus L2レビューの入力構成の案件依存性(過去実測45.2万字 vs 本実測13.5万字/8.3万字)** — Opus入力サイズは案件ごとに3〜5倍のばらつきがあり、`opus-consultant.md`に入力量の目安・上限指示がないため予測不能なコスト変動になっている(3節・T3報告2-4節と合わせて確認)。

## 6. Failure mode 1〜8 該当実例(実測ベース)

| # | Failure mode | 本Phase 1での該当有無 | 実例 |
|---|---|---|---|
| 1 | Fableの巨大SSOT全文再読 | **該当なし(実測)** | 3節参照。SSOT巨大3ファイルは全件Grep/行範囲指定 |
| 2 | Sonnetの実装前後の同一SSOT/REPORT全文再読 | **一部該当** | PM-CLOSEOUT-CONSOLIDATION-69でREPORT4回再読(重複15,631字、ただしいずれもFable自身、Sonnet実装前後の比較はデータ不足) |
| 3 | Fable→Sonnet→Opusの三重読込 | **該当(部分)** | PM-RECOVERY-AFTER-SHUTDOWN-2026-09-11-01でFable→Sonnetの二重読込(REPORT 7,395字)を実測。三重読込(+Opus)の直接実例は本サンプルになし(T3報告のみ) |
| 4 | Opus L2への旧運用残存(コード全文+REPORT全文+SSOT全文) | **該当(過去実測の再掲)** | T3報告: 3V Phase1 Opus L2で45.2万字(コード8ファイル37.9万字+REPORT7.3万字)。本Phase1実測2件はコード比率13〜18%とやや低いが、REPORT+SSOTは依然大きい |
| 5 | Sonnet REPORT整理済みなのにOpusが元ファイル全文再読 | **判定不能(データ不足)** | 本サンプルのOpus 2件はいずれも「設計レビュー」であり、直前にSonnet REPORTが整理されていた形跡はGrep範囲では確認できず |
| 6 | Historyファイルの念のため全文読込 | **該当なし(実測)** | History読込は299字のみ、全件部分読込 |
| 7 | compact後復旧での巨大SSOT再読 | **判定不能** | 本Phase1のデータ源にcompact直後の明示的マーカーがなく特定不可 |
| 8 | 同一管理IDでAgentごとに同じRepo調査のやり直し | **該当** | PM-CLOSEOUT-CONSOLIDATION-72でFableが2セッションにまたがり同種のgit status/grep調査を繰り返し(重複8,374字) |

## 7. 改善案(Sonnet提案A〜H、品質影響とリスク付き。採用判断はユーザー)

注: 「改善案A〜H」の原案(ユーザー提示)そのものは本委任文に含まれていなかったため、5〜6節の実測に基づきSonnetが8方向を再構成した。ユーザー原案と別に存在する場合は突合が必要。

| # | 方向 | 品質を落とさず削減できるか | 期待削減量 | リスク | 分類 |
|---|---|---|---|---|---|
| A | 委任文テンプレートの定型部分(厳守事項・出力形式等)を`docs/pm/`側の固定文書として1回だけ渡し、以降は参照のみにする | 可能性あり(定型部分は情報量が変わらない) | 委任文744,841字のうち定型部分比率次第(未計測、次点調査項目) | 定型部分の版管理がずれるとSonnet/Opusが古いルールを参照するリスク | 新ルール(要承認、委任文テンプレート変更) |
| B | Fable→Sonnet引き継ぎ時、直前にFableが読んだgovernance/REPORTの該当箇所を委任文に転記し、Sonnetの再読を省略 | 可能(既読内容の転記であり情報欠落なし) | PM_BRIEF/ACTIVE_TASK/PM_GOVERNANCEの重複28,815字相当(本実測分のみ) | 転記漏れがあるとSonnetが文脈不足のまま作業する | 既存ルール運用強化(実施可、委任文作成時の注意) |
| C | Opus委任文に「対象コードは変更差分(git diff相当)のみ」を必須化 | リスクあり(T3報告2-2と同一懸念: 変更箇所以外の文脈欠落) | 3V Phase1実例(45.2万字)ベースで数万字規模まで圧縮の可能性(推定) | Opusの網羅的レビュー機能低下(Fact Safety類似リスク) | 新ルール(要承認、opus-consultant.md変更) |
| D | Opus委任文に入力ファイル数/文字数の目安(例: 20万字超は要約を先に用意)を明記 | 可能(目安であり強制圧縮ではない) | 予測可能性向上、実際の削減量はケース次第 | 目安を超えた正当なケースで委任者が萎縮し必要な文脈を削る可能性 | 新ルール(要承認、agent定義への追記) |
| E | 同一管理ID内でOpus/Sonnetが同一ファイルに複数回Grepする場合、1回目の結果をSonnet/Opus自身が使い回す(委任文側ではなくAgent運用の注意) | 可能(情報量は変わらない、実装側の注意喚起のみ) | Opus単体重複34,846字相当(本実測分のみ)、頻度次第で他タスクにも波及 | 過度な使い回しで最新化漏れ(SSOT更新後の陳腐化)リスク | 既存ルール運用強化(実施可) |
| F | REPORT間の階層的引き継ぎ(元REPORT→DECISION_LOG該当エントリ→OPEN_ITEMS該当行)について、後続タスクが「どの段階まで読めば十分か」を委任文で明示する運用ルール化 | 可能(T3報告2-5と同一方向) | 定量化困難(T3報告と同じ、実例では最終段のみで足りるケースが多い) | 詳細確認省略による事実誤認・Reconciliation漏れ | 新ルール(要承認、PM_GOVERNANCE 11節への追記、T3報告2-5と統合検討) |
| G | Haiku-workerの適用範囲拡大(定型read-only集計をSonnetからHaikuへ) | 可能(定義上、判断を含まない作業限定のため品質影響は理論上小さい) | 本サンプルでは実績1件のみで削減量未測定(要Phase 2実測) | 「判断を含まない」境界の見極めミスでHaikuに不適切な判断業務が漏れ出るリスク | 既存ルール運用強化(2026-09-10新設ルールの適用拡大、実施可) |
| H | 委任文からの管理ID抽出・Agent間重複追跡を自動化し、Fableが委任前に「同一ファイルを直近で読んでいないか」を機械チェックする仕組みを追加 | 可能(監査であり生成物の品質に直接影響しない) | 本Phase1のようなAgent間重複(7.0%)の可視化・削減の基盤になる | 新規ツール(`er011_pm_agent_read_audit_01.py`相当)の保守負荷、誤検知時の運用停止判断が必要 | 新ルール(要承認、PM運用ツールの常設化) |

## 8. Phase 2 Trial設計案(実施はFable/ユーザー判断)

候補: 次回のDiscovery系Opus L2解釈タスク、またはNews Stage4系Opus L2タスクで、Before(現行委任文構成)/After(B案: 既読内容転記+D案: 入力目安明記を適用)を比較する。

比較項目:
- Fable/Sonnet/Opus読込文字数(本Phase1と同じ手法で`er011_pm_agent_read_audit_01.py`を再実行)
- Agent間重複文字数・重複率
- 総読込文字数(delegation含む)
- Opusレビュー品質(必要論点を落としていないか、Sonnet REPORT記載の論点との突合チェックリスト)
- 見落とし件数(Before/Afterで人間または別Agentが論点カバレッジを比較)
- 作業時間(タスク開始〜closeoutまでの実時間、Git commit timestampで代替測定可能)
- compact回数(該当あれば)

比較のBaselineとして、本Phase1で実測した`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`(135,397字)または`FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`(82,628字)を「Before」実測値として使用可能(新規Beforeサンプルを別途取得する必要がない)。

## 9. STOP条件該当有無

該当なし。本タスクは委任1回目・read-only・SSOT/Production/Prompt変更なし。ループ上限(初回+修正3回)に対しては初回のみ消化。

## 10. Closeout

Phase 1(実測監査)完了。Phase 2(Trial実施によるBefore/After比較)は未実施であり、実施要否・実施タイミングはFable/ユーザー判断に委ねる。

## 付録: 出力物
- `er011_pm_agent_read_audit_01.py`(パーサ本体、repo root)
- `er011_output/pm_agent_read_audit_01/per_call.jsonl`(615レコード、生データ)
- `er011_output/pm_agent_read_audit_01/per_agent_task_summary.json`(198管理ID別集計+再読込上位40件)
- `er011_output/pm_agent_read_audit_01/summary.md`(集計サマリ、人間可読)
