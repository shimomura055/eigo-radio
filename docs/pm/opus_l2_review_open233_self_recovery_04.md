# Opus L2 レビュー #4 — OPEN-233-SELF-RECOVERY-TRIAL-01(読み取り専用・診断のみ)

実行モデル: `claude-opus-5[1m]`(Opus 5 / 1M context。指定の `claude-opus-5-5` ではなく、CLI 版の実 model_id はこちらでした)
日付: 2026-09-30 / 管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01 / 範囲: Trial 限定、Production 変更提案なし
API 呼び出し: 0 件(¥0)。既存 json/コード/設計書の読み取りのみ。

---

## 0. 先に: 今回の調査で見つかった最重大の新規事実(Q1〜Q3 すべてに影響)

**rep10 `hormuz_run03_standard` sample1 の cycle2 で、paired J-1 の段落 Rewrite が JA 側を壊したまま「解決」として完了している。**

Evidence(すべて `er052_output/open233_self_recovery_flow_runner_01_rep10/` 内、instance json と summary で同一):
- `instances_s1/hormuz_run03_standard.json` L5: `final_state: "RESOLVED_REWRITE_THEN_DOWNGRADE"`、L6 `stage4_reason: null`。
- 同 L421 / `summary_rep10.json` L1094: cycle2 の `ja_en_equivalence_verdict: "FAIL"`(これまで FAIL 0 件だったものの初 FAIL)。
- `summary_rep10.json` L1105: cycle2 の `ja_recheck_overall_status: "LEDGER_DEVIATION"`。
- cycle2 の `ja_text_before_rewrite`(L1091)と `ja_text_after_rewrite`(L1092)の実差分:
  - BLOCKING と指摘された JA 文「このとき確認できるのは、撤回の直後にBrent先物が下落したわけではない、ということです。」は **一字一句そのまま残っている**(修正されていない)。
  - 代わりに**直前段落の別の文**「報道時点では約二点六パーセント高で、一バレル八十五ドルを超えていました。」が**削除**された(HF-009 の `numeric_value: 約 +2.6%、$85/バレル超` に対応する記述)。
  - EN 側は正しく「Brent prices rose less for a short time, then soon went back near their earlier level.」へ修正済み。→ JA と EN が別内容になった(だから equivalence が FAIL)。

**なぜ止まらなかったか(コード上の継ぎ目、`er052_open233_self_recovery_flow_runner_01.py`)**:
- L3291-3293 で `ja_ok` は正しく False になる。しかし L3327 `if en_ok and ja_ok:` を抜けた後、L3339 で**次 cycle の Stage1 deviations を EN の `recheck_parsed` からのみ再構築している**(JA 側 `ja_recheck_parsed` の deviations は一切使われない)。
- その結果 cycle3 は `blocking_claims` が空になり、L3006-3007 で `RESOLVED_REWRITE_THEN_DOWNGRADE` として break する。**JA 側の LEDGER_DEVIATION は消える。**
- `ja_en_equivalence_verdict` は L3236 で cycle_record へ記録されるだけで、フロー制御に一切使われない(設計書どおり「測定専用」)。FAIL でも何も起きない。

**含意**:
1. Gate 項目「Safety 誤通過なし」は、厳密な STOP 条件文言(Safety-critical 10 / Safety 12 が BLOCKING でなくなる)には触れないが、**実質的な false PASS(指摘された JA 文が未修正のまま「解決」)が rep10 で実測された**。「安全≠成功」原則の観点では未充足扱いが妥当。
2. REPORT §19-2 の「A-2 escalate_to_paragraph で 2/2 sample 改善(rep9 STAGE4 → rep10 RESOLVED)」という PASS 判定は、**sample1 に関しては「壊れた JA を出力して RESOLVED になった」ものであり、改善ではなく検出漏れの可能性が高い**。rep9 の STAGE4(`cycle_limit_exhausted_after_recheck`)の方が正しい挙動だった可能性がある。この再解釈は §19-2 に反映されていない。
3. 委任_19 worker の A-1 論拠(「paired J-1 は全文 Recheck が唯一の安全網だから条件(c)を維持」)は、**その唯一の安全網(JA 全文 Recheck)自体が現状 fail-open** であることを見落としている。つまり (c) を維持しても paired の実リスクは塞がれていない。

---

## Q1. 局所 QA を基本形にできるか

### Q1(c) 先に: worker の「別箇所に初めて存在」論拠の妥当性 → **部分的に正しいが、原因の帰属が誤り。Fable の見立てが正しい。**

**判定: worker の観測事実は本物。しかし「だから全文 Recheck を毎 cycle 残す」という結論は導かれない。**

根拠(`er052_output/..._rep9/instances_s1/hormuz_run03_standard.json`):
- cycle1 L12: claim「Oil prices did not fall across the whole market after the plan was withdrawn.」(body、ladder `3_sentence`)
- cycle2 L227 / L273: 2 claim。片方は **cycle1 で書き換えた文そのもの**、もう片方は「"Oil prices moved briefly, then returned to a high level"; "oil prices stayed high"(also reflected in the headline)」
- cycle3 L488: 「"High Oil Prices Stay"(headline); "oil prices stayed high"(one-line summary)」

決定的な事実: **この headline と in-one-line は記事の元テキストであり、Rewrite が作ったものではない。** `summary_rep10.json` L881(rep10 cycle1 の `en_text_before_rewrite`)に、Rewrite 前の時点で `# The Fee Plan Leaves, But High Oil Prices Stay` と `## In one line\nThe fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.` が存在し、rep10 の全 cycle を通じて一度も変更されていない(L1089/L1090 でも同一)。

したがって:
- 「1 文の局所 Rewrite が見出しに新しい問題を作った」のではない。**Stage 1 初回(全文)が、同一 fact_id (HF-009) の別箇所を列挙し損ねた recall 不足**である。Fable の見立てが実測で裏付けられる。
- 全文 Recheck が後から拾えたのは、Recheck が `prior_issues`(HF-009 の scope 問題)を入力に受け取るため、**同一 fact_id を記事全体で狩りに行くよう priming されているから**(L3265-3275)。つまり全文 Recheck の有効性の実体は「全文を毎回見ること」ではなく「同一 fact_id を全箇所で探すこと」である。
- その機能は Stage 1 初回へ移せる。**しかも追加 call は不要**: Stage 1/Recheck の出力 schema に「各 deviation について、同じ fact を主張している記事内の全文(title/hook/in-one-line を含む)を列挙する」フィールドを足すだけで、call 数は変わらない(¥0 の限界コスト)。

**代替可能か → Yes、ただし条件付き。** 注意すべき副作用を 1 つ明記します: Stage 1 で全箇所を列挙すると cycle1 の claim 数が増え、既存条件 (b) `multiple_claims_rewritten_same_cycle` が発火して結局全文 Recheck に戻る。これは欠陥ではなく**リスク比例の正しい形**(分散している難しい記事は全文、単純な記事だけ局所)ですが、「Stage1 列挙を入れれば削減効果が出る」という期待は単純には成立しないことを Fable は織り込むべきです。

### Q1(a) ラダー①〜③(JA/EN ペア含む)の後に全文 Recheck を省略すると Safety が下がるか

**判定: 「無条件に外す」は NG。「条件付きで外す」は Safety を下げない。ただし現状のまま外すのは危険。**

全文 Recheck が実際に何かを捕まえた実例の全数は 5 件で、内訳は以下のとおり(disclosure §1-4-5 の 4 件 + 委任_19 の新規 1 件):

| # | 実例 | narrowing(c) 後に何が捕まえるか | Safety 低下か |
|---|---|---|---|
| 1-2 | `safety_A2A3` s1/s2 | 条件 (e) `safety_fixture` で維持 | しない |
| 3 | `safety_A5` s1 | 条件 (e) で維持 | しない |
| 4 | `meta_run03_standard` s2 | 条件 (d) floor で維持 | しない |
| 5 | `hormuz_run03_standard` s1 cycle3(headline/one-line) | **現条件では誰も捕まえない**(cycle1 は repeat_fact_ids 空、ladder=3_sentence) | **する**(worker の指摘は正しい) |

つまり Safety を下げるのは 5 件目だけで、しかもその 5 件目は「Rewrite が作った問題」ではなく「Stage1 の取りこぼし」です。**取りこぼしの補償手段としては、毎 cycle の全文 Recheck(高価・非決定的)より Stage1 同一 fact_id 全箇所列挙(¥0 限界コスト・決定的な入力範囲)の方が正しい対処**、というのが私の判定です。

さらに、Q1 に関して見落とされている重要な点が §0 の JA fail-open です。**paired J-1 について「全文 Recheck を残せば安全」という前提自体が rep10 で反証されています**(JA recheck が LEDGER_DEVIATION を返したのにフローが握り潰した)。条件 (c) を維持することは、この穴を塞ぐ代わりにはなっていません。

### Q1(b) 全文 Recheck を残すべき最小条件集合(推奨)

**維持(証拠あり)**
- **(a) ladder が ④段落 / ⑥全体 / ⑤削除** — 省略時に取りこぼす実例: rep10 `hormuz_run03_standard` s1 cycle2(`ladder_level_used: 4_paragraph`)。書き換え範囲が対象文±1 文の window を構造的に超え、実際に window 外の JA 文(+2.6%/$85)が消えた。
- **(d) deterministic floor claim** — 省略時の実例: `safety_er009_changed_number`(rep10 s1/s2、`precheck_floor` と `deterministic_floor:changed_number` の 2 経路が同一 title claim を指す)。Safety 側 fail-closed を緩めない原則として無条件維持。
- **(e) Safety fixture** — 実例: `safety_A2A3` ×2run、`safety_A5` ×1run(disclosure §1-4-5)。**ただし警告**: `instance_id.startswith("safety_")` は Trial fixture 命名に依存した条件で、Production には存在しない信号です。Production 配線を検討する段階になったら「Ledger fact が Safety-critical 指定」等の実信号へ置換が必須。現状のままでは Trial の数字が Production へ外挿できません。
- **(f) same_fact_id_reappeared_across_cycles** — 安価(¥0)で cycle2 以降の再発を拾う。維持。

**縮小を推奨**
- **(c) paired(J-1)** — blanket 維持ではなく「paired **かつ**(ladder ≥ ④ **または** JA 側決定論ガード不通過)」へ縮小。
  - JA 側決定論ガード(¥0、新規提案): (i) BLOCKING と指摘された JA 文が Rewrite 後も逐語で残っていないか、(ii) 対象段落以外の JA 文が消えていないか、の 2 点を文分割の差分で機械判定する。rep10 cycle2 の欠陥は **この ¥0 ガードで確実に捕まります**(実際 (i)(ii) の両方に該当)。JA 全文 Recheck(¥0.27/call)より安く、かつ現状より強い。
- **(b) multiple_claims_rewritten_same_cycle** — 維持してよいが、単独の実証例はありません(disclosure §1-4-5 の `meta_run03_standard` s2 は (d) でも捕まる)。維持コストは低いので「保守側で残す」で構いませんが、「実証済み条件」として報告しないこと。

**新設を推奨**
- **(g) 対象 claim の `section_type` が `title` / `hook` / `in_one_line`** — これらは前後 1 文が存在しない(または 1 文で 1 セクション)ため局所 QA の window 概念が成立しません。実例: `neg3_hormuz_prodrunner_b1b`(section_type `in_one_line`)、`safety_er009_unsupported_new_claim`(title 全体が 1 文 → 削除で空文字化、disclosure §1-1-4)。
- **(h) `ja_en_equivalence_verdict != PASS`** — 現在は測定専用。rep10 の唯一の FAIL が実際の JA 破損と一致したため、gating へ昇格する価値が実測で示された。

**廃止を推奨する設計(条件ではなく本体側)**
- L3339 が EN の recheck deviations だけから次 cycle を再構築している点。**JA の LEDGER_DEVIATION を次 cycle へ渡すか、渡せないなら `ja_ok=False` のまま loop を抜ける経路を STAGE4 にする**。これは条件集合の議論以前の fail-open 修正です。

### Q1(d) 期待コスト削減(rep9/rep10 実測からの概算)

実測単価:
- `stage1_recheck`: rep10 20 call ¥5.5059(平均 ¥0.2753)、rep9 26 call ¥8.0884(平均 ¥0.3111)、iter6 35 call ¥12.5997(平均 ¥0.3600)。
- 全体に占める比率: rep10 44.6%(¥5.5059/¥12.3479)、rep9 42.1%、iter6 40.9%。
- `local_qa`: 実測 1 件のみ、¥0.1120(REPORT §18-7)。**全文 Recheck の約 36〜40% の単価**。

シナリオ試算(rep10 の 14 instance-run、総額 ¥12.3479 = ¥0.882/instance-run を基準):
- **現状(条件 a〜f のまま)**: fastpath 発火 0/14 → 削減 **¥0**(実測済み)。rep9 も 3 試行 0 成功、正味 +¥0.112。
- **(c) を上記のとおり縮小した場合**: rep10 で `full_recheck_required_reasons` が `["both_ja_en_changed(paired_j1)"]` 単独だった cycle は 4 件(`hormuz_run03_standard` s1 c1 / s2 c1、`bgroup_B3` s1 c1 / s2 c1、いずれも ladder=`1_word_connective`)。各々 EN+JA の全文 Recheck 2 call を回避 → 8 call × ¥0.2753 ≈ **¥2.20 削減**、局所 QA 4 call × ¥0.112 ≈ ¥0.45 追加 → **正味 ≈ ¥1.75 / 14 instance-run = ¥0.125/instance-run(rep10 平均の約 14%)**。
- **理論上限(全 Recheck を局所 QA へ置換)**: rep10 で 22 call(recheck 20 + confirm 2)¥5.90 → 局所 QA 14〜20 call ¥1.6〜2.2 → 削減 ≈ ¥3.7〜4.3 = **¥0.27/instance-run(約 30%)**。ただし Safety 上あり得ない上限値であり、参考値としてのみ扱うべき。
- 29 instance × n=2 の広い Trial(概算 ¥58〜62、iter6 sample1 ¥30.8348 の 2 倍換算)で見ると、(c) 縮小の期待削減は **¥7〜8 程度**。

**コスト面の結論**: 局所 QA 導入は「+¥2/記事の上限を守るための必須策」ではありません(rep10 実測 ¥0.882/instance-run で既に上限内)。導入の主目的は**ユーザー指示の「念のため全文チェック禁止」= 非決定性と過剰 BLOCK の削減**であり、コストは副次効果(1〜2 割)と位置づけるのが正直な整理です。「コスト削減のために局所 QA を入れる」と説明すると、実測が伴わず説明責任を果たせません。

### Q1 推奨(まとめ)

1. **先に Stage 1 の同一 fact_id 全箇所列挙(schema 拡張、追加 call ¥0)を入れる。**
2. **先に JA fail-open(L3339 + equivalence 非 gating)を塞ぐ。¥0。**
3. その 2 つが入った後に限り、**(c) を「paired かつ(ladder≥④ or JA 決定論ガード不通過)」へ縮小**し、(g)(h) を新設する。
4. 順序を逆にしない。今 (c) だけ外すのは、worker の懸念(5 件目)と §0 の JA 穴の両方が未対処のままなので危険です。

### Q1 リスク

- Stage 1 列挙の schema 拡張は Stage1 出力形式を変えるため、既存の reuse fixture(`stage1_mode: "reuse"` の 26/29 instance)との互換に注意が必要。reuse 側は列挙フィールドが無いので、無い場合は従来動作へ安全側 fallback する実装が必須。
- 局所 QA の `adjacent_sentence_affected` は隣接 1 文のみで、離れた段落間の整合(REPORT §18-5「未網羅」)は依然カバーされません。条件 (a)(g)(h) がその代替である、という整理を明文化すべきです。

---

## Q2. neg3 の解釈

### 事実の確定

Ledger(`er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt` L58-64、HF-009):
- claim: Brent 先物が一時的に上げ幅を縮小したが、ほどなく発表前に近い高い水準へ戻った。記事掲載時点で約 2.6% 高、$85/バレル超。
- `conditions`: 撤回発表以外にも、**米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた**。
- `causal_strength: CAUSAL_STATED_BY_SOURCE`
- `notes_for_writer`: 撤回後に原油価格が全面的に下落したとは書かない。

対象 claim(`.../c_negative/neg3_hormuz_prodrunner_b1b/V4A/run_1.json` L12、section_type=`in_one_line`):
「The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.」

### 判定: **BLOCKING が妥当。ユーザー許容線を根拠に QUALITY へ落とすことはできない。**

理由を許容線に 1 対 1 で当てます。
- **因果部分(「the events driving oil prices」)→ 許容範囲。** ユーザーの例示「市場が海上リスクを重視したから価格が戻った」とほぼ同型で、確認済み Fact(海上リスク事象の継続 / 価格の回復)を人間が自然につなぐ解釈です。**ここだけなら QUALITY。**
- **時制・状態部分(「the events ... quickly returned」)→ NG 側。** Ledger `conditions` は「継続していた(continued)」と明記しています。「returned」は「いったん去った後に戻ってきた」を含意し、確認済み条件と**逆方向**です。これは解釈差ではなく状態の反転で、ユーザー NG リストの「time の重大変更」「Fact と逆方向」に当たります。
- **統語的な逃げ道は弱い。** 「the events ... —and the prices themselves— quickly returned」は 2 つの主語が同一 VP を共有する並置で、最も自然な読みでは両方が「returned」します。「returned は価格だけにかかる」という読みは可能ではあっても自然読解ではなく、「人間が自然に導く範囲」の側に立てません。
- **記事内整合からも裏付け。** 同記事本文は「けれど、海峡をめぐる緊張に関するニュースは、舞台に残ったままです」(= stayed)と書いており(`summary_rep10.json` L883)、in_one_line だけが「returned」に反転しています。記事自身が「継続」と言っているので、これは表現差ではなく要約時の事実変形です。
- **Rewrite の実害が小さいこともこの判断を支持。** rewrite_hint は「"the events driving oil prices—and" を削る」という最小削除(`.../rep10/instances_s1/neg3_hormuz_prodrunner_b1b.json` L51)で、rep10 は 2/2 sample とも `1_word_connective` 1 段で解消(s1 ¥0.7211、s2 ¥0.5417)。過剰 Rewrite でも品質劣化でもありません。
- **判定の安定性。** rep10 で 2/2 とも `llm_materiality: BLOCKING` かつ `floor_reason: deterministic_floor:changed_time`(L166-174、L207-215)、委任_19 の n=3 でも 3/3 BLOCKING(REPORT §19-3)。iter4/5 の QUALITY は少数派で、floor を外しても LLM 単独で BLOCKING になります。

**Safety を緩めない範囲での結論**: floor の `changed_time` も Stage2 rubric も、このケースのために緩める必要はありません。何も変更しないことを推奨します。

### negative 群ラベル「不要 Rewrite 0 が正解」の妥当性

**判定: neg3 についてはラベルが誤っている可能性が高い。ただし「分子から外す」のではなく「係争中(disputed)として両建て報告」を推奨。**

- 根拠: 上記のとおり claim は HF-009 の `conditions` を実際に反転しており、「クリーンな記事(Rewrite 不要)」という negative 群の前提を満たしていません。これは既に neg5 について行われた訂正(`er052_open233_self_recovery_flow_runner_01.py` L3007 `UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS = {"neg5_hormuz_div_a2"}`、Opus L2 #3 訂正 1)と**同じ性質の誤ラベル**です。
- ただし neg5 の除外は「B3 と同一 claim である」という機械的に検証可能な事実を根拠にしており、neg3 の根拠は**私の編集判断**です。同じ強度ではありません。Trial の正解ラベルを診断層の判断だけで書き換えるのは、Trial 設計の独立性を損ないます。
- **推奨する扱い**: `UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS` へ neg3 を足すのではなく、集計を **(i) neg3 込み、(ii) neg3 を disputed として除外** の 2 通りで併記する。iter6 数値なら (i) 4/9 = 44.4%、(ii) 分子・分母とも除外で 3/8 = 37.5%、分子のみ除外で 3/9 = 33.3%。どれを採るかは Fable/ユーザー判断。
- 併せて、REPORT §18-2 の「neg3 = 解決策なし」という記載は、**「解決策が無い」ではなく「解決すべき問題ではない可能性が高い」** に読み替えられるべきです。これが確定すれば、不要 Rewrite の未解決残件は 4 件中 0〜1 件になり、Gate 項目 4 の見え方が変わります。

### Q2 リスク

- 「in_one_line は要約だから多少の丸めは許す」方向へ一般化すると、`bgroup_B3`(同じく in_one_line、Safety-critical 回帰の監視対象)へ波及します。委任_16 の RUBRIC_R4_HOOK_AWARE が `bgroup_B3` を誤降格させた前例(REPORT §16-4)があるため、**in_one_line に対する一般的な緩和は提案しません**。今回は「個別ラベルの妥当性」の話に留めるべきです。

---

## Q3. 広い Trial(29 instance × n=2、≈¥50〜60)への Gate

### 9 項目の充足判定

| # | Gate 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | 局所 QA 是正 | **未充足** | rep9 3 試行 0 成功、rep10 **0/14 発火**(REPORT §19-1、§19-5)。locate バグ是正(SequenceMatcher 0.85)は unittest のみで実 run 検証ゼロ。「基本形」になっていない |
| 2 | 全体 Rewrite 3 件の立証 | **充足** | disclosure §1-1(3/3 が locate 失敗の副作用、「必要だった」根拠 0 件)+ 経路是正後 `6_full_article` は rep9/rep10 で 0 回(REPORT §18-1、§19-5) |
| 3 | 不要 Rewrite 4 件の開示 | **充足** | disclosure §1-2-1〜§1-2-4 で全件・原因分類つき開示済み |
| 4 | 解決策 | **部分充足** | neg1=Hook 専用 Stage2 で解消(実測)、neg2=disclosure-gap downgrade で 2/2 解消、`meta_run03_advanced`=検証機会なし(Stage1 が claim 自体を検出せず、REPORT §18-2)、neg3=Q2 のとおりラベル側の問題の可能性。**4 件中 1 件(meta_run03_advanced)は未検証** |
| 5 | 人間確認残存 | **部分充足(不安定)** | rep9 STAGE4 2 件 → rep10 0/14。ただし REPORT §19-3 自身が「neg3 s2 の rep9 STAGE4 消失は非決定性」と認めており、`hormuz_run03_standard` の消失は §0 のとおり**破損 JA での誤 RESOLVED**。n=2 では確立不能 |
| 6 | 代表ケース動作確認 | **充足(範囲限定)** | rep10 14/14 完走、Guardrail 内(¥12.3479/¥13)。ただし選定 7 instance は fastpath を一度も起動できない構成で、**項目 1 を検証できない代表ケース選定になっていた** |
| 7 | Safety 誤通過なし | **未充足** | §0 の実測。指摘された JA 文が未修正のまま残り、`ja_recheck=LEDGER_DEVIATION` / `ja_en_equivalence=FAIL` を握り潰して `RESOLVED_REWRITE_THEN_DOWNGRADE` で完了。Safety 12 / Safety-critical 10 の claim ではないため STOP 条件の文言には抵触しないが、「安全≠成功」原則には抵触 |
| 8 | 不要な全文 Check・全体 Rewrite の削減 | **半分充足** | 全体 Rewrite: 充足(⑥ 0 回)。全文 Check: **未充足**(削減 0 件、rep10 で `stage1_recheck` が総額の 44.6%[¥5.5059/¥12.3479]、rep9 42.1%) |
| 9 | 平均コスト影響 | **部分充足** | rep10 ¥0.882/instance-run、rep9 ¥1.75/instance-run(¥19.2263/11)、iter6 ¥1.0633/instance。+¥2/記事の上限内。ただし `local_qa` の単価根拠が 1 データ点(¥0.1120)のみで、「目的/省略時の悪化/安価代替」表(REPORT §18-7、§19-5)に local_qa 行が rep10 で消えている(0 回のため) |

**総合: 充足 3 / 部分 4 / 未充足 2 → 広い Trial の Gate は未充足。** 特に項目 7(Safety 誤通過)と項目 1(局所 QA が一度も機能していない)は、29 instance × n=2 を回しても自動的には解消しません。

### 広い Trial 前に必要な最小の追加作業(¥ 見積付き)

前提: 残予算 ¥169.50、広い Trial 概算 ¥58〜62、Phase 2(10 記事 × n=2)を残す必要あり。

| 作業 | 内容 | 費用 | Gate |
|---|---|---|---|
| **W1** | JA fail-open の封鎖: (i) L3339 の次 cycle 再構築へ JA recheck の MAJOR deviations を合流、または `ja_ok=False` のまま loop を抜ける経路を STAGE4 にする、(ii) `ja_en_equivalence_verdict != PASS` を gating 化、(iii) ¥0 決定論 JA 差分ガード(指摘 JA 文の逐語残存 / 対象段落外の JA 文消失)。unittest 込み | **¥0** | 7、5 |
| **W2** | Stage 1 の同一 fact_id 全箇所列挙(Stage1/Recheck の出力 schema 拡張、追加 call なし)。reuse fixture に当該フィールドが無い場合は従来動作へ fallback | **¥0** | 1、8 |
| **W3** | 条件集合の更新: (c) を「paired かつ(ladder≥④ or JA ガード不通過)」へ縮小、(g) short-section、(h) equivalence 非 PASS を新設。unittest 込み | **¥0** | 1、8 |
| **W4** | **fastpath が実際に起動できる代表ケース**での微小 Trial: `hormuz_run03_standard` / `bgroup_B3` / `meta_run03_standard` / `neg1_meta_b3prod_a2` を n=2(8 instance-run)。検証目標 3 点 = (i) fastpath が 1 回以上発火し正しく全文 Recheck を代替、(ii) Stage1 列挙が cycle1 で headline/one-line の HF-009 を surface、(iii) W1 の JA ガードが rep10 cycle2 の欠陥を捕捉 | **¥8〜10**(rep10 実績: hormuz n=2 ¥3.890 + B3 n=2 ¥1.218。meta/neg1 を rep9 相当で加算し Guardrail ¥10) | 1、7、8 |
| **W5** | neg3 ラベルの両建て集計(コード変更なし、REPORT の記載のみ) | **¥0** | 4 |

**追加作業合計 ≈ ¥8〜10。** 実施後の残額 ≈ ¥159〜161、広い Trial 後 ≈ ¥97〜103 が Phase 2 用に残ります。

**予算に不安がある場合の代替案(Fable 判断用)**: 広い Trial を一律 n=2 ではなく、**判定が安定している 20 instance を n=1、非決定性が実測されている 9 instance(neg1/neg2/neg3/meta_run03_advanced/meta_run03_standard/hormuz_run03_standard/hormuz_run03_advanced/bgroup_B3/safety_A2A3)を n=2** とすると ≈¥40 に収まり、¥18〜20 を Phase 2 へ回せます。非決定性の測定が必要なのは後者だけなので、統計的な損失は小さいと考えます。

### Q3 リスク

- W1〜W3 は ¥0 ですが**コード変更を伴う**ため、Trial runner の既存 224 件 unittest の regression 確認が前提です(特に W2 の schema 拡張は reuse 経路 26/29 instance に触れます)。
- W4 を省いて W1〜W3 のまま広い Trial に入ると、「Gate 項目 1 を 29 instance の本番で初めて試す」ことになり、失敗時に ¥58〜62 を溶かします。**W4 は省略しないことを強く推奨します。**
- 委任回数の上限(Sonnet 初回+修正 3 回 = 最大 4 回)に対し、本件は既に委任_19 まで到達しています。W1〜W5 を 1 委任に束ねられるかは Fable 側の管理 ID 運用の判断事項です(私からは判断しません)。

---

## 追加で気づいた重大点

1. **REPORT §19-2 の PASS 判定は要訂正候補。** 「A-2 で 2/2 sample 改善」の sample1 は §0 のとおり破損 JA での誤 RESOLVED。escalate_to_paragraph が「解決率を上げた」のか「検出を潰した」のかが区別できていません。少なくとも REPORT へ本件を追記し、PASS を「sample2 のみ PASS / sample1 は要再判定」へ改めるべきです。
2. **条件 (e) `instance_id.startswith("safety_")` は Production へ外挿できない。** Trial fixture の命名規約に依存しており、Production 記事には該当する信号がありません。今の測定結果を「Production でもこの安全網が効く」と読むのは誤りです(Trial 限定の但し書きが REPORT / design 書に無いようです)。
3. **`stage2_second_judge_2of2` が floor claim では発火しない構造**(L1434 `floor_reason is None` 条件)。neg3 のように floor と LLM が一致する claim は 2-of-2 による安定化確認を一度も受けません。disclosure §1-2-4 が指摘済みですが、Q2 の判定(私は BLOCKING 妥当と判断)においては「floor に守られているから検証されていない」という構造的死角がある点を Fable は認識しておくべきです。
4. **`safety_A2A3` が rep10 で 2/2 とも `RESOLVED_REWRITE_THEN_DOWNGRADE`** (`summary_rep10.json` L470、L526)。Safety fixture が「BLOCKING 1 件 + QUALITY 2 件」の構成で最終 downgrade 経由の解決になっており、これが期待どおりの経路かは REPORT で明示されていません。広い Trial 前に確認しておく価値があります(¥0、既存 json の読み取りで可)。
5. **本レビューで参照できなかったが精度に影響しうる範囲**: Production 側 `er010_ledger_local_rewrite_09.py` の `run_diff_qa_for_accepted_rewrite`(L289-333)は Fact Checker A'(web_search 込み)を使いますが、OPEN-233 の局所 QA は web_search 無しの 1 call です。**両者は同名でも守備範囲が違う**(Production は外部事実確認あり、Trial は Ledger 突合のみ)ため、「Production 局所 QA と同等」と説明することはできません。Trial 側の局所 QA は「Ledger 局所突合」と呼ぶのが正確です。

---

## 出力先について

本文は `docs/pm/opus_l2_review_open233_self_recovery_04.md` へ逐語保存してください(私は読み取り専用のため書き込んでいません)。Production 採用の可否はここでは判断していません。次の対応(W1〜W5 の実装に進むか、ユーザー判断を仰ぐか)は sandwich-pm 側の判断に委ねます。

参照した主要ファイル(絶対パス):
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01.py`(L2395-2442 `full_recheck_required`、L2445-2481 `find_sentence_context`、L2599-2634 `run_local_qa_fastpath`、L3238-3261 fastpath 配線、L3289-3344 recheck/cycle 判定、L3006-3007 downgrade 判定)
- `C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_flow_runner_01_rep10\summary_rep10.json`(L881-895 cycle1、L896-1106 cycle2、L1094 equivalence FAIL、L1105 ja_recheck)
- `C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_flow_runner_01_rep10\instances_s1\hormuz_run03_standard.json`(L5、L421)
- `C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_flow_runner_01_rep9\instances_s1\hormuz_run03_standard.json`(L5-6、L227、L273、L488、L538)
- `C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_phase1_step3_stage1_compare_01\c_negative\neg3_hormuz_prodrunner_b1b\V4A\run_1.json`(L12-54)
- `C:\Users\tensh\eigo-radio\er019_output\family_x_refresh_e2e_01\hormuz\run_03\ledger\verified_fact_ledger.txt`(L58-64、HF-009)
- `C:\Users\tensh\eigo-radio\docs\pm\open233_iter6_rewrite_disclosure_01.md`(§1-1〜§1-5)
- `C:\Users\tensh\eigo-radio\docs\pm\design_open233_self_recovery_flow_01.md`(§6-5 L1909-1987、§6-6 L1989-2038)
- `C:\Users\tensh\eigo-radio\OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§18 L1338-1443、§19 L1444-1533)
- `C:\Users\tensh\eigo-radio\er010_ledger_local_rewrite_09.py`(参照のみ、Production 側局所 QA の守備範囲確認)
