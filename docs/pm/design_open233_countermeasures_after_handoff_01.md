# OPEN-233 受け渡し修正の後に残る問題への対策設計案(Trial/検証用、実装前・Opus独立レビュー前)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_48、2026-10-02)
性質: 設計案のみ。**実装していない。Trialを回していない。API費用¥0。** コード・Prompt・テスト・SSOTは編集していない。
Status: 到達上限Statusなし(OPEN-233のStatusは変更しない)。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の条件A(新しい構造・処理フローの設計)に該当するため、実装の前にFableがOpusレビューを依頼する。Production採用は人間ユーザーだけが承認する。

## 読み方(用語と出所の記法)

- 「Rewrite」=Checkerが指摘した箇所をLLMで書き直す工程。「Recheck」=書き直した全文をもう一度Checkerで検査する工程。「Stage 4」=人間確認に回す終了状態(安全側の止まり方)。「周回(cycle)」=検査→書き直し→再検査の1往復。
- 「fail-closed」=判断できないときに、通さず人間確認へ倒す設計。「fixture」=過去の検査結果を固定して再利用する入力データ(固定fixture)。
- 出所の略記(いずれも`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_<番号>_result.md`。委任の最終報告をそのまま保存したもの): R41=委任_41、R42=委任_42、R43=委任_43、R44=委任_44、R45=委任_45、R46=委任_46。DL=`DECISION_LOG.md`、SPEC=`CURRENT_SPEC.md`、DSG=`docs/pm/design_open233_self_recovery_flow_01.md`、HO=`docs/pm/design_open233_violation_span_handoff_01.md`、OP5=`docs/pm/opus_l2_review_open233_self_recovery_05.md`、RPT=`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`。
- コードの行番号は、commit `850cfe3f`時点の作業ツリーの`er052_open233_self_recovery_flow_runner_01.py`(以下「runner」)。
- 数値は出所つき。測っていないものは「未測定」「見積もり」と書く。

## 結論(全体、先に読む部分)

1. 対策は4系統(A=受け渡しの追補、B=Checker出力形式、C=見逃しと重大度の揺れ、D=英語だけ修正)。すべてTrial runner内のスイッチで切り替え可能にでき、**既定値は現行のまま**にできる。Production正式path(er003等)には触れずに実現できることを、呼び出し関係で確認した(§3-6、§5-5)。
2. 実装が小さく効果の根拠が明確なのはA1(末尾句読点)・A2(位置ラベル誤確定の防止)・D(英語だけ修正。実体はrunnerの`current_ja_text`を`None`にする数行+ガード)。Bは必要性が「中程度」で両論あり、C1はこれまで一度も測ったことがなく、C2は過去に不採用になった機構と重なる。
3. **Fable骨子への指摘が複数ある**(§11)。特に(i)Bの「配列からコードが`claim_in_article`を組み立てる」は、現在の照合関数が配列を受け取れないため、文字列を作るだけでは足りない、(ii)C2は既存のS1-U(Stage 1がPASSのときだけ1回追加する検査)と過去の不採用実績(2×V4-A和集合)に重なり、既存記録から推定できる改善は割れていて結論が出ない(fresh Stage 1では増分0、固定Stage 1のRecheckでは3組の小標本で増分あり)、(iii)A3のまとめて渡す案は実現可能だが、グループ内の「問題の種類」の決め方に設計判断が残る。
4. **予算**: 残り¥105.97で(i)限定確認(約¥36〜49の概算)と(ii)29件横断の再確認(過去実費¥25.0〜39.5)は、(ii)を1回なら収まる。(ii)を上限額で2回回すと¥10〜23不足する(§7-5)。ユーザーSTOP条件「¥600予算上限超過が必要」に関わるため、Fableへ必ず報告する。
5. 新しいProduct原則・Safety原則の変更・Production正式仕様の変更は、今回の設計範囲には含めていない。ただしA4の(b)案は「安全用ガードを緩める変更に当たるか」の読みが分かれる(§2-4)。Production採用時にユーザー判断が要る事項(日本語の扱い・日本語タイトル)は§5-6にまとめた。

---

## 0. 前提とスコープ

**結論**: すべてTrial/検証用の範囲。Production正式pathは変更しない。ユーザーが2026-10-02に出した指示(DL 16977行以降に逐語で保存済み)に従う。今回やらないことは、文ID・文字オフセット方式、文単位スナップ、別AIの引用による救済、周回上限の単純な引き上げ、降格ルールの変更。

### 0-1. ユーザー指示の逐語引用(DL 16986〜17240行、委任_42が逐語で追記した原文から)

> ただしProduction正式pathは変更禁止です。Trial/検証用の範囲で進めてください。

(§1より)

> - Checkerが示した違反範囲を後段で再推測しない
> - 複数文なら複数文のままRewriteへ渡す
> - 離れた複数箇所なら複数範囲として渡す
> - 別AIの引用でRewrite対象を決めない
> - 類似度や単語重なりで勝手に1文へ縮小しない
> - 文ID・文字オフセット方式は現時点では採用しない
> - 最小修正優先ルールを維持する

> 文の一部が違反だからといって、最初から文全体Rewriteへ広げないでください。

(§3より)

> ただし、判定基準そのものは変えず、**違反範囲の出力形式だけを変える**こと。

> 対策後、
> - 特定不能率
> - 検出漏れ
> - false PASS
> - 出力失敗
> - Human Reviewへの影響
> を確認してください。

(§4より)

> **日本語は、エンターテイメント性のある英語記事を作るための手段。LedgerとのDeviationが英語側にあるなら、英語を直せばよい。**

> 単に「日英整合を保ちたい」という理由だけなら、日本語まで遡って修正する必要はありません。

> 実害がなければ、日本語側の複雑な推測処理は外す方向で設計してください。
> 実害がある場合は、その経路を具体的に示した上で最小限の対策を提案してください。

(§5より、周回の扱い)

> ### 周回構造そのものが原因
> cycle上限を安易に増やすのではなく、
>
> **なぜ複数周必要になるのかを減らす設計**
>
> を優先してください。

> 原因分析だけでSTOPせず、Guardrail内で対策実装＋限定再確認まで進めてください。

(§6より)

> 先に正式採用したOpus独立技術レビューGateに従ってください。
> 新しい構造案を実装する前にOpusレビューが必要な条件に該当する場合は、必ず実施してください。

(§7より)

> **最新版で29件横断再確認**
> ↓
> 重大な新問題がなければ
> **実記事N増し**

(§8より、STOP条件)

> 以下の場合のみUSER_DECISION_REQUIREDとしてSTOPしてください。
> - 新しいProduct原則の採用が必要
> - Safety原則の変更が必要
> - Production正式仕様の変更判断が必要
> - ¥600予算上限超過が必要
> - Claude案とOpusレビューが重要点で対立し、Fableで解消できない
> - 複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要

> 単に1回TrialがFAILした、1つ新しい変種が出た、という理由だけでは戻さず、Guardrail内で原因特定→対策→限定再確認まで進めてください。
> Production正式pathは変更禁止です。

> VALIDATEDでもProduction採用ではありません。

### 0-2. Trial専用であること・Production正式pathに触れないこと
- 対象はTrial専用のrunner(`er052_open233_self_recovery_flow_runner_01.py`)とTrial専用の追記ブロックだけ。Checkerの本体Prompt(`er003_v1_en_direct_vfl_01_generate.py`の`DEVIATION_PROMPT_TEMPLATE`、502〜541行)とschema(455〜493行)は変更しない。Trial側の追記は既にrunnerが「Promptの末尾へ文字列を足す・schemaをローカルにコピーして拡張する」形で行っており(§3-5)、同じ手口の範囲に収める。
- `HANDOFF_MODE`(runner 321〜323行)は現在、新方式`violation_span`が既定。本設計の新スイッチも「Trialで明示的に有効化する」形にし、既定は現行の挙動に固定する(§6)。

### 0-3. 今回やらないこと
| 項目 | 理由 |
|---|---|
| 文ID・文字オフセット方式 | ユーザー指示§1(現時点では採用しない) |
| 文単位スナップ(Checker文字列を含む文へ拡張して確定範囲にする) | ユーザーが不採用(委任_42指示)。水準③(範囲を含む文)は、水準①が解消できなかった場合のRewrite段の拡張であり、確定範囲そのものの拡張とは別(§2-1) |
| 別AI(判定役Stage 2のhint)の引用による救済 | ユーザー指示§1(別AIの引用でRewrite対象を決めない) |
| 周回上限の単純な引き上げ | ユーザー指示§5。`MAX_CYCLES=2`、`HARD_MAX_CYCLES=3`(runner 278・282行)は変更しない |
| 降格ルールの変更(`changed_scope`を降格の除外条件から外す等) | §4-4。決定論的な安全ルールを緩める変更で、STOP条件「Safety原則の変更が必要」に当たりうる |
| 日本語タイトルの作り直し | Production正式pathの変更が必要(§5-6) |

---

## 1. 現状の事実(委任_41〜46の結果)

**結論**: 受け渡し修正は目的の範囲では効いた(2文取りこぼしによるStage 4は0)。残る問題は、(1)Checker文字列の照合(末尾句読点22行、説明文混入12行)、(2)2周目以降に新しく出る指摘(85行の最大要因は「元記事にあったのに前の周回で出なかった」34行)、(3)日本語側の処理の重さ(JA関連の検査費用¥35.9=約13.9%)。

### 1-1. 受け渡し修正の限定Trial rep22(R42 §5、`er052_output/open233_self_recovery_flow_runner_01_rep22/analysis_rep22.json`)

| 項目 | 結果 | 費用 |
|---|---|---|
| T1(固定Stage 1、`meta_run03_standard`、n=4) | 4件とも2文claim(MUSE-HC-011)が1周目に2文1範囲(L1)で水準①の対象。s1/s3/s4=`RESOLVED_REWRITE_THEN_DOWNGRADE`、s2=`STAGE4_ESCALATION`/`cycle_limit_exhausted` | s1 ¥1.1210、s2 ¥2.1773、s3 ¥1.3140、s4 ¥1.0118(計¥5.6241) |
| T2(rep20 s2 cycle2再現、n=2、Stage 3以降・1周のみ) | 範囲は離れた2文(L4)。①は「最小編集で解消できない」(declined)、③は主体置換ガードが新語`users`で棄却(2/2)、④で成立。ENの前回指摘は解消。**JA暫定経路(`en_multiple_ranges`)が2/2、JA Recheck未解決(`ja_ok=False`)**。s2はEN側に別の新規MAJOR(MUSE-HC-010)も | ¥1.0338/¥1.0143(各6call) |
| T3(Safety、changed_number、n=1) | run1(是正前)=`STAGE4_ESCALATION`/`violation_span_unverified`(実装不具合)。是正後run2=`RESOLVED_REWRITE`(「more than 30 million」→「more than 13 million」=Ledger F-002の1,300万件)。floorは2claimとも発火、false PASS 0 | run1 ¥0.1992、run2 ¥0.2311 |

- 成功条件6項目は、R42が「達成」と報告(取りこぼし起因Stage 4=0、①の対象==確定範囲6/6、T3でfloor発火・false PASS 0、①開始6/7、⑥=0、確定不能0件)。最終分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はFable。
- **T1 s2のStage 4の原因(R42 §6)**: 受け渡しではない。cycle2で、元記事にあったMUSE-HC-010「some calls needed user information to continue」をcycle1のRecheckが初めて指摘(MAJOR、BLOCKING)。cycle3で、同じ文MUSE-HC-012「They enjoyed AI’s convenience…」が、cycle1・2のQUALITYからBLOCKINGへ揺れた。blocking件数が減らず新しいfact_idもないため追加周回なし→`cycle_limit_exhausted`。
- **T3の不具合と是正(R42 §7)**: 同じ周回に、LLMのclaimとprecheck floorのclaimが同じ文を指していた。先行claimのRewriteで文が変わり、後続claimのChecker文字列が現在の本文から消えて「不一致」と誤判定された。是正として`carry_forward_resolution`/`collect_replaced_units`(runner 3954〜4008行)を追加。**これはOpusレビュー#5の設計にない小機構**(R42が要Fable確認と明記)。
- 費用: 今回¥8.1025、Phase累計¥494.0300/総枠¥600、残¥105.9700。ただし予算stateの`cumulative_jpy`はT3 run1の¥0.1992が欠けており、正式な費用はinstance JSONのcall_log合計(R42 §1)。

### 1-2. 特定不能35件の原因分類(R45 §2、`er052_output/open233_handoff_log_aggregation_01/unverified35_classification_01.csv`)
重大指摘261件中35行(13.4%、13種類・32 run)。目視分類:

| 区分 | 行 | 種類 | 内容 |
|---|---|---|---|
| C1 言い換え | 0 | 0 | なし(委任_41の「言い換え・要約21行」は診断の誤りで実体はC2) |
| C2 句読点の差 | 22 | 3 | 文を節の途中まで引用し、末尾の句読点を替えただけ(語は一字も違わない)。20行は固定fixture1件の再生 |
| C3 説明文混入 | 12 | 9 | 断片は全て逐語。混入物は位置ラベル・Checkerの説明文・日本語のつなぎ語。複数箇所のうち1箇所しか直せていない例が10行 |
| C4 省略記号 | 1 | 1 | 「A ... B」の中略 |
| 合計 | 35 | 13 | |

実LLMのRecheckが返した行は8行(8/58=13.8%)で全てC3。固定fixture再生が27行で、独立なChecker出力は13種類のみ(R45 §3)。直近(rep17〜21、iter8、最新29件横断)の確定不能は0件(strict)。

### 1-3. 周回2以降の新規BLOCKING 85行の原因内訳(R44 §3-5、§4、`er052_output/open233_cycle_new_issue_analysis_01/results_01.json`)
2周以上実行されたrun 69件(全277ファイル中)の「cycle 2以降の最終BLOCKING指摘」85行:

| 原因 | 行 | 率 | 内容 |
|---|---|---|---|
| P2a+P2b 見逃し | 18+16=**34** | 40% | 元記事にあったのに前の周回で(MAJORとして)出なかった。同一fact別箇所18、factが初出16 |
| R1+R_older 書き換え起因 | 19+1=**20** | 24% | 直前のRewrite範囲またはその付近が再指摘。20行中13行はfloor引き上げ(委任_35で廃止済みの一括適用の副作用)。修正後のrep20・rep21は0行 |
| P1 重大度の揺れ | **15** | 18% | 前の周回では非BLOCKING(QUALITY等)だった同じ範囲が後でBLOCKING。Checker自身のseverityは85行すべてMAJORで揺れていない。揺れたのはStage 2の最終判定(flagの出入りと、それに連動する降格・floor) |
| P3 取りこぼし | **8** | 9% | 受け渡しの取りこぼし(委任_42の修正対象) |
| U 判定不能 | **8** | 9% | 説明文混在で文字列を確定できない |

限界(R44 §2): CheckerがMINORとした指摘は次周回の入力から落ちて記録に残らない。P2は「MAJORとして出なかった」であり「完全に見逃した」かどうかは記録から区別できない。版違いのrun(iter5〜rep21)を合算している。

### 1-4. `meta_run03_standard`の見逃し(MUSE-HC-010、R46 A-4/A-5、R44 §3)
- 文: 「Also, some calls needed user information to continue.」。Ledger(MUSE-HC-010)は「電話の遂行にユーザー情報が必要となる場合」という**条件**。記事は「some calls needed」で発生を断定。
- **正解ラベルではSafety-critical(Meta-1)**: runnerの`SAFETY_CRITICAL_CLAIM_DEFS`(5676〜5681行)に`meta_run03_standard`の`Meta-1`(related_fact_id=MUSE-HC-010、text_substring=「needed user information to continue」)として登録。DSG §4-21(1404〜1427行)・§7-0-iter29(3614行以降)がBLOCKING維持と定める(R46 A-4)。なお同じ文のLedger対記事の読みは「判断が分かれる」とR46は書いている(Stage 2の字面の基準では「矛盾」まで言えずQUALITY寄り、ただし設計書のV4原則を採ればBLOCKING)。正解ラベルはFableの設計書側。
- **23実行の数え直し**(R46 A-5の表を、本設計で行ごとに数え直した。R46の結論と一致):
  - 全23実行(iter5〜rep21。rep22は集計外)のうち、文が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終了したのは**5実行**(rep16 s1/s2、rep18 s1/s2、rep21 s2)。
  - 文が元のまま残り未指摘だがStage 4(別の理由で人間確認)で終わったのが2実行(iter8 s2、rep20 s2)。
  - freshのStage 1(Stage 1を毎回実行した実行)は16実行(iter5〜7、rep9、rep11、rep12、rep16、rep18の各s1・s2)。そのうち12実行で1周目のStage 1がHC-010を指摘、4実行(rep16 s1/s2、rep18 s1/s2)は指摘しなかった。**12/16**。
  - 固定Stage 1(rep19〜21、iter8)の7実行は、固定fixtureのdeviationsにHC-010がそもそも無い。HC-010の文が本文に残ったまま行われたRecheckは8回で、指摘は**4回**(iter8 s1 c2、rep19 s1 c2、rep20 s1 c2、rep21 s1 c3)、指摘なし4回(iter8 s2 c2、rep20 s2 c2、rep21 s1 c2、rep21 s2 c2)。
  - 指摘された16実行のRewrite後の文は、すべて「might/could need」や「if a call needed」へ弱められていた(R46 A-5)。
- **rep22のT1 4実行について、同じ正解ラベル照合は委任_47で確認中**。結果は未確定のため、本設計は数値を書かない(委任_46が生成途中に一時的に観測した所見があるが集計外で確定していない)。

### 1-5. 日本語側の事実(R43、R46)
- 日本語の**本文**はユーザーへ届かない。英語本文・Comment・Preview・Key Phraseの訳・音声・playerの本文行は英語記事(`article.md`)から作られる(R43 Q1表の行6〜8)。日本語記事は、英語記事の生成原稿(忠実英訳の入力)と、検査の「起源タグ付け」の参考入力にだけ使われる。
- 届くのは**日本語タイトルだけ**(音声のjapanese_titleセグメントとplayerの「Japanese title」行)。`derive_japanese_title`(`er019_family_x_audio_production_runner_01.py` 133〜147行)は日本語R2(`ja_writer/runtime_evidence.json`の`title`、無ければ`revision2.md`等の1行目)を入力にし、**英語記事を入力にしない**(R46 C-1)。
- 英語見出しがBLOCKING指摘に含まれた例: 厳密6行(bgroup_B4、neg1、hormuz_run03_standard)、見出しを`same_fact_id_locations`として列挙9行などを含め「見出しに触れる」のは16行/BLOCKING 346行(R46 C-2)。
- JA関連の検査費用: JA Recheck 82回=¥27.33、日英等価チェック82回=¥8.60、合計¥35.9で総費用¥257.84の約13.9%(R43 Q5)。
- Stage 4の理由は277 instance-run中40件、最多が`ja_deviation_unresolved`の**11件**(27.5%、うち10件がj1_*の書き換えを行った経路、R43 Q5)。この11件が英語だけで解消するかは未測定。
- 再生成経路(Production): 段落数retry・must-fix retry・`--regenerate-stage advanced`は日本語R2から英語を翻訳し直す(R43 Q2)。Self-Recovery Flowの結果がProductionの`ja_writer`を更新しないまま再生成が走ると、元の誤りが英語へ戻りうるが、再生成後の英語は必ず逸脱検査を通るので無言では戻らない。**現状、Self-Recovery FlowはProduction未配線**。

---

## 2. 対策A: 受け渡し修正の追補(委任_42の実装への差分、小さい順)

**結論**: A1(末尾句読点の同値変換)とA2(位置ラベル誤確定の防止)は小さく、`resolve_violation_spans`(runner 2955行)の中で完結する。A3はまとめて渡す案が実現可能で、後続指摘の`issue`が書き換えへ伝わる点でcarry-forwardより強い。A4は(a)据え置きと(b)基準変更で、(b)が安全ガードの緩和に当たるかは「ガードの目的」の読み次第(資料を§2-4に示す)。A5は実装しない。

### 2-1. A1 末尾句読点の同値変換

**何をするか**: 照合関数`vs_match_levels`(runner 2876〜2902行。現在L0=そのまま、L1=囲む引用符を外す、L2=空白・曲線引用符の同一視、L3=大文字小文字の同一視)に、最後の段階(仮にL5)として「候補文字列の**両端**の句読点(`. , ; : ! ? 。 、`)を除いた文字列が、記事内にちょうど1箇所ある」場合を確定とする照合を足す。確定範囲は、記事の文字列そのもの(文の途中までの節)。`vs_resolve_in_text`(2912行)の断片照合(L4)にも同じ関数が使われるので、断片にも効く。

**根拠(R45 §2、§4)**: 22行/3種類(U03=「…vanished overnight.」、U04=「…left the stage.」、U07=「…before recovering.」。記事側は「,」や「:」で続く)が、語を一字も落とさず、記事内ちょうど1箇所で一致する(R45の診断で3/3種類)。注意: 20行はU07の固定fixture再生で、**独立なChecker出力としては3種類**にすぎない。一般化の根拠は弱い。

**「再推測」ではなく「文字単位の同値変換」と言える根拠**: R45 §4の線引き(文字単位の同値変換=Checkerが書いた文字そのものを、記法の差だけ吸収して照合すること。再推測=似ていることを根拠に範囲を選ぶこと、または書かれていない範囲を補うこと)に当てはめる。
1. 捨てるのは両端の句読点だけで、語は1字も足さない・落とさない・置換しない。残った文字列は、Checkerが書いた語の列そのまま。
2. 候補を比べて選ぶ操作がない。「ちょうど1箇所」のみ確定で、0箇所・2箇所以上は確定不能のまま。類似度・単語重なりは使わない。
3. 範囲を文へ広げない(文単位スナップをしない)。確定範囲は記事の文字列のまま。

**言えなくなる境界(確定不能のまま人間確認に残す)**:
- 短い断片(例: 「continued」)が複数箇所に一致する場合→複数箇所一致=確定不能。
- 両端以外の句読点を除く(内部の「,」を落とす等)→しない(語の並びの変更に近づく)。
- 候補が記事内の語の途中に一致する場合(例: 「attacks」が「attacked」の途中)→**単語境界条件**を課す(一致箇所の直前直後が英数字でないこと)。既存のL0〜L3は単語境界を要求していない(substring一致)ので、新段階だけ条件を足す(これは本設計の追加提案)。
- Checkerが文を途中で切って句点を付けた場合、確定範囲は「切った位置まで」になる。Checkerの意図が後半にあった場合は範囲が縮むが、これはChecker自身が書いた範囲であり、後段が縮めたのではない。水準①で解消しなければ既存の水準③(範囲を含む文、`vs_expand_to_sentences`、runner 3022行)へ上がる。
- 記録: `level="L5"`として照合レベルを残し、除いた句読点を`handoff`に記録する(見分けるため)。

**水準との関係**: 水準①はこの節(確定範囲そのもの)を対象にする(`rewrite_ranges_ladder`、runner 3198行。①の対象==確定範囲)。①が`declined`・guard失敗なら③(範囲を含む文)、④(段落)へ既存どおり進む。⑥は既定OFFのまま。Opus#5が文単位スナップで防ごうとした「文の途中から書き換えると大文字小文字・末尾ピリオドが乱れる」リスクは、①のE1 Prompt(最小編集)と③への昇段で緩和されるが、**未測定**。

**効果の見込み(R45 §4)**: C2の同値変換を入れると、新方式で人間確認が増えるrunは22→4(U02の3 run+U05の1 run)。

### 2-2. A2 位置ラベルの誤確定の防止

**問題(R45 §2-4)**: `“In one line”`のような位置ラベルだけの文字列が、記事の見出し行(`## In one line`)に一致して「確定」になり、見出しを範囲にしかねない。記事の構造は、確認した1記事では先頭の`# タイトル`と`## In one line`の2種類の見出しだけ(`er019_output/family_x_refresh_e2e_01/meta/run_03/a2/article.md`で確認: 1行目`# …`、21行目`## In one line`。他の記事での確認は未実施)。

**現在のコードで確認した、この問題の起き方**:
- `claim_in_article`(Checkerの主たる出力)の照合: `resolve_violation_spans`(2955行)→`vs_match_levels`は**位置ラベルを特別扱いしない**。`“In one line”`はL1(囲む引用符を外す)で`In one line`となり、記事内で`## In one line`の1箇所に一致して確定する。つまり**`claim_in_article`の照合でも起きうる**。
- `same_fact_id_locations`の経路: `expand_same_fact_id_locations`(runner 1159〜1190行)が、各locationを「記事本文に逐語で実在するか」(`loc_s not in article_text`、1182行、**生の文字列でのsubstring確認**)でふるい、通ったものを独立のclaimにしてから同じ照合へ回す。引用符つきの`“In one line”`は記事本文にそのまま(引用符込みで)は無いのでここで捨てられる(R45が数えた「K2で捨てられた14件」のうち位置ラベル引用3件がこれ)。**引用符なしの`In one line`だけ**が、この事前確認を通って後段で見出し行に一致する。
- したがって、現在の実運用での露出は小さい(実LLMの出力で位置ラベル単独の引用が`claim_in_article`に出た記録は、R45の13種類にない)。ただし、**対策Bで`violation_spans`を入れ、引用符を禁じると、`expand`の事前確認(生の文字列のsubstring確認)を通る形になり、露出が増える**(§6)。

**対策案の比較**:

| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| A2-a | 確定範囲が既知の構造ラベル行そのもの(`In one line`の見出し行、前後の`#`と空白を除いて一致)なら、確定不能(理由`label_only`)にする | 小さい(確定後の1判定)。fail-closed。ラベル語彙は`In one line`の1つだけ(記事の見出しは2種類のみで、タイトル行は違反箇所になりうるので対象外) | 構造が変わり新しい見出しが増えたら更新が必要 |
| A2-b | 照合対象の本文から、`##`で始まる見出し行を除く(同じ長さの空白に置換して位置を保つ。先頭の`# タイトル`は残す) | ラベル語彙の判断が不要。他のラベルにも効く | 位置を保つマスク処理が必要。見出し行そのものが本当の違反箇所(2段目見出し)になる例は現状記録にない(R46 C-2の厳密6行は全て先頭のタイトル行) |
| A2-c | 短い文字列(例: 30文字未満)で行全体と一致するものは確定不能 | 汎用 | 短い正当な指摘(例: 短いタイトル)を弾く。**非推奨** |

**推奨(本設計の見立て)**: A2-a。実装が最小で、既存の確定不能の経路(`violation_span_unverified`)をそのまま使い、fail-closedを維持する。判断はFable・Opus。

### 2-3. A3 同じ周回に同じ範囲を指す指摘が2件あるとき

**現状(委任_42の追加機構、`carry_forward_resolution`、runner 3978〜4008行・`run_stage3_for_claim_spans` 4011〜4050行・`_run_stage3_cycle`の5248〜5268行)**: 周回ごとに、先行claimのRewriteで置換した範囲(前→後)を記録し、後続claimの文字列が現在の本文から消えていて、その範囲が先行claimのRewrite対象に含まれていたら「書き換え済み」としてRewriteせずスキップする。解消の判定は全文Recheckに任せる。

**弱点(コードで確認)**:
- 後続claimの`issue`(例: 先行は数値の誤り、後続は主体の誤り)は、Rewriteの入力に一度も渡らない。
- 「全文Recheckに任せる」の実体: 後続claimは`prior_issues`(runner 5488〜5492行は`blocking_claims`全件から作る)に残るので、Recheckは「その指摘は解消したか」を明示的に聞かれる。したがって、純粋に「Recheckの自発的な見逃し(検出率が5〜7割程度)」だけに依存するわけではない。ただし、解消していないと判定されれば**次の周回(または周回上限でStage 4)になる**。ユーザー指示§5の「なぜ複数周必要になるのかを減らす」に反する。Recheckの解消判定の精度は未測定。
- carry-forwardは、後続claimの文字列が**消えた**場合だけに働く。先行Rewriteが同じ文の別の部分だけを変え、後続claimの範囲がまだ現存する場合は、後続claimも同じ文をもう一度Rewriteする(互いの存在を知らない、順序依存)。

**代替案(まとめて渡す)**: Rewriteの前に、確定範囲が同じ(または一方がもう一方を含む)指摘をまとめ、1回のRewrite呼び出しに全部の`issue`と`rewrite_hint`を渡す。

実現可能性(コード上の確認):
1. 周回開始時の範囲は`annotate_claim_span_identity`(runner 3058行、呼び出し5079〜5080行)が既にclaimへ記録している(`span_resolution_cycle_start.ranges`、文字列のlist)。範囲は全て「記事内ちょうど1箇所」で確定した文字列なので、包含判定は文字列の包含(`r_a in r_b`)で足り、位置は不要。
2. Rewrite呼び出し`rewrite_ranges_ladder`(3198行)は、`issue`(3212行)と`rewrite_hint`(3213〜3214行)を文字列として1つ受けてPromptの`{issue}`/`{rewrite_hint}`へ入れる。**Prompt本文は変えず**、グループの`issue`を番号つきで連結した文字列、hintを連結した文字列を渡せば足りる。
3. 追加が必要な部分: グループ化関数(`_run_stage3_cycle`の前に、同言語・両立する`rewrite_kind`のclaimだけを束ねる)、結果を元のclaimごとに記録へ展開する処理(`rewrite_records`は1claim=1record、`handoff.grouped_with`を足す)。規模は見積もりで100行前後+テスト6〜8件(未実装、概算)。
4. **残る設計判断**: (a)グループ内に`delete`型と置換型が混ざる場合→束ねず、既存の経路(carry-forward)に残す。(b)グループの「問題の種類」(`classify_problem_kind`、`filter_levels_by_problem_kind`が初期水準を決める)は、メンバーのflagの和をとるか、最小水準を保つか。設計書の最小修正優先を保つなら、和のflagで既存の優先順位に決めさせるのが素直だが、意図しない昇段が起きる可能性があり、Opusに見てほしい。(c)floor claim(precheck)は、LLM claimと違い`issue`が決定論の文言(runner 5053〜5055行)。束ねても渡せる。

| 比較軸 | carry-forward(現行、委任_42) | まとめて渡す(代替) |
|---|---|---|
| 後続指摘の`issue`がRewriteに伝わるか | **伝わらない**(後続は書き換え済み扱いでスキップ) | **伝わる**(全`issue`が1回の呼び出しに入る) |
| Recheckの見逃し(検出率5〜7割)に依存するか | 後続claimは`prior_issues`に残るので明示的に聞かれる。ただし解消していないと判定されれば次周回(未測定) | 同じ`prior_issues`で全件を聞く。Rewriteが全`issue`を見ているぶん解消の見込みが高い(未測定) |
| 追加LLM呼び出し | なし(Rewrite 0回に減る) | なし。グループ内のRewrite呼び出しが1回にまとまり、むしろ減る |
| 実装の単純さ | 実装済み(小) | 新規約100行+テスト(中) |
| fail-closedか | 書き換え済みが偽でもRecheckが止める。確定不能は従来どおりStage 4 | 各対象の変化guard・主体置換ガード・Recheckは既存のまま。グループ化できない場合は既存へ戻る |
| 先行Rewriteが一部だけ変えた場合 | 後続が現存すると二重Rewrite(順序依存) | 1回で整合してRewrite |

**本設計の見立て**: Fableの考え(まとめて渡す案を第一候補)に同意。carry-forwardは、グループ化できなかった場合の安全網として残してよい(削除せず併存。どちらも既存のfail-closedを緩めない)。

### 2-4. A4 主体置換ガードの誤棄却(T2で2/2)

**ガードの現在の判定範囲(コードで確認)**:
- `actor_rewrite_guard_ok(before_text, after_text, ledger_text)`(runner 436〜441行)。Rewrite後にだけ新しく現れた主体語(`_ACTOR_NOUN_PATTERN`、423行。user(s)・employee(s)・worker(s)・staff・contractor(s)・agent(s)・executive(s)・customer(s)等)が、Ledger本文(小文字化)に**含まれていなければ**False(棄却)。
- 新方式の呼び出しは3363行: `all(actor_rewrite_guard_ok(t, r, ledger_text) for t, r in zip(targets, revised))`。**beforeはRewriteの対象範囲そのもの**(段落ではない)。したがって、T2のように水準③(範囲を含む文)で書き換えた文に`users`が現れ、`users`が**対象の文の外の同じ段落**にしか無かった場合、「新しい主体語」と数えられる。水準④(段落)ではbeforeが段落なので、同じ`users`は新規と数えられず通る(T2で④が成立した理由)。旧方式のpaired経路は3528行・3820行。
- 参考: Ledgerは日本語が主(R46 A-1)なので、英語の主体語がLedger本文に含まれる例は少なく、実質は「新しい主体語は一律棄却」に近い(**本設計の観察。含まれる頻度は未測定**)。

**導入経緯(DSG・DLをGrep)**:
- DSG §0-5(270〜274行): 「主体・対象の置換はLedgerに明示された主体・対象にのみ行う。不明な場合は対象語を削除する/一般的な表現へ弱める/元文を維持する。未確認の具体主体への置換は禁止する」。
- DSG 2363〜2368行(是正3): 「Rewrite後にのみ新しく現れた主体語(一般的な役割名詞)が、Ledger本文に一語も含まれない場合はRewriteを却下する。新しい主体語が一つも導入されていない場合(既存語の保持・削除のみ)は常にTrue」。DL 15280〜15283行: 例は`users`→`employees`(neg1 cycle2、MUSE-HC-012)で、`employees`はLedger本文に一度も出現しない。
- 委任_31 Part1(DSG 1517〜1538行): 「problem_kindに関係なく常に評価」へ変更(`changed_scope`と`changed_actor`が同時に真のとき評価されなかった盲点の是正)。その際「新しい主体語が導入されない場合は常にTrueを返すno-op設計(§0-5既存仕様)」と説明。

**選択肢**:
- (a) 変更しない: ③を棄却して④(段落)へ進む。T2では2/2で④が成立し最終的な前回指摘は解消したが、不要に段落Rewriteまで広がる(最小修正優先に反する)。広がった費用(追加LLM call 1回=③の分)と段落Rewriteの質の差は未測定。この棄却が起きる頻度は、新方式の記録(`actor_guard_rejected`)にrep22のT2の2件しかなく(旧方式は別の文言で未集計)、**一般にどれだけ起きるかは未測定**。
- (b) 「新しい主体語」の基準を、Rewrite前の同じ段落に既にある語は新規としない、に変える(beforeを対象範囲から、範囲を含む段落へ広げる)。

**(b)は安全用のガードを緩める変更に当たるか(材料)**:
- 緩めると読む材料: 設計書の文言(§0-5)は「**Ledgerに明示された**主体にのみ」で、記事にあるかどうかを基準にしていない。記事に既にある語でも、Ledgerにない語なら、「未確認の具体主体」への置換にあたる余地がある(例: 段落内に`users`と`employees`があり、`employees`の箇所を`users`に替える)。(b)はこの置換を通す。
- 緩めない(目的の範囲内)と読む材料: 禁止の中心は「記事に無い主体を持ち込む置換」(`users`→`employees`の例は、`employees`がLedgerに無いことが問題とされた)。範囲の外の同じ段落に既にある語を使うのは、新しい主体を持ち込むことにはならない、という読み。委任_31の説明も「新しい主体語が導入されない場合は常にTrue」で、「新しい」の基準(Rewrite前の何と比べるか)は文書で明示されていない(範囲か文か段落か)。
- どちらかは文書から決まらない。**判断はFableとOpus**。(b)を採る場合の中間案: 「同じ段落に既にあり、かつ主体の入れ替わりでない(範囲の中の既存の主体語を別の既存の主体語へ替えていない)」場合に限る。これは判定が複雑になる。
- Safety原則の変更に当たると判断された場合は、STOP条件(Safety原則の変更が必要)に該当しうる(§9)。

### 2-5. A5 省略記号「A ... B」(U05、1行/1 run)
実装しない(人間確認のまま)。理由: 「A ... B」を「Aの先頭〜Aの後の最初のBの末尾」と読む規則は標準解釈で決まるが、同値変換とは言い切れず(R45 §4・Opus判断項目)、該当は1行/1 run(古い固定fixture)で費用対効果が低い。

### 2-6. A6 委任_42が仕様外で判断した2点の妥当性
1. **delete型で範囲が文の一部のとき、決定論的削除の対象を範囲を含む文へ拡張**(R42 §2。`rewrite_ranges_ladder` 3255〜3281行、記録`handoff.delete_expanded_to_sentence`)。妥当性は**条件つき**。断片だけ削ると不自然な断片が残る、というコメントの理由は妥当だが、ユーザーの「最初から文全体へ広げない」の文字どおりの適用とは緊張する(Stage 2が「削除」と決めたclaimだけが対象なので、置換型より削除の意図が強い)。rep22のどのrunでこの拡張が起きたかの件数は報告にない(記録`delete_expanded_to_sentence`で¥0の集計ができる)。Fable確認事項。
2. **JA本文でのみ確定し、originが`ja_source`でない指摘は確定不能(`violation_span_unverified`)**(R42 §2、runner 4096〜4100行)。妥当。JA側を直す経路が`ja_source`のpaired経路にしかなく、無理に推測しない=fail-closed。対策D(英語だけ修正)では「JA本文は照合対象から外す」ことで、この規則がそのまま全指摘に一貫して適用される(§5)。

---

## 3. 対策B: Checkerの違反範囲の出力形式(Trial専用Prompt)

**結論**: 骨子どおり、Trial側のschemaに`violation_spans`(文字列の配列)を設け、違反範囲の唯一の情報源にする設計は実現できる。ただし(1)コードは配列を単純に文字列へ連結するだけでは既存の照合を通らないので、**配列を別フィールドとして照合関数へ渡す改修が要る**(Fable骨子への指摘、§11)、(2)必要性は「中程度」で、入れる根拠と入れない根拠の両方がある(§3-7)、(3)骨子外の代替案として「確定不能になったときだけCheckerへ返し直す(B-alt)」を併記する。委任_45のPrompt文案から「文全体を引用」の行を外し、「問題の語句だけでよい。ただし記事内でちょうど1箇所に定まる長さにする」へ置き換える。

### 3-1. 骨子の具体化(現在のコードへ当てた実現方法)
- 新しいTrial schema: `build_deviation_schema_with_enumeration`(runner 1150行)と同じ「ローカルにコピーして拡張する」手口で、`build_deviation_schema_with_spans`を足す。`claim_in_article`を`properties`と`required`から外し、`violation_spans`(`{"type": "array", "items": {"type": "string"}}`)を足す。strictモードなので全propertyをrequiredに入れる。
- 差し込み先(Trial側の既存の追記の仕組み): Stage 1初回=`stage1_fresh_with_enumeration`(1298〜1360行、Promptは1316〜1322行で組み立て、schemaは1323〜1324行)。Recheck=`run_recheck`(1504〜1573行、Promptは1520〜1528行、schemaは`build_recheck_schema`、1489〜1501行)。確認用Recheck=`run_recheck_confirm`(1667行、`build_recheck_schema_confirm` 1627行。`remaining_sentence`を別途要求する別schemaで、`violation_spans`の対象外とする)。
- コードが`violation_spans`から`claim_in_article`を組み立てる部分: 現在の`claim_in_article`の読み取りは9箇所(runner 1013、1036、1173、1185、1187、1273、1477、5041、5225行。ほかに文字列としての言及)。`claim_text`(表示・同一判定・Stage 2への表示用)は、配列の各要素を` / `で連結した**表示用文字列**にする。
- **ただし、照合には配列そのものが要る**(Fable骨子への指摘): 現在の`resolve_violation_spans(claim_text, en, ja)`(2955行)は単一の文字列を受け、複数範囲は「引用符で囲まれた断片が2つ以上あり、残りがつなぎ語・句読点だけ」(L4、`_VS_FRAG_RE`、2822行)のときだけ分解する。配列を連結した文字列は、要素が文中に曲線引用符(“ ”)を含むと断片分解が壊れる。したがって、claimへ`violation_spans`のlistを別フィールドで持たせ、`resolve_violation_spans`に`spans`引数(各要素を`vs_match_levels`でそれぞれ「ちょうど1箇所」確認する経路)を足すのが素直。この場合、**すべての要素が確定できない限り確定不能**(1要素でも不一致・複数箇所なら`violation_span_unverified`、fail-closed)。
- 固定fixture(配列が無い)のアダプタ: `violation_spans`が無いdeviationは、既存の`claim_in_article`から受け渡し修正の照合(L0〜L4+A1)で範囲を復元し、内部表現を「確定範囲のlist」に統一する。26/29 instanceはStage 1をreuse fixtureで読むので(DSG 1196行、RPT 1833行)、これが必須。
- `claim_in_article`を読むほかの経路(`same_fact_id_locations`のexpand、reuse fixtureの決定論fallback 1249〜1293行)は§3-4で扱う。
- 判定基準(何を逸脱とするか、severity、10種類のflag)は変えない。追記するPromptは「違反箇所の書き方」だけを定める。

### 3-2. Prompt文案(Trial専用の追記ブロック。実装しない)
委任_45 §5-4の文案を土台にし、**「文の一部だけが問題でも、その語句を含む文全体を引用してください」の行を採用せず、次の2行に置き換える**(ユーザーの「最初から文全体Rewriteへ広げない」に反するため):

```
- 文の一部だけが問題の場合は、その語句・節だけを引用してかまいません(文全体に広げる必要はありません)。ただし、引用は記事内でちょうど1箇所に定まる長さにしてください。同じ語句が記事内の別の場所にも出てくる場合は、前後の語を足して1箇所に定まるようにしてください(足すのは問題の語句の前後の連続した語だけで、説明や接続語は入れないでください)。
- どの語句が問題かはissueに書いてください。
```
その他の行(逐語・語の置換や省略の禁止・大文字小文字・句読点・アポストロフィ・空白を変えない・引用符で囲まない・見出しは先頭の「#」を除く・位置の説明やあなたの説明文や接続語を要素に入れない・同じ事実の複数箇所は別の要素・離れた複数箇所は別の要素・連続した複数文が1つの逸脱を構成する場合だけ連続した1要素・特定できなければ空配列でissueに理由・引用できないことを理由に報告を省略しない)は委任_45 §5-4のとおり。**引用は英語記事本文からのみ行う**ことを冒頭に1行足す(§3-5、対策Dとの関係)。

「短すぎる危険」と「長すぎる危険」のバランス:
- 短すぎる(語句だけ)→複数箇所一致=確定不能→人間確認(安全側)。同じ語句が繰り返される記事で起きる。
- 長すぎる(文全体や段落)→水準①の対象が大きくなり最小修正優先が損なわれる。Checkerが安全のため長めに引用する傾向が出ると、実質的に文全体Rewriteへ広がる(**この傾向は未測定。Trialで「引用の長さの分布」を記録して確認する**)。
- 中間(本案): 問題の語句を含む最短の連続した語列で、ちょうど1箇所に定まるもの。確定不能になったら人間確認(B-altで返し直しも可、§3-8)。

### 3-3. `same_fact_id_locations`との関係(統合か、別のままか)

**現在の使われ方(受け渡し修正後のコードで確認)**:
- Stage 1初回のみ(`stage1_fresh_with_enumeration`、Promptは`SAME_FACT_ID_ENUMERATION_INSTRUCTION`、runner 1140〜1147行)。Recheckでは委任_35で既定OFF(`run_recheck`の`enable_fact_id_enumeration=False`、1504〜1518行)。reuse fixtureは決定論fallback(1249〜1293行)で、claim_in_articleの数値・固有名詞トークンと記事内他文のキーワード重なりから候補を作る(固定fixtureのみの¥0処理)。
- 照合: `expand_same_fact_id_locations`(1159〜1190行)が、各locationを記事本文のsubstringとして実在確認し(1182行)、通ったものを`detected_by_enumeration=True`の**独立したdeviation**に展開する。以後は他のclaimと同じく、**Stage 2の判定を個別に受け**(各箇所を独立に判断する設計=重大誤解原則)、Rewriteも別々に行う。
- 実測(R45 §5-2): 「exact verbatim substring」と明示しても約6%(採用213に対し逸脱14件)が位置の説明・位置ラベルを返した。

| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| 統合 | 同じ事実の他の箇所も、その逸脱の`violation_spans`の要素にする | 配列が1つで済む。Checker出力欄が減る | 意味が変わる。`violation_spans`の全要素は**1回のRewriteで全て変えさせる**(各対象の変化guard、`rewrite_ranges_ladder`の3345〜3359行)。他の箇所は、Stage 2が個別にACCEPTABLE/QUALITY(Hook・見出しの許容等)と判定したはずのものまで書き換えを強制する→不要Rewriteの増加。委任_44が見つけた、一括適用の副作用(floor引き上げ)と同型の危険 |
| **別のまま(本設計の見立て)** | `same_fact_id_locations`は現状のまま(各箇所を別のdeviationへ展開、Stage 2が個別に判定)。ただし各locationは、A1・A2と同じ照合を通す(引用符つき・末尾句読点つきも救う) | 重大誤解原則(各箇所は独立に判断)を保つ。既存の機構を変えない | 配列が2つ(`violation_spans`=その逸脱の範囲、`same_fact_id_locations`=別の逸脱候補)。区別をPromptに明記する必要 |

### 3-4. 英語だけ修正(対策D)との関係
引用は英語記事から行うようPromptに指示する(上記冒頭1行)。日本語記事からの引用しか返らなかった場合(英語本文に一致しない): 現在の照合は、EN・JAの両本文で確定を試み、JAでだけ確定した場合に`ja_source`でなければ確定不能にする(runner 4096〜4100行)。対策Dでは、`current_ja_text`を`None`にするので(§5)、JA本文は照合対象に含まれず、英語本文に一致しない指摘は全て確定不能→人間確認(fail-closed)になる。案2として、Promptで「英語記事からのみ引用」を明示し、確定不能になった場合のB-alt(返し直し)がある。

### 3-5. Stage 1初回とRecheckの両方へ同じ形式を適用する方法・Production pathへ触れないことの呼び出し関係
- Production(er003)側: `DEVIATION_PROMPT_TEMPLATE`(502〜541行)、`DEVIATION_JSON_SCHEMA`(455〜493行)、`_apply_deviation_post_hoc_validation`(544行以降)、`build_prior_issues_instruction`(678行、`prior_issues`の`claim_in_article`を文字列に整形)。Production呼び出し側は`er003_v1_n3_01_articles_generate.py`等。**変更しない**。
- Trial側の既存の追記の仕組み(確認済み): (1)er051の`build_trial_prompt_template("V4A")`(232〜243行)は`vfl01.DEVIATION_PROMPT_TEMPLATE + TRIAL_PROMPT_DIFF_BLOCK_V01 + TRIAL_PROMPT_DIFF_BLOCK_V4A`の**文字列連結**を返すだけ(er003の定数自体は書き換えない)。(2)er051の`build_trial_deviation_item_schema`(262〜270行)は`vfl01._extended_deviation_item_schema`を土台にTrial限定5フィールドを足す。(3)runnerがその出力を**ローカルにコピーして**`same_fact_id_locations`を足している(`build_deviation_schema_with_enumeration`、1150〜1156行)。(4)Stage 1初回(`stage1_fresh_with_enumeration`)とRecheck(`run_recheck`)は、同じ`trial.build_trial_prompt_template("V4A")`に`vfl01.RELATED_FACT_ID_INSTRUCTION`、`ORIGIN_INSTRUCTION_TEMPLATE`、(Recheckのみ)`build_prior_issues_instruction`、(任意で)`SAME_FACT_ID_ENUMERATION_INSTRUCTION`を足している。
- B用の追記は、同じ位置(`prompt += ...`の直後)に、新しい定数`VIOLATION_SPANS_INSTRUCTION`を足し、schemaを`build_deviation_schema_with_spans`で差し替える形で、**Stage 1初回・Recheckの両方へ同じ関数経由で適用**できる(`build_recheck_schema`も同じ関数でラップ)。スイッチ(`CHECKER_SPANS_MODE`、既定=`off`)で`off`なら現行どおり。
- er003がProduction pathから使われるのは、er003自身の`run_deviation_check`(Family Xの検査関数の定義元、R43 Q1)。runner・er051のTrial追記はer003の`import`先を読むだけで、er003は逆にrunner・er051をimportしない(`git grep -n "er052_open233" -- "er003*.py" "er0[0-4]*.py"`=0件、R42 §1で確認済み)。この関係はB実装後も保たれる。

### 3-6. D-1・D-2・D-3の比較表(R45 §5-3を現在のコードで再確認して更新)

| 案 | 内容 | 既存コードへの影響(現在のコードで確認) | 検出への影響リスク | 固定fixture互換 |
|---|---|---|---|---|
| D-1 | `claim_in_article`の書き方だけ指定(単一文字列) | schema不変。Promptに追記のみ | 小 | 完全互換 |
| D-1b | 改行区切りで複数箇所を1文字列に | schema不変。照合側が改行で分解(区切りを守らない恐れ。引用に改行が含まれる場合がある) | 小 | 完全互換 |
| **D-2** | `violation_spans`(配列)を唯一の情報源にし、`claim_in_article`は表示用にコードが組み立てる | schema差し替え(Trial側のコピー)。`claim_in_article`の読み取り9箇所と`resolve_violation_spans`に配列経路を足す(§3-1)。`classify_parsed_result_trial`(er051 162〜178行)・`_apply_deviation_post_hoc_validation`は`claim_in_article`を読まないことを確認 | 中(出力負荷。測定要。固定fixtureの比較ができない=Stage 1の非決定性が混ざる、OP5観点6) | アダプタが必須(既存の`claim_in_article`→復元) |
| D-2b | 配列と`claim_in_article`の両方を書かせて一致検査 | 同上+一致検査 | 中。二重化はOpus#5(OP5 §5-7)の指摘に反する | 同上 |
| D-3 | 各要素を`{location_kind, quote}`に | schema・処理とも増える | 中 | アダプタ |
| B-alt(骨子外) | Stage 1・Recheckの現行schemaは変えず、**確定不能になった指摘だけ**同じCheckerへ「逐語の配列で返し直して」と1回聞く(+1call) | 照合失敗の経路に1関数足す。schema・Promptの本体は変更なし | **本体Promptを変えないので86%の指摘は影響なし**。返し直しの出力も揺れうる | 完全互換(固定fixtureをそのまま使える) |

### 3-7. 必要性の評価(入れる/入れない、両論)

| | 内容 |
|---|---|
| 入れる根拠 | (1)実LLMのRecheckが返した行8/58=13.8%が説明文混入型で、新方式なら全て人間確認に回る(R45 §3)。(2)10行(7種類)は「複数箇所のうち1箇所しか直せていない」(Stage 4が7行、降格終了が3行、R45 §3)。次周回で取りこぼした箇所が再指摘される例が多い(P3 8行、R44 §4)。(3)A1で足りるのはC2(22行)だけで、C3(12行)は受け取り側だけでは解消できない(R45 §1) |
| 入れない根拠 | (1)直近(rep17〜21、iter8、最新29件横断)の確定不能は0件、rep22も最終runで0件(R42 §5・R45 §3)。13.4%の大半(27行)は固定fixtureの再生(R45 §3)。(2)A1でC2の22行は解消見込み。残るC3は、確定不能=人間確認(fail-closed)で安全側に倒れ、費用は小さい。(3)出力形式の変更は検出を揺らしうる(OP5観点6、HO §8-2。未測定)。(4)前例`same_fact_id_locations`は明示しても約6%逸脱した(R45 §5-2)ので、受け取り側の完全一致照合は必須で、Promptだけで確定不能は0にならない。(5)固定fixtureでの比較ができなくなる(26/29がreuse) |
| 中間 | B-alt(確定不能のときだけ返し直し)。同じChecker自身への再依頼で、「別AIの引用」には当たらない。本体Promptを変えない |
| R45の判定 | 必要性「中程度」。委任_42の限定Trialと29件横断の再確認を見てから判断を推奨 |

**本設計の見立て**: 現時点の確定不能0件の事実を踏まえると、BをTrial既定にする優先度は低い。ただしC3は「複数箇所のうち1箇所しか直せない」実害の源(Stage 4 7行)なので、**(1)まずA1・A2とA3(まとめて渡す)を入れて残件数を測る、(2)残る確定不能が実LLMのRecheckで1〜2割あるなら、B-altまたはBを限定確認する**、が順当。骨子はBを対策に含めているので、設計としては両方書く(Fableが選ぶ)。

### 3-8. B-altの補足
確定不能(`explanatory_mixed`/`multi_match`/`mismatch`)のときだけ、同じCheckerに「この指摘について、記事本文からの逐語引用だけを配列で返し直す」と聞く。+1call(平均¥0.32〜0.43、R45 §4・R44 §7)に、確定不能率(Recheckで13.8%)を掛けた見込み額は1指摘あたり約¥0.04〜0.06(**見積もり、未測定**)。返し直しが空なら人間確認。

---

## 4. 対策C: 見逃しと重大度の揺れ(周回を増やさず、1周目でまとめて検出する)

**結論**: C1(全件走査のPrompt追記)は追加呼び出しなしだが、これまで一度も測っておらず、既存記録から効果を推定できない(無料推定の材料が無い)。C2(1周目の検査を2回)は、既存の記録から推定できる改善が割れていて結論が出ず(fresh Stage 1では増分0、固定Stage 1のRecheckは3組の小標本で増分あり、§4-5)、過去の不採用(2×V4-A和集合)と実質同じ機構。C3(揺れの記録)は¥0で入れてよい。C4(降格ルールの変更)は今回やらない。C5(安全側固定)は記載のみ。

### 4-1. C1(委任_44のE1) fact駆動の全件走査
- 内容: Trial専用Promptに「Verified Fact Ledgerの各factについて、記事内でそのfactに触れる文を1つずつ全て確認し、重大度を問わず列挙せよ」の手順を追記する。件数上限は無し。追加呼び出しなし(出力量が増える分の費用は未算定、基準はRecheck 1回の平均¥0.427、n=13、R44 §7)。
- **現在のChecker Promptに「全件列挙せよ」に当たる指示が無いことの確認**: `DEVIATION_PROMPT_TEMPLATE`(er003 502〜541行)の末尾は「該当するdeviationがなければ、deviationsを空配列にしてください」のみ(541行)。件数上限・優先順位・「主要な逸脱のみ」の記述も無い(R44 §5-2と一致)。er051のV01ブロック(184〜204行)は前後1〜2文の限定語・留保の確認、V4Aブロック(216〜229行)は10種類が排他的でなくflagを全てtrueにせよという指示で、いずれも「全件列挙」の指示ではない。また`same_fact_id_locations`(runner 1140〜1147行)は「**見つけた逸脱に対して**他の箇所を探す」形で、見つけられなかったHC-010には働かない(R44 §5-2)。
- 検出が増える見込み: 根拠はHC-010が固定Stage 1のRecheckで4/8回出た(R44 §3-3、R46 A-3)という小標本のみで、**効果は未測定**。
- 誤検出・書き換え・人間確認が増える危険: (1)候補が増えるとStage 2・Rewriteの費用と不要Rewriteが増える(Stage 2がQUALITY/ACCEPTABLEなら書き換えないが、判定自体に費用)。(2)**Promptへの追記が判定を変える前例**(委任_16 B-2: 共通rubricへの例示リスト追記がSafety-critical bgroup_B3の誤降格=prompt primingを起こした、R44 §7・DSG 2002〜2008行のコメントで参照)。Checker側で「全件列挙」を指示すると、MINOR級の候補が増え、`severity`を揃えるためのflag乱発(10種類を排他的でなく全てtrueにする指示、V4Aブロック)と相互作用して、**降格・floorの発火が変わる**かもしれない(未測定)。
- 出力schemaに「確認したfact_id一覧」を足して走査漏れを機械的に検査する案(R44 E1)は、B(配列形式)とは別にschema拡張が要る。Trial用のschema拡張として可能だが、今回の限定確認では**確認fact一覧はあくまでログ**(判定には使わない)に留める案を推奨(本設計の見立て)。

### 4-2. C2(委任_44のE2) 1周目の検査を2回行い、結果を合わせる(和集合)
- 内容: cycle1のCheckerを独立に2回呼び、範囲の重なりで重複を除いた和集合をStage 2へ渡す。同じ範囲・同じfactの指摘が両方にある場合の重大度は、重い方(安全側)を採る。
- 追加費用(1記事あたり、過去の単価記録): Stage 1初回1回の平均¥0.359(範囲¥0.14〜0.66、R45 §6)〜¥0.43(R44 §7)。**+¥0.36〜0.43/記事(Stage 2の追加分は別、未実測)**。既存のS1-Uは固定費約¥0.45/記事(R44 §6)。
- **過去に「2×V4-Aの和集合」が不採用になった経緯(逐語引用)**:
  - RPT 940行: 「対象7 instance(iter2でS1-U適用済み)で(a)2xV4-A union、(b)S1-D effort=medium、(c)S1-D effort=lowを比較(21 call・Y5.136、Y5 Guardrail内)。既知recall miss3件(B2_hormuz/B3/hormuz_run02_advanced)の捕捉数: 3案とも2/3(いずれか1件を取り逃す組み合わせが異なる)。負例group内の追加false BLOCK: v4a_union 2件、s1d_medium 3件、s1d_low 3件。採否条件(3件全捕捉かつ負例false BLOCK 1件以下)を満たす案は無し。よってiteration3のStage1 union構成はS1-U(effort=high、単価Y0.45/call)を維持する」。
  - DSG 5939行(別の検討、BLOCKING確定claimに限定した和集合)は「**そもそもACCEPTABLE誤判定[検出漏れ]には無効**(Stage1が見逃した場合はunion対象にすら入らない)」として検出漏れ対策として不採用。
- **今回との違い**: R44 §6は、E2は「目的と位置が違う」(当時=Stage 1がPASSの記事の見逃し、今回=2周目以降に出る指摘の前倒し)と整理した。しかし、(1)機構は同じ(2サンプルの和集合)で、(2)当時の測定は「既知recall missの全捕捉」で、今回の目的に対する効果は測っていない。(3)**既存のS1-Uは「Stage 1がPASS(deviationsが空)のときだけ+1call」**(RPT 762行以降、`run_instance`の`enable_s1u`)で、Stage 1が別のdeviation(HC-011・HC-012)を1件でも出している`meta_run03_standard`では発動しない。したがって、HC-010型の「他は見つけたが1件見逃し」には、**既存の機構は効かない**。この意味でC2は既存にない効果を狙うが、効果の根拠はHC-010 4/8という小標本の仮定(独立なら約75%、R44 E2)のみ。独立性は検証していない。
- 追加の注意: 2回のStage 1の結果を和集合にすると、Stage 2に渡るclaimが増える。1周目で同じ範囲を指す指摘が2サンプルから出ると、対策A3の「同じ範囲の指摘が増える」状況が頻発する(§6)。

### 4-3. C3(委任_44のE4) 重大度の揺れの記録
同じ範囲・同じfactの最終判定が周回間で変わったら、flag・`llm_materiality`・floor・降格の差をStage 4レコードやcycle記録に残す。¥0、判定は変えない、追加LLM呼び出しなし。実装: `run_instance`のcycleごとに、前周回の`stage2_results`と範囲(`claim_span_text`)・fact_idで突き合わせる(`find_matching_prior_record`、runner 5118行付近と同じ仕組みが使える)。Opusレビューの重い論点にならない見込みだが、構造に記録フィールドを足すので、同じレビューで確認してもらう。

### 4-4. C4 降格ルールの変更は今回やらない
- 対象: `apply_disclosure_gap_downgrade`(runner 2040〜2066行)。降格の条件の一つは、`DISCLOSURE_GAP_DISQUALIFYING_FLAGS = FLOOR_FLAGS + ["changed_scope"]`(2037行、`FLOOR_FLAGS`は452〜455行の5種類)のいずれもtrueでないこと(2044行)。P1(重大度の揺れ)の直接原因は、Checkerが`changed_scope`をtrueにするかどうかで降格が外れたり外れなかったりすること(R44 §5-4: 同じ条件を満たす82回のうち42回が降格でQUALITY、29回が`changed_scope=true`でBLOCKINGのまま)。
- E3a(`changed_scope`を降格の外す条件から外す等)は、降格を増やす=決定論的な安全ルールを緩める変更で、ユーザーSTOP条件「Safety原則の変更が必要」に当たりうる(R44 §7)。**今回は実装しない**。

### 4-5. C1とC2の比較表と、無料で推定できること

| 比較軸 | C1(全件走査Prompt) | C2(1周目を2回、和集合) |
|---|---|---|
| 検出率への効果 | **未測定**。既存記録に無し(C1のPromptは一度も実行していない) | **既存記録からの推定は小さい**(下記) |
| 費用 | 追加callなし。出力量増の費用は未算定(Recheck平均¥0.427が基準) | +1call=¥0.36〜0.43/記事+Stage 2の追加分(未実測) |
| 非決定性 | Promptが変わるので固定fixture比較が不可(fresh Stage 1のみ) | 揺れを2サンプルで平均化する効果。ただし和集合は偽陽性も合わせる |
| 人間確認・不要な書き換えへの影響 | 候補が増える→不要Rewrite・人間確認が増える危険(priming前例あり) | 同上。過去のv4a_unionは負例false BLOCKが2件増(上記RPT 940行) |
| 実装の単純さ | 小(追記ブロック1つ+スイッチ) | 中(2回呼び出し+範囲の重なり除去+重大度は重い方) |
| 過去の実績 | なし | 2×V4-Aは採否条件未達(3/3全捕捉せず2/3、負例false BLOCK+2) |

**無料の推定(既存記録のみ、R46 A-5の表を数え直した結果)**:
- **fresh Stage 1(HC-010の1周目検出)の同条件ペア**: iter5・iter6・iter7・rep9・rep11・rep12・rep16・rep18の各(s1,s2)が「同じ記事・同じ条件のStage 1を2回取った組」にあたる。8組のうち、**両方検出6組、両方未検出2組(rep16・rep18)、片方だけの組は0**。2回の和集合で検出できる組は6/8、1回の検出率は12/16=6/8。**2回の和集合で増える分は、この記録からは0**(2サンプルが、版・設定が同じ組の中でほぼ完全に一致=独立な揺れでなく版による差に見える)。注意: iter5〜12とrep16・18は版(PromptやStage 2の規則)が違うので、組の内部だけが同条件。
- **固定Stage 1のRecheck(cycle2、文が残っている状態)の同条件ペア**: iter8(s1指摘・s2指摘なし)、rep20(s1指摘・s2指摘なし)、rep21(s1もs2もcycle2では指摘なし。s1はcycle3で初出)の3組(s1・s2とも記録がある組。rep19はs1のみで組にならない)。cycle2で1回あたりに検出できたのは6件中2件(iter8 s1・rep20 s1)=33%、2回の和集合で検出できるのは3組中2組(iter8、rep20)=67%。**この小標本の範囲では、2回に増やすと検出が増える**(片方だけが検出する組が2組あり、揺れが独立に近く見える)。ただし(1)n=3組、(2)各組のcycle2の入力記事は、cycle1のRewrite結果が違うので完全に同じ入力ではない、(3)cycle3まで含めるとrep21 s1も検出されている、ため**統計的な意味はなく、期待改善の根拠にはできない**。
- **独立性の仮定(R44 E2: 1回50%なら和集合約75%)は、fresh Stage 1の記録(2サンプルが一致)では支持されない**。固定Stage 1のRecheckでは矛盾しない(2/3)が、検証にならない小標本。まとめると、無料の推定は「fresh Stage 1では増分0、固定Stage 1のRecheckでは増分あり(n=3組)」と**割れていて、結論は出せない**。
- C1の効果を推定できる既存記録は**無い**(全件走査のPromptを走らせた記録が無いため)。

**本設計の見立て**: 無料の推定からは、C2の期待改善を保証する根拠が弱い。C1は費用が安く、見逃し対策の主案として入れる価値があるが、限定確認で**悪化がないこと**(Safety対照で新しい見逃しがない、負例でfalse BLOCKが増えない)を確かめるのが先。C2は、C1の効果が不十分なときの次の段階としてよい(R44の最小組み合わせの所見と同じ)。**Opusに見てほしい**: C1とC2のどちらを先にするか、C2を既存S1-Uと統合するかどうか(§10)。

### 4-6. C5(選択肢として記載のみ)
重大度を安全側に固定する案: 同じ範囲・同じfactが**一度でもBLOCKINGになったら、以後の周回でも降格させない**(Q→B→Qの揺れを止める)。安全側だが、書き換え・人間確認が増える(P1 15行のうち「降格が外れたもの」が逆に固定される側ではなく、**降格が効いた周回でも維持される**=QUALITY扱いになっていた周回が減る)。C4の緩和ではなく**強化**の方向なので、STOP条件(Safety原則の変更が必要)に当たるのは「緩和」であって「強化」ではない、という読みが成り立つか、Opusとユーザーの確認が要る。**採否はOpusレビュー後にFableが判断**(今回は記載のみ)。

---

## 5. 対策D: 英語だけを修正する構造(Trial runner内)

**結論**: ユーザー方針(日本語は手段、LedgerとのDeviationが英語側にあるなら英語を直す)をTrial runnerで実現する切替スイッチ`JA_MODE`は、**`run_instance`冒頭で`current_ja_text = None`にする数行**でほぼ実現できる(runner 5010行)。日本語側の処理(JA Recheck・`ja_pending_deviation`・`ja_fail_open_guard`・日英等価・`paired_rewrite`・JA合流・JA precheck)は`current_ja_text is not None`を条件にしているため、迂回される。Checkerへの日本語記事の引き渡し(起源タグ用)は、`fixture["source_article_text"]`に元の日本語が残るので維持できる(D1)。削除はせずスイッチで迂回する。Production採用時のユーザー判断は§5-6にまとめ、今回のスコープ外とする。

### 5-1. 骨子の具体化
- スイッチ: `JA_MODE`(`"paired"`=現行(既定)/`"english_only"`)。`run_instance`の`current_ja_text = fixture.get("source_article_text")`(5010行)の直後に、`english_only`なら`current_ja_text = None`にする。**`fixture["source_article_text"]`は変えない**ので、Stage 1・Recheck・Stage 2に渡る起源タグ用の日本語(元の記事)は維持される(`working_fixture["source_article_text"]`は`current_ja_text`がNoneでないときだけ上書きされる、5033〜5036行)。
- english_onlyで`run_stage3_for_claim`(4153行)の`use_pairing`(`origin=="ja_source"`かつ`current_ja_text is not None`かつ`source_article_text is not None`、4156〜4160行)は常にFalse。`ja_source`の指摘も`translation`と同じく英語単独のRewrite(`single_text_rewrite`→`rewrite_ranges_ladder`)になる。JA本文は`resolve_violation_spans`へ`None`で渡るので、JAでしか確定しない文字列は`mismatch`の確定不能(fail-closed)。
- 追加が必要な小さな改修: (1)`baseline_precheck_ja`(5025〜5028行)は`fixture["source_article_text"]`から計算するので、english_onlyではスキップ(結果が使われなくなるだけで無害だが、記録をきれいにするため)。(2)`_run_stage3_spans_core`の暫定経路(4125〜4150行、`ja_provisional_path`)はenglish_onlyで通らない(`use_pairing`がFalse)。
- 英語側のRewrite・Recheck・人間確認は変えない。
- **英語見出しを書き換えた場合の記録**: Rewrite前後のタイトル行(1行目の`# …`)を比較して、変わっていたら`en_title_rewritten=True`と前後の文字列を`cycle_record`へ残す(¥0、決定論)。現在のrunnerに`en_title_rewritten`/`japanese_title`は存在しない(Grep 0件)。

### 5-2. Checkerへ日本語記事を渡し続けるか(D1/D2)

| | D1(渡す、起源タグ用。**推奨**) | D2(渡さない) |
|---|---|---|
| 測定の連続性 | 保たれる(過去のrunと同じPrompt) | 切れる。固定fixtureのStage 1と構成が変わる |
| 非決定性 | 変化なし | Promptが変わるので揺れが混ざる |
| 起源の統計 | `origin`(`ja_source`/`translation`)が取れる | 取れない |
| 日本語を理由にした再指摘の揺れ(R43 Q6: コード・Promptからは確認できず、実測未確認) | 残りうる(古い日本語が渡り続ける) | 消える |
| Stage 2への影響 | `er052_open233_self_recovery_stage2_production_01.py`は`source_article_text`と`origin`をStage 2のPromptへ渡す(67・76・94行、235〜282行)。変化なし | 「(なし)」に変わり(240行、282行)Stage 2の判定が変わりうる→Stage 2を含む全体の非決定性が増す |

**`origin`の値が後段のどこで使われているか(english_onlyにした後も必要か)**: (1)`use_pairing`の条件(runner 4157行)=english_onlyでは不要。(2)`_run_stage3_spans_core`のJA本文でのみ確定した場合の分岐(4096〜4100行)=english_onlyではJA本文を渡さないので不要。(3)次周回へのJA指摘合流で`origin="ja_source"`を付ける(5618行)=english_onlyでJA Recheckを行わないので不要。(4)`llm_claims`の`origin`(5041行)と`claims_for_second`(2276行)でStage 2へ渡る=Stage 2のPromptに載る参考情報で、判定に使われうる。(5)集計・記録。**したがって`origin`の値自体はenglish_onlyでも残す**(Stage 2の入力と起源の統計のため)。

### 5-3. 日本語記事からの引用しか無い指摘(英語本文に一致しない)の扱い
- 案1: 確定不能→人間確認(fail-closed)。english_onlyで自動的にこうなる(JA本文を照合に渡さない)。
- 案2: 対策BのPromptで英語から引用させる(§3-2)。確定不能は、B-alt(§3-8)で返し直せる。
- 両方の併用が自然。案1が最終的な安全網。

### 5-4. 外す処理の一覧(関数名・呼び出し箇所・影響を受けるテスト件数の概数)

テスト件数は`er052_open233_self_recovery_flow_runner_01_test_01.py`(4768行、`def test_`381件、`class Test`95件)に対する、名前のGrep(一致した**行数**、概数)。呼び出し側の関数単位の迂回であり、削除しない。

| 外す処理 | 関数名 | 定義行 | 呼び出し箇所(runner) | english_onlyでの迂回方法 | 名前を含むテスト行数(概数) |
|---|---|---|---|---|---|
| ペア書き換え | `paired_rewrite` | 3618 | 4113(`_run_stage3_spans_core`)、4170(legacy) | `use_pairing=False`(4156〜4160行。`current_ja_text`がNone) | 24 |
| JA対応箇所の推定(5段) | `locate_ja_counterpart_by_position`(+`locate_best_sentence`等) | 2561(2305) | `paired_rewrite`の3676・3690 | `paired_rewrite`が呼ばれない | 2 |
| JA Recheck | `run_recheck`(JA本文を渡す側) | 1504 | 5503〜5506 | `current_ja_text`がNone(5503行の条件) | 2(`ja_recheck`) |
| JA未解決フラグ | `ja_pending_deviation` | (変数、5019) | 5019、5095、5478、5550 | JA Recheckが無いので常にFalse | 3 |
| JA未解決のStage 4理由 | `ja_deviation_unresolved` | — | 5096〜5097 | 発火しない | 3 |
| JA fail-openガード | `ja_fail_open_guard`(+`is_predominantly_ja`、`split_ja_sentences`) | 4383(2495、2482) | 5387、5454〜5463 | `ja_text_before_rewrite is not None`が偽(5386行の条件) | 7+4 |
| JA/EN等価チェック | `run_ja_en_equivalence_check` | 1064 | 5425 | `current_ja_text is not None`が偽(5424行の条件) | 0(名前なし。gating側が7) |
| 等価の判定への反映 | `resolve_ja_ok_after_equivalence_gating` | 4314 | 5525 | JA Recheckが無いので`ja_ok=True`固定 | 7 |
| JA指摘の次周回への合流 | (インラインの処理) | — | 5609〜5621 | `ja_recheck_parsed is None`なので入らない(5609行の条件) | 0(名前なし) |
| JA側precheck | `baseline_precheck_ja`、`rewrite_new_findings_ja` | — | 5025〜5028、5411〜5414 | スキップ(小改修) | 0(名前なし) |
| 全文Recheck要否のJA引数 | `full_recheck_required`の`ja_guard_ok`/`ja_equivalence_verdict` | 4235 | 5447〜5450 | JA結果が`None`で渡る | (他テストと共通) |
| 暫定経路(JA暫定) | `_run_stage3_spans_core`の4125〜4150行 | 4053 | 4112〜4150 | `use_pairing=False`で通らない | 受け渡し修正のテスト群(51件の`span_unverified`等)の一部 |

(参考: 新方式の受け渡し関連のテストは`span_unverified|resolve_violation_spans|vs_`で51行、`carry_forward|collect_replaced`で6行、`@_legacy_handoff`/`HANDOFF_MODE`で15行。)

条件(骨子どおり): 削除ではなくスイッチで迂回する。**既定は`JA_MODE="paired"`**で、既存のテスト(381件)と旧方式(`HANDOFF_MODE="legacy"`)が動き続けること。english_only用のテストは新規に足す(§6-3)。

### 5-5. Production正式pathへ触れないこと(呼び出し関係)
`JA_MODE`はrunner内の定数でありProductionに存在しない。english_onlyで外す処理は、すべてrunner内の関数で、er003・er012・er019等のProductionコードからは呼ばれない(R42 §1の`git grep -n "er052_open233" -- "er003*.py" "er0[0-4]*.py"`=0件)。

### 5-6. Production採用時に必要になるユーザー判断(今回のスコープ外)
- **日本語タイトル**: 英語見出しだけを直すと、日本語タイトルに誤りが残る経路が成立する(`derive_japanese_title`が英語記事を入力にせず、`runtime_evidence.json`の`title`が優先、R46 C-1・C-4)。実害の実例は2系統(Meta Muse見出しの「前提」、hormuzの「原油高」)で、いずれも現行の正解ラベルでは許容側の読みがある(R46 C-3)。これを防ぐ対策は**Production正式pathの変更が必要**なので今回やらない。R46 C-4の候補(逐語引用):
  1. 「英語見出しを書き換えた記事のみ、日本語タイトルを英語見出しから作り直す: LLM要(翻訳または生成1回)/Production変更要(`derive_japanese_title`の入力変更と呼び出し側)」
  2. 「英語見出しを書き換えた記事は日本語タイトルを人間確認へ回す: LLM不要/Production変更は不要の可能性が高い(Trial側のフラグで止める運用なら)。ただしProductionへ接続するなら停止点の追加が必要」
  3. 「日本語タイトル(`runtime_evidence.json`の`title`)に、JA側のfact-check(`ja_writer`の既存deviation check)を適用済みかを確認し、未適用のrunだけ適用: 既存機構の再利用でLLM要(1回)/Production変更は要確認」
  4. 「英語見出しは見出し専用の最小Rewrite(見出しのみ)に限定し、日本語タイトルは触らず記録だけ残す(ユーザー原則「日英整合だけを理由に日本語へ遡らない」に沿う): LLM不要/Production変更不要。ただし実害は残る」
  5. 「英語見出しをRewrite対象から外す(見出しは指摘対象外、または見出し専用の事前Checkへ): LLM不要/Trial runner側の変更のみ(Production変更不要)。ただし本文の同じ誤りは別途拾う必要がある」
  - 本設計での扱い: Trialでは候補4(記録だけ残す、`en_title_rewritten`)を採る。どの候補を採るかは、日本語タイトルをLedger逸脱として扱う基準を先に決める必要がある(R46 C-4)。
- **承認済みの仕様との関係**: SPEC 1272行付近(項目6「新記事構造(途中Heading廃止・**忠実英訳**・段落境界3分割…」、`APPROVED_FOR_PRODUCTION`)=英語Advancedは日本語R2の忠実英訳。英語だけを直せば英語は日本語R2の忠実な訳でなくなる。SPEC 1242行(項目5「ja_source MAJOR時の暫定retry拡張(**案B**、`APPROVED_FOR_PRODUCTION`)」)=ja_sourceのMAJORで英語を盲目的に再生成せず、JAをOriginal段へ差し戻し1回。今回のユーザー指示(日本語は手段)はこれらを緩める方向で、Production化の前にユーザーの明示判断が必要になる見込み(R43 §8)。**今回は実装しない・判断しない。**
- **再生成経路**(R43 Q2、案A1〜A3): Production組み込み時に「再生成後も必ずSelf-Recovery Flowを通す」(A1、追加コード小)等。組み込み前に決める。
- Opus#1論点4「audioはEN/JA双方から作られる」は、日本語タイトル以外は現行の音声経路に一致しない(R43 Q1、§4)。

---

## 6. 実装順序・相互作用・切替

**結論**: 実装の順序は D → A(A1、A2、A3)→ C3 → C1 → B(必要なら)→ C2(必要なら)。BとA1・A2は「配列が入っても残る」関係で、Bを入れてもA1・A2は不要にならず、むしろA2の重要度が上がる。すべてスイッチで切り替え可能にし、既定値は現行のまま。

### 6-1. 依存関係・相互作用
- **Bを入れるとA1・A2の必要性が変わるか**: A1は残る(i)固定fixtureアダプタ(26/29はreuse)が`claim_in_article`から範囲を復元する、(ii)Bの配列でもCheckerが末尾句読点を付ける例が残りうる(前例の逸脱6%)。A2は**重要度が上がる**(§2-2): Bで引用符を禁じると、`expand_same_fact_id_locations`の事前確認(生の文字列のsubstring確認)を通る形になり、位置ラベルが見出し行に一致しやすくなる。
- **DとBの引用言語**: Bは英語記事からの引用を指示する。Dはenglish_onlyで日本語本文を照合に使わない。日本語からの引用しか返らなければ確定不能→人間確認(§3-4、§5-3)。**両方入れると整合する**(Dを先にすれば、Bの有無に関わらず日本語経路がない)。
- **A3とC2**: C2(1周目を2回)で2サンプルの和集合を作ると、同じ範囲を指す指摘が増える。A3(まとめて渡す)を先に入れておくと、C2のための前提が整う。逆にC2だけ入れてA3を入れないと、carry-forwardのスキップが頻発して、後続指摘の`issue`が書き換えに伝わらない。
- **A1とA3**: A1で確定できる指摘が増えると、同じ範囲を指す指摘も増えうる(A3の前提がよく満たされる)。
- **C1とB**: どちらもCheckerのPrompt・出力を変える。同時に入れると原因を分けられないので、限定確認は別々の腕で行う(§7)。
- **DとA3**: english_onlyならJA側の対応を考えなくてよく、A3のグループ化は英語だけで済む(単純になる)。

### 6-2. 切替スイッチ(すべてTrial既定=現行のまま)

| スイッチ | 値 | 既定 | 備考 |
|---|---|---|---|
| `HANDOFF_MODE`(既存) | `violation_span`/`legacy` | `violation_span` | 変更しない |
| `JA_MODE`(新設) | `paired`/`english_only` | `paired` | 5節 |
| `SPAN_MATCH_EDGE_PUNCT`(A1) | on/off | off | 既定offなら現行どおり |
| `SPAN_LABEL_GUARD`(A2) | on/off | off | 同上 |
| `GROUP_SAME_RANGE_CLAIMS`(A3) | on/off | off(carry-forwardが現行) | 同上 |
| `CHECKER_SPANS_MODE`(B) | off/schema/retry(B-alt) | off | 同上 |
| `FULL_SCAN_INSTRUCTION`(C1) | on/off | off | 同上 |
| `STAGE1_DOUBLE_SAMPLE`(C2) | on/off | off | 同上 |
| `SEVERITY_FLIP_LOG`(C3) | on/off | on(¥0・判定不変)でもよい | 記録のみ |

固定fixtureとの互換: 配列が無い固定fixtureはアダプタで`claim_in_article`から範囲を復元する(§3-1)。新スイッチがoffなら、既存の381件のテストが無変更で通ることを実装の条件にする。

### 6-3. 必要なテストの一覧(実例ベース)
- **A1**: R45のU03・U04・U07(それぞれ末尾句読点を除いて記事内1箇所→確定)、短い断片が複数箇所に一致する場合は確定不能、単語の途中に一致する場合は確定不能(単語境界)、両端以外の句読点は除かない、U05(省略記号)は確定不能のまま、U01・U02・U06・U08〜U13(説明文混入)は確定不能のまま。
- **A2**: `In one line`単独(引用符あり・なし)が`label_only`の確定不能になること、タイトル行(`# …`)への正当な指摘は影響を受けないこと、`same_fact_id_locations`のexpand経由・`claim_in_article`直接の両方。
- **A3**: T3の同一範囲2指摘(LLM claim+precheck floor claim、「more than 30 million」)で1回のRewrite呼び出しに両方の`issue`が入ること、包含関係(短い範囲が長い範囲に含まれる)、`delete`型と置換型の混在はまとめないこと、グループのRewriteが全対象の変化guardと主体置換ガードを通ること、グループ化できないときcarry-forwardへ戻ること、`rewrite_records`が元のclaimごとに残ること。
- **A4**: T2の主体置換ガード(範囲の外・同じ段落の`users`)。(a)据え置きなら③棄却→④成立、(b)なら③成立。`users`→`employees`型(Ledgerにも記事にも無い語)は(b)でも棄却されること。
- **B**: `violation_spans`の配列が各要素「ちょうど1箇所」で確定、1要素でも不一致なら確定不能、空配列は確定不能(人間確認)、配列が無い固定fixtureのアダプタ、連結文字列に曲線引用符が含まれる要素、日本語だけの引用は確定不能。
- **C3**: 同じ範囲・同じfactの最終判定が周回間で変わったら記録されること、判定自体は変わらないこと。
- **D**: `JA_MODE="english_only"`で`paired_rewrite`・JA Recheck・`ja_pending_deviation`・`ja_fail_open_guard`・等価チェックが呼ばれないこと、`ja_source`の指摘が英語単独のRewriteになること、JA本文でのみ確定する文字列が確定不能になること、`origin`と`source_article_text`がStage 1・Stage 2へ渡り続けること(D1)、英語見出しの書き換えで`en_title_rewritten`が記録されること、**既定(paired)で既存の381件が通ること**。

---

## 7. 限定確認の設計(実行しない。設計だけ)

**結論**: 予算は残り¥105.97。(i)対策の限定確認(概算¥36〜49)と(ii)29件横断の再確認(過去実費¥25.0〜39.5)は、(ii)を1回ならまかなえる。(ii)を上限額で2回回すと不足する。比較は「対照(現行)と処置を同じ記事・同じLedger・同時期に取る」形で、処置を一度に全部入れずに分ける。判定は「悪化しないこと」を主に置く(サンプル数が小さく、改善の有意差は出せない)。

### 7-1. 過去の29件横断の実費(RPT)
| 回 | 内容 | 実費 | 出所 |
|---|---|---|---|
| iter7 | 29 instance全量(9 instanceがn=2、計38 instance-run) | ¥39.5475 | RPT 1721行・1754行以降、2847行付近(後のiter8の比較表3041行) |
| iter8 | 29 instance全量(同じ38 instance-run、現行既定構成) | ¥24.9738 | RPT 2847行・3041行(「総コスト ¥39.5475 → ¥24.9738(改善)」) |
| 参考 | 平均¥0.6975/instance-run(iter8)、iter7は¥1.0407 | | RPT 2819行 |
| 参考 | rep22 T1(固定Stage 1、meta、n=4) | ¥5.6241(1 runあたり約¥1.41) | R42 §1 |

(ii)は、最新版(実装後)の29件横断を想定して**¥25〜40**(iter8〜iter7の範囲)と見積もる。注意: 対策Bを入れて全記事でStage 1をfreshにすると、iter8のSafety12は構造上reuseだった(RPT 2840行付近、DSG §7-0-iter32)のでiter8の額よりも高くなる可能性がある(未測定)。DによってJA関連の検査費(総費用の約13.9%)は減る見込みで、費用は下がる方向。

### 7-2. 予算の逆算
- 残額 ¥105.97(R42 §1、Phase累計¥494.0300/総枠¥600)。
- (ii)を1回、上限額¥40で見積もると、(i)に使える上限は ¥105.97−¥40=**¥65.97**。iter8並み¥25なら¥80.97。
- (ii)を2回(再実行)上限額¥40×2なら、(i)の上限は ¥105.97−¥80=**¥25.97**。iter8並み¥25×2なら¥55.97。
- なお、(ii)の後の「実記事N増し」の費用はここに含めていない(未算定)。

### 7-3. 測るもの
- ユーザー指示§3の5項目(逐語): 「特定不能率」「検出漏れ」「false PASS」「出力失敗」「Human Reviewへの影響」。
  - 特定不能率: 新方式(A1・A2込み)での確定不能÷BLOCKING指摘数。素の逐語率(正規化なし)も併記。
  - 検出漏れ: 正解ラベルでBLOCKINGとされるfact(DSG §7)を、BLOCKINGで検出できなかった率。
  - false PASS: 正解がBLOCKINGの記事で、結果が全MINOR/空になった率(Stage 1単体)。全フローでの最終PASSは別途。
  - 出力失敗: JSON/schema失敗、API失敗、MAJORなのに`violation_spans`が空の率。
  - Human Reviewへの影響: Stage 4に回る割合(実フローで測る、オフライン再計算も可)。
- 正解ラベルに対する「**Safety-criticalな文が残ったまま人間確認なしで終了**」の数(MUSE-HC-010のMeta-1等。`SAFETY_CRITICAL_CLAIM_DEFS`(5659行)と、委任_46の`check_01.py`と同じ照合を使う。¥0)。委任_47がrep22のT1 4実行を同じ照合で確認中。
- 周回数、成立した水準(①③④)、Stage 4理由の分布、費用。

### 7-4. 比較の組み方(2案以上)
共通: **同じ記事・同じLedger・同時期に、対照(現行)と処置を交互に取る**。対照どうしの揺れ幅を先に測り、処置と対照の差が揺れを明確に超えたときだけ「処置の影響」とみなす(R45 §6)。比較はfact_id単位(`claim_in_article`の文字列ではなく)。単価: Stage 1初回¥0.359(範囲¥0.14〜0.66、R45 §6)、Recheck¥0.322(R45 §6)・平均¥0.427(R44 §7)、固定Stage 1のflow 1 runあたり約¥1.0〜2.2(R42 T1、R44 §7)、worst instance(safety_A4)は¥4.5〜9.0(RPT 1829・1855行、R45 §6)。**サンプルが小さいので、改善の有意差は検出できない。判定は「Safety対照に対照にない見逃しが出ないか」「HC-010の検出が対照より悪化しないか」の悪化検出に限る**。

**案X(Stage 1単体、3腕。推奨の第一段階)**
- 対象記事8種: 問題記事5(`meta_run03_standard`、`hormuz_run03_standard`、`neg1_meta_b3prod_a2`、`bgroup_B4`、`safety_A4`)+Safety対照3(`safety_A2A3`、`safety_A5`、`safety_er009_*`から1種)。
- 3腕: 対照(現行V4A+列挙)/処置B(`violation_spans`)/処置B+C1(+全件走査)。
- n=3(`meta_run03_standard`はHC-010の検出が焦点なのでn=5)。呼び出し=(7記事×3+meta 5)×3腕=78 call。費用≈¥0.359×78=**¥28.0**(範囲¥10.9〜51.5)。
- C2は、**対照の2サンプルから追加呼び出しなしで模擬**する(2サンプルの和集合をオフラインで計算)。費用¥0。
- 長所: 原因が分かれる(B単独とC1の追加分が比較できる)。短所: Stage 1だけでは、書き換えと人間確認への影響(5項目の最後)は測れない。

**案Y(Stage 1+代表記事のflow、2腕)**
- Stage 1: 同じ8記事、2腕(対照/B+C1)、n=3=48 call、≈¥17.2。
- flow(全周回を実行): 代表3記事(`meta_run03_standard`、`hormuz_run03_standard`、`safety_A4`)×2腕×n=2=12 flow-run。1 runあたり¥2を目安(`safety_A4`は¥4.5を超えうる)に≈¥24(範囲¥17〜40)。
- 合計≈**¥41**(範囲¥30〜60)。長所: Human Review・周回数・成立水準まで見える。短所: BとC1が混ざる(分離不能)。
- 組み合わせ: 案Xを先に行い、悪化がなければ案Yのflowだけを足す2段階(合計¥28+¥24=¥52、範囲¥35〜75)も可。

**D(対策D)の確認(上記とは独立、案X・Yに足す)**
- 固定Stage 1(`meta_run03_standard`、rep22 T1と同じ)をenglish_onlyでn=4(≈¥5.6)、T2再現(Stage 3以降)n=2(≈¥2.0)。合計≈**¥8**。Dは決定論的な構造変更で、固定Stage 1を使えるため揺れが混ざりにくい。比較は旧方式(`paired`)のrep22 T1・T2の記録をそのまま使える(新規のpaired腕は不要)。

### 7-5. 予算の収まり(Fableへの報告事項)
| 組み合わせ | (i)の概算 | (ii)1回(¥25〜40) | (ii)2回(¥50〜80) |
|---|---|---|---|
| 案X+D | 28+8=**¥36**(範囲¥19〜60) | 残¥105.97−36=69.97 → **収まる**(余裕¥30〜45) | 69.97−80=−10.03(上限額で不足¥10)/−50=+19.97(iter8並みなら収まる) |
| 案X→Yの2段階+D | 52+8=**¥60**(範囲¥43〜83) | 45.97 → **収まる**(余裕¥6〜21、上限額でぎりぎり) | 45.97−80=**−34.03(不足¥34)**/−50=−4.03(iter8並みでも不足¥4) |
| 案Y+D | 41+8=**¥49**(範囲¥38〜68) | 56.97 → **収まる**(余裕¥17〜32) | 56.97−80=**−23.03(不足¥23)** |

- **(ii)を1回ならすべての組み合わせで収まる。(ii)を再実行が必要になる(2回)と、上限額では不足する**(案X+Dで不足¥10、案Yで¥23、案X→Yで¥34)。
- 注意: 費用の範囲は単価の範囲(¥0.14〜0.66等)に基づく見積もりで、**実測ではない**。「実記事N増し」の費用は含まない。
- **ユーザーSTOP条件「¥600予算上限超過が必要」に関わる**ため、Fableへ必ず報告する(§9)。限定確認(i)を案X+Dに絞れば、(ii)が1回で済む想定では余裕がある。

### 7-6. 合否の基準案(Fableが決めるための案)
**REJECTED(その処置を入れない)の例**:
- Safety対照(`safety_A2A3`、`safety_A5`、`safety_er009_*`)で、対照に無い見逃し(false PASS、BLOCKINGの検出漏れ)が1件でも出る。
- `meta_run03_standard`のMUSE-HC-010の1周目検出率が、対照より下がる(n=5での悪化)。
- 負例(正常な記事)で、false BLOCKが対照より増える。
- `violation_spans`の確定不能率が現行の13.4%を下回らず、かつ出力失敗(JSON/schema/空配列)が増える(Bのみ)。
- english_only(D)で、Safety-criticalな文が残ったまま人間確認なしで終了する数が、旧方式のrep22/rep21並みの記録より増える。

**VALIDATED(Trialで有望、Production採用ではない)の例**:
- 上記のREJECTED条件に1つも当てはまらない。
- かつ、少なくとも次のどれかが成り立つ: HC-010の見逃し(「残ったまま・未指摘・人間確認なし」)が対照より減る、周回数が減る、`ja_deviation_unresolved`型のStage 4が消える(D)、確定不能率が下がる(A1・A2・B)、不要Rewriteが増えない。
- VALIDATEDでもProduction採用ではない(ユーザー指示§8)。**サンプルが小さいことを報告に必ず書く**。

---

## 8. 残るリスク・未確定点

1. **正解ラベルの前提**: MUSE-HC-010をBLOCKING(Safety-critical)とするのはFableの設計書側(DSG V4原則)で、Ledgerと記事の突き合わせでは「判断が分かれる」(R46 A-4)。見逃し対策の効果は、この正解ラベルに依存する。
2. **C1・Bの効果は未測定**。C2の期待改善は既存記録から推定すると割れていて結論が出ない(§4-5)。
3. **Stage 1の非決定性**: BとC1はPromptを変えるので固定fixtureが使えず、揺れが混ざる(OP5観点6)。限定確認は、対照どうしの揺れ幅を先に測る。
4. **A3のグループ内の問題種類の決め方**(§2-3の(b))、**A4の読み**(§2-4)は設計判断が残る。
5. **Dの未確認事項**(R43 §9): 日本語タイトルにLedger逸脱が実際に入ったことがあるか(R46 C-3は2系統で「入っている」と判定したが、逸脱として扱うべきかは別)、`ja_deviation_unresolved`の11件が英語だけで解消するか、Production組み込み後の再生成頻度、古い日本語を理由にChecker/Stage 2が揺れる実測(未確認)。
6. **rep22のT1 4実行の正解ラベル照合**は委任_47で確認中(本設計は数値を書いていない)。
7. **費用**: (ii)を再実行すると予算が不足する(§7-5)。「実記事N増し」の費用は未算定。
8. **新しい構造の副作用**: A3のグループ化と、Dの`current_ja_text=None`は、`run_instance`内の多数の条件分岐に波及する。既存の381件で回帰を確認し、新スイッチoffでの無変更を条件にする。
9. 受け渡し修正の最終分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はFable未実施(R42)。`carry_forward_resolution`の追加機構もFable確認待ち。
10. 周回ごとの新規指摘(P2、40%)の対策C1・C2はいずれも「周回を増やさない」ための前倒しであり、効果が出ない場合でも周回上限は引き上げない(ユーザー指示§5)。

---

## 9. ユーザーのSTOP条件への該当性(6条件)

| # | 条件(ユーザー指示§8) | 判定 | 理由 |
|---|---|---|---|
| 1 | 新しいProduct原則の採用が必要 | 非該当 | Trial内の構造と出力形式の変更で、新しいProduct原則は不要。D(日本語は手段)はユーザーが既に示した方針で、Trial runner内の迂回。Production採用時の日本語タイトルの扱いは新しい判断になりうるが、今回のスコープ外(§5-6) |
| 2 | Safety原則の変更が必要 | **要注意** | C4(降格ルール変更)は今回やらない。A4の(b)案(新しい主体語の基準変更)が、ガードを緩める変更に当たるかの読みが分かれる(§2-4)。(a)据え置きなら非該当。C5(安全側固定)は強化方向で、緩和ではない |
| 3 | Production正式仕様の変更判断が必要 | 非該当(今回の範囲)/Production採用時は該当 | 全てTrial runner内。Production採用時は「忠実英訳」(SPEC 1272行)・案B(SPEC 1242行)・日本語タイトル・Checker出力契約(violation_spans)の変更判断が要る(スコープ外) |
| 4 | ¥600予算上限超過が必要 | **要注意** | (i)+(ii)は(ii)を1回なら残¥105.97に収まる。(ii)を上限額で再実行すると¥10〜34不足(§7-5) |
| 5 | Claude案とOpusレビューが重要点で対立し、Fableで解消できない | 判定不能(未レビュー) | Opusレビュー前。Opusが対立しうる論点は§10 |
| 6 | 複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要 | **要注意** | C1(安価・効果未測定)対C2(+¥0.4/記事・過去に不採用)、Bを入れる(検出への影響が未測定・確定不能を減らす)か入れない(0件のうちは不要)か。QCDの差が「明確」になるかはOpus・限定確認の結果次第 |

---

## 10. Opusに特に見てほしい論点(10項目)

1. **A3の2案**: carry-forward(現行)と、まとめて渡す案の比較。グループ内の問題種類(`classify_problem_kind`)の決め方(§2-3)。carry-forwardを併存させてよいか。
2. **A4(b)がガードの緩和に当たるか**: 「新しい主体語」の基準(§2-4の材料)。当たる場合の扱い。
3. **Bの必要性**: 確定不能が直近0件の下で入れるか(§3-7)。B-alt(確定不能のときだけ返し直し)で足りるか。
4. **配列を唯一の情報源にする是非**(`claim_in_article`を表示用に降格、照合経路を別フィールドで持つ)。二重化を避けつつ、26/29のreuse fixtureとの共存。
5. **`same_fact_id_locations`との統合**: 統合すると「全要素を1回で全て書き換える」意味になり、各箇所の独立判断(重大誤解原則)が損なわれないか(§3-3)。
6. **C1対C2**: どちらを先にするか。C1のpriming危険(委任_16 B-2の前例)、C2と既存S1-U・過去の不採用との関係(§4-2・§4-5)。
7. **C5**: 重大度の安全側固定(降格の禁止)を、強化方向としてSTOP条件に当たらないと読めるか。採るか。
8. **Dの切り方**: `current_ja_text=None`で迂回する方式が、`run_instance`の条件分岐のどこかに副作用を残さないか。D1(JAをCheckerとStage 2へ渡し続ける)でよいか。英語見出しの書き換えの記録だけで十分か(日本語タイトルの再作成はProduction変更なので今回外す)。
9. **限定確認の組み方**(§7-4): 案X(Stage 1単体3腕)を第一段階にしてよいか、C2を「対照の2サンプルから模擬」で足りるか、対照どうしの揺れ幅の使い方、サンプルが小さい下での合否基準。
10. **予算**: (ii)を2回回す場合の不足(§7-5)を、どう防ぐか(限定確認の範囲を絞る等)。

### 10-2. OPUS_INDEPENDENT_REVIEW_BLOCKの12観点への自己点検(Opusが独立に答える材料の場所)
| 観点 | 本設計の該当箇所 |
|---|---|
| 1 そもそも必要か | A1・A2=小さな追補で必要性の根拠あり(§2)。Bは必要性「中程度」で両論(§3-7)。C1・C2は効果未測定(§4)。Dは実害確認済みの範囲で必要性あり(§5、R43) |
| 2 より単純な構造 | B-alt(§3-8)、Dは`current_ja_text=None`の数行(§5-1)、A3の併存(§2-3) |
| 3 既存処理・既存データの利用 | A1は既存L0〜L3の延長、A3は`span_resolution_cycle_start`・既存Rewrite Promptの再利用、C3は既存の`find_matching_prior_record`相当、無料推定は既存記録(§4-5) |
| 4 前段の情報の喪失・再探索 | A3(後続指摘の`issue`が伝わらない=前段の情報の喪失、§2-3)、B(Checkerの範囲をそのまま使う) |
| 5 不要なLLM処理 | 追加呼び出しはC2(+1)とB-alt(確定不能のときだけ+1)のみ。A3はむしろ呼び出しを減らす |
| 6 非決定性 | B・C1はPromptを変える→固定fixture比較不可(§3-6、§8-3)。限定確認で対照の揺れ幅を先に測る(§7-4) |
| 7 Human Review | A1・A2は確定不能を減らす/label_onlyで増やす(§2)。D(`ja_deviation_unresolved`11件の消滅見込み、未測定)。C1・C2は人間確認が増える危険(§4) |
| 8 不要Rewrite | A3はグループで1回にまとめる。C1・C2の候補増(§4)。A4(a)は段落Rewriteまで広がる(§2-4) |
| 9 コスト | §7 |
| 10 retry・fallback・regeneration | `MAX_CYCLES`・`HARD_MAX_CYCLES`・⑥既定OFF・`ja_pending_deviation`相当(D以外)は変更しない。carry-forwardは併存 |
| 11 Failure時に安全側 | 確定不能・空配列・label_only・JAのみ確定は全て人間確認。A4(b)は読みが分かれる(§2-4)。C5は強化方向 |
| 12 再発防止か | 受け渡しの追補(A1〜A3)は個別バグの連続ではなく、確定範囲を使う設計の延長。ただしOP5が指摘した「周回ごとの新規指摘の揺れ・重大度の揺れ・JA/EN対応」の3つのうち、後2つに対応するのがC・Dで、構造的原因(Recheckが単発のChecker呼び出しである点、R44 §5-1)への対策はC1・C2 |

---

## 11. Fable骨子への指摘(骨子の無理・矛盾・見落とし)

骨子は黙って変えていない。以下は指摘であり、骨子の設計はそのまま§2〜§7に書いた。

1. **B(配列からコードが`claim_in_article`を組み立てる)の見落とし**: 現在の`resolve_violation_spans`(runner 2955行)は単一の文字列を受け、複数範囲は曲線引用符の断片(L4、`_VS_FRAG_RE`)だけで分解する。配列を連結した文字列は、要素が曲線引用符を含むと壊れる。**照合関数が配列を別引数で受ける改修が必要**(§3-1)。骨子の「既存処理へ渡す」はこの改修を含めて読む必要がある。
2. **Bの効果は固定fixtureで測れない**: 26/29 instanceはStage 1をreuse fixtureで読む(DSG 1196行、RPT 1833行)。Bの効果は、fresh Stage 1でしか測れず、Stage 1の非決定性が混ざる(OP5観点6)。骨子は「固定fixtureはアダプタで読む」としているが、**アダプタが担保するのは互換性であって効果の測定ではない**。限定確認(§7)は、対照と処置を同時期に取り、対照どうしの揺れ幅を先に測る形にした。
3. **C2は既存のS1-Uと過去の不採用実績に重なる**: 骨子は「過去の不採用との違いがあるかどうか」を求めた。結論: 機構は同じ(2サンプルの和集合)で、過去の測定条件(既知recall miss全捕捉、負例false BLOCK≤1)に対して2/3・+2件で未達(RPT 940行)。今回の目的(2周目以降の指摘の前倒し)に対する効果は測っていない。さらに、**既存のS1-U**(Stage 1がPASSのときだけ+1call)は、`meta_run03_standard`のように他のdeviationが出ている場合は発動せず、HC-010型の見逃しには効かない。骨子のC2は、S1-Uと**位置づけの整理(統合か別か)が必要**(§4-2)。**無料で推定できる改善は割れている**(fresh Stage 1の2サンプルは一致=増分0、固定Stage 1のRecheckは3組の小標本で増分あり、§4-5。結論は出せない)。
4. **C1の効果を既存記録から推定できない**: 骨子は「無料で推定できるものは推定する」。C1は走らせた記録がなく、推定できない(「無い」と書いた)。priming前例(委任_16 B-2)の存在を骨子のリスクに加えるべき(§4-1)。
5. **A1の効果の根拠が弱い**: 骨子は「22行/3種類が解消する見込み」。20行は固定fixture1件の再生で、**独立なChecker出力は3種類**(R45 §3)。直近の実運用の確定不能は0件。A1は小さく安全だが、効果の一般化は弱い。
6. **A3のまとめて渡す案は実現可能だが、グループの問題種類の決め方に設計判断が残る**(§2-3の(b))。骨子はこの判断に触れていない。
7. **`same_fact_id_locations`の「統合」は意味が変わる**: 骨子は統合案と別案の比較を求めた。統合すると全要素が1回のRewriteで全て書き換え対象になり、現在の「各箇所をStage 2が独立に判定する」設計(重大誤解原則、`expand_same_fact_id_locations`)と衝突する(§3-3)。**別のまま**を推奨する材料が揃っている。
8. **A2は`claim_in_article`でも起きる**(骨子は`same_fact_id_locations`だけの問題かを確認せよとした): 両方で起きうる。ただし現在のrunnerでは、引用符つきの位置ラベルは`expand`の事前確認で`same_fact_id_locations`側だけ捨てられている(§2-2)。**Bを入れるとこの防御が効かなくなる**ので、A2はBの前提になる。骨子の実装順(A→B)に合致するが、「Bを入れるとA1・A2の必要性が変わるか」の答えは「A2の重要度が上がる」。
9. **Dは骨子より小さく実現できる**: `current_ja_text=None`で、骨子が列挙した処理の大半が条件分岐により自動的に迂回される(§5-1)。ただし、骨子が列挙した「日英等価チェック」「JA側の指摘の統合」「JA precheck」は個別のスイッチ分岐ではなく、この一点の迂回で足りることを確認した。`baseline_precheck_ja`だけは5025行で`fixture`から計算するため、小改修が要る。
10. **D2(Checkerへ日本語を渡さない)は、Stage 2のPromptも変える**(`source_article_text`を`(なし)`にする、stage2 240行・282行)。骨子はCheckerのみを想定していたように読めるが、**Stage 2の判定も揺らす**。D1推奨。
11. **予算の収まりの見積もりに不確定要素**: 残額¥105.97は、予算stateではなくinstance JSONのcall_log合計に基づく(R42 §1: 予算stateの`cumulative_jpy`は¥0.1992欠け)。(ii)の費用は、iter8(¥24.97)〜iter7(¥39.55)の幅があり、Bを入れてfresh Stage 1を増やすと上振れしうる。骨子は(ii)を1回と読めるが、**再実行を含めると不足する**(§7-5)。
12. **骨子のC5(安全側固定)**: 降格の禁止は、C4(降格ルールの緩和)と対の関係で、強化方向。ただし、強化でも人間確認が増えるので、ユーザー指示の「Human Reviewを安易な逃げ道にしていないか」(DSG §0-6)との整合をOpusに確認してほしい。
13. **A6の1点目(delete型の文拡張)はユーザーの「最初から文全体へ広げない」と緊張する**(§2-6)。骨子はこれを「妥当性を1〜3行」で聞いたが、妥当性は条件つき(件数の集計が必要)。

## 12. Opusレビュー#6後の採否(Fable決定)

(追記: 2026-10-02、委任_49。既存の節は編集していない。正本は`DECISION_LOG.md`末尾の2026-10-02エントリ5と、`docs/pm/opus_l2_review_open233_self_recovery_06.md`のFable PM評価。Production採用の可否は判断していない。)

### 12-1. §1の「委任_47で確認中」に対応する確定値
rep22のT1(固定Stage 1、meta_run03_standard、4実行)で、正解ラベルでSafety-criticalな文「Also, some calls needed user information to continue.」(MUSE-HC-010、Meta-1)が、元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終了したのは**新方式3/4**。旧方式の固定入力7実行では**1/7**(回数が少なく新旧の差の因果は断定できない)。出所: `er052_output/open233_rep22_truth_label_check_01/`(委任_47)。§6の「確認中」の注記(603行)もこの値で置き換わる。

### 12-2. 各対策との対応表

| 設計書の対策 | 採否(Fable決定) | 委任_49での扱い |
|---|---|---|
| A1 末尾句読点の同値変換 | 採用・実装(`VS_MATCH_EXT`、既定OFF) | L5_edge_punct。Opus#6の修正(一致箇所の先頭側・末尾側の両方が単語境界)を入れて英語本文のみに適用。¥0再生: 確定不能→確定22件(U03 1・U04 1・U07 20)、確定→確定不能0件 |
| A2 位置ラベル(A2-a) | 採用・実装(同スイッチ) | `label_only`(`## In one line`行そのもの)。346行中の該当0件 |
| (単語境界のL0〜L4への拡張。Opusは「別途検討」) | 採用・実装(同スイッチ内、安全側) | 346行の再生で確定→確定不能0件(有効化の判断材料) |
| A3 同一周回で同じ範囲を指す指摘 | 見送り(Fable骨子のまとめ渡しを取り下げ) | carry-forwardを維持し、先行・後続の`issue`・fact_id・flag集合の一致と、Recheckでの解消扱いの記録だけ追加 |
| A4 主体置換ガード | (b)基準変更は実装しない(Opus判定=安全用ガードの緩和、ユーザー判断が必要になる変更。据え置き) | 対象外 |
| A5 省略記号 | 今回の委任の範囲外(未実装) | — |
| A6 委任_42が仕様外で判断した2点の妥当性 | 今回の委任の範囲外(未実装) | — |
| B 出力形式(`violation_spans`)・B-alt | 見送り | 直近の確定不能は0件で、確定不能は人間確認に倒れるため |
| C1 fact駆動の全件走査 | 本体のChecker Promptへ入れることは見送り | 出口検査の候補Prompt(DET-C)として固定本文に対し検出器の直接比較で測定 |
| C2 1周目の検査を2回 | 見送り(対策の位置がずれている。固定Stage 1では働かない) | — |
| C3 重大度の揺れの記録 | 採用・実装(記録のみ) | `severity_wobble`(周回間の最終判定の違いのflag・LLM判定・floor理由・basis) |
| C4 降格ルールの変更 | 実装しない(ユーザー判断が必要になる変更) | 降格ルールは変更しない。MUSE-HC-012の文が既存の降格ルールの対象型かの確認結果はユーザーへ報告 |
| C5 安全側固定 | 見送り(承認済みの降格ルールの意図を1回の判定で上書きするため) | — |
| D 英語だけ修正 | 採用・実装(`JA_MODE`、既定`paired`) | Opus#6の必須補正を、「`ja_source`の指摘を書き換えた周回は全文Recheck必須」(`english_only_ja_source_requires_full_recheck`)として実装(fastpath全面無効ではなく、日本語側ガードが担っていた範囲だけ)。日本語のみで確定する指摘は`ja_only_match_english_only`で確定不能。英語見出しの書き換えは`en_title_rewritten`で記録 |
| 評価の追加(Opus#6の主張) | 採用・実装(記録のみ) | `residual_at_pass`、MINORを含む全指摘`all_deviations_raw`、既知問題集合による見逃し疑いの一覧(`er052_output/open233_known_issue_residual_check_01/`) |
| 合格直前の出口検査 | 測定結果を見てから決める(今回は実装しない) | 検出器の直接比較(Checker呼び出しのみ44call・¥20.99)を実施。結果は`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§36-6 |
| MINORの指摘を後段へ渡す変更 | 実装しない(ユーザー判断が必要になる変更。測定でMINOR仮説が確認された場合、Production Checker PromptのMINOR規定とStage 2のV4原則の食い違いをユーザーへ報告) | 検出器の直接比較では、該当文がMINORで返った例は候補Prompt(DET-C)の4callのみ(現行Recheck・Stage 1相当では0件) |
| 限定確認(案X/案Z) | 案Zを採用(固定入力で測れ、費用が小さく、仮説を切り分けられる) | 検出器の直接比較として実施 |
| 予算 | Phase累計¥494.03/総枠¥600(委任_49前)。29件横断は1回分のみ見込み、2回目が必要ならユーザーへ戻す | 委任_49の費用¥20.9881、Phase累計¥515.0181、残¥84.9819 |

---

## 付録: 参照した主なファイル・範囲(Read・Grep)
- 委任_41〜46の報告(`docs/pm/delegation_log/..._41〜46_result.md`、transcriptから最後の報告をそのまま抽出して保存、ファイル冒頭に抽出元を記載)。
- `DECISION_LOG.md` 16977〜17246行・15250〜15289行。`docs/pm/design_open233_self_recovery_flow_01.md` 46〜73行・270〜290行・1517〜1550行・2360〜2373行・4422〜4441行・5055〜5084行(+Grep)。`docs/pm/opus_l2_review_open233_self_recovery_05.md` 全文。`docs/pm/design_open233_violation_span_handoff_01.md`(Grep)。`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` 全文。
- `er052_open233_self_recovery_flow_runner_01.py` 270〜330、415〜465、1130〜1220、1296〜1363、1485〜1573、1879〜1905、1990〜2070、2780〜3070、3198〜3407、3954〜4195、5012〜5125、5236〜5386、5386〜5625、5659〜5700行。`er003_v1_en_direct_vfl_01_generate.py` 455〜604行。`er051_open233_checker_trial_variant_01.py` 160〜295行。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(Grep、2802〜2842行)。`CURRENT_SPEC.md`(Grep、行番号のみ)。
- 事前指定の一覧外のRead: `er019_output/family_x_refresh_e2e_01/meta/run_03/a2/article.md`(Grep、記事の見出し構造の確認)、runnerの`run_instance`周辺5012〜5125・5386〜5625行(Dの迂回箇所の確認)、`er052_open233_self_recovery_stage2_production_01.py`(Grep、`origin`・`source_article_text`の使用箇所)、`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`(上書き前の形式確認)、`er052_output/**/*.json`(Grep、`actor_guard_rejected`の件数のみ)、`docs/pm/delegation_log/..._48.md`(T-0)。
