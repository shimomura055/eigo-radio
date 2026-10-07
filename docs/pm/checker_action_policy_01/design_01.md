# OPEN-233-CHECKER-ACTION-POLICY-DESIGN-01 設計書 01(段階1、委任_01、2026-10-07、¥0・API無し)

位置づけ: 設計案であり決定ではない。Production変更なし、`APPROVED_FOR_PRODUCTION`なし。実装・コード編集・SSOT編集・gitはこの委任の範囲外(Fableが後で扱う)。
参照した入力: `docs/pm/opus_l2_review_stabilization_strategy_01.md`(Opus所見)、`er052_output/open233_stage0_01/reclass/RECLASS.md`(段階0-A)、`er052_output/open233_stage0_01/stability/STABILITY.md`(段階0-C)、`er052_output/open233_stage0_01/danger/DANGER_COVERAGE.md`(段階0-B、**存在を確認して反映済み**)、`er052_output/open233_control_checker_polysemy_trial_01/eval/RCA_jb9k_qvqc.md`、`docs/pm/design_open233_self_recovery_flow_01.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§83/§86)、`DECISION_LOG.md`、`OPEN_ITEMS.md`。

## 0. 目的・原則・held-outの取扱い

- **重大誤解原則(上位)**: 「英語学習者に記事の本質について重大な誤解を与えるものだけを止め、それ以外は元記事を守る」(`docs/pm/design_open233_self_recovery_flow_01.md` §0-1)。本設計はこの原則を弱めず、Checkerが重大なものを「範囲逸脱(軽微)」と読み違える穴(②)と、Rewriteが新しい誤りを作る穴(①)だけを塞ぐ。
- **安全≠成功**: 誤りを止める規則が通っても、面白さ(語り)が失われたら成功ではない。**削除文数・書換え文数・Checker前後の変更文比率を全測定で必ず報告する**(§5)。
- **面白さを縛らない**: Writerの単一パス自由生成は変えない(ユーザー決定A)。Writer生成promptへの禁止事項追記はしない(Opus: 効果未証明)。④の自己注釈も、記事本文の生成promptを変えない形を第一案にする(§3)。
- **型から重大度を機械的に決めない**(Opus注意): 文の型(否定・全称等)は「格下げしてよいか」の守りを厚くする条件にしか使わず、重大度はStage2が改めて判定する(§2)。
- **held-outの取扱い**: `split.json`は開いていない。設計で使った数値は、RECLASS(全144件の集計)とDANGER_COVERAGE(100記事全体・型別)の**集計値のみ**で、dev/held-outの分離はされていない(各書が全件集計)。DANGER_COVERAGE §4の見逃し一覧は項目IDだけでdev/held-outの区別がなく、一部はheld-out項目の可能性がある。**そのため、個別項目に合わせた規則調整は行わず、型(T1〜T6)レベルの結論だけ使った**。規則の閾値・語彙の調整は段階2でdev 100件のみで行い、held-outは確定後に1回だけ使う(§5)。
- 過学習注意: jb9k(否定・不在1件)、qvqc(タイトル1件)、HC-012(ロールバック方向13件)、統合軍(7件)に引っ張られない。各規則は「型」として定義し、これらは回帰確認にのみ使う。
- 記述の区別: 【確認】=コード・ログで確認した事実、【推測】=未検証。

## 1. ①構造要素Rewrite規則

### 1-1. 対象の定義と検出(決定論、API無し)
| 要素 | 定義(現行コード) | 検出 | 本設計での扱い |
|---|---|---|---|
| タイトル | `# `で始まる最初の行(`_en_title_line`、`split_units`のT)。`structural_element_reasons`は「先頭の非空行」(位置の重なり) | 既存 | 構造要素(既存) |
| 見出し | `#`行(H{n}) | 既存 | 構造要素(既存) |
| 一行要約 | `In one line`見出し直下(L{n}) | 既存`in_one_line` | 構造要素(既存) |
| Hook | 本文第1段落(`split_units`のrole=hook、S1.x) | **既存の`structural_element_reasons`には含まれない**(`preflight_degenerate`のみ) | **新規に構造要素へ追加**(C) |
| コメント文 | 現在は独立した位置として扱われていない(RECLASS注: 「締め」=最後2段落にコメントを含みうる) | 位置=最後の段落。④の注釈で「fact_idなし・新規固有名詞/数値なし」の文をコメント文とする | **新規**(C)。④導入までは**Hook段落までを先行対象**とし、コメントは④導入後 |
- 【確認】現行の構造要素判定(`er052_open233_self_recovery_flow_runner_01.py` L6037付近の`structural_element_reasons`)はtitle/heading/in_one_line/preflight_degenerateのみ。Hookと締めは対象外のため、Hookへは現状1語置換が許可されている。

### 1-2. 許可する処置/禁止する処置
| 処置 | タイトル・見出し・一行要約 | Hook文 | コメント文 |
|---|---|---|---|
| 元のまま(QUALITYとして記録) | 可(Stage2がQUALITY/ACCEPTABLE) | 同左 | 同左 |
| 削除 | **不可**(空=degenerate。既存仕様、`DECISION_LOG.md`委任_07「構造要素を空にせず」) | 可(段落が成立し`measure_section_role_violation`が合格するとき) | 可 |
| Recheck付き文脈内再生成 | **可(唯一の書換え手段)** | 可(削除が不成立のとき) | 可 |
| 語の置換(1語置換・ladderの`1_word_connective`・`e1_minimal_word_edit`を含む) | **禁止** | **禁止** | **禁止** |
- 「文脈内再生成」の定義: 要素を、**本文の検査済み内容(Stage2/Recheckを通過した文)だけ**を入力に作り直す。出力後に**必須の4照合**(決定論、API無し):
  1. 主体照合: 出力に現れる固有名詞・主体名が本文(検査済み)またはLedgerに存在する。さらに、変更前後で主語・主体表現が変わった場合(「I→Meta」型)は、本文中で同じ動作の主体として使われている語と一致するか確認し、一致しなければ却下。
  2. 極性照合: 否定語・不在語の有無が元要素、または参照した本文文と同じ。
  3. 数値照合: 出力の数値が本文の数値の部分集合。
  4. **形式保存**: タイトルは`# `行のまま、見出し・一行要約は元の記法のまま(下記W1)。
  その後、必ず**Recheck判定単位にその要素を含めて**再判定する(下記W2/W3)。
- 生成案が1〜4のいずれかで却下された場合: **既存のladder枯渇経路**(`blocking_structural_after_ladder` → 許可リストSTOP、`STAGE4_ALLOWLIST`、`docs/pm/design_open233_self_recovery_flow_01.md` §5-10)へ進める。本設計は新しいHuman Review出口を作らない。

### 1-3. Recheck単位の配線の不具合: 原因候補と修正点(提案のみ。変更はFableが決める)
RCA(`RCA_jb9k_qvqc.md`)は「タイトルがcycle2のstage2判定単位に無い」と記録した。コードとrep2の実ログ(`er052_output/open233_control_checker_polysemy_trial_01/runs/meta/nb/rep2/checker/runs/meta_run03_advanced.json`)を突き合わせた結果、**RCAの説明は一部不正確で、原因は3つに分解できる**:
- **W1(【確認】)Rewriteが`# `記法を落とした**: cycle1のhandoffの`ranges`は`# I Followed an AI Phone Agent and Found a Human`(`# `込み)、`revised`は`Meta Tested an AI Phone Agent and Found a Human`(`# `なし)。`en_title_after=None`、`en_text_after_rewrite`の先頭は`Meta Tested ...`(`# `無し)。結果、`split_units`はこの行をタイトル(T)として認識せず、第1段落の文(S1.1、role=hook)として扱った。`recheck_coverage.scope_ids`にはS1.1が含まれる(=判定単位に**入っていた**)が、タイトルとしてではなくHook文として判定され、title専用の扱い(section_type=title)を受けていない。→ 修正点: Rewrite後に`_en_title_line(after)`が`None`になる、または記法が変わる案は決定論で却下。コード候補箇所: runnerのladder成功判定(L6350前後、`each_target_changed`付近)と`quality_degradation_en`計測(L9358付近)の間に形式保存チェックを追加。
- **W2(【確認】)`STRUCTURAL_PAIRS_TO_RECHECK`はcoverage_unionのRecheckでは何も渡さない**: スイッチの参照箇所は`run_recheck`(L2183〜2186、legacy)と記録用の件数(L9546〜9549)のみ。承認構成(`RECHECK_MODE=coverage_union`)のRecheckは`run_recheck_coverage`(L1929)→`cov.run_recheck_scope`(`er052_open233_stage1_coverage_checker_01.py` L1032)で、`before_after_pairs`を引数に取らない。つまりスイッチがtrueでも、承認構成では「書き換えた前後の対」はRecheckに渡らず、`I`→`Meta`は「今の文が台帳と整合するか」の単独判定になる。rep2では`recheck_structural_pairs_n=1`と記録されるのに実際には使われていない。→ 修正点: `run_recheck_scope`に`structural_pairs`を渡し、変更単位の判定promptに「変更前/変更後」を併記(legacyの`build_before_after_instruction`を流用)。判定は主体・極性・数値に限定。
- **W3(【確認】)actor_guard(ag1_strict)は`new_classes=[]`**: 「Meta」はLedgerに既出の主体クラスで、「新しい主体クラスの出現」には当たらない。「一人称体験の主体Iが別主体Metaへ入れ替わった」ことはag1の検知対象外(【推測】ag1はクラス新規出現のみを見る設計。未検証)。→ 修正点: 構造要素の再生成では、上記照合1(主体入替の却下)を新ガードとして追加。
- 反証された仮説: 「cycle2のRecheck単位にタイトルが入らない」(RCA原文)。実際はS1.1として入っていた。ただし**Stage1がS1.1をどう判定したか(per-unitのr3 status)は保存が無く未確認**(n_union_candidates=0のみ。§3のR9と同じ未保存問題)。
- 過去事例との対応: OPEN-238(無関係文置換)の原因はprecheckの数値抽出偽陽性(案1でPRODUCTION_WIRED済み)でqvqcとは原因が別。ただし「BLOCKING指摘の修正案が新しい誤りを作りRecheckが拾わない」という失敗様式は共通。過去の「title delete」(タイトルが空になる)は`STRUCTURAL_ELEMENT_REWRITE`(委任_07)で解決済みで、今回はその解決策(書換えへ回す)が1語置換を許したことが新しい穴を作った。

### 1-4. 既存仕様との関係
- 既存(A): 構造要素を空にせず書換えへ回す(委任_07)、before/afterをRecheckへ渡す(委任_08)、ag1_strict。いずれも維持する。
- 変更点(C): 構造要素の書換え手段から1語置換を外し、文脈内再生成と4照合を必須化する。`STRUCTURAL_REWRITE_HINT_SUFFIX`(L6030)の「keeps only what the Ledger supports and drops the unsupported detail」が1語置換を誘発した可能性がある(【推測】hint文面とqvqcの因果は未検証)。Hookの構造要素への追加も新規。

## 2. ②反転型の格下げ禁止

### 2-1. 何が起きたか(【確認】)
jb9kのStage1は文を候補化(MAJOR、changed_scope/unsupported_new_claim=true)したが、Stage2はbasis=`ledger_scope`でQUALITYと判定し、2nd opinion(2-of-2)も同判断、cycle2は前回の非ブロッキング判定を再利用(`reused_nonblocking_verdict=true`)した。現行rubric(V7b、`MISCONCEPTION_PRINCIPLE_TEXT_V7B`、`er052_open233_self_recovery_stage2_calibration_01.py` L608〜)は(3)で「否定の反転・方向の反転・主体の取り違えはBLOCKING」と既に書いてあるが、jb9kは「台帳が言う『自己持ち出しなし』より広い『外へ出た報告なし』」として**範囲拡大(scope)**に分類され、否定の反転とは見なされなかった。**ラベルの選び方で重大度が変わる**構造が問題で、rubricに「否定反転はBLOCKING」を足すだけでは同じ失敗が残る。

### 2-2. 格下げの条件
Stage2が`ledger_scope`/`ledger_claim`等を根拠にQUALITY/ACCEPTABLEへ**格下げしてよい**のは、次を全て満たすときだけ(対象は否定・不在・全称・主体特定・数値を含む文):
- 読者がこの文を信じたとき世界について信じる内容(reader_belief)が、Ledgerの**どの肯定factとも矛盾しない**。
- 範囲が広がっているだけで、広がった範囲に含まれる事象についてLedgerが逆の事実を述べていない(jb9kはここで落ちる: EVID-008は「外部到達あり」)。
- 主体・極性・数値が台帳と一致。

**格下げしてはいけない**: reader_beliefがLedgerの肯定factと矛盾する/否定・不在主張が台帳の肯定factと食い違う/全称が台帳の個別例と食い違う/主体の不一致/数値の不一致。

### 2-3. 重大性は機械的に決めない(型→重大度にしない)
- 反転型は「格下げ禁止」であって「自動重大」ではない。Stage2のLLM判定が、新しい出力フィールドを埋めた上で改めて重大性を判定する。
- 否定・不在・全称・主体・数値を含む文を「**ガード対象**」とするのは決定論の粗い規則(§4)で、**ガード対象はStage1が既に候補化した文だけ**(1記事あたり数〜十数件)。検出(Stage1)は変えない。DANGER_COVERAGEの負荷71%は全文への検出の数字で、ここでは影響しない。
- 守りは2段:
  (a) Stage2 promptに「読者信念テスト」を追加(§2-4)。出力にreader_beliefと`belief_vs_ledger`(contradicts/unsupported_new_claim/consistent/unclear)を持たせる。
  (b) 整合性チェック(決定論): ガード対象で`belief_vs_ledger=contradicts`なのにQUALITY/ACCEPTABLEなら出力を無効として1回再問合せ、なお矛盾なら格下げ不成立(BLOCKINGのまま)。`unclear`も格下げ不成立。`unsupported_new_claim`は既存rubric(新規の具体的事実の追加=BLOCKING、周辺の背景=QUALITY)に従いStage2が決める。
- 「contradicts→BLOCKING」は**Stage2自身が同じcallで文とLedgerの両方を見て出した判断**に対する整合性チェックで、文の型から決めているのではない。

### 2-4. prompt差分案(Stage2 body rubricの末尾に追加。既存V7b本文は変更しない。実装時はV7c相当の新定数)
```
【読者信念テスト(対象: 否定・不在・全称・主体の特定・数値を含むclaim。materiality判定の前に必ず先に行う)】
1. reader_belief: 読者がこの文を信じたとき、世界について何を信じるかを1文で書く
   (claim文の言い換えではなく、読者が受け取る帰結として書く)。
2. belief_vs_ledger: そのreader_beliefをLedgerと照らし、次のいずれかを選ぶ。
   - contradicts: Ledgerの肯定factのどれかと矛盾する(contradicting_fact_idsに挙げる)
   - unsupported_new_claim: Ledgerに無い、世界についての新しい主張である
   - consistent: Ledgerの範囲内に収まる
   - unclear: 判断できない
3. basisに`ledger_scope`(範囲の逸脱)を選んでQUALITY/ACCEPTABLEにするのは、
   belief_vs_ledgerが`consistent`のときだけです。範囲が広がった結果、読者が信じる内容が
   Ledgerの肯定factと矛盾するなら、それは範囲の問題ではなく矛盾です(contradicts)。
4. 判定: contradictsなら、読者が主要な事実関係について誤解するためBLOCKINGです。
   unsupported_new_claimは、従来の基準(新しい具体的事実の追加はBLOCKING、周辺の背景はQUALITY)で
   決めてください。unclearはBLOCKINGとしてください。
5. 対象でない文には、この手順は不要です(reader_beliefは空でよい)。
```
- 出力schemaへの追加: `reader_belief`(string)、`belief_vs_ledger`(enum)、`contradicting_fact_ids`(array)。**これらは保存し、後段の機械比較には使わない**(使うのは同一callの`belief_vs_ledger`と`materiality`の整合チェックだけ)。
- 期待: jb9kはreader_belief「AIがテスト環境から外へ出たことは一度も報告されていない」、belief_vs_ledger=contradicts(EVID-008が外部到達あり)→BLOCKING。**期待であって実測ではない**(段階2のoffline replayで検証。jb9k 1件では有効性は言えない)。
- 副作用の懸念: 「There is nothing wrong with getting help from a human」(meta 249j。価値判断で不在主張ではない)のような文は、reader_beliefが世界の事実でなくなり`consistent`/`unsupported_new_claim`(周辺)になる想定。誤BLOCKINGの量は段階2の不要Rewrite率で測る。

### 2-5. 2nd opinionとcycle2の前回判定再利用をすり抜けさせない
- 2nd opinion(`STAGE2_SECOND_OPINION`、2-of-2): 両callとも同じrubric・同じモデルで**誤りが相関する**(jb9kは2回とも同じQUALITY)。対策は2回とも新rubricを使い、**ガード対象の格下げは両callが`consistent`のときだけ成立**(どちらかが`contradicts`/`unclear`なら不成立=BLOCKING)とする。既存の2-of-2(格下げ確認)の延長で、新しい承認ゲートではない。
- 前回判定の再利用(`STAGE2_VERDICT_REUSE_NONBLOCKING`、`nonblocking_registry`のkey=`claim_materiality_key(claim_text, fact_id, en_text)`、runner L8450・L8766): (i) registryに登録するのは、**ガード対象外**の2-of-2非BLOCKING、または**belief_vs_ledger=consistentが2回とも記録された**判定のみ。(ii) 旧rubric版(読者信念テスト導入前)の項目は再利用しない(rubric版をkey/値に含める)。(iii) ガード対象で`unsupported_new_claim`だった項目は毎cycle再判定する。これでjb9kの「cycle2で前回判定を再利用」経路は塞がる。
- 本文不変・2-of-2 BLOCKINGの固定(`MATERIALITY_BLOCKING_PIN`)は不変。

### 2-6. DIRECTIONAL-MISREAD TRIAL-03がREJECTEDになった理由と、同じ失敗を避けられているか
- 【確認】TRIAL-03(`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §86)は、Ledger側の事象を事前抽出し、記事側の事象を別callで抽出し、**2つの抽出ラベル(事象名・phase)を機械比較**する方式。退行要因は「Ledger側ラベルの反復揺れ(電話発信機能/機能/電話機能)」「記事側phase判定の誤り」で、HC-012/A5-0が3/3→0〜1/3へ退行、誤重大も発生した。**別々のcallが出す自由記述ラベルの一致に依存**したことが失敗の核。
- 本設計の②は、**1回のStage2 callが文とLedger全文の両方を見て直接判断**し、別callのラベルとの突合を行わない。ラベルの機械処理は同一call内の`belief_vs_ledger`と`materiality`の整合チェックだけ。STABILITY.mdが示すとおり自由記述フィールド(主語・述語・scope)は75〜87%程度しか一致しないので、**これらを比較の材料にしない**。安定している極性(100%)・数値(97%)に限る(§4)。→ TRIAL-03と同型の失敗(抽出ラベルの揺れ依存)は**設計上は**避けられている。ただし`belief_vs_ledger`自体の反復安定性は未測定で、段階2で同一claim×3回の一致率を測る(§5)。
- 残る懸念: `contradicts`判定自体もLLMの読みの揺れに依存する。2回のうち片方でもcontradicts/unclearなら格下げ不成立なので、揺れは「BLOCKINGへ倒れる」方向(不要Rewriteの増加)に出る。不要Rewrite率で測る。

### 2-7. HC-012系は3回目の修正に当たるか(条件B判断材料)
- 経緯: HC-012(ロールバックの方向)の修正は、台帳Note(OPEN-237系)・rubric V6/V7b・TRIAL-01〜03(DIRECTIONAL-MISREAD-SAFETY)と複数回あり、REPORT §86-7が「次の修正はHC-012に対する3回目のパッチ=条件B(Opus必須)」と記録している。
- 本設計の整理: ②の差分は**否定・不在・全称・主体・数値が対象で、方向語(restored/ロールバック)を新たなターゲットにしない**(「方向の反転」は既存V7b(3)の文言のまま触らず、本差分の対象リストにも入れない)。段階0-BのDIRWORD規則(HC-012由来、負荷4.7%・検出15.9%)も**本設計に採用しない**。したがって②は**HC-012に対する3回目の修正ではない**と整理する。HC-012/A5-0は**回帰確認にのみ**使う(②導入で既存挙動が悪化しないこと)。
- ただし、**同一rubric(R3→R3'→R3''→R3'''→V6→V7→V7b)は累積的にpatchされてきた**(【確認】定数名のチェーン)。②は別の機序(否定・不在の読み方)への追加だが、同じ問題の再発修正と見なすかはFable/Opus判断(§6-3論点1)。

## 3. ④Writer自己注釈(support_fact_ids、振り分け専用)

### 3-1. 【確認】前提となる制約
- JA Writer(`er019_family_x_ja_writer_o_r1_r2_01.py`の`run_ja_writer_o_r1_r2`)の入力は**Selected Fact Brief**(`.../storyline_b3/selected_brief.md`、要約したbullet)で、**Ledgerのfact_id(MUSE-HC-006等)はWriterの入力に含まれない**(rep2のruntime_evidenceで確認)。Writerにfact_idを直接書かせることはできない。
- `fact_selection_evidence.json`の`selected_fact_ids`はfact_id列。bulletに番号(F1..Fn)を付ければ、Writerが書く番号→fact_idへ決定論で写像できる(【推測】bullet順=`selected_fact_ids`順の一致は実装確認が必要)。
- JAはOriginal→R1→R2の連鎖(previous_response_id)で書き換わる。Originalに付けた注釈はR2で文が変わると対応が崩れる。
- EN記事はJAからの別生成で文の1対1対応は無い。**JA注釈はEN文のfact対応を与えない**。EN側の初出誤り(RECLASS: EN初出12〜13%)は④の対象外で、Stage1 r3の`support_fact_ids`(R9、未保存)を保存して使う。

### 3-2. 最小prompt差分(第1案: 記事生成promptを変えない後段注釈、推奨)
- JA R2確定**後**に、同じ会話(`previous_response_id`)で1回だけ追加callする。記事本文・R0/R1/R2のpromptは一切変更しない=**語りへの影響がゼロ**(面白さの懸念を構造的に除去)。
```
上のR2記事の各文について、その文が[ニュース]欄のどの項目(F1〜Fn)に基づくかを書いてください。
- 事実を述べる文(数値・固有名詞・出来事・因果・否定・全称を含む文)は、基づく項目番号を全て挙げてください。
- 語りかけ・問いかけ・比喩・場面描写・コメントなど、事実を新たに述べない文は、番号を付けず"narration"としてください。
- どの項目にも基づかない事実を述べた文は、正直に"none"としてください(減点しません)。
出力: JSON配列 [{"sentence_head": 文の先頭15字, "support": ["F2","F3"] | "narration" | "none"}]。
```
- 追加原価: 1記事1call(出力は短い)。実測は未取得(段階2で測る。【推測】数円規模)。
- 第2案(同一responseで本文+注釈を出力): 記事生成時にWriterがfact対応を意識して語りが痩せる懸念と、注釈の本文混入(TTSで読まれる)リスクがあるため**採らない**。

### 3-3. 保存先
- §83 R9で未保存だった情報の保存: (a) JA注釈: 既存の`ja_writer/audit/`配下(例: `ja_writer/audit/support_annotation_r2.json`)。新しい証跡置き場は作らない。(b) Stage1 r3の`support_fact_ids`(全判定単位): 既存のchecker run JSON(`checker/runs/*.json`)の`stage1_coverage`配下へ全単位分を保存(現在は候補の`related_fact_ids`のみ)。
- 番号→fact_idの写像は`selected_fact_ids`と突合し、bullet順の仮定が崩れる場合は番号方式をやめる。

### 3-4. 用途(振り分けのみ。検証には使わない)
1. `support`が`none`、またはfact番号がStage1 r3の`support_fact_ids`と食い違う文 → 「新しい世界主張」候補として、Stage1が候補化していなくてもStage2の優先確認対象(②のガード対象)に**追加**する(重大度は決めない)。
2. `narration`の文も検証対象から外さない(Stage1 r3は従来どおり全文を見る)。ただし②のガード対象にはしない(新規固有名詞・数値が無い限り)。
3. 機械チェック(narration文のみ): 新規の固有名詞・数値が、Selected Brief/Ledgerに無ければ「語りに紛れた事実」として振り分け候補(決定論、API無し)。
4. Writerが付けたfact番号は**検証に使わない**(「その文はそのfactと整合」とはしない)。fact番号は、③のLIMIT系規則のリンク元(§4)としてだけ使う。
- 位置づけ: RECLASSで「その他」NG18件は新しい世界主張で、危険文条件では拾えない見込み(RECLASS §4)。拾える経路はStage1 r5(Ledger逆照合、既存)と、④のfact_idなし文の優先確認のみ。
- 注釈の番号が誤っても、害は「振り分けの精度低下」に限り、記事品質・安全判定には影響しない設計。

### 3-5. 面白さへの影響と対策
- 第1案は本文生成後の別callなので**本文は注釈有無で変わらない**(同一R2を使う)。面白さへの影響は構造上ゼロ。測定でも「注釈ON/OFFでR2が同一」(同一textのsha一致)を確認する。
- 残るリスク: previous_response_idによるトークン増・原価、注釈の誤り。Trialで原価と注釈のStage1との一致率を記録する。

## 4. ③危険文の振り分け(補助、検出層ではない)

### 4-1. 段階0-Bの結果(`er052_output/open233_stage0_01/danger/DANGER_COVERAGE.md`、反映済み)
- 【確認】100記事(5663文)、規則7種(NEG/UNIV/CAUSE/NUM/LIMIT_HEDGE/LIMIT_SCOPE/SUBJ)。仮ライン(検出率80%以上かつ負荷40%以下)を満たす組合せは**auto(自動リンク)で0通り**。P1(全規則)は検出auto 86.6%/oracle 97.6%だが**負荷71.0%**。負荷40%以下の最大検出率はauto 約65%(oracle 約94%)。LIMIT系はfactリンク精度(auto 63%対oracle 94%)に強く依存。NEG(検出/負荷1.1)・SUBJ(1.4)・NUM(1.4)は弁別力が低い。重大8件はP1/P4で8/8、P3(factリンク不要の規則のみ)で7/8。
- **結論の反映**: 「危険文限定の関係検査(検出層)」は語彙規則だけでは**成立しない**。したがって③を**新しい検出層とせず**、(1)②のガード対象の決定、(2)Stage2で優先して見る順序づけ、(3)人間確認パックの優先順位づけ(Opus: 上位10%を人間レビューへ)に**限定**する。検出はStage1(coverage_union、全判定単位を見る、既存)に任せ、③は「どの候補を格下げ禁止の対象にするか」を決めるだけ。この限定により負荷71%は問題にならない(適用対象はStage1が候補化した数件)。

### 4-2. 規則(決定論、API無し。段階2でdev 100件のみ使って調整)
| 規則 | 内容 | 使う根拠・留意点 |
|---|---|---|
| 否定・不在 | 存在否定に限定(「〜ていない・されていない・ありません」「報告されていない」/EN: not been reported, no evidence, nor has, there is no) | DANGER_COVERAGEの改善案(1): NEGは負荷27%で弁別力が低く存在否定に絞る。絞った後の負荷・検出率は未測定 |
| 全称 | すべて/どれも/誰も/常に/all/every/no one | 単独で検出/負荷2.0と比較的高い |
| 因果接続 | ため/により/その結果/because/led to等。時間語(後/前/直後)は別扱い | 改善案(1) |
| 主体の新規 | 固有名詞が台帳に無い。**タイトルは除外**(titleでSUBJ負荷59%) | 改善案(1) |
| 数値 | 数値を含む(既存precheckは数字のみBLOCKING、`PRECHECK_MODE=number_only`。③は格下げ禁止対象の決定だけで重複しない) | |
| 限定語消失 | 抽出に頼らず、**Ledger factに限定語リストの語(一部・約・当面・可能性・のみ・初めて等)があり、リンク先factに有る語がその文に無い**粗比較 | STABILITY.md: scope抽出の一致率55〜70%で不安定→抽出を使わず語の有無の粗比較(STABILITY「改善余地(3)」と同方針) |
- 「安定している抽出フィールド(極性100%・数値97%)」を使う振り分けは、**新しいLLM抽出callを作らず**、既存Stage1 r3のフラグ(changed_number等)または決定論の数値抽出を使う。主語・述語・scopeの抽出(75〜87%)は使わない。
- リンク元(LIMIT系のfact対応): ①Stage1 r3の`support_fact_ids`(保存後)、②④のJA注釈(JAのみ)。自動リンク(語の重なり)だけでは精度が低い(DANGER_COVERAGE)ので、**この2つのリンクが使えない間はLIMIT系を「ガード対象の決定」に使わない**。

### 4-3. 追加規則の扱い
- DANGER_COVERAGE §5の追加規則のうち、DIRWORD(方向語)はHC-012由来で過学習回避方針(§0・§2-7)に反するため**採用しない**。ANAPH/INCL/FREQは負荷2%前後・検出少で、段階2のdevで必要性が出た場合のみ追加(Fable判断)。MULTIFACT(1文が2fact以上にリンク)は、④のリンクが使えるようになってから評価。
- DANGER_COVERAGE §4の見逃し一覧にheld-out項目が含まれる可能性があるため、型レベルの示唆(T1〜T6)以上には使わない(§0)。

### 4-4. 既存機構との関係(重複回避)
- Stage1にはすでに決定論の否定検査(`STAGE1_NEGATION_MODE="a"`、`negation_mismatch_a`)と数値検査がある。③の規則は検出を増やさず**格下げ禁止対象の判定**であり、Stage1の候補を増減させない。
- 2026-10-06のユーザー承認で、数字以外の機械的な強制重大化(因果floor等)は廃止された(`OPEN233_APPROVED_FLOW_SWITCHES`、`CAUSAL_FLOOR=False`)。③は**重大度を機械的に決めない**ので矛盾しない(ガード対象=Stage2に読者信念テストを必須にするだけ)。

## 5. 期待効果と測定(事前登録の下書き。数値の仮ラインはFableが確定)

### 5-1. 段階2: offline replay(既存R0を新Checkerへ。Stage1候補は保存済みを再利用=Stage1 call 0)
- 理由: ①②はStage2・Rewrite・Recheckの変更で、Stage1は不変。Stage1候補(例: jb9kのS7.4)は既存のcheckerログに保存されている(`checker/runs/*.json`の`stage1_coverage`、【確認】jb9kはcycle1/2とも候補化)。Stage2のみ新rubricで再実行すれば、**原価は主にStage2(batch+2nd opinion、1記事約¥0.5前後)**。【推測】100記事で約¥50〜100(要実測。ログにStage1候補が残る記事のみ対象)。
- 対象: devの既知関係型NG(RECLASSの`split=dev`、約100件)で調整→held-outは確定後1回。
- 指標(仮ライン案):
  | 指標 | 内容 | 仮ライン(事前登録案) |
  |---|---|---|
  | 関係型NG検出率 | ガード対象型のdev既知NGのうち、Stage1が候補化した文が最終的にBLOCKING(または格下げ不成立)になる割合。現行Stage2のreplayと並べて比較 | 現行より悪化しない。目標: 現行比で向上(件数が少なく有意差は言えない前提) |
  | 誤検出率/不要Rewrite率 | 既知NGでない文のうち、新たにBLOCKINGとなる件数/記事 | 現行比 +0.3件/記事以内(仮) |
  | 削除文数・書換え文数 | Checker前後の変更・削除文/記事。**必ず報告** | 現行比で増加しない。構造要素の語置換は0 |
  | 構造要素の規則違反 | 構造要素に対する1語置換・`# `欠落・主体入替の件数(決定論assert) | 0件 |
  | Checker由来の新規NG | Rewriteが新しく作った主体・極性・数値の不一致(機械+人手確認) | 0件 |
  | `belief_vs_ledger`の反復安定性 | 同一claim×3回の一致率 | 3/3一致 80%以上(仮。事前固定) |
  | 原価 | Stage2追加分/記事 | 現行+¥0.5以内/記事(仮) |
- 過学習対策: jb9k/qvqc/HC-012は回帰確認として別枠で報告。dev調整のrubric版数は事前に上限を決める(例: 2版まで)。

### 5-2. 段階3: 本番経路Trial(N≥30、同一記事比較)
- 設計: 同一のJA R2に対し、**現行Checker構成**と**新Checker構成**(②+①+注釈④)を適用し、記事単位で対にして比較(Writer分散を除去)。評価者固定・盲検(構成名を伏せる)・事前登録。異なる物差しの比較は禁止(評価者間差は約2倍、RCA結論)。
- 主指標: 関係型誤り率(軽微を含む。重大は床効果でN<100では改善を示せない=Opus所見)。
- 副指標: 人間確認重大率、人間レビュー率(上位10%以内)とその中の重大捕捉率、Checkerが作った誤り、不要Rewrite率、削除文数・書換え文数、原価。
- 面白さ: 主=ユーザー盲検の読み比べ約10組(「続きを聞きたい方」の非劣性。夜間は取れないため**代理指標のみ・非劣性未確認と明記**)。副=語りの要素の保持率(`docs/pm/stage0_01/narrative_elements_v1.md`、暫定・未承認)とChecker前後の変更文・削除文比率。LLM採点は補助。
- 構造: ①②はCheckerの判定・Rewrite規則の変更で、Writerの生成は不変。④は後段注釈なので記事本文は同一。面白さが変わりうるのは「Checkerがより多く修正/削除する」場合に限り、削除文数・変更文比率で検出する。

## 6. 実装規模・影響範囲・リスク・Opus条件Aレビュー論点

### 6-1. 変更ファイル候補(提案のみ。実装はしない)
| 項目 | ファイル(コード箇所) | 規模感 |
|---|---|---|
| スイッチ追加(既定OFF) | `er052_open233_self_recovery_flow_runner_01.py`(L2403〜2420のスイッチ群の隣。`OPEN233_APPROVED_FLOW_SWITCHES`へは**入れない**。Trial用dictにのみON) | 数行 |
| ①ladder: 構造要素で1語置換を外す・Hookを構造要素へ追加 | 同runner `structural_element_reasons`(L6037)・`structural_rewrite`分岐(L6260付近)・levels_planned(L6353付近) | 数十行 |
| ①形式保存(W1)・主体入替却下(W3) | 同runnerのladder成功判定(L6350付近)に決定論チェック | 数十行 |
| ①構造要素の文脈内再生成 | 新規関数(同runnerまたは新規モジュール) | 〜100行 |
| ①Recheck配線(W2) | `run_recheck_coverage`(L1929)、`er052_open233_stage1_coverage_checker_01.py`の`run_recheck_scope`(L1032) | 数十行 |
| ②Stage2 prompt/schema/整合チェック | rubric: `er052_open233_self_recovery_stage2_calibration_01.py`(新定数V7c、既存V7bは残す)、runner `BODY_RUBRIC_DEFAULT`(L589)・`run_stage2`系schema | 数十行 |
| ②再利用・2nd opinion | runner L8750〜8800(`nonblocking_registry`)・2nd opinion箇所 | 数十行 |
| ④後段注釈 | `er019_family_x_ja_writer_o_r1_r2_01.py`(新規関数。`run_ja_writer_o_r1_r2`は不変、既定None)。保存は`ja_writer/audit/` | 〜80行 |
| ③ガード対象決定規則 | 新規モジュール(測定用`er052_output/open233_stage0_01/danger/danger_sentence_rules_v0.py`は測定専用でそのままは使わない) | 〜100行 |
| テスト | `er052_open233_self_recovery_flow_runner_01_test_01.py` | 規則・assertのunit test |
- **スイッチ化**: 全て既定OFF。Trial用スイッチ辞書でのみON。Checker全体が**Production未配線**(OPEN-238行の記載)で、変更自体が現Productionへ影響することはない。Production採用にはユーザー承認(`APPROVED_FOR_PRODUCTION`)とOpus条件C(採用提案前)が別途必要。

### 6-2. リスク
- ②の過剰BLOCKING: 不要Rewrite・削除文の増加→面白さ低下(測定対象)。2-of-2の「どちらか一方でも格下げ不成立」は安全側で、不要Rewrite率が最大の副作用。
- ①のHook追加: 現状は語置換で直っていたHookが、削除/再生成へ回りHookが痩せる恐れ。再生成は検査済み本文を入力にし、元の文体指示を保持する必要がある(要Trial)。
- OPEN-239(JA R2はChecker対象外)により、ENだけ修正されるとJA/EN不一致が増える可能性。本設計はJA側の扱いを変えない(別管理)。
- ④の写像仮定(bullet順=`selected_fact_ids`順)は未検証。
- 段階0-Bで③を検出層にできない(§4-1)ため、「危険文限定の関係検査」は本設計では**成立していない**。②の効果は「Stage1が候補化した場合」に限る(Stage1が拾わない文は救えない。RECLASSの「その他」18件は④の経路頼み)。
- rubricの累積patch(§2-7)。

### 6-3. Opus条件Aレビューの論点(5点)
1. ②は「別機序の追加」か「rubricの6回目のpatch(条件B相当)」か。Stage2判定に読者信念テスト(1call内の自己判断)を足す構造は、TRIAL-03型の失敗(別callラベルの機械比較)と十分に異なるか。
2. ①で構造要素の書換え手段から1語置換を外し、Hookを構造要素に加えることの妥当性(既存の「空にせず書換え」仕様[委任_07/08]との整合、Hookの面白さへの影響、削除可否)。
3. ④を後段注釈(本文不変)にする判断と、Writer入力にfact_idが無い制約下の番号方式の妥当性。注釈を「振り分けのみ」に限定する線引き。
4. 段階0-Bで「危険文限定の検出」が仮ライン未達だったため、③を検出層から外す整理で、Opus所見の推奨(G: 危険文限定の関係検査)が実質縮小することの是非。Stage1が全文を見る既存構造で十分か。
5. 測定: dev調整・held-out1回・N≥30の同一記事比較・「Stage1候補固定のoffline replay」でCheckerの全効果を代理できるか。床効果(重大N<100)に対する主指標の選び方。

## 7. Reconciliation表(PM_GOVERNANCE 2-1/21節: A=既存仕様、B=過去Trialの失敗/結果、C=新規)
| 提案 | 分類 | 出典・関係 |
|---|---|---|
| ①構造要素を空にせず書換え | A | `DECISION_LOG.md`(委任_07「構造要素を空にせず上位Rewriteへ進める処理」)、runner `STRUCTURAL_ELEMENT_REWRITE`・`structural_element_reasons`(L6037) |
| ①構造要素のbefore/afterをRecheckへ渡す | A(承認構成では配線が実効していない)→配線修正はC | 委任_08、`STRUCTURAL_PAIRS_TO_RECHECK`(L2403)。coverage_union Recheckでは未使用(W2) |
| ①構造要素の1語置換の禁止 | C(既存の書換え許可を狭める) | 既存ladder `1_word_connective`(委任_07/08)。qvqc(`RCA_jb9k_qvqc.md`)は過学習せず型で定義 |
| ①Hookを構造要素へ追加 | C | 現行は対象外(L6037) |
| ①文脈内再生成+4照合+形式保存 | C | 既存ladder `3_sentence`/`4_paragraph`とは別。OPEN-238(Rewriteが新規誤りを作る)の再演を避ける設計(B) |
| ①ladder枯渇時の出口 | A | `blocking_structural_after_ladder`・許可リスト(委任_11/12) |
| ②格下げ禁止(基準の追加) | C | V7b(3)に「否定反転等=BLOCKING」が既にある(A)がラベル選択で回避された(jb9k)。rubric追記は累積patchの一部(B) |
| ②2-of-2・前回判定再利用の守り | A(拡張) | `STAGE2_SECOND_OPINION`、`STAGE2_VERDICT_REUSE_NONBLOCKING`(L8766)。再利用条件の追加はC |
| ②抽出ラベルの機械比較を使わない | B(TRIAL-03の教訓) | `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §86-7(REJECTED)、Opus所見 |
| ②HC-012の方向語を対象にしない | B | REPORT §86-7(次修正=3回目=条件B)、DIRWORD不採用 |
| ③危険文の規則ベース振り分け | B(段階0-Bで仮ライン未達)+C | `DANGER_COVERAGE.md` §3・§6。既存の決定論否定検査は`STAGE1_NEGATION_MODE="a"`(A)で、③は検出を増やさない |
| ③重大度を機械的に決めない | A | 2026-10-06承認(`OPEN233_APPROVED_FLOW_SWITCHES`、`CAUSAL_FLOOR=False`)、Opus所見 |
| ③関係抽出(主語・述語・scope)を使わない | B | `STABILITY.md`(主語82〜87%、述語75%、scope55〜70%) |
| ④Writer自己注釈(後段注釈) | C | 本文生成は不変。Stage1 r3の`support_fact_ids`保存はA(既存出力の保存、REPORT §83 R9持ち越し) |
| ④fact_idなし文を優先確認に回す | C | Opus所見④、RECLASS §4(「その他」18件は④頼み) |
| 台帳側の動詞正規化+固定Note(⑤) | A(別管理、本設計の対象外) | OPEN-237 P'(Opus所見) |
| 初稿2本生成E | 対象外 | Opus所見(第2段階候補) |

## 8. Dangling Reference Check
実行結果(スクリプトで本書中のバッククォート内パス候補を存在確認): フルパス表記の17件は全て実在。実在しない扱いになった9件の内訳は次のとおり。
- 略記(実在): `DANGER_COVERAGE.md`(`er052_output/open233_stage0_01/danger/`)、`STABILITY.md`(`.../stability/`)、`RCA_jb9k_qvqc.md`(`er052_output/open233_control_checker_polysemy_trial_01/eval/`)、`split.json`(`.../reclass/`、実在確認のみで未開封)。
- run配下の相対表記(rep2の`runs/meta/nb/rep2/`配下に実在を確認): `.../storyline_b3/selected_brief.md`、`fact_selection_evidence.json`、`checker/runs/*.json`、`ja_writer/audit`。
- 提案する新規保存先(未作成が正しい): `ja_writer/audit/support_annotation_r2.json`。
- 本書で参照したコード行番号(L6037等)は2026-10-07時点のrunner(`er052_open233_self_recovery_flow_runner_01.py`)のGrep結果で、実装時に再確認が必要。
