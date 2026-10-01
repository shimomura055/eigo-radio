# OPEN-233 現行設計の説明: Checker出力からRewrite対象を決めるまで(委任_38)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01 / Status: USER_DECISION_REQUIRED のまま(変更なし)
性質: 現行構造の説明のみ。コード変更・Trial実行・API課金なし(費用¥0)。
是正案の推奨はしていない(末尾「参考」のみ)。

読み方の注意: 本文中の「検査役(Checker)」=Stage 1(記事が事実台帳[Ledger]から逸脱していないかを調べるLLM)。
「書き換え役(Rewrite)」=Stage 3(指摘された文を直すLLM)。「判定役(Stage 2)」=Checkerの指摘が本当に重大かを再判定し、
重大(BLOCKING)なら直し方のメモ(rewrite hint)も作る別のLLM呼び出し。
「Stage 4」=自動で直しきれず人間確認へ回す状態。「fail-closed」=迷ったら安全側(人間確認)に倒す方針。

最初に結論だけ(詳細は各節):
- 「違反文をそのままRewriteへ渡す」ことは、現行コードでも**大部分は既にやっている**(Rewriteへは「違反文」「理由」「直し方メモ」を渡している)。
  ただしその「違反文」は、Checkerが返した文字列をそのまま使っているのではなく、**Checkerの文字列を手がかりに、プログラムが記事から探し直した文**である。
- 探し直す理由は、Checkerが返す文字列が「記事の文と一字一句同じ」である保証がなく、位置情報(何文目・何文字目)も返さないため、
  書き換え結果を記事へ戻す処理(文字列の完全一致置換)に使えるか、プログラム側で確かめる必要があるから。
- ただし今回調べた範囲では、Checkerの返す文字列の大半は記事の逐語抜粋だった(後述)。実際に問題を起こしているのは
  「1つのclaimが複数文にまたがる」ことと、「探し直しの方法が引用符付き文字列を完全一致で見ない」ことの組み合わせだった。
- 記録上、meta_run03_standardのStage 4の理由は「対象が見つからない(target_not_locatable)」ではなく
  `cycle_limit_exhausted`/`ladder_exhausted_without_full_rewrite`だった。「特定に失敗してStage 4」という理解は、厳密には
  「複数文claimのうち1文しか直せず、残りが次のcycleに持ち越されて上限に達した」が実際の姿(5節で実データを示す)。

---

## 1. CheckerはNG判定時に実際に何を出力しているか

### 1-1. 実データ1件(生のJSON、逐語)
出典: `er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`
の `deviations[1]`(meta_run03_standardのStage 1出力を固定保存したもの。rep21のsample1は同じ固定データを再利用している。
rep21の出力ファイル `er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json` の
cycle1 stage2_results内に同一のclaim_in_article/issueが入っていることを確認済み)。

```json
{
 "claim_in_article": "“It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.”",
 "issue": "The plural “calls” presents the reported incident as involving multiple calls, while the Ledger describes one reported case.",
 "severity": "MAJOR",
 "changed_fact": true,
 "changed_scope": true,
 "changed_causality": false,
 "changed_certainty": false,
 "changed_number": true,
 "changed_actor": false,
 "changed_negation": false,
 "changed_comparison": false,
 "changed_time": false,
 "unsupported_new_claim": true,
 "explanation": "The plural wording expands the scope and number of the Ledger’s single reported case. Attribution to an employee report is retained, but it does not support multiple calls.",
 "related_fact_id": "MUSE-HC-011",
 "origin": "translation",
 "qualifier_present": true,
 "qualifier_text": "“one employee’s report”; “However, this is only one report.”",
 "ledger_field_basis": "notes_factual_constraint",
 "observation_consistent": false,
 "matched_notes_id": "MUSE-HC-011",
 "same_fact_id_locations": [
  "News reports also cited one employee’s report.",
  "However, this is only one report. It would be wrong to say all contract workers did this."
 ],
 "auto_downgraded": false,
 "severity_final": "BLOCKING",
 "action": "STOP",
 "basis": "ledger_fact",
 "rule_id": "existing_major_v2"
}
```

### 1-2. 各フィールドの意味
| フィールド | 中身 | ユーザーの質問との対応 |
|---|---|---|
| `claim_in_article` | 違反している箇所として検査役が書いた文字列。上の例は**記事の連続する2文を1組の“ ”で囲んだもの** | 「複数文をまとめたclaim」。1文だけではない |
| `issue` / `explanation` | 違反の理由(自由文、英語) | 「理由」 |
| `changed_*` 10個の真偽値、`severity` | どの種類の逸脱か、重さ | 理由の構造化版 |
| `related_fact_id` | どの事実台帳項目(MUSE-HC-011)に反するか | 事実側の紐づけ |
| `same_fact_id_locations` | 同じ事実を言っている「他の箇所」の文字列リスト | 他箇所の列挙(位置番号ではなく文字列) |
| `auto_downgraded`〜`rule_id`(末尾5個) | プログラム側の後処理で付く(`er051_open233_checker_trial_variant_01.py`の後処理が`severity_final`/`action`/`basis`/`rule_id`を追加、と記述) | 位置とは無関係 |
| **rewrite hint** | **このレコードには無い** | Checker(Stage 1)はrewrite hintを出さない。hintは次のStage 2(判定役)が別のLLM呼び出しで作る |
| **位置情報(何文目・何文字目)** | **無い** | schemaに存在しない(下記) |

### 1-3. 「記事の文を一字一句そのまま返す保証があるか」「位置を返しているか」(Prompt/schemaの根拠)
- Stage 1の出力schema: `er003_v1_en_direct_vfl_01_generate.py` 464行 `"claim_in_article": {"type": "string"}`(型が文字列というだけ。逐語・位置の制約なし)。
- Stage 1のPrompt: 同ファイル502〜541行 `DEVIATION_PROMPT_TEMPLATE`。`claim_in_article`の書き方への指示は**一切ない**(逐語で引用せよ、等の記述なし)。
  逆に「厳密な文言一致は求めません」(536〜537行)とあるが、これはLedgerとの一致についての文脈。
- 位置情報(文番号・文字オフセット)を返すフィールドは、schema・Promptのどちらにも**存在しない**。
- 例外として、`same_fact_id_locations`だけは別のPrompt追記(`er052_open233_self_recovery_flow_runner_01.py` 1119〜1126行)で
  「exact verbatim substring(逐語の部分文字列)で引用せよ」と指示されている。しかし実データでは、その指示に反して
  `"Paragraph 7"`(rep21 s1 cycle2のRecheck出力)や`"Paragraph beginning “People asking Muse to call”"`(rep20 s2 cycle2)のような
  位置の説明文を返している例がある(いずれも実ファイルから確認)。コード側は逐語で記事中に実在するものだけ採用する(1147〜1149行のコメント)。
- 実測(rep19〜21のmeta_run03_standard、Checker由来で“ ”囲みの形をしたclaim 23件、記事テキストが記録されているcycleのみ):
  引用の中身が記事中にそのまま存在したのは21件、存在しなかったのは2件(「Also, some calls...」を“Some calls...”と先頭を大文字にした等)。
  サンプルが小さく(1記事・3 run分)、一般化はできない。

---

## 2. なぜそのままRewrite Promptへ渡せないのか

### 2-1. 現行で実際にRewrite Promptへ渡しているもの(コードで確認)
`er052_open233_self_recovery_flow_runner_01.py` の `single_text_rewrite`(2731行〜)と、Prompt雛形 `E1_MINIMAL_WORD_PROMPT_TEMPLATE`(2557行〜)・`E2_GENERIC_PROMPT_TEMPLATE`(2584行〜):
- `[Sentence flagged as a Ledger deviation]` = `target_sentence`(**プログラムが記事から探して決めた文**)
- `[Checker's issue]` = Checkerの`issue`(理由、そのまま)
- `[Rewrite hint]` = Stage 2が作ったrewrite hint(空なら`materiality=..., basis=...`という合成文字列に置換、2747行)
- 加えて Ledger全文

つまり「違反した文」+「理由」+「直し方メモ」は既に渡している。ただし「違反した文」の欄に入るのは、Checkerの`claim_in_article`の文字列そのものではなく、
`locate_target`(2449行〜)が`claim_in_article`・rewrite hintを手がかりに記事本文から選び直した文である。`claim_in_article`自体はRewrite Promptに入らない。

### 2-2. 「Checkerの文字列をそのまま渡すだけでは足りない」理由(コード上の根拠)
1. **書き換え結果を記事へ戻す処理が「完全一致の文字列置換」だから**。`candidate = full_text.replace(lv["target"], revised, 1)`(2832行)、
   削除型は`full_text.replace(target_sentence, "", 1)`(2762行)、JA/EN対訳側は`ja_full.replace(...)`/`en_full.replace(...)`(3062〜3063行)。
   置換対象の文字列が記事中に一字一句存在し、かつ最初の1箇所を置換する、という前提で動く。Checkerの文字列にこの保証がない(1-3)。
2. **claim_in_articleが“ ”で囲まれて返ることが多く、その引用符は記事本文には存在しない**。locate側の完全一致判定
   (`locate_best_sentence` 2249行 `claim_text.strip() in full_text`)は引用符を外さないため、引用符付きの文字列は完全一致にならない
   (上の1-1の例で実測: 引用符付きのまま記事に含まれるか=False、引用符を外した中身が含まれるか=True)。
   なおStage 2側の`build_local_context`(`er052_open233_self_recovery_stage2_production_01.py` 188〜189行)は
   「両端の引用符を除去したうえで再照合する」処理を持っており、locate側にはこの処理がない(コード確認済み)。
3. **複数断片を結合したclaimは、記事中の連続した文字列ではない**。例: `“They could not tell if it was AI or a person” and “They did not realize it.”`
   (rep20 s2 cycle2、実データ)は、記事中の離れた2文を“ ”と"and"でつないだ合成文字列で、そのままでは置換対象にできない。
4. **JA側の対応文は、Checker出力(EN側)には含まれない**。対訳記事(origin=`ja_source`)ではJA文も同時に直す必要があるが、Checkerはその位置を返さない(3節・4節)。

### 2-3. ユーザーの見立てへの率直な評価
- **部分的に正しい**: 1文だけ・引用符を外せば記事の逐語抜粋になる、というケースは多い(実測23件中21件が逐語)。このケースなら
  「Checkerの文字列(引用符を外したもの)をそのまま置換対象に使う」こと自体は技術的に可能で、困るのは「渡す」工程ではなく
  「記事へ戻す工程」と「引用符・複数断片・大文字小文字の差など、完全一致が崩れる場合の扱い」である。
- 現行コードは、この可能な場合でも引用符付き文字列を完全一致で見ないため、探し直し(あいまい一致)に落ちている(2-2の2)。
  これは設計上の必然というより、現行locateの実装上の取りこぼしと読める(ただし、これを直すべきかは本説明の範囲外)。
- **成り立たない部分**: 複数断片の合成claim(2-2の3)・逐語でない文字列(1-3の2件)・JA対応箇所の決定(3節)は、
  文字列をそのまま使うだけでは解決しない。

---

## 3. Rewrite前に「元記事のどこか」を特定する必要がある理由(コード上で位置を使っている工程)

| # | 工程(コード位置) | 位置が無いと何ができないか |
|---|---|---|
| 1 | Rewrite対象文の決定 `locate_target`(2449行)→E1/E2 Promptの`[Sentence flagged]` | 直す文をLLMに示せない。見つからなければ`target_not_locatable`としてRewriteせずStage 4へ(2871行) |
| 2 | 書き換え後の記事への書き戻し(2762・2832・3062〜3063行の`.replace(target, revised, 1)`) | 書き換えた文を記事のどこへ戻すかが決まらない |
| 3 | 局所Rewriteの単位拡大(単語→1文→段落) `locate_paragraph_block`(2476行、2798行) | 「1文で直らなければ段落ごと」の段落が決まらない |
| 4 | JA側の対応箇所の決定(`paired_rewrite` 2957〜2973行、`locate_ja_counterpart_by_position` 2497行) | JA/EN同時に直す際、JA側の書き換え対象が決まらない(JA側は引用・語彙一致が効きにくく、最後は「EN文の位置比をJA文数に写す」近似で選ぶ) |
| 5 | 書き換え後の局所チェック(`claim_text.strip() not in candidate` 2833・2860・3066行、delete型の再出現確認 2769行) | 問題の文言が記事から消えたかを判定できない |
| 6 | 書き換え前後の断片の記録(`before_fragment`/`after_fragment`、2854・2916行) | 何を何に変えたかの記録が取れない |
| 7 | 記事内の区分判定 `detect_claim_section_type`(1844行) | claimがタイトル/hook/本文のどこかが決まらず、区分別の降格ルールが使えない |
| 8 | Stage 2へ渡す前後文脈 `build_local_context`(Stage 2側ファイル184行) | 判定役に渡す「対象を含む段落±1」が作れない(見つからなければ記事全文を渡す) |

---

## 4. 原因の切り分け

### 4-1. ユーザーの4候補ごとの判定
| 候補 | 判定 | 根拠 |
|---|---|---|
| (a) 違反対象が1文とは限らず範囲を持つ | **該当(主因の一つ)** | rep21 s1: 1つの“ ”に連続2文(1-1)。rep20 s2: 離れた2文を結合。Rewriteの既定単位は1文で、あいまい一致は2文claimに対し1文しか選べない(5節で実測)。設計書§6-17・REPORT§34も同様の整理 |
| (b) Checkerが元文を返さず要約・結合して返す | **部分的** | 「結合」は該当(2文を1つの引用に/2断片をandで結合)。「要約・言い換え」はまれ(23件中2件が大文字化の差、他は逐語)。逐語を保証するPrompt/schema記述はなく(1-3)、保証がないこと自体は事実 |
| (c) JA/EN両方の対応箇所の特定が必要 | **部分的(副因)** | origin=`ja_source`のclaimだけ対訳処理(`run_stage3_for_claim` 3199〜3203行)。rep20 s2ではJA側の対象がEN側の対象と食い違った(設計書§6-17)。rep21 s1(origin=`translation`)ではEN側のみで、JAは無関係 |
| (d) その他の実装上の理由 | **該当(複数)** | (d1) locateが引用符付き文字列を完全一致で見ない(2-2の2)。(d2) あいまい一致の「僅差なら不採用」閾値(0.08、2264行)で、5節の実例では2文claimの各文の類似度が近く(差0.066)不採用になった(一般にそうなりやすいかは未検証)。(d3) 戻し処理が完全一致置換(2-2の1)。(d4) 残った1文は次のRecheckまで検出されず、その間にcycle回数を消費する |

### 4-2. meta_run03_standardの残存失敗(固定Stage 1入力でも4 run中2 runがStage 4)
確認できた範囲(rep20・rep21、各n=2):

| run | Stage 4の記録上の理由 | 共通点 |
|---|---|---|
| rep20 sample2 | `ladder_exhausted_without_full_rewrite`(cycle2) | claimが離れた2文の結合(a+b)。EN側が2文のうち1文のみ特定、JA側のhint引用はEN側と別の箇所を指した(c)。設計書§6-17 |
| rep21 sample1 | `cycle_limit_exhausted`(cycle3) | claimが連続2文を1つの引用で囲んだもの(a)。hintが空でlocateがあいまい一致に落ち1文のみ修正。残り1文が次cycleへ(5節) |
| rep20 s1 / rep21 s2 | (解消) | 参考: 同じ固定データでも解消するrunがある(設計書§6-16・§6-17の表による。出力ファイルでの個別確認はしていない) |

- **共通する主因**: Stage 4になった2 runとも、claimが複数の文にまたがり、locateがそのうち1文しか選べなかった(a)。これは実データで確認済み。
- **副因**: (c)JA/EN食い違い(rep20 s2のみ)、(d1)引用符の扱い(rep21 s1で確認)。
- 備考(rep19、委任_35で是正済み): 別の原因(d)=floorのfact_id単位broadcast(設計書§6-15)。これは文の特定とは別の問題。

### 4-3. 「毎回別変種」とは何が毎回違うのか
固定したのはStage 1の**初回出力**のみ。毎回揺れているのは次の工程のLLM出力(実データで確認):
1. **Stage 2(判定役)のLLM出力**: 同じclaimでもBLOCKING/QUALITYの判定が割れる。さらにrewrite hintの有無・言語・引用の取り方が変わる
   (rep21 s1 cycle1は空、cycle2は英語引用つき、rep20 s2 cycle2はJA引用つき)。hintが空だとlocateの第一手がなくなる。
2. **Recheck(再検査、Stage 1の再実行)のLLM出力**: 次cycleで何を新たに指摘するか、`claim_in_article`の形(連続2文を1引用/離れた2文をand結合/先頭を大文字にした言い換え)。
3. **Rewrite(書き換え役)のLLM出力**: 同じ指摘でも何をどこまで直すか(rep21 s1 cycle1は"calls"→"a call"の1語のみ)。
(Stage 1初回の揺れは、委任_33/34で固定入力にして切り離し済み。)

---

## 5. 実例1件(meta_run03_standard、rep21 sample1)を処理順で

対象: `er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json`
(final_state=`STAGE4_ESCALATION`、stage4_reason=`cycle_limit_exhausted`、3 cycle、8 call、¥2.1567)

### 5-1. 元記事(該当箇所、逐語)
cycle1の入力(同ファイルのcycles[0].en_text_before_rewrite、15行目):
> News reports also cited one employee’s report. It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees. However, this is only one report. It would be wrong to say all contract workers did this.

JA側: このrun(origin=`translation`)ではJAを書き換えないため、rep21 s1のファイルにJA本文の記録は**なし**。
参考(別ファイル、同一固定データ由来と想定=未確認): `er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/meta_run03_standard.json` cycles[1].ja_text_before_rewrite の該当段落:
> 報道では、インターネットやケーブル料金を交渉する電話で、人間のスタッフによる人種に関する不適切な発言があったという従業員の報告も紹介されています。ただし、これは一件の報告です。契約スタッフ全体の話に広げることはできません。

### 5-2. Checker出力(Stage 1、生レコード)
1-1に示したレコードそのもの。要点: `claim_in_article`は上のEN記事の連続2文(「It said...during calls.」+「These calls were...fees.」)を1組の“ ”で囲んだ文字列。
理由は「“calls”の複数形が、Ledgerの1件の報告と合わない」。位置情報なし。rewrite hintなし。

### 5-3. 判定役(Stage 2)の出力(同ファイル cycles[0].stage2_results の該当claim)
```
"llm_materiality": "QUALITY",
"materiality": "BLOCKING",
"floor_reason": "deterministic_floor:changed_number",
"basis": "ledger_scope",
"rewrite_kind": "replace_with_ledger_value",
"rewrite_hint": ""
```
判定役LLMは重大度をQUALITY(軽微)としたが、`changed_number`が真のため機械的なfloor(安全装置)がBLOCKINGへ引き上げた。
rewrite hintは空。判定役への指示(`er052_open233_self_recovery_stage2_production_01.py` 56行)は「BLOCKING以外ならrewrite_hintは空文字列」なので、
LLMの判定がQUALITYだったことと整合するが、「これが空の原因だ」とは未確認(設計書§6-17は「非決定性」と記述)。

### 5-4. Rewrite側へ渡しているもの(`single_text_rewrite`)
- rewrite hint: 空のため、2747行により合成文字列 `materiality=BLOCKING, basis=ledger_scope` に置換される(コードからの導出。Promptの実テキストは記録なし)。
- issue: Checkerの`issue`(上記)。
- 対象文: 次の手順でプログラムが決定(`locate_target`)。
  1. hintから引用断片を抽出 → hintが空のため無し。
  2. `locate_multi_quote_span` → 引用断片が1つ(“ ”が1組)のため`not_multi_quote`で不採用(`extract_all_quoted_fragments`は2つ以上が条件)。
  3. `locate_best_sentence`: 引用符付き文字列はそのままでは記事に含まれない(実測False)ため、文ごとの類似度で選ぶ。
     本説明での再計算(記録されたものではない。同じ`difflib.SequenceMatcher`を元記事に適用): 1位 0.689「It said human staff made inappropriate comments about race during calls.」、
     2位 0.623「These calls were about trying to lower internet or cable fees.」。差は0.066で、閾値0.08(2264行)未満のため「ambiguous(僅差)」として不採用。
  4. `er010.locate_target_sentence`(単語重なり)にフォールバック。記録されたmethod: `e1_minimal_word_edit(er010_word_overlap(sentence_fallback(overlap=0.55)))`。
     どの文が選ばれたかは記録に直接はないが、元記事と書き換え後記事の差分(下記)から第1文だった。
- Rewrite Promptの実テキスト: **記録なし**(call_logにはprompt_sha256 `b3856f05fa3b8a200c729f65e15781accbdb97efb21b0e04ba5945446ded443a`のみ)。
  雛形(`E1_MINIMAL_WORD_PROMPT_TEMPLATE`)に上記の対象文・issue・hintが入る構造であることはコードから確認済み。

### 5-5. どこで特定が不完全になるか
- 「見つからない」のではなく、**連続2文のclaimのうち1文だけが選ばれた**。locateの類似度判定は1文単位で、2文をまとめた引用を1つの塊として扱う処理がない
  (複数引用断片をまとめる処理 `locate_multi_quote_span`は“ ”が2組以上の場合のみ作動する)。
- 書き換えは第1文のみ。cycle1の元記事→書き換え後の差分(同ファイル cycles[0] の before/after):
  `during calls.` → `during a call.`(1語)。第2文「These calls were about trying to lower internet or cable fees.」は元のまま残った。
- Rewrite後のチェック(`claim_text.strip() not in candidate`)は、claim_textが記事に存在しない引用符付き文字列のため、元から常に成立してしまう
  (引用符付きの文字列は書き換え前から記事に含まれない=実測False)。このため`guard_ok: true`となり、残り1文の取りこぼしはこの段階では検出されない
  (コードと上記実測からの推論。実行時に確認した事項ではない)。

### 5-6. その後の経過と結果
1. cycle1のRecheck(Stage 1再実行): `LEDGER_DEVIATION`(理由: `deterministic_floor_claim`)。新たなclaim: `“These calls were about trying to lower internet or cable fees.”`
   (同ファイル cycles[1].stage2_results、`same_fact_id_locations`は`["Paragraph 7"]`と位置の説明文)。
2. cycle2: 今度は判定役がBLOCKINGを付け、rewrite hintに引用 `“These calls were about trying to lower internet or cable fees.” 複数の電話ではなく、…「the reported call」などとしてください。参照: MUSE-HC-011` が入った。
   locateは`rewrite_hint_quote`で成功し、`These calls were`→`The reported call was`に修正(cycle2の差分)。
3. cycle3: 別の事実(MUSE-HC-010)の新規claim `“Some calls needed user information to continue.”`(記事の「Also, some calls needed...」と先頭の大文字小文字が異なる)がBLOCKINGで残った時点で、cycle上限に達した。
   cycle3ではRewriteは実行されていない(rewrite_recordsなし)。
4. 結果: `STAGE4_ESCALATION` / `cycle_limit_exhausted`。fail-closed(安全側)=自動で直し切れていない記事を「合格」にせず人間確認へ回した、という意味。false PASSではない。
- 推論(未確認): cycle1で2文claimを1文しか直せなかったことが、1 cycle分の余裕を消費し、cycle3の別claimを直す機会がなくなった。上限を先に使い切ったことと因果があるかは、実験していないため断定しない。

### 5-7. 比較用: もう1件のStage 4(rep20 sample2)の記録(要点のみ)
出典: `er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json` cycles[1](stage4_reason=`ladder_exhausted_without_full_rewrite`)。
- Checker出力のclaim_in_article: `“They could not tell if it was AI or a person” and “They did not realize it.”`(離れた2文の結合)。
- 記事側の該当2文は連続していない。記事(cycle1後のEN)は「...They could not tell if it was AI or a person. They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」で、2文の間に別の1文がある(cycles[0].en_text_after_rewriteで確認)。
- rewrite hint(JA引用つき): `「けれど、その一部では人間が話していた。しかも、適切な説明がないままなら、利用者は相手がAIなのか人間なのかを知ることができません。」…参照: MUSE-HC-012`。
- 本説明での再計算(記録外): 修正前のlocateはclaim全体との類似度で最大0.74の「They could not tell if it was AI or a person.」1文のみ、次点0.48。
- Rewrite3水準(単語/1文/段落)が全て規定のguardを満たせず終了。各水準のLLM出力・失敗理由は**記録なし**。設計書§6-17は「もう1文がどの水準の編集対象にも入らなかった」と説明するが、
  段落水準(`locate_paragraph_block`)なら段落内の両文が対象に入るはずで、説明とコード読解が噛み合うか未確認。

---

## 確認済み/未確認の区別

確認済み(コード・実データで直接確認):
- Checkerのschema/Promptに逐語引用指示・位置情報フィールドがないこと(`er003...generate.py` 464・502〜541行)。
- Rewrite Promptへ渡る項目と、書き戻しが完全一致の`.replace(..., 1)`であること。locateのあいまい一致の閾値と順序。
- rep19〜21 meta_run03_standardのfinal_state/stage4_reason、cycle別のclaim_text・rewrite_hint・差分。
- 1-1・5節のJSON/記事引用は実ファイルからの逐語コピー。23件の逐語率(21/23)は、記録されたEN記事テキストに対する本説明での機械照合。

本説明での再計算(記録された値ではない): 5-4のSequenceMatcher類似度(0.689/0.623)、5-7の0.74/0.48、逐語率。

未確認・推論に留まる:
- rep21 s1 cycle1でrewrite hintが空になった原因(判定役のQUALITY判定との関連は整合的だが、因果は未確認)。
- cycle1の取りこぼしがcycle上限到達に与えた影響(5-6)。
- Rewrite Promptの実テキスト・各水準の失敗理由(記録なし)。
- rep20 s2の段落水準が失敗した理由。
- rep21 s1のJA本文(別ファイルから参考表示。同一固定データであることは設計書§6-16〜6-17の記述に基づくのみ)。
- 1記事・3 run分という小さいサンプルの結果であり、他記事への一般化は未検証。

REPORT(`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`)§31〜§34は読んでいない(設計書§6-14〜6-17が同内容の要約であり、実データを直接確認したため)。

## 参考(推奨ではない)
- ユーザーが言及した文ID/文字オフセット方式は「Checkerが位置を番号で返す」案であり、現行コードには存在しない。現行は文字列照合のみ。
- 本説明で見えた現行locateの取りこぼし(引用符の扱い・複数文claim)を個別に直す案もあり得るが、いずれも未検証で、どれを採るかは判断事項。
