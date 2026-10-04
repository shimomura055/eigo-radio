# Opus Context Packet: OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_07(Opus#13、条件A)

作成: 委任_07(2026-10-04、Sonnet)。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。正本設計: `docs/pm/design_open233_kpi_recovery_02.md` §14(RCA・実装・AG1〜AG3)。証跡: `er052_output/open233_kpi_recovery_02_offline_01/`。Trial専用(Production未変更、`APPROVED_FOR_PRODUCTION`ではない)。

## (a) 論点(限定)

KPI(変更・緩和不可): Primary=Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内(Cap+¥3)。QCD優先順: 重大見逃し0 > Human Review 0 > 不要Rewrite増やさない > +¥2 > 非決定性・追加call最小 > Production複雑化回避。

1. **actor_guardの過剰拒否**: 全ログの`actor_guard_rejected`7試行(4 record)が全て過剰拒否、正当拒否0。根本原因を「guardが英語の主体語をLedger全文(日本語)に英語部分一致で照合する言語不一致」と見るのは妥当か。案AG1(Ledger照合型・決定論)/AG2/AG3のうち、**Safety guardを緩めずにHuman Reviewを0にできるか**。Ledger照合の決定論性、後ろ盾(Stage 2 floor `changed_actor`・Recheck)の妥当性、(iii)Checker issue名指しを許容根拠にする穴の有無。
2. **構造要素(title等)の書き換えfallback**: 決定論deleteが構造要素を空にして`degenerate_rewrite_output`になる問題を、deleteを選ばず書き換え(E1→③→④)へ回す実装(空・degenerateは次水準へ、全滅時は既存の枯渇経路)にした。Human Reviewへ逃げていないか、劣化を防げているか。Fable指定の「Ledgerのheadline/in_one_line相当factによる再生成1回」は、Ledgerにその種別が無いため実装していない(既存ladderへ統合)。この判断は妥当か。
3. **件数一致バグ是正(index別集約)の安全性**: 旧式`len(items)==len(prior_issues) and all(resolved)`を、全prior indexが揃い各グループ全resolvedでTrue・indexが欠けたpriorは未解消(安全側)へ置換。見逃し(偽のTrue)を生む経路はないか。
4. **`remains_in_final_en`の判定**: rep28の3件(B3 s1・s2、neg5 s1)を「目印部分文字列の残存(因果`so`は除去済み)」と判定した。妥当か。
5. **より単純な方法**: 上記1〜3に対し、より単純・既存処理の再利用で足りる方法はないか(例: actor_guard自体の廃止、guard後段のRecheck/floorへの一本化、Rewrite promptでの主体指定)。
6. **Production整合**: er003 `vfl01`の同一件数一致式(827行)、er010等にactor guard相当が無い点。将来の配線時に何を揃えるべきか。

### 論点と材料の対応チェック(必須)

| 論点 | 必要な材料 | 所在 | 不足時の扱い |
|---|---|---|---|
| 1 | guard実装、全7試行の逐語、AG1〜AG3比較 | (b)(c) | 不足なし(rep28逐語2件+全件表。他のrep22 repro 1件はLedger fact側のみ要約) |
| 2 | delete→書き換えの実装、rep28逐語、replay結果 | (b)(c) | 不足なし |
| 3 | 新旧式、6件の実測、index欠落の扱い | (b)(c) | 不足なし |
| 4 | 3件の本文周辺 | (b) | 不足なし |
| 5/6 | コード行・Production側の式 | (c) | 不足なし |

## (b) 主要数値表・要点

### 要点
1. rep28(委任_06)はSafety 0・Cost達成、**Human Review 3件**(actor_guard枯渇2: `safety_er009_changed_scope` s1、`meta_run03_advanced` s2。title delete劣化1: `safety_er009_unsupported_new_claim` s1)。
2. actor_guardは英語の新主体語を**日本語Ledger全文に英語部分一致**で照合するため、Ledger記載の主体(F-004「クレジットカード利用者」、MUSE-HC-006「契約スタッフ」)でも拒否。全ログ7試行が全て過剰(仮ラベル)、正当拒否の実績は0。
3. `degenerate_rewrite_output`は3 instance(rep9×2、rep28×1)すべて同一fixture(**1文のみの記事**=その文がtitle)。Stage 2が`rewrite_kind=delete`とし決定論deleteが本文を空にするのが原因。
4. 件数一致バグ: Checkerが1 prior issueを同index 2項目で返すと旧式がFalse(偽の自己矛盾)→再確認call。項目別が記録された6件(neg3)は全て該当、再確認費用¥1.51。残り31件(neg3 22・neg2 7・unsupported 2)は旧コードで項目別未記録=機序は推測。
5. 実装済み(Trial、runner): 件数一致バグ是正、構造要素のdelete禁止+書き換え。actor_guard是正は**設計のみ**(本レビュー対象)。runner単体643件OK、`er052*`687件OK、全体4610件中失敗11件=基準11件(新規0)。

### actor_guard 全ログ集計(`agg_actor_guard_01.py`)

| run/instance | cycle | 水準 | 新主体語 | 仮ラベル | 結果 |
|---|---|---|---|---|---|
| rep28 meta_run03_advanced s1 | 1 | ③ | worker | 過剰 | 後続水準で解決 |
| rep28 safety_er009_changed_scope s1 | 2 | E1/③/④ | users×3 | 過剰 | **枯渇→Human Review** |
| rep28 meta_run03_advanced s2 | 2 | ③/④ | contractors/contractor | 過剰 | **枯渇→Human Review** |
| rep22 meta_run03_standard repro | 2 | ③ | users | 過剰(関連factに主体記載なし、他factに「ユーザー」) | 未解決(repro) |

**逐語1(`changed_scope` s1、claim=F-004)**
- Ledger F-004: `より高い推奨チップ率のメニューを偶然見た乗客は、実際により多くチップを残した。…` / `scope: ニューヨーク市タクシーのクレジットカード利用者`
- Checker issue: `The Ledger supports a causal finding for New York City taxi credit-card users in the original study, but it does not report a new, direct confirmation of that finding. The article also generalizes the affected group from credit-card users to taxi customers.`
- 元文: `The taxi study's results have now been directly confirmed in New York City taxis: higher suggested tip rates on taxi screens cause customers to leave more money, just as they did in the New York City taxi data.`
- 拒否案(E1): `In the New York City taxi study, higher suggested tip rates on taxi screens cause credit-card users to leave more money.` / 拒否案(③④): `In the New York City taxi study, higher suggested tip rates led credit-card users to leave more money.`(新主体語=`users`。Checkerが求めた限定そのもの)

**逐語2(`meta_run03_advanced` s2、claim=MUSE-HC-006)**
- Ledger: `MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。`
- Checker issue(抜粋): `The article frames users as potentially being on the call … The Ledger establishes that human contract workers made some calls to businesses on users' behalf … but does not establish that users themselves were call participants …`
- 元文: `People who asked Muse to make a call might think that AI was making it. They were enjoying the convenience of AI, only to find a human on the other end of the call without realizing it. Some calls made through Meta's AI assistant were actually handled by humans, without users being properly told.`
- 拒否案(③): `People could ask Muse to call businesses on their behalf.  Some calls made through Meta's AI assistant were actually handled by human contractors on users' behalf.` / (④): `… a human contractor made the call on their behalf …`(新主体語=contractor(s))

### AG1〜AG3 比較(`agg_actor_guard_ag_compare_01.py`、¥0 replay)

| 観点 | 現行 | AG1-strict(関連fact+日英同義語表+issue補助) | AG1-ledger(同Ledger全fact) | AG2(hint強化・同段再試行) | AG3(同段で別案1回) |
|---|---|---|---|---|---|
| 過剰拒否解消(7試行/4 record) | 0/7 | 6/7(3/4)、rep28全6試行は**関連factの同義語のみで**許容 | 7/7(4/4) | 非決定(Checker要求と矛盾する懸念、推測) | 非決定 |
| 正当拒否維持(合成42ケース、推測ベース) | 42/42 | 42/42 | 42/42 | 同guard | 同guard |
| 追加call | 0 | 0 | 0 | +1/拒否(≒¥0.12〜0.2) | +1/拒否 |
| 非決定性 | なし | なし | なし | 増 | 増 |

暫定推奨=AG1-strict(ただし(iii)issue名指しは「Ledgerにも存在する場合のみ」の補助。単独根拠にすると誤主体名指しの穴)。後ろ盾: Stage 2 floor `changed_actor`(決定論のflag→floor、ただしCheckerの検出に依存)・Recheck全文(件数一致是正後はindex別に厳密)。同義語表に無い主体は拒否に倒れる(fail-closed、過剰拒否の再発はあるがSafety holeではない)。

### title delete(確認済み)
- fixture `safety_er009_unsupported_new_claim`: `article_text`=`The same New York City taxi researchers also found that male passengers tipped twice as much as female passengers when shown a higher suggested rate.`(1文のみ。`_paragraph_title`=その文)。Checker issue: `Ledgerには、推奨率の高いメニューを見た乗客がより多くチップを残したという結果はあるが、男女間の差や「2倍」という結果は記載されていない。`
- 旧挙動: `rewrite_kind=delete`→`0_delete`→本文が空→`title_degenerate`/`hook_degenerate`→`degenerate_rewrite_output`(STAGE4)。
- 実装(`STRUCTURAL_ELEMENT_REWRITE`、KPI構成ON/既定OFF): 範囲が先頭非空行(title)・`#`見出し行・`In one line`直下・deleteでdegenerateになる範囲に重なれば、deleteを選ばず`narrow_scope`として既存ladder(E1→③→④)で書き換え。空文字は`declined_empty_structural`、`degenerate`は`degenerate_structural`で却下し次の水準へ。全滅は既存の枯渇経路(新Human Review経路なし)。
- ¥0 replay(LLM mock): OFF=`0_delete`→本文空(再現)、ON=`structural_element_rewrite.reasons=["title"]`、`4_paragraph`(既存`filter_levels_by_problem_kind`が新規主張を段落水準へ)でmock書き換えを採用→本文非空・degenerateなし。**実LLMの書き換え品質は未検証**(次委任の有料run)。

### 件数一致バグ(確認済み範囲)
- 新式(`aggregate_prior_issues_resolved`): 全prior index(0..n-1)が応答に存在し、各indexの全項目resolved=trueのときのみTrue。indexが欠けたpriorは`None`(未解消)。prior 0件は旧式と同じ挙動。Checkerの判定規則・Prompt・Schemaは不変。
- 実測: rep28 neg3 s1/s2のRecheck応答(prior 1・同index 2項目・両resolved)で旧式=記録`False`→新式`True`。項目別が記録された24 recheckのうち件数不一致6件(全てneg3)は全て偽の自己矛盾、再確認call費用合計¥1.51。
- 注意: 再確認call(cite-or-release)は件数に依らず項目別集約(`apply_cite_or_release`)であり、これまで偽の自己矛盾の最終判定はPASSに落ちていた(見逃しではなく無駄なcall)。是正により偽のTrueが増える経路は、indexが重複または欠落した応答でresolvedが全trueの場合のみで、欠落は未解消=Falseとした。

### `remains_in_final_en` 3件(確認済み)
- 目印`flashy 20% plan`(HF-007)。元: `…continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly…`。最終: B3 s1 `…July 14, and the flashy 20% plan left the stage, but…` / B3 s2 `…while the flashy 20% plan left the stage, but…` / neg5 s1 `…continued on July 14. Meanwhile, the flashy 20% plan left the stage. But the chart pulled back only briefly…`。因果`so`は除去済み。3件ともBLOCKINGで指摘→Recheckで解消確認済み。判定=目印の部分一致残存(委任_63 B3 s1と同型)。

## (c) 必要なProduction code/spec section

Trial(er052)のみ。Production側(er003/er010等)に`er052_open233`への参照は0件(`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`=0件)。

| ファイル:行 | 内容 | Grep確認 |
|---|---|---|
| `er052_open233_self_recovery_flow_runner_01.py:567-587` | `_ACTOR_NOUN_PATTERN`、`extract_actor_nouns`、`actor_rewrite_guard_ok`(新主体語=after−before、全てLedger全文に英語部分一致で許可) | 済 |
| 同:5849付近(ladder)、6014付近(旧single_text)、6306付近(paired) | `actor_guard_rejected`の適用箇所 | 済(Grep `actor_rewrite_guard_ok`) |
| 同:1716付近 | `aggregate_prior_issues_resolved`(新規)。`run_recheck`の旧式`len(resolved)==len(prior_issues)`を置換 | 済 |
| 同:5573-5625(`STRUCTURAL_REWRITE_HINT_SUFFIX`、`structural_element_reasons`)、5700付近(ladder内の切替) | 構造要素のdelete禁止・書き換え | 済 |
| `er003_v1_en_direct_vfl_01_generate.py:825-828` | Production側の同一の件数一致式(`len(resolved) == len(prior_issues) and all(...)`)。**Production変更はしない**、`OPEN-233-A1-PROD`に配線時の整合項目として記録 | 済(read-only) |
| `er010_ledger_local_rewrite_09.py` | actor guard相当は**無い**(Grep `actor`=0件、確認済み) | 済 |

## (d) Sonnet要約

rep28のHuman Review 3件のうち2件はactor_guardの言語不一致(英語主体語×日本語Ledger)による過剰拒否が、1件は1文記事のtitleに対する決定論deleteの劣化が原因で、いずれも実装上の欠陥(KPI緩和の論点ではない)。件数一致バグは偽の自己矛盾で毎回再確認callを生む実装バグ(neg3で確認済み6/6、¥1.51)。実装は件数一致・構造要素の2件(Trial、テスト・¥0 replay済み)。actor_guardはSafety guardのため設計のみ。AG1-strictが¥0・追加call0・決定論で最有力だが、(1)正当拒否の実績が0で維持側は合成対照(推測)、(2)同義語表の整備とパラフレーズの扱い、(3)後ろ盾(floor/Recheck)がCheckerの検出に依存、が残る不確実性。Ledgerのheadline相当factによる再生成は実装していない(Ledgerに種別が無いため)。構造要素の書き換えは実LLM品質が未検証。

## (e) Progressive Disclosure手順

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告すること。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、必要な事実を省いてまで読込量を減らしてはならない。

## (f) 入力文字数の自己計測欄

- packet合計文字数: 10900字(目安2〜3万字以内、本packetは2万字以内)。内訳(a)/(b)/(c)/(d)/(e)/(g)は節ごとの概算で記録せず、合計のみ(Python `len()`実測)。

## (g) 発火条件と独立レビューブロック

- 発火条件: **条件A**(新しい構造・処理フローの設計): actor_guardのLedger照合型への変更設計(Safety guard)、構造要素のdelete禁止→書き換えfallbackという新しい処理フロー、Recheck解消判定の集約方法の変更。
- 重複レビューの確認: 同じ内容の既存Opusレビューなし(Opus#12は`opus_packet_open233_kpi_recovery_02_02.md`、再確認結果の合流N1′等が対象。actor_guard・構造要素・件数一致は未レビュー)。再レビューではなく初回。

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
