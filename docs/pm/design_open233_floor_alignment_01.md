# OPEN-233 機械判定(floor)の正式基準への整合設計 + 「動機」仕様の整理 + 限定flow確認の計画案(委任_58、2026-10-04)

- 管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_58)。**設計・整理のみ。コード・Prompt・テストは一切変更していない。LLM/API呼び出しなし(費用¥0)。Opus独立レビュー(条件A)前。**
- 根拠データ: 既存記録のみ(`er052_output/open233_*/`のinstance JSON 1,014 claim記録、`cases_detail_01.csv`、再分類doc)。オフライン再生スクリプト=`er052_output/open233_floor_alignment_offline_01/replay_01.py`(標準ライブラリのみ、runner/Production未import)、出力=同ディレクトリの`replay_01_result.json`・`K_rows.csv`・`replay_01_stdout.txt`。
- 用語: 「floor」=Checker(Stage 1)の5つのフラグ(主体・数値・否定・比較・時期の変更)のどれかが立っていたら、Stage 2(LLM)が軽微以下と判定しても自動で「重大(BLOCKING)」に引き上げる決定論の安全装置。「列挙の波及」=同じLedger事実に紐づく別の文へ、元の文のフラグがコピーされる仕組み(委任_35で是正済み)。

---

## 0. 結論(先に)

1. **8種類(K08・K09・K11・K12・K13・K14・K15・K17)は、すべて「floorがCheckerのフラグだけを根拠に重大へ引き上げた」ことが共通原因**(記録で確認)。内訳: 列挙の波及の残骸=6種類(K08・K09・K11・K12・K15・K17)、列挙ではなくCheckerが直接フラグを立てた=2種類(K13・K14)。**列挙の波及は委任_35(2026-10-01 15:33)で是正済み**。是正後のrun(rep21・rep22)ではfloorのみでBLOCKINGになった記録は14件中1件(7%、数値フラグ)で、主体フラグの過剰は0件。
2. **現行コードで今も再発し得る型は2つ**: (ア)役職・一般名詞の言い換え/一般化に`changed_actor`が立つ型(K13・K14)、(イ)方向語の言い換えに`changed_comparison`が立つ型(K19)。**(イ)は文字列の裏取りで安全に解放できる**(K19は事実側にも「縮小」がある)。**(ア)は文字列の裏取りでは安全に解放できない**: K13・K14と、Safety-criticalのA4-0(「users」を電話の相手と取り違え、重大)は、どちらも「役職名詞が絡む`changed_actor`」で、字面では区別できないため。
3. **記録上、floorだけが重大な誤りを止めた例が2件ある**(非列挙のfloor単独BLOCKING 18件中): Safety-critical A4-0が1/13記録(iter5、LLMはACCEPTABLE)、K16(時期の変更、重大)が1/19記録(rep9、LLMはQUALITY)。つまりfloorを一括でLLMに任せる案(F2)は、本当に重大なケースを緩める。
4. **推奨案: F4=「F1(3値の裏取り付きfloor)+決定不能分だけ独立再判定」**。floorは(1)裏取りで不一致を確認できたもの=従来どおりBLOCKING、(2)整合の積極的証拠があるもの=解放しStage 2のLLM判定に委ねる(K19が該当)、(3)どちらとも決まらないもの(役職名詞のactor、時間関係のtime等)=現行どおりfloor維持を既定とし、**Opusレビューで承認された場合のみ**、Stage 2をもう1回(フラグを見せない独立呼び出し)実行して「どちらかがBLOCKINGならBLOCKING」とする。**どの案も現行より厳しくなる箇所はない**(floorが発火する集合の部分集合)。
5. **Safety対照のオフライン再生(決定論部分のみ)**: F1/F4はSafety12(er009の9フラグ)・Safety-critical 5件・既知の重大2件(A4-0・K16)で**解放0件**。F2(階層化)は上記2件を含む11件を解放するため不採用推奨。Hormuz NG5はStage 2単体の対照でStage 1フラグが無く、floor変更の影響外=実flowでの確認は要実測。
6. **「動機」の仕様不一致は、整理で解消できる(USER_DECISION_REQUIREDにしない)**: 「動機の帰属=軽微」はLedgerが確認済みの事象に理由づけを添えるだけで新しい具体的事実を加えないもの、「根拠のない動機の創作=重大」はLedgerに無い人物・組織の意図や仕組みを新事実として書くもの。**ユーザー自身が2026-09-30の同じ指示で両方を述べており、実質は別の事象**。V7は既存より厳しくなっていない(逐語確認済み)。ただし文言整合の案文を作った(§3-3)。残る小さな論点が1つ(notes_for_writerが明示禁止している因果・動機の帰属の扱い)あり、Opusに確認を依頼する。
7. 限定flow確認の費用見積もり: 6 instance×n=2=12 run=**¥12〜26**(+F4採用時の再判定¥1〜3)、29件横断=**¥35〜60**(38 instance-run)。上限案: 限定flow¥30・29件¥70。

---

## 1. 機械判定の全体像(作業2-2)

結論: **「Checkerのフラグだけで重大を確定させる」決定論は`apply_floor`の1箇所**。他は(a)Ledger/記事の文字列と照合する決定論(precheck・丸め・降格条件・Rewriteガード)、(b)記録・監視用(判定に使わない)。floorだけがフラグを無裏取りで信用する。

評価順(`run_stage2`、`er052_open233_self_recovery_flow_runner_01.py` 2337〜2375行): 丸め除去 → `apply_floor` → (`apply_floor_cited`は反実仮想で記録のみ) → Hook降格 → 開示不備降格。

| # | 名前(関数、行) | 発火条件 | 効果 | 根拠にする情報 | 導入目的・出典 |
|---|---|---|---|---|---|
| 1 | `apply_floor`(1896)/`FLOOR_FLAGS`(518) | 5フラグ(actor/number/negation/comparison/time)のいずれかtrue、かつ列挙複製でない | BLOCKINGへ**昇格** | **Checkerのフラグだけ**(記事・Ledgerの文字列比較なし) | Stage 2(LLM)の誤降格に対するfail-closed。ユーザーNG5項目(2026-09-30)。`changed_certainty`は委任_12(iter4)でfloorから除外、列挙複製は委任_35で除外(設計書§4-3・§6-16) |
| 2 | precheck floor(`build_precheck_floor_claims`、5383) | `precheck.run_precheck`が数値等のLedger不一致を決定論検出(Stage 1が既に検出済みのfact_idは除く) | BLOCKINGへ昇格(Stage 2を通さない) | **記事とLedgerの文字列比較**(Ledger実値との機械照合) | 委任_18 2-1。Stage 1の見逃し防止 |
| 3 | `_sanitize_dev_for_rounding`(1874) | `changed_number`が立っているが記事側が通常の四捨五入で得られる近似値のみ | `changed_number`をfalseへ(floor不発) | Ledger `numeric_value`との数値比較(`precheck.changed_number_is_natural_rounding_only`)。**判定不能なら従来どおりfloor発火(fail-closed)** | 委任_14 B-1(2026-09-30ユーザー新方針item1)。**「フラグ+決定論の裏取りで解放」の既存の前例** |
| 4 | `apply_floor_cited`(1950)/`floor_cited_eligible`(1918) | floor発火+Stage 1のissue/explanationがLedger値を引用 | 反実仮想として計算し**記録のみ**(実フロー制御に使わない) | issue/explanation内の数値・4文字以上語のoverlap | 委任_14 B-2 |
| 5 | `apply_hook_aware_downgrade`(2119) | title/hook/in_one_lineのclaimで`changed_scope`単独、floor不発 | BLOCKING→QUALITYへ降格 | フラグ+区分(位置) | 委任_14 B-5(Production HOOK_CLAUSEとの整合) |
| 6 | `apply_disclosure_gap_downgrade`(2176) | floor不発・unsupported_new_claim/certaintyのみ・否定形の「知る手段がなかった」・新しい数値/固有名詞なし | BLOCKING→QUALITYへ降格 | フラグ+claim文の否定形正規表現+記事/Ledgerの数値・固有名詞の包含(precheck抽出器) | 委任_18 2-2(MUSE-HC-012パターン) |
| 7 | `apply_stage2_two_of_two`(2407) | Normal群・floor不発・Stage 2がBLOCKING | もう1回Stage 2を呼び両方BLOCKINGの場合のみ維持(降格方向) | LLM再判定 | 委任_13(Stage 2の非決定性。n=3で2:1に割れる実測) |
| 8 | Stage 2失敗の固定BLOCKING(`stage2_api_failure_failclosed`/`schema_index_mismatch_failclosed`、2323〜2336) | Stage 2のAPI失敗・index不一致 | BLOCKING固定 | なし | fail-closed |
| 9 | `actor_rewrite_guard_ok`(502)/`_ACTOR_NOUN_PATTERN`(489) | Rewrite後に新しい役職名詞が出現しLedgerに無い | **Rewriteを却下**(判定ではなくRewrite側のガード) | 記事のbefore/afterとLedger文字列 | 委任_27 Part1-3(未確認の具体主体への置換防止) |
| 10 | `classify_problem_kind`(446)/`filter_levels_by_problem_kind`(471) | floorフラグの種類 | Rewrite開始水準を決める(判定ではない) | フラグ | 委任_27 Part1-2 |
| 11 | `detect_rewrite_new_precheck_findings`(1180)、`measure_section_role_violation`、`ja_fail_open_guard`(4911) | Rewrite後の新規precheck不一致、title/hook/IOL破壊、JA側fail-open | Rewrite却下/Stage 4へ | 記事文字列 | 委任_18・委任_35等 |
| 12 | `SAFETY_CRITICAL_CLAIM_DEFS`(6351)/`detect_safety_critical_misdowngrades`(6423) | 登録claimが最終BLOCKING以外 | **記録・監視のみ**(判定に使わない) | 逐語核心句+fact_id | 委任_33(silent_pass_candidate自動検知)、委任_55で5件へ |
| 13 | body rubric V7の文言「数値・主体・否定・比較・時期の差は…従来どおり明確にBLOCKING」(`s2c`、`s2p.MATERIALITY_RUBRIC_V7`は「機械的にBLOCKING」) | Stage 2のPrompt | LLMへの指示(決定論ではないが同趣旨) | Prompt文言 | 委任_55(rubric_diff.md)。**K19は例として別途QUALITYと明記されている**ため、文言と例が食い違う(§2-5の論点) |

---

## 2. 8種類+K19+K04の1件ずつの確認(作業2-1)

結論: **全件で「正式基準では重大でない」が正しく、floorの発火は(a)Checkerフラグの過剰または(c)列挙波及によるもの**。K04はfloorが発火していない(LLM判定だけだった)。出所: `er052_output/open233_cycle_new_issue_analysis_01/cases_detail_01.csv`+各instance JSON(`stage2_results`)+`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`。「列挙」=`dev.detected_by_enumeration`。

### 2-0. Ledger事実(逐語。出所: 再分類docの各節)

- **L1 MUSE-HC-010**: `Meta従業員は、人間の契約スタッフが電話を担当すると、電話中にユーザーの機微情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、社内でプライバシー上の懸念を示した。`(conditions: `電話の遂行にユーザー情報が必要となる場合`、notes: `懸念の存在を示す事実。実際の大規模な情報漏えいが発生したと断定しない。`)
- **L2 MUSE-HC-012**: `MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。`(scope: `Meta社内テストの人間コンシェルジュ機能`、conditions: `適切な開示なしで契約スタッフが電話を担当していたテスト`)
- **L3 HF-002**: `ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。`
- **L4 HF-003**: `7月13日の20％償還料の投稿および同日の発言では、徴収主体、支払義務者、評価方法、徴収通貨、免除、執行方法、法的根拠などの具体的制度設計は示されなかった。`
- **L5 HF-009**: `Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。`(conditions: `撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。`、notes: `撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。`)

### 2-1. 確認表

| 種類 | 原文(逐語) | Ledger | Checkerのtrueフラグ(floor対象は太字) | 発火した機械判定 | LLM判定→最終 | なぜMajorへ上がったか | 正式基準での判定 | 安全上残すべき検出か | 過剰ならどう直すか |
|---|---|---|---|---|---|---|---|---|---|
| K04(例1) | `some calls needed user information to continue.`(rep19 cycle2) | L1 | changed_fact・changed_certainty・unsupported_new_claim(**floor対象なし**) | **なし(floor不発)**。LLM判定のみ | BLOCKING→BLOCKING(V6時) | Stage 2が「条件→断定」(旧V4原則の一律BLOCKING)で判定。floorは無関係 | 軽微((a)条件→発生、ユーザー決定の例1) | 不要(重大でない) | floorの問題ではない。rubric V7で解消済み(委任_55 d: QUALITY 2/2)。floorは変更不要 |
| K08 | `But sometimes, a human was speaking instead.`(rep19 cycle3) | L2 | changed_fact・changed_scope・changed_certainty・**changed_actor**・unsupported_new_claim・列挙複製 | `apply_floor`(deterministic_floor:changed_actor)、**列挙の波及** | ACCEPTABLE→BLOCKING | Checkerが別文(利用者が知り得なかった)に対し「従業員テストの範囲をMuse利用者へ広げた」としてchanged_actorを立て、そのフラグが同じfact_id(HC-012)の複製文へコピーされた | 問題なし((iii)言い換え/(i)導かれる状況) | 不要(主体の取り違えではない) | 列挙複製をfloor対象外にする(委任_35で是正済み) |
| K09 | `The problem was telling users who was speaking.`(rep19 cycle3) | L2 | K08と同じ | 同上 | QUALITY→BLOCKING | 同上 | 問題なし((i)開示なしから導かれる推論) | 不要 | 同上(是正済み) |
| K11 | `A Meta executive admitted the mistake. The test had begun without clearly telling users.`(iter7 cycle2) | L2 | changed_fact・changed_scope・**changed_actor**・unsupported_new_claim・列挙複製 | `apply_floor`、列挙の波及 | ACCEPTABLE→BLOCKING | 元文K13と同じ指摘(「users were not clearly told」は、Ledgerが社内テストのMeta従業員を述べるのに利用者へ置換)のフラグが複製された | 軽微((b)副社長→executiveの一般化+(iii)言い換え) | 不要 | 同上(是正済み)。根の過剰フラグ(K13型)は別途(下) |
| K12 | `A user might think the exchange was with AI, even though a person was involved.`(iter7 cycle2) | L2 | K11と同じ | 同上 | QUALITY→BLOCKING | 同上 | 問題なし((i)留保付き推論) | 不要 | 同上(是正済み) |
| K13 | `The test began without clearly telling users that contract workers would make the calls.`(iter7 cycle2) | L2 | changed_fact・changed_scope・**changed_actor**・unsupported_new_claim(**列挙ではない**) | `apply_floor`(Stage 1が直接立てたフラグ) | ACCEPTABLE→BLOCKING | Checkerが「Ledgerは社内テストのMeta従業員を述べ、利用者全般が開示を欠いた対象とは確認していない」としてusers≠employeesの主体置換を指摘 | 問題なし((iii)同義の言い換え。L2のconditionsは開示対象を限定していない) | 不要(LLM判定は記録1件でACCEPTABLE) | **要設計**(§2-4。役職名詞の一般化は文字列だけでは区別できない) |
| K14 | `トランプ氏は、アメリカがホルムズ海峡の安全確保に使う費用について、海峡を通るすべての貨物に二割の償還を求めると投稿した。`(rep16 cycle2) | L3・L4 | changed_fact・**changed_actor**・unsupported_new_claim | `apply_floor`(直接) | ACCEPTABLE→BLOCKING | Checkerが「すべての貨物を支払義務者として特定しているように読めるが、Ledgerは支払義務者を特定していない」とした。実際にはL3の言い換え(主体・対象・率・動詞が一致) | 問題なし((iii)言い換え) | 不要。ただし同じ構造のK18(`貨物を運ぶ側に返してもらう`=支払う側の特定)は重大で、フラグだけでは区別できない | **要設計**(§2-4) |
| K15 | `During that period, attacks between the United States and Iran, a sea blockade, and concerns about tanker safety continued.`(rep16 cycle2、5記録) | L5 | changed_fact・changed_causality・**changed_time**・unsupported_new_claim・列挙複製 | `apply_floor`、列挙の波及 | ACCEPTABLE→BLOCKING | 元の文K16(`…quickly returned`、継続→一度消えて戻った、**重大**)のフラグが複製された。K15自体はL5 conditionsの言い換え | 問題なし((iii)言い換え) | K16の元フラグは**残すべき**(重大)。K15への波及は不要 | 列挙複製をfloor対象外(是正済み)。元のK16のfloorは維持 |
| K17 | `The fee plan may be replaced, but events continuing at the same time do not simply disappear backstage because of one announcement.`(rep16 cycle2、5記録) | L5 | K15と同じ | 同上 | QUALITY→BLOCKING | 同上 | 軽微((c)確定事実をmayで弱めた一般論) | 同上 | 同上(是正済み) |
| K19 | `Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level.`(iter6 cycle2) | L5 | changed_fact・**changed_comparison**・unsupported_new_claim | `apply_floor`(直接) | BLOCKING(V6時)→BLOCKING | Checkerが「価格そのものが下落し始めた」と「Ledgerの上げ幅の一時縮小」の差を方向の置換としてchanged_comparisonを立てた | **軽微**(ユーザー決定2026-10-03) | 方向の完全な反転(上昇→下落)の検出自体は残すべき。ただし**事実側にも「縮小」という下向きの語がある**ケースは重大でない | 方向語の裏取り(案F1)でCLEARED(§2-4)。rubric V7のLLM判定はQUALITY(委任_55 d、2/2)だが、floorがあるとV7のQUALITYがBLOCKINGに戻る |

### 2-2'. 原因の切り分け(作業2-3)

結論(件数、8種類について): **(b)floorがフラグだけを根拠に裏取りしていない=8/8(必要条件)**。(c)列挙の波及=6/8、そのうち元フラグ自体が過剰(a)なもの=3〜4種類(K08・K09・K11、K12は元文を特定できず推測)、元フラグが妥当(K16)な複製=2種類(K15・K17)。(a)Checkerのフラグ自体が過剰で列挙でもない=2/8(K13・K14)。K19は8種類の外だが(a)+(b)。

| 原因 | 種類 | 件数 | 現状 |
|---|---|---|---|
| (c)のみ(元フラグは妥当) | K15・K17 | 2 | 委任_35で是正済み |
| (a)+(c)(元フラグが過剰で、さらに複製) | K08・K09・K11・K12 | 4 | 複製分は是正済み。元の過剰フラグは(a) |
| (a)+(b)(直接のフラグが過剰、floorが裏取りなし) | K13・K14 | 2 | **現行コードで再発し得る** |
| (a)+(b)(8種類の外) | K19 | 1 | 現行コードで再発し得る |

補足(記録): 全1,014 claim記録のうち、floorが発火した記録は258件。LLM判定が非BLOCKINGなのにfloorだけでBLOCKINGになった記録(floor単独)は54件(Ledger取得可能な250件中)。うち**列挙複製36件(是正済み)・非列挙18件**。是正後のrun(rep20〜22)ではfloor発火14件中、floor単独は1件(rep21の`changed_number`)のみ。(`replay_01_stdout.txt`)

「Checkerのフラグが過剰か」の根拠(記録で確認できたこと): K13・K14のCheckerの`issue`文自体が「利用者を従業員の代わりに使っている」「貨物を支払義務者として特定している」と、一般化・言い換えを主体の置換として扱っている。推測: 同種のフラグ過剰は今後も出る(Checker PromptはユーザーがPrompt変更なしと決定済み)。

---

## 3. 設計案(作業2-4)

結論: **文字列の裏取りで安全に解放できるのは「数値・否定・方向語・年月日」まで。役職名詞の入れ替え/一般化(K13・K14とA4-0・K18の区別)と時間関係の変更(K16)は字面では判別できない**。そのため、(1)裏取りが取れたものだけ解放(F1)は安全だが解消できるのはK19型と一部の数値型に限られ、(2)全部をLLMに任せる(F2)は重大を緩める。推奨は、F1に「決定不能分だけ独立再判定」を加えたF4。

### 3-0. F1の3値判定(裏取りの定義)

各フラグについて、claimとLedger(全文またはrelated_fact_idの事実)を決定論で比較し3値を返す。**既存の前例=`_sanitize_dev_for_rounding`(丸め)と同じ構造で、「判定不能ならfloor発火のまま」(fail-closed)**。

| フラグ | CONFIRMED(不一致を確認=floor維持) | CLEARED(整合の積極的証拠=解放) | UNDETERMINED(決まらない=floor維持) |
|---|---|---|---|
| changed_number | claimの数値トークン(英語数詞・漢数字・万/億・割を正規化)がLedger全文に無い | claimに数値があり全てLedgerにある | claimに数値トークンが無い |
| changed_negation | 否定語の有無がLedger事実の1行目と異なる | 両方とも肯定(否定反転は起き得ない) | 両方に否定語(二重否定・述語違い)/fact_id不明 |
| changed_comparison | claimの方向語(上昇/下落、日英)がLedger事実に無い | claimの方向語が全てLedger事実にある(K19: 事実側に「縮小」) | 方向語が無い/fact_id不明 |
| changed_time | claimの年・月日がLedger全文に無い | claimに年月日があり全てLedgerにある | 年月日トークンが無い(継続/再発のような時間関係の変更は字面で判別不能=K16) |
| changed_actor | Ledger全文に一度も現れない固有名詞(英語、文頭語除く) | **出さない**(役職・一般名詞の一般化/入れ替えは判別不能) | 上記以外すべて |

言語をまたぐ扱い(Ledgerは日本語、claimは英語が多い): 数値・年月日は記号・数詞で言語を越えて比較できる。方向語は小さな日英辞書(上昇/下落語)で比較する。**固有名詞は日本語Ledgerの訳語(United States=米国等)を「新規」と誤判定する**(記録上`United States and Iran`の3記録が該当=安全側=floorが残るだけで解放されない。実装時は日英別名表を検討=Opus論点)。役職名詞の日英対応は辞書を作ると**個別例外**に近づくため行わない。

### 3-1. 案の比較

| 案 | 内容 | 8種類+K19+K04 | Safety対照(オフライン再生、決定論部分) | 実装規模 | retry/fallback/regenとの整合 | 非決定性 | Production配線時のリスク |
|---|---|---|---|---|---|---|---|
| **F1** 3値の裏取り付きfloor(決定不能はfloor維持) | CONFIRMED→BLOCKING、CLEARED→解放(LLM判定へ)、UNDETERMINED→現行どおりBLOCKING | 解消: K19(CLEARED)。是正済み: K08・K09・K11・K12・K15・K17(列挙)。**未解消: K13・K14**(UNDETERMINED) | Safety12(floorフラグあり6件): CONFIRMED4(actor・number・scope→actor・time)・UNDETERMINED2(comparison・negation。再生側でfact_id欠落)、**解放0**。Safety-critical 5件: floorフラグがあるのはA2A3-0(CONFIRMED。ただし固有名詞の訳語誤判定による可能性あり)とA4-0(13記録とも UNDETERMINED=維持)のみ、**解放0**。A4-0・K16(floor単独で止まった2件)も維持。非列挙floor単独18件中の解放は1件(`changed_number`のCLEARED) | 小(`apply_floor`の直前に関数1つ。丸めの`_sanitize_dev_for_rounding`と同型) | 変更なし(判定がBLOCKINGなら従来のRewrite/retry/fallback) | なし(決定論) | 小。Ledger形式(日本語)依存の辞書が要る |
| **F2** フラグの階層化 | number・negationはfloor維持。actor・comparison・timeはfloorを外しLLM判定のみ(フラグはQUALITY下限) | 8種類+K19: 全て解消 | **11件を解放**: 非列挙floor単独18件中、actor8・time2・comparison1。**そのうち重大の2件(A4-0 1/13記録、K16 1/19記録)が止まらなくなる**。Safety12のactor・scope(actor)・comparison・timeの4 fixtureとSafety-criticalのA4-0・A2A3-0はLLMのみで保持(LLM記録はSafety12全件BLOCKING、V7対照も9/9・5/5、ただしn=2) | 小 | 変更なし | なし | **「本当に重大なケースを一括して緩める」に当たる恐れ**=不採用推奨 |
| **F3** Stage 2へのフラグ再提示 | floorはBLOCKING確定せず、フラグ内容をStage 2のPrompt入力へ含め再判定 | 要実測 | 決定論では再生できない=**要実測** | 中(Stage 2入力変更。Stage 2の独立性が下がる) | Stage 2再較正が必要 | 増(LLM) | 中〜大。**委任_16でprompt priming(誤降格)が実測された前例**があり、独立判定の利点を失う |
| **F4(推奨)** F1+決定不能分の独立再判定 | F1に加え、UNDETERMINEDのうちactor/time/comparison/numberでStage 2が非BLOCKINGのものだけ、Stage 2を**もう1回**(同rubric V7、**フラグは見せない**)呼び、**どちらかがBLOCKINGならBLOCKING**、両方非BLOCKINGなら解放(QUALITY記録) | K19: F1で解消。K13・K14: 再判定で非BLOCKINGが続けば解放(確率は要実測。記録ではK13・K14ともLLM判定は非BLOCKING 1/1) | F1と同じ決定論部分は解放0。再判定の効果は記録済みLLM判定率からの推定のみ: A4-0はBLOCKING 12/13、K16は18/19 → 両方が見逃す確率の目安 約0.6%・0.3%(独立と仮定、実際は非独立の可能性)。**要実測** | 中(既存`apply_stage2_two_of_two`の逆方向の仕組みを流用できる) | 既存の2-of-2と同じ枠。上限回数・Gateは不変(再判定は1回、最終的にBLOCKINGなら従来のラダーへ) | 増(ただし対象はUNDETERMINEDの数件のみ。post-fix runで0〜1件/run) | 中。**floorの「固定BLOCKING」を「再判定でOR」に変えるため、Safety方針の変更**(Opus条件A、ユーザー判断事項になり得る) |

所見:
- **現行より厳しくなる箇所はない**(F1/F2/F3/F4とも、最終BLOCKINGになる集合は現行のfloor発火集合の部分集合。F4の再判定はfloor対象のclaimだけに呼ぶ)。
- F1だけなら**Safetyは現状と完全に同じ**(解放は決定論で整合を確認できたものだけ)。ただし解消できるのは8種類中0種類(K13・K14は残る)+K19のみ。ユーザー指示「同種ケースに再発しない形」は、actor型を再判定に委ねるF4の承認が前提。
- 記録上のfloor単独BLOCKING 5件(UNDETERMINEDの旗付き非列挙): A4-0(重大)・K16(重大)・K13・K14・B2「vanished overnight」の3件が過剰。**重大2:過剰3**で、floorを外す側の損失は無視できない。

### 3-2. 推奨と理由

- **推奨: F4**(ただし(3)UNDETERMINED分の再判定はOpusレビューの承認後に有効化)。
- 理由: (1)F1の決定論部分は安全でユーザー基準に合う(K19が解消)。(2)K13・K14型は字面で区別できないため、LLMによる意味判断を使うしかない。正式基準(V7)を持つのはStage 2のLLMであり、基準との整合はそこで取れる。(3)独立再判定(フラグを見せない)にすれば、priming(F3の問題)を避けつつ、重大の取りこぼし(F2の問題)を「どちらかがBLOCKINGならBLOCKING」で抑えられる。(4)対象はUNDETERMINEDの数件のみなので費用は小さい。
- 代替: Opusが「再判定でも重大の取りこぼし確率がゼロでないこと」を受け入れないなら、F1のみを採用し、K13・K14型の残りは**過剰品質として受容する案**(ユーザー判断事項)。

### 3-3. 既存より厳しくなる箇所がないことの確認

- F1: `apply_floor`が発火する集合を減らすだけ(部分集合)。
- F4: 再判定はfloor発火したclaimのみ。最終がBLOCKINGなのは「floor発火または(再判定でBLOCKING)」であり、現行(floor発火=BLOCKING)より広がらない。
- 逆に**緩む箇所**(重大を緩めない原則に照らして明示): F1のCLEARED(数値・否定・方向語・年月日がLedgerと整合と確認できたもの)と、F4の再判定で両方非BLOCKINGになったUNDETERMINED。後者はLLM判定の信頼性に依存する(記録上A4-0・K16は各12/13・18/19でBLOCKING)。

### 3-4. 再較正の計画(作業2-5)

決定論部分(F1)はLLMを使わないため、再較正は**オフライン回帰(¥0)+Stage 2の関連対照**で足りる。

- 構成(委任_55の`er052_open233_element_trial_safety_control_05.py`と同じ入力): (a)Safety-critical 5件、(b)Safety12(er009 9フラグ)、(c)Hormuz許容5/NG5、(d)例1・例2・K19、(e)K16・K20(B4-a型)、(f)K11・K12・K13(負例)。加えて8種類のうち未収録のK08・K09・K14・K15・K17(新しい対照グループ)。F4の再判定対象(A4-0・K16・K13・K14・B2「vanished overnight」・bgroup_B4比較)をn=5で独立に呼ぶ。
- 単価(委任_55の実測、`er052_output/open233_safety_control_03/budget_state_c233ao_55.json`): 26 call・n=2で¥4.3666(1 callあたり¥0.03〜0.42、平均¥0.17)。
- 見積もり: 既存構成n=2 ≈¥4.4 + 追加グループ(K08・K09・K14・K15・K17、5〜6 call)≈¥0.8 + F4再判定(6 claim×n=5=30 call、キャッシュ有で¥0.05〜0.2/call)≈¥3 = **約¥8〜10**(n=3にしても¥12以内)。Phase累計¥536.4930、残¥363.5070に対し十分余裕。上限案: ¥15。
- 合格基準: Safety-critical 5件・Safety12 9件が全件BLOCKING(Stage 2単体+floor+F4)、(d)(e)(f)が期待どおり、(c)従来と同じ、K13・K14が解放(F4採用時)またはK19が解放(F1)、重大2件(A4-0・K16)が止まる。

---

## 4. 「動機」の仕様不一致の整理(作業3)

結論: **同じ事象ではなく、実質が違う。整理で解消できる(`USER_DECISION_REQUIRED`にしない)**。「動機の帰属」=Ledgerが確認済みの事象に自然に付随する理由づけで、新しい具体的事実を加えないもの(軽微)。「動機の創作」=Ledgerに無い人物・組織の意図や仕組みを新事実として書くもの(重大)。**ユーザー自身が2026-09-30の同じ指示で両方を述べている**。V7は既存より厳しくなっていない。

### 4-1. 出典(作業3-1)

| 出典 | 逐語 | いつ・どの委任 | ユーザー承認 |
|---|---|---|---|
| Stage 2 production rubric(`er052_open233_self_recovery_stage2_production_01.py` 41〜42行) | `QUALITY: Ledgerの観測と矛盾しないが、Ledgerが保証していない関係付け(因果接続詞・動機の帰属・強調)が加わっている。` | 2026-09-30(設計書§4 rubric R2/R3構成、初出commit `4cec048e`)。委任_55で「迷えばBLOCKING」の1行のみ置換(`MATERIALITY_RUBRIC_V7`)、この文は不変 | rubric自体の文言承認は未確認(要確認)。claim単位の正解ラベル整理はユーザー承認済み(2026-09-30委任文§1・§4、設計書§7冒頭) |
| 設計書§0-2(235〜248行) | `BLOCK候補(記事の主要な意味・主体・方向・規模・時間軸を誤認させる場合): …未確認の人物・行動・動機・数字の追加/因果の逆転。` | 2026-09 設計書の最上位原則(§0) | §0-1は「重大な誤解だけ止める」。§0全体の承認日は未特定(要確認)。ユーザー基準に基づくと設計書に記載 |
| Stage 2 calibration rubric(R3、`er052_open233_self_recovery_stage2_calibration_01.py` 127〜137行) | `(b)Ledgerに無い人物・数字・出来事・具体的な行動・仕組み(メカニズム)を新たに追加している…(c)根拠のない人物・組織の意図や動機を断定している。` | 委任_12(iteration 4、2026-09-30ユーザー新方針「許容線の再設計」)で再構成 | ユーザー指示(iteration 4)に基づく。`DECISION_LOG.md`「iteration 4実測完了(許容線の再設計…」エントリ |
| ユーザーの許容線(同エントリ、`DECISION_LOG.md` 14128行以降) | 許容: `『市場が海上リスクを重視したから価格が戻った』程度までは今回のProduct基準でぎりぎり許容`。NG: `…根拠のない意図・動機の断定/Factと逆方向の因果/actor取り違え/…` | 2026-09-30 | **ユーザー指示そのもの** |
| B1-c(設計書§7-0-iter4、3582行) | 旧BLOCKING→新QUALITY: `「市場が海上リスクを重視したから価格が戻った」程度の断定は、確認済みFact…を人間が自然に読めば導ける解釈であり、新しい具体的事実(誰が・いつ・いくら)を発明していない` | 委任_12 | 上記ユーザー許容線の適用(Fable再ラベル) |
| B4-a(`when AI struggled, a person could help`型、K20〜K22) | BLOCKING。再分類doc: `動機・機構の新規主張`、`新しい具体的事実の追加(V7(1)(イ)で拾う)` | 委任_07で発見(Stage 2がQUALITYへ降格)→R3で是正、委任_51で再分類 | claim単位ラベルとして2026-09-30ユーザー承認の整理に含まれる。委任_55でも「BLOCKING、変更なし」 |
| V7(1)(イ)(`rubric_diff.md`) | `Ledgerに無い新しい具体的事実(人物・出来事・発言・数値)を加えている` | 委任_55(2026-10-03) | ユーザー決定(線引き正式採用)に基づく |
| DECISION_LOG 17601・17939行(委任_51・委任_57) | `「動機の帰属=QUALITY」(production MATERIALITY_RUBRIC)はFable案(4)・設計書§0-2・K20〜K22と食い違うが、現行flowはBODY_RUBRIC_DEFAULT=V6/V7を使うため実害なし。Production配線時に再確認。` | 委任_51・委任_55 | Fableの観察(未解消の記録) |

### 4-2. 整理(作業3-2)

(a) **同じ事象か**: 別の事象。
- 「動機の帰属」(軽微): 例「市場が海上リスクを重視したから価格が戻った」。Ledgerが確認している事実(海上リスクの存在・価格の反発)の間に理由づけを添えるだけ。新しい人物・出来事・数値・仕組みは増えない。
- 「動機の創作」(重大): 例B4-a「The idea was practical: when AI struggled, a person could help.」。LedgerにないAIから人への引き継ぎという**仕組みと設計意図**を新しい具体的事実として書いている(再分類doc: `(b)Ledgerに無い…具体的な行動・仕組み(メカニズム)の新規追加`に当たる)。
- 文言の食い違いは、rubricの`QUALITY`行に「根拠のある/新しい具体的事実を加えない」の限定が無く、設計書§0-2に「根拠のない」の限定が無いために生じている。

(b) **既存仕様が軽微と想定していた事象**: 導入時の較正例は**B1-c**(HF-009の市場動機・価格回復理由の断定)。理由=確認済みFactから自然に導ける解釈で、新しい具体的事実を発明していない(§7-0-iter4)。

(c) **正式基準での整理**: できる。「新しい具体的事実(人物・出来事・発言・数値・仕組み・意図)の追加に当たる動機の創作=重大(V7(1)(イ)+R3(b)(c))」「Ledgerの事実に自然に付随する理由づけで新しい具体的事実を加えないもの=軽微または問題なし」。

(d) **V7が既存より厳しくなっていないか**: 厳しくなっていない。`rubric_diff.md`の逐語確認: (1)条件→断定は旧V4「一律BLOCKING」を「核心の主張まで断定/新しい具体的事実/notes禁止」の3条件に**限定**(緩和)、(2)自然な推論は**許容を明記**(緩和)、(3)迷えば重大な誤解で決める(旧「迷えばBLOCKING」より緩和)、「数値・主体・否定・比較・時期の差は…従来どおり明確にBLOCKING」は**従来どおり**(不変)。厳しくなった箇所は見つからなかった。**唯一の注意**: V7(1)(イ)の列挙(人物・出来事・発言・数値)に「仕組み・意図」が書かれていない。B4-aがBLOCKINGで保たれているのは基底rubric(R3(b)(c))による。これは緩みではなく書き漏れ(§4-3の案文で補う)。

(e) **今回の一般化が不用意に厳しくなっていないか**: 厳しくなっていない。今回の整合設計(F1/F4)はfloorの発火集合を減らす方向のみ。動機の整理も「軽微/重大の境界の文言を既存の運用に合わせる」だけで新しい禁止を加えない。

### 4-3. 案文(作業3-3、実装しない。Opusレビュー後にFableが判断)

**(1) rubric(`MATERIALITY_RUBRIC`/`_V7`のQUALITY行)**: 現行
`- QUALITY: Ledgerの観測と矛盾しないが、Ledgerが保証していない関係付け(因果接続詞・動機の帰属・強調)が加わっている。`
→ 案
`- QUALITY: Ledgerの観測と矛盾せず、Ledgerが確認済みの事象同士を結ぶ関係付け(因果接続詞・理由づけ・動機の帰属・強調)が加わっているが、新しい具体的事実(人物・出来事・発言・数値・仕組み・意図)は増えていない。`
(ねらい: 「動機の帰属」に「新しい具体的事実を増やさない」の限定を明記し、重大側との境界をV7(1)(イ)と揃える。既存の判定は変えない=書き漏れの補足)

**(2) V7(1)(イ)**: 現行 `(イ)Ledgerに無い新しい具体的事実(人物・出来事・発言・数値)を加えている`
→ 案 `(イ)Ledgerに無い新しい具体的事実(人物・出来事・発言・数値・仕組み・意図)を加えている`
(ねらい: R3(b)(c)と同じ範囲を明記。**既存のBLOCKING対象を変えない**書き漏れの補足であり、Opusに「既存より厳しくなっていない」ことの確認を依頼する)

**(3) 設計書§0-2のBLOCK候補**: 現行 `未確認の人物・行動・動機・数字の追加`
→ 案 `未確認の人物・行動・仕組み・数字の追加(Ledgerに根拠のない人物・組織の意図・動機の断定を含む。Ledgerが確認済みの事象に自然に付随する理由づけで、新しい具体的事実を加えないものは含まない)`

**残る小さな論点(USER_DECISION_REQUIRED候補、Opus確認後にFableが判断)**: B1-cはHF-011のnotes_for_writerが因果推論を明示禁止していた(旧BLOCKINGの根拠)。委任_12でQUALITYへ再ラベルされたが、「notes_for_writerが明示的に禁じた断定=BLOCKING」(基準1)との整合は文言上は未整理。実害は確認されていない(現行flowはV7で判定)。**この1点だけは「notes禁止の因果・動機の帰属を軽微とするか」という価値判断を含み得る**ため、Opusが整理で解消できると判断しなければユーザーへ戻す。

---

## 5. 限定flow確認の計画案(作業4、実行しない)

結論: **6 instance×n=2=12 runで¥12〜26(F4採用なら+¥1〜3)、上限¥30。29件横断は38 instance-runで¥35〜60、上限¥70。少数flowで1つでも停止条件に当たれば29件へ進まない**。

### 5-1. 少数flow(ユーザー指示§7①と§6)

- 対象(固定Stage 1入力): `meta_run03_standard`(K04/K08〜K10のMUSE-HC-010〜012、最小Rewrite・Human Review測定)、`hormuz_run03_standard`(HF-009)、`neg3_hormuz_prodrunner_b1b`(K14・K15・K16・K17)、`safety_A4`(A4-0=floor単独で止まった前例)、`safety_A2A3`(K18・K19)、Safety対照`safety_er009_changed_number`。
- n=2(合計12 run)。比較対象: rep22・rep21の同入力の記録(`er052_output/open233_self_recovery_flow_runner_01_rep22`・`rep21`)。
- 有効にするスイッチ(Trial専用、Production経路は変更しない): `HANDOFF_MODE=violation_span`(既定)、`VS_MATCH_EXT=True`、`VS_EXPLAIN_SPLIT=True`(P-strict-closed、2026-10-04`APPROVED_FOR_PRODUCTION`)、`JA_MODE=english_only`、rubric V7、機械判定修正版(委任_59で実装、スイッチ名は実装時に決定)。実行スクリプトは`er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`を踏襲。
- 測る値: `residual_at_pass`(0であること)、既知問題集合の見逃し疑い、Stage 4理由分布、成立水準(P確定の件数と`dropped_remainders`)、floor単独BLOCKING件数(非列挙、0に近いこと)、不要Rewrite(軽微/問題なしへのRewrite件数)、Human Review(Stage 4)件数、最小Rewrite(Rewrite範囲がviolation_spanに収まる)、retry/recheck(`stage1_recheck_confirm`がRewriteの後に呼ばれていること・同一claim再BLOCKの扱いが仕様どおり)、JA処理が呼ばれていない証跡(`call_log`に`ja_*`系のstageが無い、JA本文・タイトルのハッシュが不変)、費用。
- §6(英語だけ修正・再生成後のChecker再検査)の確認: (1)`JA_MODE=english_only`で日本語本文・日本語タイトルが不変、(2)英語Rewrite後にStage 1 Recheck(Checker呼び出し)が必ず実行される。**制約(確認できていないこと)**: 「古い日本語から英語を再生成するProduction経路」(`er012_e_family_entertainment_two_level_runner_01.py`等、`OPEN-233-A1-PROD`行に記載)はTrial runnerでは再現されない。この経路の再検査はProduction配線時のGate 3で確認する(限定flowでは確認できない旨を報告に明記する)。
- 合否基準案: false PASS=0(Safety-critical 5件・Safety12のfloor/Stage 2いずれでもBLOCKING維持、`residual_at_pass`=0)、floor単独BLOCKING(非列挙)が0〜1件/run以下で、rep22以下、不要Rewriteがrep22以下、Human Review(Stage 4)がrep22以下、最小Rewrite違反0、JA処理呼び出し0、すべての新規Stage 4が`fail-closed`理由。
- 費用: rep22実測1 runあたり¥1.0〜2.2 → 12 run=¥12〜26(+F4再判定¥1〜3)。上限案¥30。

### 5-2. 29件横断(少数flow合格後に1回だけ)

- 構成: iter8と同じ38 instance-run(29 instance)、上記と同じスイッチ。見積もり¥35〜60(上限案¥70)。
- 29件へ進まない判定(少数flowで1つでも): false PASS≥1、Safety-critical誤降格≥1、Human Reviewがrep22を上回る、floor単独BLOCKING(非列挙)が残る、JA処理の呼び出し検出、P確定の`dropped_remainders`が説明のつかない欠落、費用が見積もり上限の1.5倍超。
- STOP: 29件完了で必ず止まり、ユーザーへ報告(5記事×2レベルの次Trialは開始しない)。

---

## 6. Opusに見てほしい論点(10項目以内)

1. **F1の3値設計**: 「判定不能はfloor維持(fail-closed)」は既存の`_sanitize_dev_for_rounding`と同型。CLEARED条件(特に方向語が事実側に両方向あるとき、K19のように解放される)は緩すぎないか。
2. **F4の独立再判定(OR-of-2)**: floor固定→再判定ORへの変更は「Safety方針の変更」か(ユーザー判断事項にすべきか)。独立性(フラグを見せない)と再判定の信頼性。記録上のA4-0・K16の救出率の推定は妥当か。
3. 役職名詞のactor(K13・K14 vs A4-0・K18)を字面で区別できない前提は正しいか。別の決定論的区別(Checkerの同時フラグ: K13はchanged_scope+unsupported併発、A4-0はactor単独、等)は有効か(n=1〜13と少ない)。
4. 固有名詞の日英別名表を実装時に入れるか(現状は訳語を「新規」と誤判定して解放されず=安全側だが過剰判定が残る5件の原因)。
5. K19: rubric V7の文言「比較の差は…従来どおり明確にBLOCKING」と例「prices began to fall→QUALITY」の食い違い。文言を直すか、floor側(F1のCLEARED)だけで足りるか。
6. §4-3の案文(2)「V7(1)(イ)に仕組み・意図を追加」は既存より厳しくならないか。
7. B1-cのnotes_for_writer禁止の扱い(残る小さな論点)は整理で解消できるか、ユーザーへ戻すか。
8. 列挙複製に対するfloor免除(委任_35)の後も、**元の過剰フラグ**(K13型)が複製元として残る。複製元の過剰判定は設計の対象に含めるべきか。
9. Safety対照のオフライン再生は、決定論部分のみ。Hormuz NG5(Stage 1フラグなし)の実flow確認を、限定flow(§5)の対象にいつ入れるか。
10. 限定flowの合格基準(floor単独BLOCKING 0〜1件/run以下など)は妥当か。n=2で十分か。

---

## 7. 確認できたことと推測の区別

- **確認できたこと(記録・実コードによる)**: 8種類+K19+K04のフラグ・floor_reason・LLM判定・列挙の有無(instance JSON)、floorの評価順と各機械判定の条件(runnerの該当行)、列挙是正の日時(委任_35、commit da79bbb5、2026-10-01 15:33)、post-fix runのfloor単独件数、floor単独で重大を止めた記録(A4-0・K16)、オフライン再生の決定論結果、V6→V7差分、委任_55の単価・結果。
- **推測**: K12の元フラグの出所、同種のフラグ過剰が今後も出ること、F4の再判定でK13・K14が解放される確率、再判定の見逃し確率(記録のLLM判定率からの目安、非独立の可能性あり)、V7(2026-10-03)の設計書§0・rubric文言のユーザー承認日(未特定=要確認)。
- **要実測**: F3、F4の再判定効果、Hormuz NG5の実flow、日英別名表の効果、Ledger未取得のinstance(bgroup_B1・neg4/neg6_smallbag、再生対象8記録)。

## 6. Opusレビュー#8後の採否(Fable判断、2026-10-04、委任_59)

(本文は書き換えない。Opusレビュー#8全文: `docs/pm/opus_l2_review_open233_self_recovery_08.md`。)

2. 採用(Fable判断で確定): (a)F1の「整合の証拠による自動解放(CLEARED)」は廃止する。Opusがコードで示したとおり、比較の裏取りは事実文に両方向の語があるとどの方向でも解放され、ユーザーが禁じる「撤回後に原油価格が下落した」も解放されうる。数値・時期・否定の自動解放は付け替え・反義語の反転を見逃す。(b)F4は撤回する。Stage 2は現行でもフラグを見ておらず(calibration_01.py 627〜638行)、「フラグを見せない独立再判定」は同じpromptの引き直しにすぎない。(c)決定論で不一致を確認できたもの(CONFIRMED)はBLOCKING確定を維持する(維持方向にしか働かず安全)。(d)V7の文言「数値・主体・否定・比較・時期の差は…明確にBLOCKING」は、既存の基底rubric R3(e)に揃えて「Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は…明確にBLOCKING」へ直す(新基準の作成ではなく既存への整合。再較正必須)。(e)動機: 「帰属」と「創作」は別事象。委任_58の案文(2)(V7(1)(イ)へ「仕組み・意図」を追加)は採らない(B4-aは基底R3(b)(c)でBLOCKINGが保たれており不要。限定なしの「意図」は既存より厳しくなりうる)。案文(1)はProduction配線時に、案文(3)は文書のみ反映可。B1-cはユーザーの2026-09-30の判断と基底R3のQUALITY行で整理済みとし、「notes禁止=BLOCKING」と自然な推論の優先順位はProduction配線時の確認項目として記録する(ユーザー判断は不要)。(f)限定flowの合格基準から「floor単独BLOCKING 0〜1件/run」を外し監視値にする。解放は全件ログ+人がラベル付け、重大ラベルのclaimが1件でも解放されたらSTOP。(g)Production配線時の必須対策(解放claimを2-of-2降格の対象から外す/`dev`のフラグを書き換えない/確認callの失敗はBLOCKING固定/cycleごとに再評価)とruntime evidence項目を`OPEN-233-A1-PROD`に追加する。
3. ユーザーへ戻す(Opus指摘に同意): 「Checkerのフラグが立ったclaimを、LLMの確認で解放するか」。機械判定の決定論的な保証を、確率的な保証(確認callが見逃す可能性)に置き換える新しいリスク許容の判断であり、ユーザーのSTOP条件「Safety原則の変更が必要」に当たる。決定論だけでは、役職の一般化(K13・K14)と主体の取り違え(A4-0)を字面で区別できず、比較の目印(K19)も安全に解放できない。したがって「機械判定を正式基準に一致させる」には、(i)LLM確認による解放を導入する(F5)か、(ii)現状維持で一部の軽微な文が機械判定で重大のまま残ることを受容するか、のどちらかになる。
4. Fableの推奨: F5を**比較(`changed_comparison`)と時期(`changed_time`)に限って**導入し、主体・数値・否定は決定論のまま維持する。理由: ユーザーが「本当に重大」と名指しした主体取り違え・数値改変・否定反転を確率的な判定に委ねない。K19型(比較)はこれで解放され、K16型(時期)は確認callで止める(2回とも非BLOCKINGのときだけ解放、失敗はBLOCKING固定)。K13・K14型(主体の一般化)は過剰品質として受容する(是正後の実行で機械判定単独は14件中1件)。導入前に、Opus指摘の単体測定(重大ケースK16・A4-0・K18・A2A3-0と敵対的合成ケース[「After the plan was withdrawn, oil prices fell.」・20%の付け替え・7/13と7/14の取り違え]、過剰ケースK13・K14・K19・B2「vanished overnight」・B4「Names…」をn≥10、¥10〜30)で見逃し0・解放の妥当性を確認してから有効化する。

### 正誤表(Opusが指摘した本文の事実誤認4点。本文は未修正)
1. F4の前提: 本文は「Stage 2をフラグを見せずに再判定すれば独立性が得られる」とするが、Stage 2は現行でも`dev`のフラグを見ていない(`calibration_01.py` 627〜638行)。F4は同じpromptの引き直しにすぎない。
2. 「非列挙floor単独18」→現行コードに関係するのは14件(是正後run rep20〜22でのfloor発火14件のうち、LLM非BLOCKINGでfloorだけBLOCKINGは1件)。
3. 「UNDETERMINED旗付き5」→8件。
4. K19の`CLEARED`は整合の証拠ではない(事実文に両方向の語があるため方向を問わず解放される)。

(本節の項番6は、本文末尾の「7. 確認できたことと推測の区別」の後に追記したため順序が前後する。)

進行判断(Fable): 上記3はSTOP条件に該当するため、`USER_DECISION_REQUIRED`としてSTOPする。限定flow確認と29件横断(承認済み)は、機械判定の扱いが決まってから1回で行う(2回に分けて費用を重ねない)。Production採用の可否は判断していない。

## 8. 実装・単体確認・再較正(委任_60、2026-10-04、ユーザー決定[4回目]=判断D案1)

- 実装(検証用runner、`FLOOR_VERIFY_MODE`既定`off`): 本書§2-4のF5を比較・時期に限定し、確認2回・逐語引用必須・失敗時BLOCKING固定で実装した。対象=LLM判定が非BLOCKINGでdeterministic floorだけがBLOCKINGにした指摘のうち、trueのfloorフラグが`changed_comparison`/`changed_time`のみ。主体・数値・否定は対象外(決定論のまま)。CONFIRMED(決定論の不一致確認)は維持方向のみ。詳細は`CURRENT_SPEC.md`のOPEN-233節「案1」。
- 判定原則文: V7(3)→V7b(基底R3(e)へ整合)。動機: §0-2を更新、criteria docへ節を追加(動機の帰属=軽微/創作=重大)。
- 単体安全確認(`er052_open233_floor_verify_unit_check_01.py`、¥2.336/23 call): **STOP**。重大期待の合成ケースS1(方向反転「After the plan was withdrawn, oil prices fell.」)が、trial2で確認2回とも非BLOCKING(QUALITY)=解放された。確認の説明は「Ledgerは上げ幅の一時縮小を確認しており、`fell`はその短時間の下落を指すなら矛盾しない」というもの(HF-009の「上げ幅を縮小」を根拠にした)。他: K19=3/3解放、B4「Names…」=2/3解放、B2「vanished overnight」=0/3(引用が逐語でないためBLOCKING固定)。
- 再較正(V7b): 単体確認STOPのため未実施。限定flow・29件横断は未実施。
- Fableへの論点(判断・修正は行っていない): (1)S1型(台帳に下向きの語[縮小]がある方向反転)は、確認promptが禁じた「上昇/下落語が台帳にあるだけ」に近い根拠で解放された。(2)判定原則文の「prices began to fall=軽微」の例が確認Promptに含まれており、方向反転の一部を軽微と読ませている可能性(例示によるpriming)。(3)対策案の例(未実装): 方向を決定論で扱う(台帳の符号と一致しない方向語はCONFIRMED扱い)、確認Promptから例を外す、確認を3回以上にする等。いずれも既存より厳しくなる/ユーザー判断事項のため実装していない。
