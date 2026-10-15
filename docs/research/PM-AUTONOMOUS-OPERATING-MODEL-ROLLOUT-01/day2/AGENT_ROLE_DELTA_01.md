# AGENT_ROLE_DELTA_01: Agent役割差分(F1〜F5の実行可能性・Sonnet・Opus・矛盾整理)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day2 Phase A 委任_B / 2026-10-15
性質: read-only調査+設計文書。規則・Agent定義・SSOT・Production無変更、JPY0。Status上限: ROLE_GATE_DRAFT(Fable受入・Opus条件Aレビュー待ち)。**以下の文案はすべて「提案」であり、未適用**。
表記: [確認]=本調査で一次ファイルを確認、[推定]=推論、[未確認]=確認できず。行番号は2026-10-15時点。

## §0 前提(確認済み事実)
1. Fable(`.claude/agents/sandwich-pm.md` L4): `tools: Agent(sonnet-worker, opus-consultant), Read, Grep, Glob`。Bash/Edit/Write無し。[確認]
2. **本文L12-21は「haiku-workerを呼んでよい」と書くが、frontmatter L4のAgent許可リストに`haiku-worker`が無い**。`Agent(a, b)`が許可リストとして働くなら、Fableはhaiku-workerを起動できない。[確認: 文面の不一致 / 推定: 実行時に拒否される。実機未検証=§6相当の未確認]
3. 各Agentの手段: Sonnet=Read/Grep/Glob/Edit/Write/Bash(唯一テスト・git・実行が可能)。Opus=Read/Grep/Glob(テスト・git実行不可)。Haiku=Read/Grep/Glob(Fable自身の道具と同じ。**追加の検証能力は無く、トークン節約だけが価値**)。[確認]
4. `RESULT_PACKET.md`/`ACTIVE_TASK.md`/`RESULT_PACKET_*.md`は`.gitignore`済み(L49,50,56)。[確認] つまり**Sonnetの報告原本も、将来「受入記録」を置く場所としても、gitに永続しない**。永続するのは`docs/pm/delegation_log/*`(約1,560ファイル、T-0で全文保存)、REPORT_LEDGER、OPUS_FINDINGS_LEDGER、UDR_REGISTER、SSOT(いずれもtracked確認済み)。
5. 受入関連の既存規則: PM_GOVERNANCE Gate 7(L243-246)、§1 L137-138(Fableの責務に「Gate 7による報告受入判定」)、§11 Gatekeeper原則(L1757-)、sandwich-pm.md手順4(L36-40)。**いずれも「何を確認するか」の列挙止まりで、(a)確認の手段 (b)確認項目の選び方 (c)結果の記録先 (d)受領と受入の区別 が規則に無い**。[確認]
6. KGORA監査(`er071_output/m2p0_n01_production_wiring_01/opus_review_root_cause_audit_01/AUDIT_REPORT_01.md` §7): Fableのhand-back後37秒・tool_use 0でユーザー報告、Opus受領から委任まで53秒・tool_use 0。台帳OF-226/227/228/232の4/11行がOpus原文と不一致。[確認(監査報告の記載)]

## §1 Fable(F1〜F5)
共通の設計方針: **Fableの道具(Read/Grep/Glob)で実行できる照合に限定し、動的な照合(テスト実行・git)は独立した新規sonnet-worker委任(検証専用)で行う。Fable自身が実行できない作業を「Fableの責務」と書くだけの文案は採らない。**

### F3 独立受入(最重点)
**現行規則の所在**: Gate 7 PM_GOVERNANCE L243-246、§1 L137-138、sandwich-pm.md L36-40(手順4)、§11 Gatekeeper。
**不足(実行不能になっている点)**:
| # | 不足 | 根拠 |
|---|---|---|
| a | 証拠を読む許可が曖昧。L29「`er0XX_output/`配下のディレクトリを自分で読まない」とL36-40「照合する」が衝突し、安全側(読まない)に倒れる。 | sandwich-pm L29 |
| b | 受領と受入の区別が無い。Agent結果が返った時点で「完了」と読める。 | KGORA §7(hand-back後37秒) |
| c | 確認項目が「全部確認」型で、リスクに応じた選び方の基準が無い。結果として「確認しない」に倒れる。 | Gate 7 |
| d | 受入結果の記録先が無い(RESULT_PACKETは非永続、REPORT_LEDGERは報告状態用)。Fableは書き込み不可。 | §0-4 |
| e | 動的証拠(test・git・実行)をどう取るかが規則に無い。haiku-workerはこの用途に使えない(§0-2,3)。 | §0 |
| f | Sonnet自己申告の「PASS」と、独立再実行との区別が無い。 | AUDIT §7 |

**Fableに実際に使える照合手段(現行ツールのまま)**:
| 区分 | 手段 | 何が確かめられるか | 限界 |
|---|---|---|---|
| S1 既定値Grep | `rg "<FLAG> = os.environ"`等でProductionコードの既定値行を直接読む | 未承認機能が既定OFFか(VALIDATION_OFF_01 §0の1行と同一内容を独立に確認できる) | 実行時の値(環境変数・monkeypatch)は不明 |
| S2 テスト内容Grep | テスト名と`assert`行をGrepし「欠陥を期待値に固定していないか」を読む(例: `test_failed_alignment_keeps_kp_flags_failed_not_human_review`) | testが欠陥を保証していないか | PASS数の真偽は不明 |
| S3 SSOT・台帳突合 | OPUS_FINDINGS_LEDGER行と保存済みOpus原文(判定語・推奨・方向)をGrepで照合 | 台帳と原文の不一致(4/11の型) | 原文が保存されていなければ不可(§3で保存を運用化) |
| S4 証拠ファイルの存在・中身 | Glob/Grepで`evidence_*.json`の`status`・API呼出数、`regression/*.txt`のpassed/failed行を読む | 報告書の数値と生の証跡の一致 | 生成物自体の真正性(捏造が無い保証)は不明 |
| S5 承認済み仕様との文言照合 | CURRENT_SPEC/DECISION_LOGの原文をGrepし、実装・Prompt文言と並べて読む | 規則文面の矛盾(KGORA欠陥1型) | 実行時挙動は不明 |
| D1 独立再実行 | **新規のsonnet-worker委任(検証専用、実装・編集禁止)**:「次のコマンドを実行し、passed/failed件数・exit codeを原文のまま返せ」「失敗経路を実データで1例再現し最終成果物を貼れ」 | 動的事実(test結果・失敗経路の最終成果物・git状態) | 実行者もSonnet(ただし実装者本人とは別contextなので自己申告よりは独立) |
| (除外) haiku-worker | S1〜S5と同じ道具。frontmatter許可リストにも無い | なし | 使わない。Fableが自分で読む方が確実 |

**リスク階層による確認対象の選定(毎回全再読・全再実行はしない)**:
| 階層 | 該当する報告 | 必須の確認 |
|---|---|---|
| T-low | 既存仕様内の通常バグ修正、docs、ログ追加、typo(11-3「不要の例」と同範囲) | S4を1件(報告の主要数値1つを生証跡で確認)。D1不要 |
| T-mid | 新規Prompt/検査ルール/テスト追加、既存Gate周辺の変更、Trial結果のStatus分類 | S1・S2・S5から2件以上、うち1件は失敗経路に関するもの |
| T-high | Opus条件A〜D該当、retry/fallback/Human Review/STOP/承認機構/複数Family/再発不具合、Production有効化の提案 | S1・S2・S3・S5を全件、**D1を1件以上**(失敗経路の最終成果物の実例を含む) |

**受領と受入判定の区別(提案)**: 状態を2段にする。Agent結果が返った時点は`RECEIVED`。以下の「受入記録」を作成して初めて`ACCEPTED`/`ACCEPTED_WITH_CONDITIONS`/`REJECTED`(差戻し)になる。**`RECEIVED`のままの報告を「完了」としてユーザーへ出さない**(出す場合は「未受入」と明記)。

**受入記録(5行、様式固定)**:
```
受入記録: <管理ID・委任番号>
判定: ACCEPTED / ACCEPTED_WITH_CONDITIONS / REJECTED(差戻し理由)　階層: T-low/mid/high
目的(ユーザー基本要件1文)と最終成果物の適合: <失敗終了時の例を含む。根拠=ファイル:行>
照合した証拠(最低件数は階層表): <S1〜S5/D1の種別 ファイル:行 → 結果>
照合しなかったもの・残存リスク: <1〜2行>　Status分類: VALIDATED/PRODUCTION_WIRED/UDR等(格上げ無し)
```

**記録先(新規の台帳は作らない)**: Fableは書けないため、**次の委任文の冒頭ブロック「前委任の受入記録」としてFableが書く**。委任文はT-0で`docs/pm/delegation_log/<管理ID>.md`に全文保存される(=gitに永続、既存機構)。最終の委任(次が無い場合)は、SSOT記録委任(DECISION_LOG追記を行う委任)の文案に同ブロックを含める。ユーザー報告には同ブロックの要約を載せる。REPORT_LEDGERの「備考」には`受入=ACCEPTED(階層T-high)`の1語を足す(既存列、列追加無し)。

**変更案(sandwich-pm.md、提案文)**:
- L29を「コード全体・大量ログ・`er0XX_output/`配下の**ディレクトリ走査**は行わない。受入判定のための**特定ファイル・特定行の読取とGrep**は、受入判定の手段として許可する(読取対象は委任文またはRESULT_PACKETに記載されたパス・行に限る)。」へ置換。
- 手順4の後に追加:「4-2. 受入判定: Agent結果の受領(RECEIVED)と受入(ACCEPTED等)を区別する。受入は、リスク階層に応じた照合(S1〜S5、T-highではD1の検証専用sonnet-worker委任)を**少なくとも1回のtool使用で**実施し、『受入記録』を次の委任文冒頭に書いて確定する。受領直後にtool使用なしでユーザー報告しない。」
- L4を`Agent(sonnet-worker, opus-consultant, haiku-worker)`へ(本文L12と整合させる場合)、または本文L17-21のhaiku記述を「現行の許可リストに無いため使わない」へ。どちらにするかはFable/ユーザー判断(haiku追加は検証能力を増やさないので、削除側を推奨)。

**実行手段・権限の有無の結論**: S1〜S5はFableの現行ツールで**実行できる**(L29の文言修正が前提)。D1はsonnet-worker経由で**実行できる**(新しいAgent種別・ツールは不要)。受入記録の「書き込み」はFableに**できない**ので、委任文冒頭への記載(T-0で永続)で代替する。動的検証の真正性は「実行者がSonnetである」限界が残る。完全な独立はG3(Production有効化)でのユーザー承認が最終的に担う。
**運用か規則修正か**: sandwich-pm.md本文の追記(L29修正・4-2追加)=**Agent定義の変更(ユーザー承認要)**。階層表・受入記録様式の正本は`docs/pm/PM_GOVERNANCE.md` Gate 7への追記(§5案#5)。
**その他の保証(任意・後回し)**: マーカーStop hook(DAY1_C §3、実機検証未了)に「受入判定行の有無」検査を足す案はあるが、`--agent`で効くか未確認、1回のtool使用で形式的に満たせるため効果も限定的なので**採用しない**。

### F1 目的・優先順位・QDC統括
- 現行所在: PM_GOVERNANCE §1 L136-139(「タスク定義[目的・受入条件・STOP条件]」)、sandwich-pm.md手順3、委任文テンプレート(DELEGATION_STANDARD_TEMPLATE「性質」節)、CLAUDE.md「開発方針」。
- 不足: 委任文テンプレートに「**この工程の目的(ユーザー基本要件の1文)**」欄が無い。Opusに渡す目的記述が任意になり、KGORAではOpusが「修正前より悪化しないか」を基準にした(AUDIT §1②)。QDCの比較軸「学習者の聴く/読む結果」が選択肢比較に必須化されていない。
- 変更案: DELEGATION_STANDARD_TEMPLATEの「管理ID」節直後に`目的(ユーザー基本要件の1文)`行を1つ追加し、Fable自己チェックに1項目「目的1文と、失敗終了時の最終成果物が一致するか」。Charter(Day3予定)のQ>D>C≫開発費は参照のみ。
- 実行手段: Fableが委任文を書くだけ(Write不要。委任文はFableの出力としてSonnetがT-0で保存)。権限あり。
- 運用/規則: テンプレート1行追加=規則修正(軽微)。ユーザー承認: Day2運営規則変更の一部として要確認(AUDIT §10-2)。

### F2 自律的問題解決と再計画主導
- 現行所在: PM_GOVERNANCE §14(7段階)、§11-1(既存仕様内は完成まで)、§11-4(Opus/Fable改善ループ3回)、sandwich-pm.md L84-90「上限到達=UDR」。
- 不足/矛盾: 「上限到達 or 仕様変更が必要=USER_DECISION_REQUIRED」(L84-90、CLAUDE.md L59-64)が既定の逃げ道になり、再計画(問題の捉え直し)を行う義務が書かれていない。§11-4は3回で停止してユーザーGateという別の上限も持つ。
- 変更案(DAY1_REPORT §8の#3と整合): L84-90を「同一failure modeが2回再発 or 上限到達: (1)問題の捉え方を見直した再計画を1回行う(§14の一般化段階)、(2)条件Bに該当ならOpus独立レビュー、(3)それでも未解決、または仕様・品質ライン・予算/Scopeの変更が必要な場合のみ`USER_DECISION_REQUIRED`」。ユーザー決定が必要(DAY1_REPORT §9 #2、LOOP-03の趣旨と整合)。
- 実行手段: Fableの判断+新規sonnet-worker委任(再計画案の調査)。権限あり。
- 運用/規則: sandwich-pm.md・CLAUDE.md L59-64の文言修正=**規則修正(ユーザー承認要)**。

### F4 承認Gate・Production完成管理
- 現行所在: Gate 2(L174-190)、Gate 3(L182-)、Gate 4(Dangling)、Gate 5、PM_BRIEF「正式Status語彙」、sandwich-pm.md手順5(L41-44)、ACTIVE_TASK固定ヘッダ「APPROVED未配線」欄。
- 不足: (1)Gate 3に「失敗終了パスの最終成果物」「不要になった旧ルールの撤去/残置判断」の項目が無い(AUDIT §8 B3)。(2)「approved specとProduction挙動の一致」を**どう確かめるか**が無い(Fableは差分を見られない)。(3)flagの規約が文書化されていない(PM_GOVERNANCEの`flag`記述は無関係な1件のみ[確認]。既定OFFは各コードの慣行)。
- 変更案: Gate 3にチェック項目を2つ追加(§5 #5)。照合手段=F3のS1(既定値Grep)+S5(承認原文と実装文言)+D1(失敗経路実例)。flag規約は`GATE_MECHANISM_MAP_01.md` §2のとおり、新規制度でなく既存のGate 3/4+`DefaultOffIsolation`型testを使う(「Production到達経路に入る未承認機能は、明示ON無しでAPI 0・出力不変をtestで証明する」を1行)。
- 実行手段: Fableが読む(S1,S5)+Sonnetが再現(D1)。権限あり。
- 運用/規則: Gate 3項目追加=規則修正(軽微、ユーザー承認要)。`Production承認の代行禁止`は現行どおり。

### F5 ユーザー判断・Open Item・過去決定管理
- 現行所在: UDR_REGISTER(`docs/pm/USER_DECISION_REGISTER_01.md`)、PM_GOVERNANCE §10-2/§12/§21、PM_BRIEF、REPORT_LEDGER。
- 不足: 台帳が古い(DAY1: 行59件/集計55件/見出し35件のズレ)ため「判断済み」の特定が難しい。無言承認禁止の明文が常駐規則に無い(DAY1 T11)。判断依頼前の「3確認(過去決定/技術解決を試みたか/なぜ今)」が常駐していない。
- 変更案: Charter(Day3)に3確認と無言承認禁止を置く。UDR台帳のズレ是正は別委任(台帳小修正)。ユーザー判断を求める前のFable自己チェックに「§21のA/B/C+技術的に解決を試みた証跡(Sonnet報告)の有無」。
- 実行手段: Grep(UDR_REGISTER・DECISION_LOG)=Fableの現行ツールで可能。台帳の書換えはSonnet委任。
- 運用/規則: 3確認=Charter(新規文書)、台帳是正=運用。

## §2 Sonnet
### 2-1 技術的不確実性→ユーザー転送の既定動作の所在
| # | 場所 | 文言(要旨) | 問題 |
|---|---|---|---|
| 1 | `sonnet-worker.md` L12-15 | 「拡大が必要だと判断した場合は、実装せず**Fableまたはユーザーへ報告し判断を仰ぐ**」 | 範囲拡大(正当)と技術的不確実性(原因不明・方式が選べない)を区別せず同じ「判断を仰ぐ」に落とす。報告先に「ユーザー」が並記される。 |
| 2 | `sonnet-worker.md` L22-24 | 「新しい仕様候補・改善案を発見…報告する(`USER_DECISION_REQUIRED`**文化を踏襲**)」 | 仕様候補(正当なUDR)と、既存仕様内で解くべき技術問題の区別が無い。 |
| 3 | `sandwich-pm.md` L84-90 | 上限到達/仕様変更が必要→`USER_DECISION_REQUIRED`でSTOP | 再計画の義務が無く、上限到達=ユーザー転送が既定。 |
| 4 | `sandwich-pm.md` L77、L81 | Opusレビューで「新しいUDRが発生」したらSTOP/L3診断後は「人間ユーザーの判断を仰ぐ」 | L81は§11-3解釈2で維持。L77の「新しいUDR」の定義が曖昧で、技術未解決を含みうる。 |
| 5 | `CLAUDE.md` L59-64(上限到達=UDR)、L81 | 同上 | agent定義と二重化。 |
| 6 | `PM_GOVERNANCE.md` §11「守ること」3「`USER_DECISION_REQUIRED`をSonnetだけで解決しない」 | Sonnetが自力で解決を試みてよい範囲が不明 | 「解決を試みるな」と読まれうる。 |
実際の振る舞い: §11-1が「既存仕様・Gate・コスト範囲内なら完成まで進める」と定めるが、agent定義の既定が逆向きで、KGORAでは基本品質要件の領域(Q2: 失敗時の扱い)をUDRとして提示した(`REVIEW_AUDIT_01.md` 観点5)。

### 2-2 是正文案(提案のみ)
`sonnet-worker.md`の範囲節を次の趣旨に置換する:
> 範囲拡大が必要な場合は、実装せずFable(PM)へ報告する。**ユーザー判断が必要になるのは、新仕様の正式採用・品質ラインの変更・重大なQDCトレードオフ・予算/Scopeの変更に限る。**技術的な不確実性(原因が不明、方式が決められない、テストが通らない)は、Fableへ「原因・証拠・解決案(複数なら比較と推奨)」を添えて報告する。ユーザーへ直接転送しない。調査は委任範囲内で、仮説→反証→再現証跡のループを2周まで自力で行ってから報告する。

新節「**既存仕様整合の義務(報告に必須)**」:
> RESULT_PACKETに次の3行を必ず書く(書けない場合は未確認と明記):(1)既存仕様整合: A既存仕様あり/B過去Trialあり/C新規、と照合したファイル:行 (2)Production到達経路に入る未承認機能の既定値と、その確認方法(Grep行) (3)失敗終了時の最終成果物の実例(実データまたは実行ログ)と、目的要件への適合。不整合出力を期待値として固定するtestを書かない(不整合を検出して止める/通知して止めるtestは可)。

### 2-3 既存仕様整合確認の義務化方法
| 手段 | 実行時強制か | 内容 |
|---|---|---|
| 委任文テンプレートの「報告」節に上記3行を必須項目として書く | 文書(Fableが書く) | 既存の委任文標準(D-2)に載せるだけ |
| `check_delegation_prompt.py`が委任文の「報告」節に`既存仕様整合`の語があるか警告(非ブロッキング) | 実行時(警告のみ) | 既存スクリプトの1行拡張。形式検査の限界とFAIL常態(DAY1_C: 約49%)があり効果は小さい。**採用は任意・後回し** |
| Fable受入(F3)で上記3行をGrepして存在と中身を確認 | Fable実行(Grep) | 未記載=差戻し |
→ 実質の強制はF3受入。新機構は作らない。
- 運用/規則: `sonnet-worker.md`変更=Agent定義変更(ユーザー承認要)。RESULT_PACKET標準項目の追加=テンプレート修正(軽微)。

## §3 Opus
### 3-1 依頼範囲の標準
現行: 12観点ブロック(`OPUS_INDEPENDENT_REVIEW_BLOCK.md`)をcontext packetへ貼る(PM_GOVERNANCE 11-3、`OPUS_CONTEXT_PACKET_TEMPLATE.md`(g))。KGORAでは**未使用**で、ユーザー9観点の充足は明示3/部分5/含まれない1(AUDIT §3)。
標準依頼(提案): packet(a)の先頭に次の4項目を固定し、(g)でブロックを**そのまま貼る**(貼付確認はFable自己チェック):
1. 工程の目的(ユーザー基本要件の1文)
2. 失敗終了時の最終成果物はこの目的を満たすか?(満たさないなら、許容/通知のみで終える設計は不可と明記)
3. 12観点ブロック貼付。観点11の注記:「安全側=最終成果物が目的要件を満たす側。品質欠陥を残す側は安全側でない」(`REVIEW_AUDIT_01.md` §4案)
4. 12観点が直接問わない4問(a欄に番号付きで固定): ①承認済み規則・Prompt文言と新しい検査ルール/文言が矛盾しないか(誤NG時にどの経路へ入るか) ②その変更で不要になる旧ルール・旧機械NG・旧testはどれか(撤去/残置の理由) ③他Family・他経路への影響 ④誤PASS/誤NGの副作用
「不要例(11-3)」の変更では貼らない(儀式的起用の禁止は維持)。回数は増やさない。
運用/規則: 12観点ブロックは2026-10-02ユーザー決定の正本なので**改変しない**。追加の4項目・4問はpacketテンプレート(a)欄への追記にとどめる。観点11の注記のみブロックへの追記になるため**ユーザー承認を要する**(§5 #9)。

### 3-2 所見原文の保存・台帳転記
現行: 11-5(台帳運用)。Opus(Read/Grep/Glob)は書けず、Fableも書けない。原文は会話記録(非commit)にしか無く、台帳は人手の要約で作られ4/11行がずれた(AUDIT §5)。
提案(運用改善、新機構なし):
1. Opus hand-back直後、Fableは次のSonnet委任文に「**Opus所見原文(逐語)**」節として原文を貼り、保存先`<管理ID>/opus_review_NN_VERBATIM.md`(既存のer0XX_output構造)を指定する。委任文はT-0で`delegation_log`にも全文保存されるため二重に永続する。
2. 台帳(OPUS_FINDINGS_LEDGER)行は、VERBATIMの「OF-n見出し・判定語・推奨」を原文のまま引用して作る。台帳の「Fable採否」セルに、所見ごとに採否+**理由1行**+「再レビュー要否: 要/不要+理由」を書く(列追加なし。一括『Opus総評を採用』を禁止)。
3. Fable受入(F3)でS3(台帳とVERBATIMのGrep突合、判定語・推奨・過大/過小の向き)を実施。
4. C1(台帳初稿の自動抽出script)は**見送り**。理由: 手順1〜3で同じ不一致を検出でき、まず運用で足りるか確認する。受入でズレが再発した場合のみ導入を再判断。
運用/規則: 運用改善(11-5が既に「台帳を作る」を規定。原文保存・理由1行・突合はその徹底)。

### 3-3 再レビュー条件
現行: 11-3「重複レビューの回避」の5条件((1)設計変更(2)実装方針の重要変更(3)retry/fallback等への新しい配線(4)新しい重大リスク(5)前提崩れ)。KGORAでは修正後に再レビュー**要否の判断記録が無かった**(AUDIT §6)。
提案: 再レビュー要否の**判定を毎回必須(1行、台帳のFable採否セル)**、実施は次の場合のみ・**差分と失敗経路の2〜3論点に限った軽量確認**(フル再レビューではない): (i) retry/fallbackの既定を変えた (ii) Pass/Failを変える新ルール(機械NG等)を入れた。それ以外は再レビューしない。同内容の重複レビュー禁止は現行維持。
運用/規則: 運用改善(11-3の(2)(3)の適用例を1行例示するのみ。回数上限は変えない)。

## §4 Agent間のSTOP・承認・役割の矛盾と整理案
| # | 矛盾 | 該当(ファイル:行) | 整理案 | 運用/規則 |
|---|---|---|---|---|
| C1 | haiku-workerが本文では起動可、frontmatterの許可リストに無い | sandwich-pm L4 vs L12-21 | haikuの記述を削除(検証能力が増えないため)。残す場合はL4へ追加。実機で拒否を確認[未確認] | 規則 |
| C2 | Fableは「証拠を自分で読まない」(L29)一方、Gate 7は「Fableが受入判定する」 | sandwich-pm L29 vs PM_GOVERNANCE L243-246 | §1 F3の置換文(特定ファイル・行の読取を許可) | 規則 |
| C3 | 「テストはすべてSonnetへ」(L28)で、独立検証が自己申告になる | sandwich-pm L28 | D1(検証専用sonnet-worker委任)を受入手順として明文化 | 規則(+運用) |
| C4 | STOP_NOTICEの適用範囲が3種: sonnet-worker.md L48-49=全`*STOP_NOTICE*`、PM_GOVERNANCE §26-2(d)=該当管理ID、`tools/stop_scope_check_01.py`=構造化scope+fail-closed。**agent定義・PM_GOVERNANCE・CLAUDE.md・PM_BRIEFに`stop_scope_check`への言及は0件**(Grep確認)。`stop_scope_check_01`を参照するrunnerは3ファイル(`er077_m1_oov_multi_pronunciation_01_evidence_runner.py`・`er071_gloss_alignment_correction_01_trial.py`・`er071_gloss_alignment_01_replay.py`) | sonnet-worker L48-49 / PM_GOV §26-2(d) / tools | 正本を`stop_scope_check_01.py`の判定ルールに一本化し、agent定義と§26-2(d)は「`tools/stop_scope_check_01.py`で判定する。未使用のrunnerは全`*STOP_NOTICE*`を停止扱い(fail-closed)」の1文に揃える。新ライブラリ不要 | 規則(文言統一)+運用 |
| C5 | 「Fableまたはユーザーへ判断を仰ぐ」(sonnet-worker L14)vs §11-1(完成まで進める)vs Charter「Humanには重要Decisionだけ」 | §2-1 | §2-2の置換文 | 規則 |
| C6 | 上限到達=UDR(sandwich-pm L84-90、CLAUDE.md L59-64)vs §11-4(自律3回→ユーザーGate)vs Charter(自律再計画) | 同左 | §1 F2の置換文。§11-4の「別カウント」はそのまま | 規則 |
| C7 | Opus条件Aは「実装前」(11-3)なのに、委任の指示にOpus呼出が無く実装・配線・push後になった(KGORA: push 20:47 → Opus依頼 20:58) | PM_GOVERNANCE 11-3 vs 委任_04 | 委任文テンプレの「Opus Gate判定」行を、判定結果だけでなく『実装着手前に実施済み/実施予定』を書く形にする。配線済みの場合は配線OFF(flag)で条件Aを実施(AUDIT A2) | 運用(+テンプレ1行) |
| C8 | 依頼文が「git diff相当」を求めてもOpus(Read/Grep/Glob)は実行不可(AUDIT §2) | opus-consultant tools | 依頼時、差分はpacketに貼る(ファイル+行範囲。(c)欄の既存形式) | 運用 |
| C9 | `RESULT_PACKET`が非永続(.gitignore)で、受入・証跡の原本にならない | .gitignore L49-56 | 証跡は`er0XX_output/`または`delegation_log`に置く(既存ルールどおり)。RESULT_PACKETは要約のまま | 運用(現行維持) |
| C10 | 「Production採用=人間のみ」(手順5)と、安全措置としてのflag既定値変更の線引きが曖昧 | sandwich-pm L41-44 | KGORAの区別を明文化: 「安全措置としての既定値変更(OFF化)」は採用ではないが、『未承認機能のON』は常に採用扱い | 規則(Charter) |

## §5 変更案一覧
| # | 対象ファイル | 文案(要旨) | 運用徹底/規則修正 | ユーザー承認 |
|---|---|---|---|---|
| 1 | `.claude/agents/sandwich-pm.md` L29・手順4-2 | §1 F3の置換文/追加文(特定ファイル・行の読取許可、RECEIVED/ACCEPTED区別、リスク階層、受入記録) | 規則修正(Agent定義) | 要 |
| 2 | `.claude/agents/sandwich-pm.md` L4 / L12-21 | haikuの整合(削除推奨) | 規則修正 | 要(軽微) |
| 3 | `.claude/agents/sandwich-pm.md` L84-90、`CLAUDE.md` L59-64 | 上限到達=UDRを再計画+条件B→残る場合のみUDRへ | 規則修正 | **要(DAY1_REPORT §9 #2)** |
| 4 | `.claude/agents/sonnet-worker.md` L12-15,22-24 | §2-2の置換文+既存仕様整合3行の義務 | 規則修正(Agent定義) | 要 |
| 5 | `docs/pm/PM_GOVERNANCE.md` Gate 3 / Gate 7 | Gate 3に項目2つ(失敗終了パスの最終成果物の実例1件/不要になった旧ルール・旧機械NG・旧testの撤去または残置理由)、Gate 7に階層・受入記録様式 | 規則修正(軽微) | 要 |
| 6 | `docs/pm/PM_GOVERNANCE.md` §26-2(d)、`sonnet-worker.md` L48-49 | STOP適用範囲の1文化(C4) | 規則修正(文言統一) | 軽微(DAY1 §8 #5に含まれる) |
| 7 | `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md` | 「目的(ユーザー基本要件1文)」行、Opus Gate判定を『実装前実施』形式、報告節に既存仕様整合3行、Fable自己チェックに目的と失敗時最終成果物 | 規則修正(テンプレ、軽微) | 要(軽微) |
| 8 | `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md` (a)欄 | §3-1の4項目+4問(12観点ブロックは無改変) | 規則修正(テンプレ) | 軽微(packet形式追記) |
| 9 | `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` 観点11 | 『安全側=最終成果物が目的要件を満たす側』の注記1行 | 規則修正 | **要**(2026-10-02ユーザー決定の正本) |
| 10 | Opus所見原文保存・台帳転記・再レビュー判定(§3-2,3-3) | VERBATIM保存、採否+理由1行+再レビュー要否、F3で突合 | **運用徹底**(11-5・11-3の範囲内) | 不要 |
| 11 | 受入記録を次委任文冒頭に置く(§1 F3) | 5行様式 | 運用(様式正本は#5) | #5に含む |
| 12 | `docs/pm/tools/check_delegation_prompt.py` | 『既存仕様整合』語の警告(任意) | 機構変更(小、任意) | 不要(警告のみ)。**採用は後回し推奨** |

新規Hook/Validator/台帳/scriptの提案: **0件**(#12は既存スクリプトの1行拡張で任意。C1自動抽出scriptとマーカーStop hookへの受入判定検査は見送り)。
