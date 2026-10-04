# Opus Context Packet: OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_10(Opus#14、条件B+ユーザー指示による必須レビュー)

作成: 委任_10(2026-10-04、Sonnet)。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。正本: `docs/pm/design_open233_kpi_recovery_02.md` §17(改善案A〜F比較・推奨)、`docs/pm/rca_open233_rep29_stage4_01.md`(逐語RCA)。証跡: `er052_output/open233_kpi_recovery_02_offline_01/agg_rep29_stage4_rca_01.json`(`.py`・`_stdout.txt`)、`er052_output/open233_self_recovery_flow_runner_01_rep29/instances_s1/{meta_run03_advanced,safety_A4}.json`・`instances_s2/meta_run03_advanced.json`。Trial専用(Production未変更、`APPROVED_FOR_PRODUCTION`ではない)。**あなたは読み取り専用。実装・Production採用可否の宣言はしない。**

## (a) 管理ID・性質・到達上限・禁止事項

- 管理ID: `OPEN-233-KPI-RECOVERY-REDESIGN-02`(親`OPEN-233-SELF-RECOVERY-TRIAL-01`、委任_10)。性質: Step 7(再ループ)の前半=¥0。rep29(`er052_output/open233_self_recovery_flow_runner_01_rep29/`、38 runs)で残ったHuman Review 3件(s1/s2 `meta_run03_advanced`、s1 `safety_A4`)の構造的RCA、worst費用超過のRCA、後段設計の改善案比較。**実装・有料API実行は未実施**。設計変更はOpus#14→Fable評価の後に委任_11で実装する。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先順: 1重大見逃し0 > 2 Human Review 0 > 3 不要Rewriteを増やさない > 4 +¥2 > 5 非決定性・追加call最小 > 6 Production複雑化回避。「Safetyを理由にHuman Reviewへ逃がさないこと。Human Reviewゼロ自体がKPI」。
- 到達上限Status: `IN_PROGRESS`。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`には進まない。
- 禁止: Production正式path変更、Checker本体Prompt・Schema・判定規則・V7b・`ACTOR_SYNONYM_CLASSES`の変更、KPI緩和案・Human Review温存案・「LLMなので保証困難」を結論とすること。
- 費用: Phase累計¥695.39/¥900、残¥204.61。再Trial(rep30、≈¥26)は1回分を見込む。「限定確認(数instance≈¥5)→rep30 1回」で判定できる設計が条件。
- 本packetの使い方: (a)〜(f)で診断できない場合のみ追加でファイルを読んでよい。読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、診断結果の最後に追加で読んだファイル一覧と概算文字数を自己申告すること。

## (b) ユーザー指示原文(該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
必須作業2 後段設計見直し
「AI1回で重大→問題なし」が可能な構造は禁止候補…
必須作業3 Opusを改善ループの一部に
原因分析→設計→Opus批判レビュー→Fable評価→自律改善→限定Trial→KPI確認→未達なら再設計→必要なら再Opus→本当に判断が必要な場合だけユーザーへ。
Opusから問題を指摘されたら、そのままユーザーへ投げず、採用/不採用/修正して採用をFable/Claudeで判断
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
「設計した→レビューした→報告した」で終わらない。KPIを満たすまで、Guardrail内で自分たちで改善ループを回すこと。
````

## (c) 現行フロー要約と該当コード(`er052_open233_self_recovery_flow_runner_01.py`、本委任時点、編集なし)

### フロー
Stage 1(Checker、fixtureでは指定deviation)→ handoff(`resolve_violation_spans`でClaimの違反範囲を記事側へ確定)→ Stage 2(判定役、materiality: BLOCKING/QUALITY/ACCEPTABLE)+ S1(降格の2-of-2確認)→ BLOCKINGのclaimごとにStage 3 Rewrite(`rewrite_ranges_ladder`、ladder ①1_word_connective→③3_sentence→④4_paragraph、`problem_kind`で開始levelが決まる)→ guard(書き戻し・actor_guard)→ Recheck(全文、`prior_issues`の解消をindex別に判定)→ `normalize_recheck_outcome`でPASS/NEXT_CYCLEへ。`MAX_CYCLES=2`(L279)、`HARD_MAX_CYCLES=3`(L283)。cycle 3は条件付きで1回だけ許可(L8195〜8225)。

### 引用(論点に直結する行)
1. **ladder成功判定**(L6011〜6031): `if not (candidate != full_text and all(changed)): attempt["result"]="guard_failed"` → actor guard(L6023、新主体クラス=after−before)→ `attempt["result"]="success"`(L6031)。issueの焦点(主体語・数値・否定・時期)の残存/入替、箇所の過去の状態への復帰は見ない。
2. **levelの引継ぎ**: なし。`ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP=False`(L311、委任_27、§0-4「各箇所は独立に初期単位から判断する」)で、`escalate_to_paragraph`flagはladderに無効(L5952/6164/6436)。毎cycle、`problem_kind`の初期level(`PROBLEM_KIND_INITIAL_RANK`、L514、`actor`=1)から再開。
3. **`same_claim_fact_id_reblocked`のSTAGE4**(L8178〜8184): `exhausted_matched_records = [m for m in matched_records if m.get("escalated_to_paragraph")]`→非空で`stage4_reason="same_claim_fact_id_reblocked"`。`matched_records`は`find_matching_prior_record`(L1319、fact_id一致∧正規化claim文のSequenceMatcher≥0.75)。**`escalated_to_paragraph`の記録は`bool(c.get("escalate_to_paragraph"))`(L8264)**で、flagは(i)前回claim再発時(L8193)(ii)同一fact_idが過去cycleに存在するとき(L8250)に付与される。ladderがflagを無視するため、「④を試した」記録ではない。
4. **`violation_span_unverified`のSTAGE4**(L8342〜8347): `unlocatable_records`があれば`stage4_reason="violation_span_unverified"`。原因は`resolve_violation_spans`(L4703)の`unverified`(`explanatory_mixed` L4804、`mismatch`等)。
5. **`HARD_MAX_CYCLES`**(L8724〜8726): `cycle += 1; if cycle > HARD_MAX_CYCLES: stage4_reason="cycle_limit_exhausted_after_recheck"`。cycle 3のRecheckで残ったclaimは**Stage 2/S1を通らない**。
6. **複数claimのRewrite**(L8286〜`_run_stage3_cycle`): claimごとに`run_stage3_for_claim`を順に呼ぶ。同じ文を指す後続claimは`covered_by_earlier_rewrite_in_cycle`でskip(L6856/6869)。
7. **Recheck mergeの未解消prior claimの現行文差替え**(`normalize_recheck_outcome`、L2182〜、差替えはL2221): `if cur and "\n" not in cur: dev["claim_in_article"]=cur`。複数範囲のRewrite後文は`\n`連結(`resolve_prior_issue_text`、L6648)のため**差替えがskipされ、古いclaim文言が次cycleへ渡る**。
8. **Recheck全文Recheckの必須化**: `full_recheck_required_reasons`(例: `english_only_ja_source_requires_full_recheck`、`multiple_claims_rewritten_same_cycle`、`same_fact_id_reappeared_across_cycles`)により、cycleの最後は常に全文Recheckで現行本文を検証する。
9. **同fact別箇所の列挙**: `expand_same_fact_id_locations`(L1518)。Recheck側は`enable_fact_id_enumeration=True`のときのみ(L1975、既定False、委任_35)。

## (d) rep29の3件のRCA(要約。逐語は`docs/pm/rca_open233_rep29_stage4_01.md`)

### (1) s1 `meta_run03_advanced`(`same_claim_fact_id_reblocked`、¥2.48、3 cycle)
MUSE-HC-006(契約スタッフが電話し相手は企業・店舗)に対し、原文 `And if this was not properly explained, users had no way to know whether they were talking to AI or a person.`が`changed_actor`。
- cycle 1: level 1 `…users had no way to know whether AI or a person was making the call.`(`users`残存、guard OK)→ Recheck `index 0 resolved=false`(`The article retains the cited claim that users had no way to know whether AI or a person was making the call`)。merged claim=2引用の合成(`“Users had no way to know …” and “a human on the other end of the call.”`)。
- cycle 2: level 1から再開(`levels_planned=[1,3,4]`)。2範囲を`users had little way to know …`/`a human on the call`へ(`no`→`little`、`other end`→削除)。Recheck: `The role-relocation concern is resolved … However, it retains the unsupported assertion that users had little way to know who was making the call`。merge: HC-012(現行文)+HC-006(`normal_gap`、**古い合成claimのまま**=L2221でskip、`agg_rep29_stage4_rca_01.json` `s1_c2_prior_issue_text`で確認)。
- cycle 3: HC-012はS1で降格確定。HC-006の古いclaimがBLOCKING。`escalated_to_paragraph=True`(実際はlevel 1のみ試行、`same_claim_reblocked_vs_actual_ladder`: `max_ladder_level_actually_used=1`)→ STAGE4。cycle 3のRewrite call=0。
- オフライン追跡: 古い合成claimをcycle 3開始時の記事でspan解決→`unverified/mismatch`(確認)。記録バグだけ直しても次の出口(`violation_span_unverified`)で倒れる。

### (2) s2 `meta_run03_advanced`(`violation_span_unverified`、¥1.73、3 cycle)
- cycle 1: level 1 `users`→`businesses`(guard素通り: `businesses`は`ACTOR_SYNONYM_CLASSES`に無く新主体クラス検出なし)。Recheck: `The article still says businesses had no way to know…`。
- cycle 2: HC-012(`businesses`の文)がlevel 1 `businesses`→`users`で**原文に完全復帰**(`article_equals_original_before_cycle1=true`)。HC-006は`covered_by_earlier_rewrite_in_cycle`。Recheck: `The article still says users were talking to AI or a person, framing users as call participants`。merged claim=`“Users had no way to know whether they were talking to AI or a person” and, in the one-line summary, calls were handled by humans “without users being properly told.”`(**引用の間に地の文**)。
- cycle 3: `resolve_violation_spans`=`explanatory_mixed`(L4804)→ STAGE4。
- オフライン追跡: 引用ごとに分割すると2片とも一意に解決(`Users had no way…`=L3、`without users being properly told.`=L0、`span_replay.s2_c3_HC006_claim_vs_cycle3_start_article`、確認)。

### (3) s1 `safety_A4`(`cycle_limit_exhausted_after_recheck`、¥4.34、20 calls、3 cycle)
- Recheck新規MAJOR 5件は**全て原文に最初から在った文**(Rewrite起因0)。`MUSE-HC-006`(`The idea was practical: when AI struggled, a person could help.`、`But that backup plan changed the meaning of the call.`)は前cycle未検出(Stage 1 recall)。`MUSE-HC-012`(「人々がAIと話していると思っていた」)は記事内3箇所に分散し、うち2箇所(`That was what people thought as they spoke.`、`So people who thought they were speaking with AI were actually speaking with human staff.`)はcycle 1のS1で降格確定、cycle 3のStage 2は`BLOCKING`(`changed_causality`、隣接文を足したclaim)。
- 最終: cycle 3のRecheckで残った1件(`“An AI called. That was what people thought as they spoke.”`、`recheck_major`)は**Stage 2/S1を通らずSTAGE4**。同じ文はcycle 1・2のS1で降格確定済み。
- 費用: Stage 2 ¥0.957、S1 ¥0.637、Rewrite ¥0.428、品質regen ¥0.399、Recheck ¥1.923(計¥4.3435)。cycle別: ¥1.875/¥1.101/¥1.368。

### rep27/28/29のHuman Review推移(各3件)と原因(確認)
| run | 件数 | 理由コード | 根本原因 |
|---|---|---|---|
| rep27 | 3 | `ladder_exhausted_without_full_rewrite`×2(A4 s1、A5 s1)、`unconfirmed_after_reverify`×1(neg3 s1) | L6とcarry-forwardの順序不整合、Recheck件数一致バグ(偽の自己矛盾) |
| rep28 | 3 | `ladder_exhausted_without_full_rewrite`×2(changed_scope s1、meta s2)、`degenerate_rewrite_output`×1(unsupported_new_claim s1) | actor_guardの日英言語不一致による過剰拒否、1文記事のtitle delete |
| rep29 | 3 | `same_claim_fact_id_reblocked`、`violation_span_unverified`、`cycle_limit_exhausted_after_recheck` | 上記(1)〜(3) |
9件全て「Rewriteが本当に直せない重大」ではなく別々の実装・形式不整合(確認)。rep29aの1件(related_fact_id空のfail-closed)も同様。

### 共通構造(Sonnetの解釈、Opusに批判してほしい)
- **S-1** Rewrite「成功」≠issue「解消」: 成功=変更∧書き戻し∧新主体語ガード。解消判定は1cycle後のRecheck(¥0.4〜0.8)のみ。
- **S-2** 履歴・再発判定のキーがclaim(fact_id+本文)で、記事内の「箇所」ではない: 兄弟fact_id(HC-006↔HC-012)が同じ文を行き来する、合成claim・古いclaimで一致/span解決が崩れる。
- **S-3** Human Reviewの出口(`same_claim`/`span未特定`/`cycle上限`)が計数・形式条件で、現行本文へのmateriality判定(Stage 2+S1)を呼ぶ前に発火する。

## (e) 改善案A〜F比較と推奨組合せ(正本: 設計書§17-2〜§17-4)

| 案 | 要点 | 3件の追跡 | 主なリスク |
|---|---|---|---|
| A1 成功判定: 主体語の残存 | level 1成功に「元の主体語が残っていない」を追加→同cycleで昇段 | (1)cycle 1のみ | level 1成功7試行中3件の残存、うち2件は正当(誤検出)。表外の語(`businesses`)は検出不能 |
| A2 成功判定: 振動(revert)検出 | 同一箇所の過去の状態と一致する候補は却下→昇段 | (2)cycle 2 | 初回の誤編集は検出不能 |
| A3 他の焦点要素(数値等) | A1の拡張 | 寄与0 | 誤検出増(推測) |
| B′ location単位のlevel引継ぎ+記録バグ是正 | `escalated_to_paragraph`を実際に④を試したかで記録。同一箇所(前Rewriteの置換後文)の再BLOCKINGは前levelの上位から | (1)(2)の昇段、(1)の誤STAGE4を除去 | §0-4(ユーザー上位原則)との整合解釈 |
| C actorを③から開始 | `PROBLEM_KIND_INITIAL_RANK["actor"]`を1→2 | (1)(2)cycle 1 | §0-4と衝突、不要Rewrite増。actorのlevel 1解消=2/5(小標本・非独立)。**不採用推奨** |
| D span未特定の決定論連鎖 | 引用分割→現行文への写像→Rewriteなし+全文Recheck | (1)の古いclaim、(2)の合成claim | Recheckが同じ指摘を返し続ける場合はcycle上限へ |
| E1 全claimを1 Rewrite | まとめて1回 | 節約僅少 | 非決定性・品質劣化。**不採用** |
| E2 同fact全箇所の列挙 | `expand_same_fact_id_locations`をRecheckにも | (3)の箇所分散 | 費用増・NORMAL群への不要Rewrite(未集計)。**今回は論点のみ** |
| G 上限後funnel | cycle上限直前に残るRecheck MAJORを既存Stage 2(+S1)に1回通す | (3) | 結果は有料call無しに確定不能 |
| T 最終手段 | 構造要素以外は既存`0_delete`+全文Recheck 1回 | 不発動の見込み | 品質劣化・実発動例0 |
| F1 費用 | 品質regen(¥0.399、9%)の発火条件調整 | (3)の費用 | 品質規則の変更(Fable/ユーザー判断) |
| F2 上限を増やす | 3→4 | — | KPI Cap違反。**不採用** |

**推奨組合せ(Fable評価用)**: B′+A2(+A1は誤検出を確認のうえ)+D+G(+T、実装は限定確認後)。全て既存処理(`rewrite_records`の置換前後文・`resolve_prior_issue_text`の¥0情報・`0_delete`・Stage 2+S1・全文Recheck)の再利用で、新しいLLM処理・retry loopはない。

**設計後も残るHuman Review経路**: `same_claim_fact_id_reblocked`(同一箇所で④まで実際に試行済み∧削除不可な構造要素のみ)、`cycle_limit_exhausted_after_recheck`(Stage 2+S1が「BLOCKING」と確認した重大が3 cycle後も残り、かつ削除不可な構造要素のみ)。`violation_span_unverified`は残さない。実例は0件(rep27〜29)。

限定確認→rep30の計画: (a)¥0 unit/replay(新ルール、rep29の3件の入力、負例)、(b)有料≈¥5(meta s1・s2、A4のStage 2+S1のみの再判定)→ rep30(≈¥26)1回。事前基準: Primary 0件・見逃し0件・平均+¥2・Cap+¥3・NORMAL群不要Rewrite≤rep29(5/14)。

## (f) Opusへの観点

1. **なぜ「Rewrite成功」と「issue解消」が乖離できたか**: 成功判定(L6011〜6031)が文字列の変化・書き戻し・新主体語のみで、解消はRecheck任せになった設計判断の妥当性。A1/A2/B′でその乖離が閉じるか(閉じない種類: `no`→`little`の表層変更、`users`→`businesses`の誤った主体入替)。
2. **Human Reviewへ倒す経路を決定論的解消に置き換える案が「重大見逃し」を生まないか(Safety hole)**: (i)Dの「Rewriteせず+全文Recheck」は、指摘が実在するのにspanを特定できないclaimを実質的に保留する。最終PASSが全文Recheck(`_recheck_ok`)に依存することで安全側と言えるか。(ii)Gは上限後の残指摘を既存Stage 2+S1(2-of-2降格)に通す。ユーザー指示の「AI1回で重大→問題なし」禁止に照らして、funnelの再利用は許容されるか。(iii)T(削除)は新しい未確認claimを加えない一方、構造要素・必須文でどう扱うか。(iv)B′の「同一箇所」判定(置換後文の逐語一致)の穴(文が部分的に変わった後の箇所の同一性)。
3. **不要Rewrite・非決定性・追加call・worst費用への影響**: A1の誤検出(3件中2件)による不要な昇段、Gの追加call(上限時のみ≈¥0.4〜0.5)、worst(A4型)は1 cycle≈¥1.1〜1.9でありcycle数を減らさない限りCap内に収まらない点、F1(品質regen)の扱い。
4. **より単純・決定論的な代替**: 例: Recheckの`claim_in_article`を引用1つに強制する(Checker Prompt変更は禁止のため後段で)、`escalated_to_paragraph`記録の是正だけで十分か、location単位の状態を作らず「同じ文の過去の候補一覧」だけで足りるか、Rewrite promptへ前cycleの失敗案を渡す等。Recheckの解消判定を毎cycle受けずladder内で局所的に確認する案(追加call)との比較。
5. **個別穴埋めの繰り返しになっていないか(条件B: 必ず明示判定)**: rep27→28→29でHuman Review 3→3→3、毎回別の実装不整合(9件、実例上「Rewriteが本当に直せない重大」は0件)。Sonnetは「個別の穴だが、S-1〜S-3の共通構造が背後にある」と判断し、location単位の履歴・成功判定・出口のfunnel経由化を一体で設計することを推奨した。この判定は妥当か。根本設計に別の問題(例: Recheckを「Stage 1 recallの補完」として使う運用、1 cycle=1〜2件ずつの逐次発見、HARD_MAX_CYCLES=3という計数的上限そのもの)はないか。
6. **限定確認→rep30 1回で判定できる設計か**: 事前基準は十分か。再現しにくい経路(上限到達=38 runs中1、同一箇所の振動=1)を限定確認でどう網羅するか(replay対象)。

### 論点と材料の対応チェック(必須)

| 論点 | 必要な材料 | 所在 | 不足時の扱い |
|---|---|---|---|
| 1 | 成功判定のコード・3件のlevel別before/after | (c)1/2、(d)、`rca_open233_rep29_stage4_01.md` §1〜§3 | 不足なし |
| 2 | funnel・Recheck依存・Stage 2+S1、既存の降格確定の履歴 | (c)5/8、(d)(3)、設計書§17-4 | 不足(Tの品質影響は未測定、推測) |
| 3 | 費用内訳、level別解消率、誤検出 | (d)(3)、設計書§17-2 | 不足なし(A1の誤検出はn=3) |
| 4 | 現行コード・既存関数 | (c)7/9 | Opusが追加探索可(`er052_open233_self_recovery_flow_runner_01.py`、Grepキー: `escalated_to_paragraph`・`resolve_prior_issue_text`・`normalize_recheck_outcome`・`explain_split`) |
| 5 | 9件の履歴 | (d)推移表、設計書§12・§14・§16・§17 | 不足なし |
| 6 | 事前基準・費用 | (e) | 不足(上限到達の再現例が少ない) |

## (g) 発火条件と独立レビューブロック

- 発火条件: **条件B**(同じ問題へ2回以上修正しても再発: Human Review 3→3→3)+ユーザー指示による必須レビュー(後段Safety設計変更は実装前にOpus)。条件A(新しい構造・処理フローの設計: location単位の履歴・上限後funnel・最終手段)にも該当。
- 重複レビューの確認: 同じ内容の既存Opusレビューなし(Opus#13は`opus_l2_review_open233_kpi_recovery_02_13.md`、actor_guard・構造要素delete・件数一致が対象。location履歴・上限後funnel・span fallback連鎖・ladder成功判定は未レビュー)。再レビューではなく初回。

---
【Opus独立技術レビューの目的】
あなたの役割は「重要な技術設計に対する独立レビュー」である。Claude/Fableの案を
追認することが目的ではない。必ず次を独立に評価すること。
- そもそもその設計が必要か
- より単純な方法がないか
- 既存処理をそのまま利用できないか
- 不要な複雑化をしていないか
- 根本原因に対する対策になっているか
- 別のFailureを生まないか

【最低限、独立してレビューする12観点】
1. そもそもこの変更・設計は必要か
2. より単純な構造にできないか
3. 既存処理・既存データを利用できないか
4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
5. 不要なLLM処理を追加していないか
6. 非決定性を増やさないか
7. Human Reviewを増やさないか
8. 不要Rewriteを増やさないか
9. コストを不必要に増やさないか
10. retry / fallback / regenerationと矛盾しないか
11. Failure時に安全側へ倒れるか
12. 個別パッチではなく再発防止になっているか

【追加観点(発火条件別)】
- 条件B(同じ問題へ2回修正しても再発): 「個別バグの連続なのか、根本設計に問題があるのか」を
  必ず明示的に判定すること。
- 条件C(Production採用候補の最終レビュー): 次の6点も必ず確認すること。
  Trial専用実装になっていないか / Production全体で矛盾しないか /
  初回・retry・fallback間で仕様が一致しているか / Dangling Referenceがないか /
  Failure時に安全側へ倒れるか / QCD上の新しい問題を生まないか。
  これはユーザーのProduction採用判断を代替するものではない(採用可否は
  人間ユーザーのみが決める。あなたは採用可否を宣言しない)。

【レビューの姿勢】
Claude/Fableの案を前提として追認しない。代替案の方が良い場合は、その代替案を
明確に提案すること。結論は「必要/不要」「推奨構造」「リスク」「代替案」の順で
簡潔に返す。
---
