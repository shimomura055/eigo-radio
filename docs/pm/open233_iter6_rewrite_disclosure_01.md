# OPEN-233 iteration6 Rewrite挙動 全件開示(委任_18a、read-only分析)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_18a)
作成日: 2026-09-30
性質: **read-only証跡開示分析**。API呼び出しなし、¥0。コード・SSOT・
REPORT・runner は一切編集していない(既存ファイルへの書き込みなし)。
証跡ソース: `er052_output/open233_self_recovery_flow_runner_01_iter6/`
(instances_s1=sample1・29件完走、instances_s2=sample2・26件完走)、
`er052_open233_self_recovery_flow_runner_01.py`(コード行番号引用)、
`er010_ledger_local_rewrite_09.py`(Production局所QA、行番号引用)、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§13/§14/§15/§16、
`docs/pm/design_open233_self_recovery_flow_01.md`§5-7/§5-8/§6、
`docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`。

**方針**: すべての数値・引用は上記ファイルから直接確認したもののみを記載する。
REPORTの記述とinstance jsonの実測値が食い違う箇所は、その食い違い自体を
明記する(隠さない)。「改善見込み」等の抽象表現は避け、コード行・
instance jsonのフィールド値で立証できることと、立証できていないこと
(推定にとどまること)を明確に分ける。

---

## 1-1. 全体Rewrite3件(ladder_level_used="6_full_article")の全件開示

### 1-1-0. 3件の特定(機械確認)

`summary_flow_runner.json`の`instance_results_sample1`/`instance_results_sample2`
を機械走査した結果、`ladder_level_used=="6_full_article"`は以下3件(全て
`rewrite_records`の1エントリ単位でカウント)。

| # | instance | run | claim identity | section | method |
|---|---|---|---|---|---|
| 1 | `safety_er009_changed_number` | sample1(`instances_s1`) | `fact:F-002` | body | `target_not_found+fulltext_fallback` |
| 2 | `safety_er009_changed_number` | sample2(`instances_s2`) | `fact:F-002` | body | `target_not_found+fulltext_fallback` |
| 3 | `safety_er009_unsupported_new_claim` | sample2(`instances_s2`) | `claim:40e72efd1108a93d` | title | `deterministic_delete(rewrite_hint_quote)+fulltext_fallback` |

段落単位(`4_paragraph`)は0件(iteration6/委任_16代表ケース双方で確認済み、
REPORT§15-6/§16-5)。「段落以上でないと直せない」ケースはiter6には存在しない。

### 1-1-1. 共通の根本原因(コード確認、①〜⑤を試したのではなく「locateできず
必然的に⑥へ落ちた」)

`er052_open233_self_recovery_flow_runner_01.py` L1763-1893
(`single_text_rewrite`)の構造:

- L1785: `target_sentence, locate_method = locate_target(claim_text, rewrite_hint, full_text)`
- L1806-1807: `if rewrite_kind != "delete": if found:`(=`target_sentence is not None`)
  の場合のみ、①単語・接続詞(L1817-1820)→③1文(L1821-1827)→④段落
  (L1830-1839、`locate_paragraph_block`成功時のみ)のラダーを試す
  (L1841-1860のforループ)。
- L1861-1862: `else: method_used = "target_not_found"` — **`found=False`の
  場合、①③④のラダーは一切呼ばれない**(forループ自体に入らない)。
- L1864-1885: `guard_ok`計算(`found`がFalseなら無条件で`guard_ok=False`
  [L1865])→ `if not guard_ok:` で水準⑥`FULL_TEXT_FALLBACK`
  (L1871-1883)を実行。

`locate_target`(L1487-1505)は第一キー=`rewrite_hint`内の引用断片
(`extract_quoted_fragment`、L1443-1464)、第二キー=`claim_text`による
`locate_best_sentence`、第三キー=`er010.locate_target_sentence`の3段
フォールバックだが、いずれも失敗すれば`None`を返す。

**結論(3件共通)**: ③=「locateできず必然的に⑥へ落ちた」であり、
「念のため広く直した」わけではない。①〜④は**呼ばれてすらいない**
(コード構造上スキップされる、試行して失敗したのではない)。

### 1-1-2. ケース1・2: `safety_er009_changed_number`(sample1・sample2、両方)

- **問題箇所**: title claim「Researchers studied more than 30 million
  credit card payments...」(Ledger正値は「more than 13 million」)。
  Stage1が`changed_number=true`を検出し、`deterministic_floor:changed_number`
  でBLOCKING確定(`instances_s1/safety_er009_changed_number.json` L12-52)。
  この claim(title、`claim:6ed4d4a0f906cccd`)は①水準
  (`e1_minimal_word_edit`)で**正常に解消**(sample1: L86-94、
  sample2: 同ファイルL86-94相当、`ladder_level_used=1_word_connective`)。
- **⑥に落ちたのは別のclaim**: 同じ数値ズレについて、**precheckが機械的に
  生成した合成マーカー文字列**が別claimとして扱われている
  (`instances_s1/safety_er009_changed_number.json` L54-79):
  `claim_text = "count values found in article not matching any ledger
  fact: [30000000.0]"`、`detected_by: "precheck"`、
  `issue: "precheck detected number_mismatch vs ledger_value=1,300万件超"`、
  `rewrite_hint: "'count values found in article not matching any ledger
  fact: ' を、fact_id=F-002のLedger値へ置換する。..."`。
  この文字列は**記事本文には一言一句存在しない**(precheckの内部表現
  そのもの)。`locate_target`の3段フォールバックいずれもこの文字列を
  記事本文中に発見できるはずがなく、`found=False`→即`target_not_found`→
  ⑥フォールバックへ必然的に到達する。
- **なぜ①〜⑤で直せなかったか**: 試行して失敗したのではなく、**そもそも
  ①③④のラダーが呼ばれていない**(1-1-1参照)。これはprecheckの出力形式
  (「記事内の数値と一致しないLedger値」という機械的な要約文をclaim_textへ
  代入する設計)に起因する構造的な限界であり、Rewrite機構自体の判断ミスでは
  ない。
- **⑥自体の結果(sample1・sample2で明暗が分かれる)**: sample1は
  `fulltext_fallback`後に品質劣化検出v2が`vocab_difficulty_increased_fragment`
  を検出し再生成を1回実施(`quality_degradation_v2_regenerated: true`、
  L156)、再生成後も同じ理由で`needs_regeneration: true`のまま
  (L157-193、解消せず)だが`section_role_violation`は0件(L143-155,
  195-207)で最終的にRecheck PASS。sample2は再生成トリガ自体が発火せず
  (`needs_regeneration: false`、L140)一発でRecheck PASS。
  いずれも最終出力の英文は自然(sample1「Researchers studied over
  13 million credit card transactions...」、sample2「...over 13 million
  credit card payments...」、L221-222/L170-171)で、目視上の破綻はない。
- **コスト**: sample1 ¥0.5472/6call(`safety_er009_changed_number.json`
  L316-318)、sample2 ¥0.4519/4call(再生成なしのため安い)。
- **Fable向け判定**: **③「locate失敗の副作用で本来①〜③で直せたはずが
  ⑥へ回された」**。ただし通常の意味の「①〜④を試したが失敗した」ではなく、
  「precheckの出力設計(claim_textに実article文でなく機械要約文を渡す)が
  ラダーそのものを起動不能にした」という、より根の深い設計上の問題である。
  同じ数値ズレを検出したtitle側claim(Stage1由来)は①水準で正常に解消して
  いるため、**この記事のこの数値ズレ自体は本質的に「最小変更で直せる」
  問題であり、⑥まで必要だったという実測的根拠はない**。

### 1-1-3. ケース3: `safety_er009_unsupported_new_claim`(sample2のみ、
**sample1との対比が重要な発見**)

- **問題箇所**: title(記事全体のtitleが単一文)「The same New York City
  taxi researchers also found that male passengers tipped twice as much
  as female passengers when shown a higher suggested rate.」。Ledgerには
  男女差・「2倍」という数値の裏付けがなく、`unsupported_new_claim=true`で
  BLOCKING(`instances_s2/safety_er009_unsupported_new_claim.json` L12-53)。
  `rewrite_kind="delete"`(claim全体を削除する指示)。
- **sample2(⑥に該当)**: `rewrite_hint`が**claim全体ではなく後半の断片**
  「"male passengers tipped twice as much as female passengers when shown
  a higher suggested rate." Delete this unsupported gender comparison
  ...」を引用(L48)。`locate_target`が`extract_quoted_fragment`で
  この断片を発見(exact substring、titleの一部)し`found=True`となるが、
  `rewrite_kind=="delete"`のため`updated_text = full_text.replace(target_sentence,
  "", 1)`で**断片のみを削除**(L1792-1796)。結果、titleの前半
  「The same New York City taxi researchers also found that .」という
  **破損した半端な文**が残る。`guard_ok`判定(L1864-1865、
  `claim_text.strip() not in updated_text`)は元のclaim全文がもう
  含まれないため通過するはずだが、実際には⑥フォールバックが発動している
  (`method: "deterministic_delete(rewrite_hint_quote)+fulltext_fallback"`)。
  **これは`delete_reoccurrence_detected`(L1801-1802、`locate_best_sentence`
  による削除後の再出現ファジーマッチ)がTrueと判定された可能性が高いと
  推定されるが、中間状態(`found`/`delete_reoccurrence_detected`の実値)は
  instance jsonへ保存されておらず、コードロジックからの推定であり
  実行ログでの直接確認はできていない(立証できない部分として明記する)**。
  結果として⑥へフォールバックし、**最終的にtitleは「...also found that
  passengers shown a higher suggested rate tipped more.」という自然な
  一文に置き換わった**(L127、質は良好、`hook_word_count`25→18語、
  `hook_shrank: false`、L104-110)。
- **sample1(⑥ではなく`0_delete`で「成功」したが、実は最悪の結果)**:
  同じclaim・同じrewrite_hintの構造だが、`instances_s1/
  safety_er009_unsupported_new_claim.json`では`rewrite_hint`が**claim
  全文を引用**(「"The same New York City taxi researchers also found
  that male passengers tipped twice as much as female passengers when
  shown a higher suggested rate." を削除してください。...」L48)。
  この場合`hint_fragment`=claim全文となり、削除対象がtitle全体と一致
  するため、削除後の`updated_text`はtitleが**完全に空文字列**になる
  (`en_text_after_rewrite: ""`、L170)。`guard_ok`はTrue扱いとなり
  (削除後のテキストに元claimが含まれないため)、⑥フォールバックは
  発動せず`ladder_level_used="0_delete"`のまま確定(L65)。
  `section_role_violation`は`hook_shrank: true`
  (`hook_word_count_before: 25 → after: 0`、L104-110)を正しく検出し、
  `quality_degradation_v2_regenerated: true`で再生成を1回試行したが
  (L112)、**再生成後も結果は同一(空文字列のまま、L113-142)**。
  それでも`final_state: "RESOLVED_REWRITE"`・`recheck_overall_status:
  "LEDGER_COMPLIANT"`・`recheck_all_prior_issues_resolved: true`
  (L172-173)として**「解決」扱いで通過している**。つまり**titleが
  空白になった状態が、既存の品質チェックをすり抜けて「成功」と記録
  されている**。
- **Fable向け判定**: この3件目は他の2件と性質が異なる。「locate失敗の
  副作用」という点では共通だが、**より重要な発見は「①〜④のラダーより
  ⑥全体フォールバックの方が実際には安全な結果を生んだ」逆転現象**
  である(sample1の局所削除=title完全消失という重大な品質劣化 vs
  sample2の⑥フォールバック=自然な文への書き換え)。この逆転は
  `rewrite_hint`の引用範囲(claim全文か、その一部断片か)というStage2
  LLMの出力非決定性に起因しており、**「全体Rewriteが不要だった」とは
  単純には言えない**。むしろ「最小変更(削除)がclaim全体=セクション
  全体と一致する場合、削除後の空文字列を検出する専用ガードが既存の
  品質劣化検出v2に欠けている」という**別の未解決バグ**が実測で確認
  された(§1-1-4参照、新規発見・未修正)。

### 1-1-4. 新規発見(未修正、Fableへの報告事項): title全文削除→空文字列の
検出漏れ

`instances_s1/safety_er009_unsupported_new_claim.json`のsample1実行で、
`en_text_after_rewrite: ""`(タイトルが完全に空)にもかかわらず、
`quality_degradation_v2.needs_regeneration: false`
(L96、理由: `vocab_difficulty_increased`系のみを見る指標のため、
「文字数0」自体は検出条件に含まれない)、`section_role_violation.
section_role_violated: true`(`hook_shrank: true`は検出、L109)だが
**この検出結果自体が最終的な`resolved`判定を覆していない**
(`quality_degradation_v2_regenerated: true`で再生成は試みるが、
再生成結果が同じ空文字列でも「再生成した」という事実だけで先へ進み、
`recheck_overall_status: LEDGER_COMPLIANT`で最終的にPASS扱いになる)。
**これはこの委任のスコープ外(read-only分析)のため修正は行っていない
が、量産導入判断の前に埋めるべき明確なガード漏れとして報告する**
(削除型Rewriteの対象がセクション全体と一致する場合、削除後の空文字列を
即座にblockingとして扱うガードが必要)。

### 1-1-5. 三択の結果集計

| # | instance/run | 判定 |
|---|---|---|
| 1 | changed_number sample1 | ③locate失敗の副作用(本来①で直った可能性が高い、title側の同種claimは実際に①で解消) |
| 2 | changed_number sample2 | ③locate失敗の副作用(同上) |
| 3 | unsupported_new_claim sample2 | ③locate失敗の副作用、かつ**結果的には⑥の方が①より安全**(sample1の①相当[0_delete]がtitle完全消失という重大劣化を起こした) |

**3/3が「必要だった」ではなく「locate失敗の副作用」**。全体Rewrite経路
そのものを残す前提(「広範囲の問題には⑥が必要」)を裏付ける実測根拠は
iter6の3件には存在しない。一方で、ケース3が示すように**⑥を単純に
禁止・縮小することが常に安全とは限らない**(局所削除がセクション全体を
消してしまう退化ケースの安全網としては機能した)。したがって
「locateロジックの精度改善(precheckのclaim_text設計・delete型の
範囲判定)」が優先課題であり、「⑥経路自体の削除」は推奨しない。

---

## 1-2. 不要Rewrite4件(negative群、v2訂正後)の全件開示+解決策

### 1-2-0. 分母・分子の再確定

`er052_open233_self_recovery_flow_runner_01.py` L188-190で
`NORMAL_GROUP_INSTANCE_IDS = negative全7件(neg1〜neg7) ∪
{hormuz_run03_advanced, meta_run03_advanced}` = **9件**(分母)。
L3007で`UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS =
{"neg5_hormuz_div_a2"}`が明示的にハードコードされている
(REPORT§13-1のOpus L2 #3訂正1を反映済み、neg5はB3と同一claim
[「so the flashy 20% plan left the stage」]で正しくBLOCKING維持の
ため不要Rewrite計上から除外)。**分母9・分子4は既にneg5訂正済みの
数値であり、これ以上の過大計上はない**(iter6のunnecessary_rewrite_v3、
sample1: `meta_run03_advanced`/`neg1_meta_b3prod_a2`/
`neg2_meta_refresh_a2`/`neg3_hormuz_prodrunner_b1b`の4件=44.44%)。

### 1-2-1. neg1_meta_b3prod_a2

- **対象記事**: `instances_s1/neg1_meta_b3prod_a2.json`(sample1)。
  **重要**: sample1は`final_state: "STAGE4_ESCALATION"`
  (`stage4_reason: "cycle_limit_exhausted"`、L5-6)であり、**単なる
  「不要な1回のRewrite」ではなく、cycle1→2→3と3回のRewrite試行を
  経てなお解消できず人間確認へ至った、より深刻な事例**である
  (total_cost ¥2.6857/13call、L654-656)。
- **BLOCKING claim(cycle1)**: 「"A call seemed to come from an AI
  agent. But as the conversation went on, the voice was not AI at all.
  It was a person. Meta had run a test that caused exactly this
  surprise."」(L12)。フラグ: `changed_fact=true, changed_certainty=true,
  unsupported_new_claim=true`(L19-28)。section_type="hook"(L52)。
- **本来なぜRewrite不要だったか**: 2026-09-30ユーザー新方針item2の
  基準「確認済みFactから自然に導ける演出・解釈は許容、新しい具体的
  Factの発明はNG」に照らすと編集判断の余地がある(監査文書
  `docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md` §A-1-3参照)。
  Ledgerは「訓練された契約労働者がMuse通話の一部に対応した」ことは
  確認しているが、「受信者がAIだと思い込み、後で驚いた」という個別の
  主観的体験までは確認していない。ユーザーは「Rewrite不要だった可能性
  が高い」と直感しているが、**監査文書は「Hook-aware判定を適用しても
  このケースは変わらなかった」と机上確認済み**(HOOK_CLAUSEの緩和対象は
  changed_scope/changed_comparisonの2種類のみで、neg1の実フラグ
  [changed_fact/changed_certainty/unsupported_new_claim]はいずれも
  対象外)。つまり「不要だった」という判断自体は**Trial上の正解ラベル
  として未確定**であり、本委任はFableへの判定材料提示にとどめる
  (§2 Fable判定の範囲外の緩和は独自に行わない)。
- **どの処理がRewriteへ送ったか**: `floor_reason: null`(floor起因では
  ない)。`basis: "unsupported_relationship"`。`stage2_two_of_two_log`
  (L59-66)で`first_materiality: BLOCKING`・`second_materiality:
  BLOCKING`→`"BLOCKING(both agree)"`。**2-of-2の両呼び出しが一貫して
  BLOCKINGと判定**しており、単発run非決定性の産物ではない
  (`stage2_two_of_two_eligible`、L1431-1436、`floor_reason is None`
  かつ`NORMAL_GROUP_INSTANCE_IDS`所属の条件を満たすため2-of-2が発火)。
- **原因分類**: Hook誤判定(section_type="hook"/"title"の物語的演出を
  Stage2 LLMが独立に2回ともBLOCKINGと判定)。数値丸め・JA-EN対応処理
  はいずれも該当しない。
- **本来止められたはずの段階**: 2-of-2自体はfail-closed設計どおり
  正しく機能している(判定が安定していることを確認する機構であり、
  判定内容そのものを緩めるものではない)。止めるとすれば**Stage2の
  判定基準自体**(rubric)しかない。
- **解決策候補**: 委任_17で実装中とされる「Hook専用Stage2(title/hook
  claimだけ別promptで判定、本文rubric不変)」は、**section_type="hook"/
  "title"のこのclaimには構造的に適用対象**であり、委任_16のB-2
  (RUBRIC_R4_HOOK_AWARE、既存Stage2 promptへの追記型)が起こした
  Safety-critical回帰(`bgroup_B3`誤降格、REPORT§16-4/§6-4)とは
  **アーキテクチャが異なる**(promptを完全に分離するため、
  body/in_one_line claimがHook-awareプロンプトへ一切触れない設計で
  あれば、委任_16で観測された「無関係なsection_typeへの寛容化バイアス
  波及[prompt priming]」は構造的に起こりにくいと推定できる)。
  **ただし、これは推定であり、実測での確認(Safety-critical 10 claimへの
  regressionテスト込み)は本委任の範囲外(read-only)のため実施して
  いない。委任_17の実装・検証結果を見るまでは「解消見込み」と断定
  できない**。
- **B3への影響**: B3(`bgroup_B3`、item4のflagship例)は本委任時点で
  `section_type`が過去に"in_one_line"と判定されたことがある
  (REPORT§16-4)。Hook専用Stage2がtitle/hookの2種類のみに限定される
  設計であれば、B3(in_one_line)は対象外となり直接の再発リスクは
  低いと推定されるが、これも実測未確認。

### 1-2-2. neg2_meta_refresh_a2

- **対象記事**: `instances_s1/neg2_meta_refresh_a2.json`。
  `final_state: "RESOLVED_REWRITE"`(L5)、¥1.3339/7call(L322-324)。
- **BLOCKING claim**: 「"They enjoyed the ease of AI. But they did not
  know that a human was on the other end."」(L12)。フラグ:
  `changed_fact=true, changed_certainty=true, unsupported_new_claim=true`
  (L19-28)。`related_fact_id: "MUSE-HC-012"`(L14)。section_type="body"
  (L52)。
- **本来なぜRewrite不要だったか**: Ledgerは「適切な開示なしにテストが
  始まった」ことを確認しているのみで、利用者の主観的認識
  (「楽しんでいた」「気づかなかった」)までは確認していない
  (`issue`、L17)。この記事内の他claimと同一パターン(§1-2-4参照)。
- **どの処理がRewriteへ送ったか**: `floor_reason: null`。
  `stage2_two_of_two_log`(L59-66)で両呼び出しBLOCKING一致
  (`"BLOCKING(both agree)"`)。neg1と同型のStage2 LLM安定判定。
- **原因分類**: 自然な解釈の過剰BLOCK(数値丸め・Hook・JA-EN対応の
  いずれでもない、body文の主観的認識に関する判定)。
- **本来止められたはずの段階**: Stage2のrubric自体(2-of-2は機能済み、
  判定基準の較正が必要)。
- **解決策**: neg2・meta_run03_advanced(§1-2-3)・meta_run03_standard
  (STAGE4、§1-3)の**3件が全て同一Ledger fact「MUSE-HC-012」かつ
  同一パターン**(「テストが適切な開示なしに始まった」という確認済み
  条件から、「利用者は実際に気づかなかった/知らなかった」という
  帰結を導く記述)でBLOCKINGと判定されている
  (§1-2-4で詳述)。この3件は**Hook専用Stage2では解決しない**
  (section_type="body"、title/hookではない)。**Stage2 rubricに
  「Ledgerが開示不備を確認している場合、『読者/利用者はその時点で
  相手を知る手段がなかった』という論理的帰結は新しい主観的事実の
  発明ではなく、確認済み条件からの自然な導出として許容する」という
  条件を追加する案が考えられるが、これは本委任のスコープ外
  (Production/Trial rubric変更は`APPROVED_FOR_PRODUCTION`相当の
  仕様判断)であり、実装は行っていない。Fable/ユーザーの判断が必要**。
- **Safety-critical 10claimへの影響検討**: `SAFETY_CRITICAL_SUB_IDS`
  に該当するclaim群のうち、「利用者の主観的認識」を扱うものがあるか
  どうかは本委任では個別に照合していない(次委任での要検証事項)。
  一般に「開示不備→気づけなかった」という論理的帰結を許容する条件は、
  「気づいた/驚いた」という**逆方向の断定**(neg1のパターン)には
  適用されないよう、条件の方向性(否定形のみ許容、肯定形の主観断定は
  従来通りBLOCKING)を明確にする必要がある。

### 1-2-3. meta_run03_advanced

- **対象記事**: `instances_s1/meta_run03_advanced.json`。
  `final_state: "RESOLVED_REWRITE"`、¥1.3042/7call。
- **BLOCKING claim**: 「"If this was not properly explained, users had
  no way to know whether they were talking to AI or a person. ..."」
  (先頭110字)。フラグ: `changed_fact=true, changed_certainty=true,
  unsupported_new_claim=true`。`related_fact_id: "MUSE-HC-012"`。
  section_type="body"。`floor_reason: null`。
- **どの処理がRewriteへ送ったか**: `basis: "unsupported_relationship"`、
  `rewrite_records`で`mechanism: "paired_ja_en(J-1)"`、
  `ladder_level_used: "paired_j1_not_laddered"`
  (JA→EN対訳ペア[origin未確認、要`origin`フィールド再確認]のため
  J-1経路を通過、段落単位で書き換え)。
- **原因分類**: neg2と完全同一パターン(MUSE-HC-012、「開示不備→
  気づけなかった」を新規主観断定として過剰BLOCK)。
- **解決策**: §1-2-2と同一(Stage2 rubricの条件追加、未実装)。

### 1-2-4. neg3_hormuz_prodrunner_b1b

- **対象記事**: `instances_s1/neg3_hormuz_prodrunner_b1b.json`。
  `final_state: "RESOLVED_REWRITE"`、¥0.7083/5call。
- **BLOCKING claim**: 「"The fee plan left the stage, but the events
  driving oil prices—and the prices themselves—quickly returned."」。
  フラグ: `changed_fact=true, changed_causality=true, changed_time=true,
  unsupported_new_claim=true`。`related_fact_id: "HF-009"`。
  section_type="in_one_line"。
- **本来なぜRewrite不要だったか(または不要でなかったか)**:
  `issue`(コード確認): 「The sentence describes the events as having
  quickly returned and as driving oil prices, whereas HF-009 reports
  that relevant attacks, blockade and tanker-safety concerns continued
  during the price movement. It changes continued events into
  returning events and asserts a causal role not established by the
  Ledger.」。**`llm_materiality: "BLOCKING"`**(floor無しでもLLM自身が
  独立にBLOCKINGと判定)。
- **どの処理がRewriteへ送ったか**: `floor_reason:
  "deterministic_floor:changed_time"`(floor起因、`FLOOR_FLAGS`に
  `changed_time`が含まれるため無条件BLOCKING強制)。ただし**llm_materiality
  自体も既にBLOCKING**であり、floorが「LLMの正しいQUALITY判定を上書き
  した」わけではない(iteration4/5報告[REPORT§14-3(a)]で挙げられた
  「floorがLLMのQUALITY判定を強制的にBLOCKINGへ上書きした」パターンとは
  **iter6のこのケースでは一致しない**。floor起因のためこのclaimは
  `stage2_two_of_two_eligible`の条件[L1434 `floor_reason is None`]を
  満たさず、2-of-2による安定化確認自体が行われていない[L1432-1436、
  コード確認])。
- **重要な追加発見(REPORTとの食い違い)**: REPORT§14-3(iteration4/5の
  分類)はneg3を「floor起因、LLM自体はQUALITY/ACCEPTABLEと正しく判定して
  いたのにfloorが上書きした」と分類しているが、**iter6のこのinstance
  jsonでは`llm_materiality: "BLOCKING"`であり、LLM自身も独立にBLOCKING
  と判定している**。これは同一claim文言に対してLLMの判定が
  iteration間で非決定的だったことを示す(iter4/5ではQUALITY、iter6では
  BLOCKING)。**floorを緩めるだけではこのclaimの過剰BLOCKは解消しない
  可能性がある**(LLM自身が独立にBLOCKINGと判断する run も存在するため)。
- **原因分類**: 数値/時制の解釈差(「quickly returned」という表現が
  Ledgerの「continued」と矛盾するとLLMが解釈)。Hook・JA-EN対応processing
  はいずれも該当しない。floor起因ではあるが、floorが誤りだったとは
  断定できない(LLM自身も同意見のrunがある)。
- **本来止められたはずの段階**: 不明確(floorとLLM判定が一致しているため、
  「どこで止めるべきだったか」の特定自体が難しい。もしこの表現が編集上
  許容範囲だとFableが判断するなら、Stage2 rubricの`changed_time`解釈
  基準そのものの見直しが必要で、floor単体の問題ではない)。
- **解決策**: 本委任では確定的な解決策を提示できない(iteration間で
  LLM判定が割れているため、単純なfloor緩和やrubric一箇所修正では
  再現性のある解消が保証できない)。次委任でこのclaim単体のn=3以上の
  再現性測定(Stage2 LLM判定のブレ幅の実測)を行うことを推奨する。

### 1-2-5. Hook誤判定分類の解消見込みまとめ

| instance | 原因分類 | 委任_17(Hook専用Stage2)で解消見込みか |
|---|---|---|
| neg1_meta_b3prod_a2 | Hook誤判定(section_type=hook/title) | **対象**(構造的に適用範囲内だが実測未確認) |
| neg2_meta_refresh_a2 | 自然な解釈の過剰BLOCK(MUSE-HC-012パターン、body) | **対象外**(section_type=body、Hook専用Stage2の範囲外) |
| meta_run03_advanced | 同上(MUSE-HC-012パターン、body) | **対象外**(同上) |
| neg3_hormuz_prodrunner_b1b | floor+LLM独立判定一致(changed_time解釈) | **対象外**(section_type=in_one_line、かつfloor起因) |

**4件中委任_17で解消見込みがあるのは1件(neg1)のみ、かつ実測未確認。
残り3件中2件(neg2/meta_run03_advanced)はMUSE-HC-012パターンという
共通の未実装rubric条件で解消しうるが未実装。neg3は原因自体が
iteration間で非決定的であり単純な解消策が見えていない。**

---

## 1-3. 人間確認残存(real_run Escalation 2/12 run)の原因+自動解決策

### 1-3-0. 対象の特定

REPORT§15-8の定義どおり、`real_run`はHormuz/Meta実データ由来の6
instance(`hormuz_run01_advanced`/`hormuz_run02_advanced`/
`hormuz_run03_advanced`/`hormuz_run03_standard`/`meta_run03_advanced`/
`meta_run03_standard`)×2 sample=12 instance-run。この定義に基づき
2/12がSTAGE4_ESCALATIONに至ったのは`meta_run03_standard`のsample1・
sample2の**両方**(`meta_run03_advanced`は両sampleとも
`RESOLVED_REWRITE`、機械確認済み)。

### 1-3-1. sample1: `same_claim_fact_id_reblocked`

`instances_s1/meta_run03_standard.json`:

- **cycle1**でclaim「"They did not realize it."」(`related_fact_id:
  "MUSE-HC-012"`)がBLOCKING、`rewrite_records`で
  `mechanism: "paired_ja_en(J-1)"`・`method: "j1_paired_rewrite_paragraph"`・
  `ladder_level_used: "paired_j1_not_laddered"`(段落単位で書き換え)。
- **実際の差分(EN)**: 書き換え前「...If no one explained this clearly,
  users could not know. They could not tell if it was AI or a person.
  They enjoyed AI's convenience, but a human was on the other end.
  **They did not realize it.** That was happening behind the
  scenes...」→書き換え後「...The test began without a clear
  explanation. **They enjoyed AI's convenience, but a human was on the
  other end. They did not realize it.** That was happening behind the
  scenes...」。**Rewriteは直前の文("If no one explained...")を
  差し替えたが、実際にBLOCKINGとフラグされた"They did not realize
  it."自体は一字一句変更されずに残った**(全文比較で確認済み)。
- **cycle2**で全く同じclaim(`related_fact_id: "MUSE-HC-012"`、
  claim_text完全一致)が再度BLOCKINGと判定され、`repeat_claim_ids:
  ["fact:MUSE-HC-012"]`(L…、コード上は`er052_open233_self_recovery_
  flow_runner_01.py` L2475-2480の`matched_records`ロジックが発火)、
  cycle残数に関わらず即STAGE4(`same_claim_fact_id_reblocked`)。
- **なぜ自動解決できなかったか**: J-1(paired_rewrite)が**段落単位の
  自由書き換え**(未ラダー化、design書§5-7既知の限界)であり、
  「どの文を修正すべきか」をモデルの自由裁量に任せていたため、
  意図とは異なる隣接文を修正して肝心の被フラグ文を素通りさせた。
  これはcycle上限やcite-or-release以前の、**Rewrite自体の精度問題**
  であり、既存のfail-closed再検出ルール(A7、design書§6-1)は
  「正しく」機能している(同一claimの再出現を見逃さず即座に人間確認へ
  回した)。

### 1-3-2. sample2: `cycle_limit_exhausted`

`instances_s2/meta_run03_standard.json`:

- cycle1で同じくMUSE-HC-010/MUSE-HC-012の2claimがBLOCKING、
  MUSE-HC-010は①水準、MUSE-HC-012はJ-1段落単位で対応、**この回は
  MUSE-HC-012が解消**(cycle2に再出現しない)。
- cycle2で**新規claim**「"It said human staff made inappropriate
  comments about race during calls. These calls were about trying to
  lower internet or cable fees."」(`related_fact_id: "MUSE-HC-011"`)
  がBLOCKING、①水準で対応。
- cycle3で**同一fact_id(MUSE-HC-011)だが異なる文言の断片**
  「"These calls were about trying to lower internet or cable fees."」
  が再度BLOCKING。`claim_text`が完全一致ではない(部分文字列)ため
  `same_claim_fact_id_reblocked`の完全一致判定にはかからず
  (コード上の識別は`claim_identity`関数依存、本委任では完全一致条件の
  詳細まで再現確認していない)、代わりに`cycle > MAX_CYCLES`
  (L2483-2495)で`cycle_limit_exhausted`に至った。
- **なぜ自動解決できなかったか**: sample1とは異なる経路
  (①水準の局所編集自体は正確に対象文を修正しているが、同一fact_idの
  claimが**記事内の別の箇所・別の文言表現**で繰り返し検出される、
  design書§6-4で言及される「fact_id複数箇所Rewrite」[item8、
  Phase2課題として凍結中]そのもの)。

### 1-3-3. 同一記事の繰り返しか

**Yes**。sample1・sample2いずれも`meta_run03_standard`という同一記事
(standard版)であり、fact `MUSE-HC-012`(sample1)・`MUSE-HC-011`
(sample2)という異なるfactではあるが、いずれも「AI通話の実態開示
不備」というこの記事固有の複数箇所に分散したLedger事実(HC-010/
011/012)を扱う構造自体が、cycle上限・同一claim再検出のいずれの
安全装置にも引っかかりやすい記事だと言える。

### 1-3-4. 委任_16/_17による解消見込み

- **委任_16のJ-1ラダー化(B-1、design書§5-8)**: sample1の
  `same_claim_fact_id_reblocked`原因(J-1段落単位の自由書き換えが
  被フラグ文自体を素通りした)に対して、①単語・接続詞水準
  (`J1_MINIMAL_WORD_PROMPT_TEMPLATE`)が先に試されれば、対象文
  ("They did not realize it.")そのものへより直接的な編集が
  行われる可能性が高いと推定できる。**ただし、この推定はコード設計
  からの論理的帰結であり、meta_run03_standard自体(またはMUSE-HC-012の
  この具体的claim)でのJ-1ラダー実測検証は行われていない**
  (委任_16の代表ケースTrialは`bgroup_B3`1件のみで検証、REPORT§16-4)。
  実測なしに「解消する」と断定することはできない。
- **委任_17のHook専用Stage2**: 両claim(MUSE-HC-012、MUSE-HC-011)の
  section_typeは"body"であり、**Hook専用Stage2(title/hookのみ対象)の
  範囲外**。この2件の解消には寄与しない。
- **sample2のfact_id複数箇所Rewrite(item8)**: design書で
  「Phase2設計課題として明示的に凍結」されている未着手項目
  (REPORT§14-5)。委任_16/_17のいずれにも含まれない。**別途の設計・
  実装が必要**。

### 1-3-5. 結論

2件のSTAGE4は異なるメカニズム起因(sample1=J-1の対象文特定の不正確さ、
sample2=fact_id複数箇所への分散)であり、**単一の修正では両方を
解消できない**。委任_16のJ-1ラダー化はsample1型には有効な可能性が
あるが未実測、sample2型(fact_id複数箇所)には対応する実装がまだ存在
しない。

---

## 1-4. 局所QA未統合の理由説明

### 1-4-1. Production局所QA(`er010_ledger_local_rewrite_09.py`)の実装内容

| 要素 | 関数/定数 | 行番号 | 内容 |
|---|---|---|---|
| 対象文特定 | `extract_point_context` | L97-114 | `target_sentence`が属する見出し区切りsection全文を返す(前後文単位ではなくsection単位) |
| 対象文/前後1文の役割分離判定 | `classify_deviation_role` | L211-235 | Ledger Deviation Checkerが引用した逸脱箇所が対象文/before/after/曖昧のどれに属するか判定(exact substring→word-overlap、閾値`_ROLE_MATCH_THRESHOLD=0.25`・tie判定`_ROLE_TIE_MARGIN=0.05`、L196-197) |
| 対象文単位のstatus再計算 | `evaluate_target_sentence_status` | L238-273 | window全体のcheck_resultから対象文に対応するdeviationのみを抽出し、対象文単位のoverall_statusを算出。曖昧なdeviationが1件でもあれば安全側でwindow全体statusへフォールバック(`match_fallback=True`) |
| Fact Checker A'差分QA | `run_diff_qa_for_accepted_rewrite` | L289-333 | Rewrite受理直後、対象文+前後1文をFact Checker A'(web_search込み)とLedger Deviation Checker(hook_aware=True)へ再投入 |
| 受理/不受理の機械判定 | `apply_diff_qa_to_resolved_rewrite` | L336-358 | `blocks_acceptance`(fc_verdict=='FAIL' or ledger_eval=='LEDGER_DEVIATION')がTrueなら`resolved=False`・`human_review_required=True`へ書き換え |
| retry上限 | `MAX_REWRITE_ATTEMPTS=3`/`MAX_REWRITE_CYCLES=3` | L29/L38 | 文単位3回・記事全体3cycleの二軸上限 |

### 1-4-2. OPEN-233との対応表(目的・入力範囲・call数・単価・非決定性)

| 観点 | Production局所QA(er010) | OPEN-233 Recheck(`run_recheck`) |
|---|---|---|
| 目的 | 修正文の局所的な安全性確認(対象文+前後1文のwindow) | 記事全体がLedger準拠かの再確認+`prior_issues`個別解消確認 |
| 入力範囲 | window(`extract_point_context`のsection単位、またはbefore/after各1文) | 記事全文 |
| call数 | Rewrite本体(最大3attempt)+差分QA1回(`DIFF_QA_CALLS_PER_ITEM=1`、L286) | Rewrite本体(ラダー段数分)+記事全文Recheck1回/cycle |
| 単価(iter6実測、sample1平均) | (Production側は本委任で実測していない、Trial側の推定に留まる) | `stage1_recheck`: 平均¥0.3600/call(35 call中、§1-5参照) |
| 非決定性 | window版Ledger Checkerもhook_aware=True一本(切り替えなし) | Stage1 Recheck自体はV4A同一promptだが記事全文を毎回再解釈するため、cycle間で異なる箇所を拾うことがある(§1-4-4参照) |

### 1-4-3. なぜOPEN-233で局所QAを使わなかったのか(文書引用)

`docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md` §A-2の表
(既存、本委任では新規調査なし、既存文書の引用のみ):

- **Fact Checker A'(web_search)差分QA**: 「web_search呼び出しは
  コスト・所要時間が不確定なため、本委任のGuardrail(¥65)内では
  新規追加を見送った」(§A-2表)。
- **`evaluate_target_sentence_status`型の対象文/隣接文分離判定**:
  「全文recheckアーキテクチャ自体の変更が必要でスコープが大きい」
  (§A-2表)。「cite-or-release(`remaining_sentence`必須化、委任_13)は
  『未解消の根拠となる文』を機械検証する点で類似の目的を部分的に
  カバーしているが、対象文/隣接文の分離そのものではない」。

**この判断根拠自体は本委任で新規検証していない(既存監査文書の記述を
そのまま引用)。予算制約・スコープ制約が理由として明記されており、
技術的に不可能だったとは書かれていない。**

### 1-4-4. 三分類(関数名レベル、既存監査doc A-2まとめの再掲)

- **そのまま使える(既に使っている)**: 記事全体cycle上限
  (`MAX_CYCLES`/`HARD_MAX_CYCLES`、既存踏襲)、fail-closed retry上限
  到達時のSTAGE4_ESCALATION、`prior_issues`による個別解消確認。
- **拡張すべき(委任_14/_16で実施済み)**: 文単位escalationの段数
  (3段階→最小変更ラダー4水準、B-3/B-1)。
- **新規が必要(未着手)**: (1) Fact Checker A' web_search差分QA相当
  (対象文+前後1文へのfact_check再投入)、(2)
  `evaluate_target_sentence_status`型の対象文/隣接文分離判定
  (全文recheckのoverall_statusを対象claimに紐づくdeviationのみへ
  絞り込む機構)。

### 1-4-5. 提案: 基本形に対し全文Recheckが本当に必要になる条件

基本形「最小修正→修正文+前後文確認→問題解消・周辺影響なしなら終了」
に対し、**iter6の29 instance×2 sample(sample1 29件+sample2 26件=
55 instance-run)のうち、cycleが2以上ある11 instance-runの
claim識別子をcycle間で機械追跡した結果**(read-only、既存jsonのみ
参照、新規API呼び出しなし):

| instance/run | cycle2以降で真に新規のclaim(fact_id)が出現したか |
|---|---|
| `bgroup_B4` s1 | なし(cycle2/3とも既出claimの再検出のみ) |
| `meta_run03_standard` s1 | なし(cycle2は既出MUSE-HC-012の再検出、§1-3-1) |
| `neg1_meta_b3prod_a2` s1 | cycle2で`MUSE-HC-008`が新規出現(ただし`materiality: QUALITY`、非BLOCKINGのためRewriteは誘発せず) |
| **`safety_A2A3` s1** | **cycle2で`HF-009`・`HF-002`の2件が新規出現**(cycle1はHF-003/HF-006のみ) |
| `safety_A4` s1 | なし(cycle2/3とも既出claimの再検出のみ) |
| **`safety_A5` s1** | **cycle2で`MUSE-HC-014`が新規出現**(cycle1はMUSE-HC-012のみ) |
| `safety_er009_changed_time` s1 | cycle2で`fact:F-004`表記に変わるが、cycle1のclaim(生text表記)と同一問題の識別子表記違いの可能性が高く、真に別問題かは本委任では未確定 |
| `bgroup_B4` s2 | なし |
| **`meta_run03_standard` s2** | **cycle2で`MUSE-HC-011`が新規出現**(cycle1はMUSE-HC-010/012のみ、§1-3-2) |
| `neg1_meta_b3prod_a2` s2 | なし |
| **`safety_A2A3` s2** | **cycle2で`HF-009`が新規出現**(s1と同一傾向、再現性あり) |
| `safety_A4` s2 | なし |
| `safety_er009_changed_scope` s2 | cycle2で`fact:F-004`表記(changed_timeケースと同型の表記揺れの可能性) |

**結論**: 55 instance-run中、少なくとも**4件(safety_A2A3×2run、
safety_A5×1run、meta_run03_standard s2×1run)で、全文Recheckが
cycle1のRewrite対象とは異なるLedger fact由来の新規BLOCKING claimを
検出した**(0件ではない、実測)。うち3件は**Safety群**
(`safety_A2A3`/`safety_A5`)であり、Safety-critical claimの見逃し
防止という観点では全文Recheckが実際に機能した証拠がある。
**ただし、この新規claimが元のRewrite箇所から物理的に近接した段落
(局所QAのwindowでも拾えた範囲)だったか、記事の別セクションだったか
までは、本委任の残り時間内では記事全文を突き合わせての確認が
できておらず未確定**(立証できない部分として明記)。

**それ以外(9/13 instance-run)では、cycle2以降に検出されたclaimは
すべて「cycle1で既にBLOCKINGだった同一claim(または同一fact_id)の
再出現」であり、これらは対象文+前後1文の局所チェックでも同等に
検出できた可能性が高い**(特に`meta_run03_standard` s1は、被フラグ
文自体が一字一句変更されていなかったことを§1-3-1で直接確認済み)。

**コスト比較**: 全文Recheck(`stage1_recheck`)の実測単価は平均
¥0.3600/call(sample1、35 call、§1-5参照)。局所QA相当
(Fact Checker A' + window Ledger Checker)の単価はOPEN-233側で
実装・計測していないため、本委任では見積り不能(Production
`er010`側でも単価の分離集計は行われていない)。

---

## 1-5. コストcall内訳(iter6実測、sample1・n=29)

`instances_s1/*.json`の`call_log`全168件(`qcd.total_calls`と一致、
`total_cost_jpy`合計¥30.8348で`qcd.total_cost_jpy`と一致)を
`recovery_stage`(および`label`内のregen/2of2/fulltext_fallback表記)で
機械分類した実測値:

| call種別 | 回数 | 平均単価(¥) | 合計(¥) | 1記事あたり平均回数(n=29) | 目的 | 省略時の悪化(実測に基づく) | より安い代替の有無 |
|---|---|---|---|---|---|---|---|
| `stage1_recheck` | 35 | 0.3600 | 12.5997 | 1.207 | Rewrite後の記事全文再チェック+`prior_issues`解消確認 | §1-4-5で実測: 少なくとも4/13 cycle≥2 instance-runで新規BLOCKING claimを検出(うち3件Safety群) | 局所QA(未実装、単価未計測) |
| `stage2_second_judge` | 35 | 0.1714 | 5.9973 | 1.207 | Stage1で検出されたclaimの2段階目materiality判定 | 省略するとStage1単独判定に戻り、Safety側floor以外の誤BLOCK/誤PASSを検出する仕組みがなくなる | なし(Trial設計上の核) |
| `stage3_rewrite`(初回、ラダー①③④) | 41 | 0.1026 | 4.2072 | 1.414 | 最小変更ラダーでの局所Rewrite本体 | 省略すると自動修復自体が不可能(手動編集必須) | なし |
| `stage3_rewrite_regen`(品質劣化検出v2再生成) | 30 | 0.1216 | 3.6494 | 1.034 | 語彙難化等の品質劣化検出後の再生成試行 | REPORT§15-10実測: 再生成の効果は限定的(iter5実測で0/3・2/5解消のみ、iter6個別事例[§1-1-2]でも再生成後も同一結果のケースあり) | 効果が限定的なため、トリガ条件の精緻化で回数削減の余地がある可能性(未検証) |
| `ja_en_equivalence` | 10 | 0.1206 | 1.2056 | 0.345 | J-1(paired rewrite)後のJA/EN対訳等価性QA | FAIL 0件(iter5から継続する改善、REPORT§13-3)、REVIEW_REQUIRED 9/10(記録のみ、通過) | なし(J-1使用時のみ発火、非J-1記事では¥0) |
| `stage3_rewrite_fulltext_fallback`(水準⑥) | 7 | 0.1776 | 1.2430 | 0.241 | locate失敗時の全文フォールバック | §1-1で詳述: 3件中3件がlocate失敗の副作用、locateロジック改善で回数削減の余地がある可能性(未検証) | locate精度向上(未実装) |
| `stage2_second_judge_2of2` | 5 | 0.1274 | 0.6369 | 0.172 | Normal群かつfloor不発火のBLOCKING claimの安定化再確認 | REPORT§14-4実測(iter5時点): 46%がdowngrade(2回目でQUALITY/ACCEPTABLEへ反転)、Stage2単発判定の非決定性が不要Rewriteを誘発していたことを裏付ける | なし(fail-closed側のみ機能、緩和なし) |
| `stage1_initial`(fresh Stage1) | 3 | 0.3020 | 0.9061 | 0.103 | Stage1未reuse時の初回Ledger Deviation Check | 大半の instance は既存fixtureをreuseし¥0(29件中26件はfresh callなし) | reuse可能な限り¥0 |
| `stage1_recheck_confirm` | 2 | 0.1948 | 0.3896 | 0.069 | cite-or-release(`remaining_sentence`機械検証) | REPORT§14-4実測: 根拠のない「未解消」判定でのSTAGE4誤生成を防止(release 0件=誤生成は起きていない) | なし |

**合計**: 168 call、¥30.8348、記事あたり平均¥1.0633(`qcd.avg_cost_per_instance_jpy`と一致)。
**最も高コストな2種**は`stage1_recheck`(合計の41%)と
`stage2_second_judge`(合計の19%)で、両方合わせて全体の60%を占める。
局所QA(§1-4)導入時の主な削減余地は`stage1_recheck`(全文再チェックを
window単位に縮小できれば単価が下がる可能性、ただし§1-4-5の4件は
全文チェックが必要だった可能性が高く、全廃はできない)。

---

## 2. Fable向け集計サマリ

### 1-1(全体Rewrite3件)
3/3が「locate失敗の副作用」(precheck合成マーカー文字列2件+delete型が
claim全体=セクション全体と一致した1件)。「広範囲の問題には⑥が
本質的に必要だった」という実測根拠は0件。ただしケース3(sample1対比)は
「⑥の方が①より安全だった」逆転現象を示しており、⑥経路自体の削除は
推奨しない。**新規発見(未修正)**: 削除型Rewriteがセクション全体と
一致した場合の空文字列検出漏れ(§1-1-4)。

### 1-2(不要Rewrite4件)
原因分類: Hook誤判定1件(neg1、委任_17で対象内だが実測未確認)、
自然な解釈の過剰BLOCK2件(neg2/meta_run03_advanced、共通パターン
[MUSE-HC-012、開示不備→気づけなかった]、未実装のrubric条件候補あり)、
floor+LLM独立一致1件(neg3、iteration間でLLM判定が非決定的、解決策
未確定)。委任_17のHook専用Stage2で解消見込みがあるのは4件中1件のみ。

### 1-3(real_run Escalation 2/12)
両方とも`meta_run03_standard`(sample1=J-1段落rewriteが被フラグ文を
素通り[実測確認済み]、sample2=fact_id複数箇所への分散[item8、
Phase2課題として凍結中])。委任_16のJ-1ラダー化はsample1型に有効な
可能性があるが未実測。sample2型は対応する実装が存在しない。

### 1-4(局所QA未統合)
Production `er010`のQA要素5つのうち2つ(全体cycle上限、
prior_issues個別解消)はそのまま再利用済み、1つ(escalation段数)は
拡張済み、2つ(Fact Checker A'差分QA、対象文/隣接文分離判定)は
予算・スコープ制約で未着手(既存監査doc記載どおり、技術的に不可能では
ない)。全文Recheckの実測有用件数: **55 instance-run中4件で新規
BLOCKING claimを検出**(うち3件Safety群)。それ以外9件は既出claimの
再検出のみで局所QAでも代替可能だった可能性が高い。

### 1-5(コスト内訳)
`stage1_recheck`(41%)+`stage2_second_judge`(19%)で全体の60%。
局所QA導入の削減余地は`stage1_recheck`にあるが、§1-4-5の4件
(うち3件Safety群)は全文チェックでのみ検出できた可能性が高く全廃は
不可。

**USER_DECISION_REQUIRED該当有無**: 本委任はread-only分析のみで
Production/Trialコードの変更を伴わないため非該当。ただし、上記の
解決策候補(§1-2の rubric条件追加、§1-1-4のガード追加)は
Production/Trial仕様変更に相当するため、実装判断はFable/ユーザーへの
提示事項として本文書に記録するにとどめる。

**費用**: ¥0(API呼び出しなし、既存json/コードの読み取りのみ)。

**変更ファイル**: 本ファイルの新規作成のみ。既存ファイルへの書き込み・
編集・削除は一切行っていない。
