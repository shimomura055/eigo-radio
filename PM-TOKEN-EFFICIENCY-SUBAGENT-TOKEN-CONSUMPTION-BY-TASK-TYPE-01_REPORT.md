# PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01(read-only実測)

## 要点(7行)

1. Fable本体転記3セッション(`294958fe...`(現行)・`a146ec25...`(2026-09-10)・`eba13a8b...`(古いOpus L2例))から`<task-notification>`内`<usage>`を機械抽出し、同一`task-id`の重複通知(累積値、初回のみ`<tool-use-id>`保持)を正しく1件へ集約した結果、**254件の重複のないsubagent実行**(sonnet-worker/opus-consultant、2026-09-07〜09-12)を得た。**合計36,590,141 token・平均144,056 token/件**。
2. **委任文(Fable→Sonnet/Opus)は254件合計743,907字(概算338,140 token)、平均2,929字(概算1,331 token)**であるのに対し、同じ254件のsubagent内部消費合計は36,590,141 tokenで、**内部消費は委任文の約108倍**。委任文削減では週次消費の大半には手が届かない(既存のPM-TOKEN-EFFICIENCY-DELEGATION-PROMPT-BOILERPLATE-MEASUREMENT-01の結論と整合)。
3. **種別平均が最も高いのは(a)Consolidationではなく(d)Production配線/実装+テスト(平均207,506 token、29件)**、次いで(b)記事生成Trial/Production run(平均167,463 token、52件)。(a)Consolidationは件数が87件と最多で総量は最大(11,360,253 token)だが、1件あたり平均は130,578 tokenで「20万token級」は例外(最大257,787、中央値126,597)。**「Consolidation系が高額」という当初仮説は平均では支持されず、実際は件数の多さ(母数87件)が総量を押し上げている**。
4. 実転記(`tasks/<id>.output`)が現存するのは254件中**18件のみ(7.1%)**、うち上位10件(token順)では**1件のみ**現存(他9件は0バイトで消失)。現存18件を`er011_pm_agent_read_audit_01.py`(無変更)で実測すると、**読込文字数の合計3,024,137字のうち27.8%(839,754字)が同一task内での同一ファイル再読込(重複)**。最大は51.7%(`FAMILY-A-DAILY-NEWS-REFERENCE`系reconcile、86,894字重複)。
5. Production配線タスクの内部消費の主因は、SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`)ではなく**`er0xx_*.py`本体コード(`production_code_er0x_py`分類)の読込**(実測3件で総読込の37〜63%)。SSOT系(`ssot_huge`)は実測3件中1件でのみ観測され(31,522字/194,381字=16%)、他2件は0字。git操作(Bash)の出力読込は各3,356〜21,414字程度で全体の1〜7%にとどまり主因ではない。
6. tool_usesとsubagent_tokensの相関は+0.68(254件)で正の関係はあるが、外れ値あり(635 tool_uses・246,799 tokenの`FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09`は他の150〜220 tool_uses帯より突出して回数が多いが token/tool_use比は逆に低い=小さい呼び出しの反復)。
7. 判定語(VALIDATED等)は付けない。削減候補は6節に期待削減量・品質リスク・実装コストとともに記載(Fable/ユーザー判断用)。

## 1. 方法・データ源

- 対象転記: Fable本体jsonl 3件(`~/.claude/projects/C--Users-tensh-eigo-radio/`配下)
  - `294958fe-da6e-491c-8a02-4f864d8195c8.jsonl`(現行セッション、4.1MB)
  - `a146ec25-1821-49c1-a6f2-3b7ad423406a.jsonl`(2026-09-10、2.9MB)
  - `eba13a8b-6eec-4381-909a-3a2d71be7123.jsonl`(古いセッション、5.9MB)
  - 上記3件は`er011_pm_agent_read_audit_01.py`のPhase 1監査(`TARGET_SESSIONS`)が対象にした3セッションと同一(選定基準を踏襲)。
- 抽出対象: `type=="queue-operation"`かつ`content`文字列に`<task-notification>`と`<usage>`を含む行。正規表現で`<task-id>`/`<tool-use-id>`/`<summary>`/`<status>`/`<subagent_tokens>`/`<tool_uses>`/`<duration_ms>`を抽出(全文Readではなく、対象3ファイルをPythonで1回ずつ走査する軽量スクリプト、repo外scratchpadに保存、Git管理外)。
- 管理ID対応付け: 同じFable本体jsonl内の`assistant`メッセージの`tool_use`(`name in ("Agent","Task")`)を`id`(=`tool-use-id`)で突合し、`input.prompt`/`input.description`から管理IDを正規表現抽出(`er011_pm_agent_read_audit_01.py`の`extract_mgmt_id`と同一パターンを踏襲)。254件中245件で管理ID抽出成功、9件は委任文が「管理ID:」形式以前の記法だったため`description`文言から手動で種別のみ補完(該当箇所に注記)。
- **重複通知の扱い(重要な補正)**: `<task-notification>`のnoteに明記の通り「同一task-idが複数回通知されることがある」ことを実測で確認(例: `a070ee8cef0720d0d`は111,518→114,283 tokenへ増加する2回の通知)。`subagent_tokens`/`tool_uses`は**累積値**であり、`<tool-use-id>`は初回通知にのみ付与される。誤って全通知を単純合計すると二重計上になるため、**同一task-idごとに最終(最大)通知のみを採用し、tool-use-idは同グループ内の初回通知から補完**する処理を実装(生290件→重複排除後254件)。この補正をしなかった場合、合計tokenが本来より過大になる。
- 実測に使った一時スクリプトはいずれもrepo外scratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\...\scratchpad\`)に保存し、Git管理外・repo内には一切書き込んでいない。`er011_pm_agent_read_audit_01.py`は無変更(import利用のみ)。

## 2. 種別ごとの集計(254件、36,590,141 token)

分類ロジック(優先順位順、正規表現ベースの近似。委任文の管理ID/descriptionの文字列パターンで判定。手作業レビューではなく機械分類のため一部に粗さがある):
1. `subagent_type=="opus-consultant"` → (e)
2. 管理IDが`PM-CLOSEOUT-CONSOLIDATION`で始まる → (a)(名称に`OPUS-L2`等を含んでいてもsubagent_type=sonnet-workerであれば(a)、実際に1件該当: `CONSOLIDATION-93...OPUS-L2-RECONCILE-03`)
3. 管理IDに`OPUS-L2/L3`等を含む → (e)
4. 管理IDに`TOKEN-EFFICIENCY`/`AUDIT`/`COST-ACCOUNTING`/`MONITOR`/`OBSERVATION`/`ANALYSIS`等を含む → (f)
5. 管理IDに`WIRING`/`PRODUCTION-FIX`/`MINIMAL-FIX`を含む → (d)
6. 管理IDに`RECONCILE`を含む → (c)
7. 管理IDに`TRIAL`/`PRODUCTION-RUN`/`ARTICLE`/`AUDIO`を含む → (b)
8. 上記いずれにも該当しない → (g)

| 種別 | 件数 | token合計 | 平均 | 中央値 | 最大(管理ID) | tool_uses平均 | token/tool_use |
|---|---|---|---|---|---|---|---|
| (a) Consolidation/SSOT反映+commit | 87 | 11,360,253 | 130,578 | 126,597 | 257,787 (`CONSOLIDATION-93-...-OPUS-L2-RECONCILE-03`) | 57.1 | 2,286 |
| (b) 記事生成Trial/Production run | 52 | 8,708,098 | 167,463 | 166,111 | 340,125 (`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`) | 82.8 | 2,024 |
| (c) Reconcile/調査(read-only) | 11 | 1,483,773 | 134,888 | 133,763 | 202,948 (`FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01`) | 47.1 | 2,864 |
| (d) Production配線/実装+テスト | 29 | 6,017,682 | **207,506** | 182,972 | 420,691 (`EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01`) | 99.0 | 2,096 |
| (e) Opus L2/L3 | 10 | 1,072,059 | 107,206 | 105,664 | 158,756 (`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-01-OPUS-L2-REVIEW-01`) | 27.6 | 3,884 |
| (f) 計測・監査 | 25 | 2,919,337 | 116,773 | 113,667 | 237,852 (`PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01`) | 47.6 | 2,453 |
| (g) その他(DESIGN/SPEC/PLAN/完了系混在) | 40 | 5,028,939 | 125,723 | 114,562 | 244,502 (`EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04`) | 48.8 | 2,576 |
| **合計** | **254** | **36,590,141** | 144,056 | — | — | — | — |

補足: (e)は全件`subagent_type=="opus-consultant"`(Opus本体呼び出し)。token/tool_use比が最も高い(3,884)のは、Opusが少ない呼び出し回数で大きめのcontext packetを一括で受け取る運用(2026-09時点で採用済みのcontext packet方式)を反映していると考えられる。

## 3. 上位10件(token順)と実転記の有無

| 順位 | token | tool_uses | 管理ID(または`description`) | 種別 | task_id | 転記(`tasks/<id>.output`) |
|---|---|---|---|---|---|---|
| 1 | 420,691 | 146 | `EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01` | (d) | `aa6ad220628f1a4fe` | 消失(0バイト) |
| 2 | 359,484 | 209 | (管理ID無し)`OPEN-127/128 Production Wiring(順次)+SSOT+commit` | (d) | `a4de74d86e3caa7a4` | 消失(0バイト) |
| 3 | 354,908 | 211 | (管理ID無し)`G1 Production修正(Gate 3)+SSOT訂正+観測Exit条件記録` | (d) | `a9a53775a5d9b8ab4` | 消失(0バイト) |
| 4 | 340,718 | 218 | `OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01` | (d) | `a8229e0c416bd57ec` | 消失(0バイト) |
| 5 | 340,125 | 148 | `FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05` | (b) | `ad363fc465acce01b` | 消失(0バイト) |
| 6 | 327,819 | 154 | `OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01` | (d) | `a54b5946e2e397294` | 消失(0バイト) |
| 7 | 321,355 | 136 | `EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02` | (b) | `a18349005260d1427` | **現存(1,733,116字)** |
| 8 | 318,922 | 80 | `EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01` | (b) | `a59908a58dfe1794e` | 消失(0バイト) |
| 9 | 317,782 | 153 | (管理ID無し)`Fact Checker A' + OPEN-129 Production Wiring(順次)` | (d) | `a74a16774ac08dce6` | 消失(0バイト) |
| 10 | 305,767 | 162 | `FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01` | (b) | `a7fdc7c8942a95aed` | 消失(0バイト) |

上位10件中9件が転記消失(tasksフォルダは一時ディレクトリのため、経過時間・後続タスクの容量圧迫等でOSレベルにより削除された可能性が高い。原因の特定はできない=正直な限界)。**254件全体でも実転記が現存するのは18件(7.1%)のみ**。上位トークン帯ほど転記が失われている(古いタスクほど削除されやすい)ため、最も知りたい「なぜ高額か」を直接検証できるサンプルは限定的。

## 4. 現存18件の実測(`er011_pm_agent_read_audit_01.py`、無変更・import利用)

### 4-1. 重複読込(改善案E該当)

18件全件について、同一task内で同一ファイルを複数回Read/Grep/Bash catした分の文字数を集計。

| task_id | 総読込文字数 | 重複分(2回目以降) | 比率 |
|---|---|---|---|
| `a5e7dc3628fe49e2e`(`LEDGER-DEVIATION-CHECKER-SEARCH-COST-RECONCILIATION-01`) | 168,157 | 86,894 | 51.7% |
| `a18349005260d1427`(`EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02`) | 336,693 | 157,401 | 46.7% |
| `a04bbc489cba68bd7`(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02`) | 169,526 | 72,354 | 42.7% |
| (以下省略、詳細は本測定の一時ログ) | | | |
| **18件合計** | **3,024,137** | **839,754** | **27.8%** |

上位例(`a18349005260d1427`)の重複ファイル内訳(抜粋): `er012_editorial_b_voices_trial_07.py`をReadで6回+Bash catで4回=**同一ファイルへ10回アクセス**、`er003_v1_n3_01_tts_generate.py`をReadで5回、`er003_v1_n3_01_assemble.py`をReadで5回。

### 4-2. Production配線タスク(d)の内部消費内訳(実測3件)

| task_id | 総読込 | 最大カテゴリ | git系Bash出力 | SSOT系(`ssot_huge`) |
|---|---|---|---|---|
| `a45175c31baa124f0`(`PRODUCTION-PATH-PHASE1-WIRING-01`) | 314,246字 | `production_code_er0x_py` 198,705字(63%) | 21,414字(6.8%) | 0字 |
| `a5559604281e6973e`(同、別回) | 185,792字 | `production_code_er0x_py` 116,246字(63%) | 3,356字(1.8%) | 0字 |
| `a142aac94ff8f6d1e`(Household prevent差替、管理ID無し) | 194,381字 | `production_code_er0x_py` 61,303字(32%) | 7,554字(3.9%) | 31,522字(16%、`DECISION_LOG.md`/`OPEN_ITEMS.md`) |

**結論**: 「Consolidation/Production配線が高額になるのはSSOT(DECISION_LOG/OPEN_ITEMS)を毎回読み込むから」という当初仮説は、実測3件中2件でSSOT読込0字であり支持されない。主因は**既存の`er0xx_*.py`本体コード(数百〜数千行規模)を配線・実装のために読み込む量そのもの**であり、これは配線作業の性質上避けにくい(コードを見ずに配線はできない)。SSOTが主因なのは1件(`a142aac94ff8f6d1e`、`OPEN_ITEMS.md`へBashで16回アクセス)のみ。

## 5. 分析(i)〜(iv)

**(i) 委任文 vs subagent内部消費**: 254件で委任文合計743,907字(概算338,140 token、平均2,929字/1,331token)に対し、内部消費合計36,590,141 token。**比率は約108倍**。既存のPM-TOKEN-EFFICIENCY-DELEGATION-PROMPT-BOILERPLATE-MEASUREMENT-01の「委任文の定型比率は4.8%に過ぎない」という結論と合わせると、**委任文(定型・非定型問わず全体)の削減では週次消費の1%未満しか動かせない**。レバーはsubagent内部側にある。

**(ii) Consolidation系がなぜ高額か**: 上記3節・4-2節の通り、平均では(a)Consolidationは(d)(b)より低く「20万token級」は例外(最大値のみ)。件数87件という母数の多さが総量(11.36M token、全体の31%)を押し上げている主因。個別の高額例(`CONSOLIDATION-93`=257,787、`CONSOLIDATION-90`=201,603)については実転記が消失しており内訳を直接検証できないが、Consolidationタスクの性質(複数SSOTファイルへの反映+commit+複数の並行成果物の突合)から、DECISION_LOG.md/OPEN_ITEMS.mdへの複数回Grep/Read、および複数の`*_REPORT.md`の読込が積み上がりやすいと推測される(推測であり実測ではない、正直に明記)。

**(iii) 同一task内の重複読込の実量**: 現存18件で実測27.8%(839,754字/3,024,137字)。最大51.7%。同一ファイルを一度読んだ内容を後続の作業で再度読み直すパターンが一貫して観測される(特にコード実装系タスクで顕著: 同じ`.py`ファイルをRead→編集→確認のため再Read、またはBash catでも重複確認)。

**(iv) tool_usesが多いタスクの共通パターン**: 254件全体でtool_usesとsubagent_tokensの相関は+0.68(正の相関はあるが完全ではない)。上位はいずれも(d)Production配線または(b)Trial/Production run(146〜218回)。外れ値として`FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09`が635回(token/tool_use比は最も低い部類)で、小さい呼び出し(個別ケースの検証・微修正の反復)を多数繰り返すパターンと推測される。

## 6. 削減候補(判定語なし、Fable/ユーザー判断用)

| # | 候補 | 期待削減量(概算) | 品質リスク | 実装コスト |
|---|---|---|---|---|
| E-1 | 同一task内の重複Read/Grep/Bash catの抑制(直前に読んだ内容をcontextに保持し再読を避ける運用ルール化) | 現存18件実測で27.8%相当。**全254件に外挿すると単純計算で約1,017万token相当**(外挿であり保証値ではない、現存サンプルが古いタスクに偏っている可能性に留意) | 低〜中(誤って古い内容を参照し続けるリスクはあるが、単一task内・単一ファイルの再読省略なので限定的) | 低(委任文への一文追加+Sonnet側の自己管理を促す運用ルール、コード変更不要) |
| D-1 | Production配線タスクでの対象コード読込範囲の絞り込み(全文Read→該当関数/該当行のみRead徹底) | (d)平均207,506token中、実測3件で`production_code_er0x_py`が32〜63%を占める。範囲限定を徹底できれば同カテゴリで数十%規模の削減余地(ただし配線には関数間の依存関係把握が必要なため限定的) | 中(必要な依存箇所を見落として実装ミスのリスク) | 低〜中(委任文で「該当関数のみRead」と明記するルール化) |
| A-1 | Consolidationの件数(87件)を減らす方向(複数の小さいConsolidationを少数の大きいConsolidationへ統合) | 総量11.36M tokenのうち、委任オーバーヘッド(起動・context読込の固定費)分を件数減で削減できる可能性。ただし1件あたりの平均は大きく変わらない可能性もあり効果は不確実 | 中〜高(統合commitは切り戻しにくく、粒度が粗くなりレビュー困難化・ロールバック単位の肥大化リスク) | 中(運用ルール変更のみだが、既存のPM-CLOSEOUT-CONSOLIDATION-N番号運用・Gate判断の粒度設計に影響) |
| F-1 | 一時転記(`tasks/<id>.output`)の保存期間延長・アーカイブ化 | 削減ではなく可観測性向上(現状254件中18件=7.1%しか残らないため、次回以降の同種監査で高額タスクの内訳検証ができない) | 低(read-only、Production非関与) | 低〜中(ディスク容量次第、保存先はrepo外を維持すべき) |
| G-1 | git出力の抑制(`--quiet`等)の徹底 | 実測3件でgit系Bash出力は1.8〜6.8%(3,356〜21,414字)。主因ではないため、効果は小さい | 低 | 低 |

## 7. 制約・限界(正直な記載)

- 分類は管理ID文字列の正規表現による機械分類であり、人手レビューではない。特に(g)その他40件は多様なタスクが混在しており、細分類すればさらに複数のサブカテゴリに分かれる可能性が高い。
- `subagent_tokens`はSDKが報告する値であり、課金tokenと完全一致するかは未検証(既存の`er011_pm_agent_read_audit_01.py`の「文字数/2.2」概算とは独立した別の計測系統)。両者はおおむね近い値になることを4節の実測(読込文字数÷2.2 ≈ subagent_tokens)で確認したが、厳密な突合検証ではない。
- 現存する実転記が18/254件(7.1%)と少なく、特に上位トークン帯(最も知りたい層)ほど消失率が高いため、(ii)の「Consolidationがなぜ高額か」の直接的な内訳検証はサンプル不足で確定的な結論に至っていない。
- E-1の期待削減量(約1,017万token)は現存18件からの単純外挿であり、外挿元サンプルが偏っている可能性(古いセッションのタスクが多い)を考慮すると過大・過小いずれの方向にも誤差がありうる。

## 付録: 生成物一覧

- 本REPORT: `PM-TOKEN-EFFICIENCY-SUBAGENT-TOKEN-CONSUMPTION-BY-TASK-TYPE-01_REPORT.md`(新規、未commit)
- 一時解析スクリプト・中間データ(repo外、Git管理外): `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\`配下(`extract_usage.py`、`classify_and_summarize.py`、`check_top10_output.py`、`subagent_usage_by_task_type_01.jsonl`、`classified.jsonl`、`dup_summary.txt`)。他Agent成果物(`er012_*`、`er011_open121_*`、`er011_output/`配下の既存artifact)には一切触れていない。
