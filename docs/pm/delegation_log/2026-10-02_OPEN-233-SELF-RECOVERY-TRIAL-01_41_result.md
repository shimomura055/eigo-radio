<!-- 抽出元transcript: agent-a64bb81b83a6c60d6.jsonl(subagents配下。指定の.outputは0バイトで抽出不能だったため同内容のsubagent transcriptを使用)。抽出日時: 2026-10-02T21:37:24。本文(最後のassistantメッセージ)は改変していない。 -->

# 委任_41 報告(OPEN-233 無料集計、¥0、実装・Trial・API呼び出しなし)

**最重要の連絡**: `docs/pm/report_open233_handoff_log_aggregation_01.md` は作成できなかった。Write時にハーネスが「サブエージェントは報告書.mdを書かず本文で返せ」と拒否した。回避せず、報告本文をこの最終メッセージに載せた。保存が必要ならFableが保存してほしい。`DECISION_LOG.md`・`OPEN_ITEMS.md`・`REPORT_LEDGER.md`には「報告本文は委任_41最終報告、集計結果は`results_01.json`」と書いた。同ファイルへのリンクは張っていない。

commit `e0ae8de0c228f1a4bf2a1890fbbce5a6b5b5ed1d`、`git push origin main` 成功(c3555de0..e0ae8de0)。

## 0. 結論(所見。最終判定はFable)
1. meta_run03_standardは、Rewriteへ進む(BLOCKING)指摘44行すべてをCheckerの文字列だけで範囲確定できた(確定不能0)。K1全体では73行中、判定不能2行を除く71行のうち確定不能は2行(2.8%、いずれも非BLOCKING)。
2. 全記事では、BLOCKING 261行のうち35行(13.4%)が確定不能。ユニークでは13/78(16.7%)。原因は言い換え・要約21行(実質2種類のB3固定文)、説明文混在12行、省略記号1行、その他1行。
3. 現行が複数文の一部だけを対象にする「取りこぼし型」が23行(ユニーク7)ある。rep21 s1、rep19、iter8 s1・s2、iter6 s2のStage 4がこの型。新方式なら複数文とも1周目の対象に入ることは決定論的に言える。
4. meta_run03_standardのStage 4全8件(全期間)すべてで、現行の対象が新方式の範囲と異なるBLOCKING指摘を含む。
5. rep20 s2型(JA側)は受け渡し修正だけでは決まらない。ENは2範囲を確定できるが、JAの対応範囲を決める情報がない。位置比を外すと、EN単独で直る→JA再検査→JA指摘が次周回へ、という経路になる。cycle上限(最大3周)には余裕がなく、収まるかは「不明」。
6. 別AI(判定役)引用救済は、metaでは不要。全体では「あれば有用だが不可欠ではない」。
7. Checker Promptは、metaでは変更の必要性が見えない。全体は既存ログだけでは判定できない(逐語Prompt後の逐語率が未測定)。
8. STOP条件3つ(多数のケースで確定不能/Prompt変更なしで構造的に成立しない/別AI引用救済が不可欠)は、metaについては所見上いずれも非該当。ただしJA側は別論点として残る。

## 1. 対象(報告項目1)
- 19ディレクトリ・277ファイル(iter5 58、iter6 55、iter7 18、iter8 38、rep7 14、rep8 10、rep9 22、rep10 14、rep11 8、rep12 8、rep13 2、rep14 2、rep15 1、rep16 9、rep17 4、rep18 6、rep19 1、rep20 4、rep21 3)。うち29ファイルは`cycles`が空(ACCEPTABLE_STAGE1)。対象は248ファイル・342 cycle。
- 対象外: `instances`(アンダースコアなし)、`smoke_instances`、iter2〜4。定義の`instances_*`に合致しないため。rep7の`b3_revert_verify`・`b3refix`は合致するため含めた。委任_39付録Aも同じ277ファイル。
- 指摘696行の内訳:

| 種類 | 行数 | うちBLOCKING | ユニーク |
|---|---|---|---|
| K1(主集計) | 464 | 272 | 152(BLOCKINGは79) |
| K2 | 213 | 55 | 79 |
| K3 | 19 | 19 | 3 |

- K1のうちStage 1初回は327行、Recheckは137行。`claim_text`と`claim_in_article`が違う行は0件。
- K2展開で捨てられた`same_fact_id_locations`要素: 14件(13種類)。記事本文が分かる周回のみで下限値。分類は「Paragraph beginning…」等の位置説明、引用符付きの文、日本語の文など。新方式の照合を当てると、説明文混在(A4)7、不一致(A4)2、A3 2、A1 3。A1の1件は見出しラベル“In one line”の誤確定。
- 判定不能(cycle1の本文記録なし)はK1で75行(BLOCKING 11行、ユニーク1)。理由: Rewriteで本文が変わった周回だけ`en_text_before_rewrite`が保存される(runner 4386〜4391)。分母から除外した。
- 日本語claim 22行(7種類)のうち、JA本文で確定5、説明文混在4、本文記録なし13。
- 検査が見た記事の特定: 委任_39付録Aの仮定は正しかった(cycle k≥2は前cycleの`en_text_after_rewrite`)。両方記録のある33組で不一致0。採用順は「同cycleのbefore、なければ前cycleのafter」。
- 補助集計(定義外): 同一fixtureのcycle1本文は記録のある全runで1種類のみ。借用して再集計した値を`supplement_borrowed_cycle1_text`に入れ、下に「補助」と併記する。

## 2. A(報告項目2)
判定の実装上の補足は2点。(a)L4のつなぎ語に`/`も含めた(rep19 cycle3の`“…” / “…”`)。(b)断片1つ+説明文も「説明文混在」で確定不能にした。原因ラベル付けと参考値にだけ診断目的で類似度とhintを使った。範囲の確定には使っていない。

| 区分 | K1全体 延べ | K1全体 ユニーク | BLOCKING 延べ | BLOCKING ユニーク |
|---|---|---|---|---|
| 判定不能(本文記録なし) | 75 | 19 | 11 | 1 |
| 判定可能(分母) | 389 | 133 | 261 | 78 |
| A1 1文以内 | 269 (69.2%) | 85 | 174 | 45 |
| ・1文全体 | 206 | 57 | 148 | 34 |
| ・文の一部 | 63 | 28 | 26 | 11 |
| A2 複数文のまま | 72 | 22 | 48 | 16 |
| A3 離れた複数箇所 | 6 | 6 | 4 | 4 |
| **確定可能 計** | **347 (89.2%)** | 113 (85.0%) | **226 (86.6%)** | 65 (83.3%) |
| A4 確定不能 計 | 42 (10.8%) | 20 (15.0%) | 35 (13.4%) | 13 (16.7%) |
| ・不一致 | 25 | 6 | 23 | 4 |
| ・説明文混在(断片2つ以上+説明文) | 11 | 8 | 9 | 6 |
| ・説明文混在(断片1つ+説明文) | 6 | 6 | 3 | 3 |
| ・複数箇所一致 | 0 | 0 | 0 | 0 |

- 補助(cycle1本文を借用): BLOCKINGは272行中36行(13.2%)が確定不能、ユニークは79中13(16.5%)。
- 確定に必要だった照合レベル(確定行のみ): 全体(延べ)はL0 162・L1 146・L2 11・L3 22・L4 6。BLOCKING(延べ)はL0 127・L1 63・L2 11・L3 21・L4 4。ユニークは全体がL0 54・L1 44・L2 2・L3 7・L4 6、BLOCKINGがL0 31・L1 22・L2 2・L3 6・L4 4。L0のうち5行は日本語本文での確定。
- A3の間: 隣接2、1文挟む1、2文挟む1、3文挟む1、17文挟む1、文の途中1(1行は3断片)。BLOCKINGのA3は隣接1・1文・2文・17文。
- 段階別のBLOCKING確定不能率: Stage 1初回 27/203=13.3%(不一致23+説明文混在4)。Recheck 8/58=13.8%(すべて説明文混在)。
- 記事別(BLOCKING 延べ):

| 記事 | 行数 | 判定不能 | A1 | A2 | A3 | A4 |
|---|---|---|---|---|---|---|
| meta_run03_standard | 44 | 0 | 28 | 14 | 2 | **0** |
| bgroup_B3 | 24 | 0 | 3 | 0 | 0 | 21(不一致) |
| safety_A4 | 23 | 3 | 10 | 5 | 0 | 5 |
| hormuz_run03_standard | 25 | 0 | 22 | 0 | 0 | 3 |
| bgroup_B4 | 11 | 0 | 6 | 1 | 2 | 2 |
| neg1_meta_b3prod_a2 | 16 | 0 | 3 | 11 | 0 | 2 |
| safety_A2A3 | 19 | 6 | 12 | 1 | 0 | 0 |
| hormuz_run03_advanced | 3 | 0 | 2 | 0 | 0 | 1 |
| bgroup_B2_hormuz | 1 | 0 | 0 | 0 | 0 | 1 |
| safety_A5 | 8 | 1 | 0 | 7 | 0 | 0 |
| safety_er009_*(8種) | 計62 | 1 | 61 | 0 | 0 | 0 |

  全fixtureは`results_01.json`の`A.by_instance_blocking_rows`・`A.by_instance_blocking_unique`。
- meta_run03_standardのK1:

| 対象 | 行数 | 判定不能 | A1(全体/一部) | A2 | A3 | A4 |
|---|---|---|---|---|---|---|
| 全指摘 | 73 | 2 | 37 (21/16) | 30 | 2 | 2(非BLOCKING) |
| BLOCKINGのみ | 44 | 0 | 28 (12/16) | 14 | 2 | 0 |
| rep19〜21 全指摘 | 23 | 0 | 5 (2/3) | 16 | 2 | 0 |
| rep19〜21 BLOCKINGのみ | 13 | 0 | 5 | 6 | 2 | 0 |

  BLOCKING 44行の必要レベルはL0 3・L1 22・L3 17・L4 2。主な表記差は引用符の囲み(L1)と先頭の大文字小文字(L3)。
- 付録Aとの差: 判定可能行数は同じ389で、meta rep19〜21も23行で一致(L1 19・L4 2・L3 2が付録Aの(b)19・(c)2・(d1)2に対応)。差が出た理由は次のとおり。(1)付録Aの(a)157に対し今回のL0は162。日本語claimをJA本文で確定した5行を足したため。(2)付録A(c)19に対し今回のL4は6。「断片以外の残りがつなぎ語だけ」の条件を課したため、説明文付きの17行が確定不能に回った。(3)付録Aの(d1)34に対しL2+L3は33。(4)付録Aの(d)33に対しA4は42。(2)で+17、JA確定で-5、その他の移動で調整。「ちょうど1箇所」は、複数箇所一致が0件で結果に影響しなかった。

**現行との比較**(K1・BLOCKINGでRewrite実行の260行)

注意: `rewrite_records`に`before_fragment`は**保存されていない**。そこで現行ロケータ(runner 2449〜2473)を、記録のclaim・hint・当時の本文から決定論的に再現した。再現の検証は記録のmethod文字列との一致で行い、162行中159行(98.1%)が一致した。`j1_*`の対ペア経路98行はmethodに特定語がなく検証できない。同cycleに複数BLOCKINGがある81行は近似。

| 関係 | 延べ行 | ユニーク |
|---|---|---|
| 同じ | 105 | 27 |
| 現行が拡大(現行⊃新) | 32 | 10 |
| 現行が縮小・新が1文以内(語句・句に絞った) | 50 | 12 |
| **現行が縮小・新が2文以上/複数箇所(取りこぼし)** | **23** | **7** |
| 一部重なり | 2 | 2 |
| 別の箇所 | 0 | 0 |
| 新で確定不能 | 34 | 12 |
| JA本文でのみ確定(EN比較不可) | 3 | 2 |
| 判定不能(本文記録なし) | 11 | 1 |

補助値は、同じ110・拡大33・縮小(1文以内)52・縮小(取りこぼし)24・一部重なり2・確定不能35・JAのみ3・現行は対象特定不能1。

「縮小・1文以内」は、ユーザー§4の最小修正優先と整合しうる(問題とは限らない)。問題になりうるのは「取りこぼし」型と「拡大」型。

現行のmethod別(延べ行):

| method | 同じ | 拡大 | 縮小(1文以内) | 縮小(取りこぼし) | 一部重なり | 新で確定不能 | その他 |
|---|---|---|---|---|---|---|---|
| rewrite_hint_quote(132) | 52 | 17 | 48 | 12 | 0 | 0 | 判定不能3 |
| exact_substring(8) | 8 | 0 | 0 | 0 | 0 | 0 | — |
| sequence_matcher(14) | 4 | 3 | 0 | 3 | 1 | 3 | — |
| er010_word_overlap(8) | 0 | 0 | 0 | **7** | 0 | 1 | — |
| multi_quote_span | 記録に0件(委任_36修正後の実走が未発生) | | | | | | |
| 対ペア(j1_*等、98) | 同じ31、拡大12、縮小(1文以内)2、縮小(取りこぼし)1、一部重なり1、確定不能32、JAのみ3、判定不能16 | | | | | | |

単語重なり(er010)で決まった8件のうち7件は、複数文の一部だけを対象にする取りこぼし型だった。

## 3. B(報告項目3)
共通: cycle1の固定Stage 1で、MUSE-HC-011の2文claim(「It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.」)がBLOCKING。新方式ではL1で確定し、A2(記事側の2文135字)になる。

### (a) rep21 s1 [Stage 4: cycle_limit_exhausted]
| cycle | BLOCKING指摘 | 現行の対象(再現) | 新方式で渡せる範囲 | 差 |
|---|---|---|---|---|
| 1 | HC-011 2文claim(**Stage 2のhintが空**) | method=er010単語重なり(overlap=0.55)で**第1文のみ**。1語句修正「during calls.→during a call.」 | 2文とも(L1、A2) | **現行が縮小(第2文を取りこぼし)** |
| 2 | HC-011「“These calls were about trying to lower internet or cable fees.”」(Recheckで第2文が指摘) | hint引用で第2文 | 第2文(L1、A1) | 同じ。この周回で直る |
| 3 | HC-010「“Some calls needed user information to continue.”」(**cycle3で初出**) | **Rewrite未実行**。`cycle>MAX_CYCLES`で追加周回条件を満たさず`cycle_limit_exhausted` | 「some calls needed user information to continue.」(L3、A1一部) | 現行は未実行 |

- 決定論的に言えること: 新方式ならcycle1で2文とも対象に入る。第2文の持ち越し周回は構造上起きない。
- LLM次第の部分: Rewriteが2文とも直すか、HC-010が何周目に指摘されるか。HC-010の初出は、rep21 s1がcycle3、rep20 s1がcycle2、rep21 s2は指摘なし。
- 上限回避の見通し: HC-010がcycle2に出れば`MAX_CYCLES=2`内で処理される。cycle3以降の初出なら、追加周回条件(runner 4194〜4226)を満たさない限り同じ結果になる。「回避できそう」は言えるが保証はない。

### (b) rep20 s2 [Stage 4: ladder_exhausted_without_full_rewrite]
| cycle | BLOCKING指摘 | 現行の対象 | 新方式の範囲 | 差 |
|---|---|---|---|---|
| 1 | HC-011 2文claim | hint引用で2文とも(1語句修正で2箇所、guard True、再検査で解消) | 2文(L1、A2) | 同じ |
| 2 | HC-012(origin=`ja_source`)「“They could not tell if it was AI or a person” and “They did not realize it.”」 | 記録: method=`+ladder6_disabled`、全水準でguard不成立(各水準のLLM出力は記録なし)。現行ロケータでの再現: `multi_quote_span`の3文(間のQUALITYの文を含む) | **離れた2範囲**(L4、A3、間に1文): 「They could not tell if it was AI or a person」「They did not realize it.」 | 現行(再現)は拡大 |

cycle2の実走は委任_36より前のもの。`multi_quote_span`追加後に、同じ経路を通った実走はまだない。cycle2で全水準がguard不成立になった真因は記録がなく**不明**(JA側か、EN複数範囲か、主体置換ガードか)。

### (c) 対照: rep20 s1 [解消]
| cycle | BLOCKING指摘 | 現行の対象 | 新方式の範囲 | 差 |
|---|---|---|---|---|
| 1 | HC-011 2文claim | hint引用で2文とも(guard True、再検査で解消) | 2文 | 同じ |
| 2 | HC-010「Some calls needed user information to continue.」(**cycle2で初出**) | hint引用で2文(Also, some calls… That information…)、段落水準(`e2_paragraph_rewrite`) | 文の途中1箇所(L3) | **現行が拡大** |
| 3 | BLOCKINGなし(HC-012はQUALITY) | — | — | 解消 |

### (d) 対照: rep21 s2 [解消]
cycle1はHC-011の2文を現行も2文で(hint引用、guard True、再検査で解消)。cycle2はBLOCKINGなしで解消。HC-010は一度も指摘されなかった。rep20 s1・rep21 s2とも、cycle1の対象は新方式と同一だった。rep21 s1が違うのはhintが空だったことだけ。

### 全期間のmeta Stage 4 8件(一覧)
| run | stage4_reason | 受け渡し起因(現行対象と新範囲の差) | 是正状況(DECISION_LOG見出し・コードコメントからの照合。各報告全文は未読) |
|---|---|---|---|
| iter6 s1 | same_claim_fact_id_reblocked | HC-012を対ペア段落水準で対象(現行が拡大)、同claim再発 | 委任_24の範囲。範囲の拡大は未是正 |
| iter6 s2 | cycle_limit_exhausted | **取りこぼし型**(cycle2で第1文のみ、cycle3で第2文) | 委任_36は断片2つ以上のみ。断片1つ・2文の型は未是正(rep21 s1で再現) |
| iter8 s1 | same_claim_fact_id_reblocked | cycle1で取りこぼし。K2のBLOCKINGがcycle2に6件・cycle3に7件 | K2は委任_34〜35で是正。取りこぼしは未是正 |
| iter8 s2 | target_not_locatable | cycle1で取りこぼし。target_not_locatableの出所はK2(ja_source、JA文) | 出所の詳細は不明 |
| rep11 s1 | ja_deviation_unresolved | 範囲ではなくJA/EN対応 | 委任_20 W1のfail-closed(安全装置が作動) |
| rep19 s1 | cycle_limit_exhausted_after_recheck | cycle1で取りこぼし。cycle3のA3(間17文)を現行は片方のみ対象(一部重なり)。K2増加 | 委任_35でK2とiol_degenerateを是正。取りこぼしとA3の片方のみは未是正 |
| rep20 s2 | ladder_exhausted_without_full_rewrite | 上記(b) | 委任_36で`multi_quote_span`追加。実走は未確認 |
| rep21 s1 | cycle_limit_exhausted | 上記(a) | 未是正(hint空→単語重なり) |

rep16〜18のmetaはStage 4ではない。

### 4つの問いへの答え
1. 1回目に渡せる範囲: cycle1のHC-011は2文。**現行も、Stage 2のhintが2文を引用すれば同じ範囲で渡している**(対照3件)。取りこぼしが起きるのは、hintが空または引用なしで単語重なりに落ちた場合。新方式が直すのは「hintに依存した範囲決定のばらつき」。
2. 余計な周回が減るか: 決定論的には「第2文の持ち越しによる1周」が構造上なくなる。傍証として、新方式と同じ範囲(複数文を丸ごと)を現行が渡したBLOCKING 24行(meta以外を含む)の結果を数えた。次周回に同factのBLOCKINGが再出現したのは1行(rep19 c2)。次周回がなく解消したのは11行。次周回に別事実が出たが同factは非BLOCKINGが12行。guard不成立は1行(rep20 s2 c2のA3合成claim)。
3. 上限到達の回避: rep21 s1型は決定論的に「取りこぼしによる1周消費」が消える。再検査が別事実(HC-010)をいつ指摘するかはLLM次第で、断定しない。
4. 残る問題: 下記。

### rep20 s2のJA側のコード上の経路
1. `use_pairing`(runner 3199〜3203): originが`ja_source`でJA本文があれば`paired_rewrite`(2920〜3193)。
2. JA対応文の決め方(2940〜2973): hint引用→claim文字列→Ledger文言→**ENの位置比をJAへ写像**(`locate_ja_counterpart_by_position`、2497〜2536)の順。位置比は文が空でない限り必ず何か返すため、**現行ではENの対象が決まればJA側もほぼ必ず(推測で)決まる**。3081〜3106の「片側のみ」経路は、現行では「ENが決まらずJAだけ決まる」場合に使われる。
3. 位置比を外すと`ja_target=None`になり、3081〜3106のEN単独Rewrite(`mechanism`=`paired_ja_en(J-1)`、`method`=`j1_single_side_en(...)`)に入る。JA本文は変わらない。
4. 4513〜4527・4559〜4560: `mechanism`が`paired`なのでJA Recheckが走る。JAは未変更のため未解消の可能性が高く、`ja_ok=False`・`ja_pending_deviation=True`になる。
5. 4606〜4631: ENのRecheckに同fact_idの指摘がなければ、JA RecheckのMAJORが`origin=ja_source`で次周回に合流する(同fact_idがENにもあれば重複として捨てられる)。JA claimはJA文字列になり、新方式の照合はJA本文に対して行う。
6. 4122〜4131: 次周回でJA指摘がBLOCKINGでなくなると、`ja_pending_deviation`が真のため`ja_deviation_unresolved`(人間確認)になる構造がある。rep11 s1が実例。
7. cycle上限(275〜279、4194〜4226、4633〜4636): 最短でcycle1=HC-011、cycle2=HC-012のEN、cycle3=HC-012のJA。cycle3は`cycle>MAX_CYCLES`のため、追加1周条件(blocking数減少、または過去BLOCKINGの同fact新箇所)を満たす場合のみ(1回)。JA指摘は同factなので満たす可能性が高いが、fact_id+claim本文の近似一致(4147〜4154)で「同一claim再発」と判定されれば即`same_claim_fact_id_reblocked`になる(JAとENの文字列類似度は低く該当しにくいが断定不可)。cycle3の再検査で新指摘が出れば`cycle_limit_exhausted_after_recheck`(4633)。
8. まとめ: 上限内に収まる余地は最小限(余裕ゼロ)で、`ja_deviation_unresolved`等で人間確認になる構造的可能性はある。収まるかは**不明**(JA Recheckの出力、Stage 2の揺れ、JA claimの逐語性に依存)。位置比を残せば、推測が当たればcycle2で収まりうる。ただし後段がJA対応を推測する処理で、ユーザー§1の基本線との関係はFable判断事項。

### それでも残る問題(記録で観測された事実)
1. 再検査が周回ごとに別事実・別箇所を新規指摘する。rep21 s1のHC-010はcycle3で初出、rep20 s1はcycle2、rep21 s2は出ない。iter8 s1はBLOCKINGがcycle2で6件、cycle3で7件に増えた。
2. Stage 2の重大度が揺れる。同じ文字列がQUALITYとBLOCKINGの両方で現れたものがmetaで3種類。「They enjoyed AI's convenience… They did not realize it.」は17行中15行QUALITY・2行BLOCKING。「They did not realize it.」は13行中8行QUALITY・5行BLOCKING。
3. JA/EN対応。対ペアのguardは「JAもENも変わる」ことを要求する(3063〜3066)ため、対応の推測が外れると失敗しうる。
4. K2のBLOCKING増加。委任_35で是正済みだが過去の記録に残る。
5. rep21 s1 cycle1のHC-011は、BLOCKINGなのにhintが空だった。
6. Checkerが間違った箇所を逐語で指す誤りは、どの方式でも検出できない。
7. 拡大型32行・縮小(1文以内)型50行の扱いは、Rewrite側の設計次第。

## 4. C(報告項目4)
**判定: metaでは「受け渡し修正だけで十分そう」。全記事では「既存ログだけでは判定できない」。**
- meta: BLOCKINGの確定不能は0/44。rep19〜21の23行はすべて確定可能で、必要な照合は引用符・大文字小文字・断片分解だけ。
- 全体: BLOCKINGの確定不能は13.4%(35/261)。内訳(行数)は言い換え・要約21(実質2種類のB3固定文)、断片2つ以上+説明文9、断片1つ+説明文3、省略記号1、その他1。**これらはどれも原文逐語の指示で減りうる種類**で、指示しても解消しない種類は見つからなかった。複数箇所一致は0件。
- 判定に必要なもの: 受け渡し修正後の限定Trialでの確定不能率。逐語指示後の逐語率は未測定。
- 参考: rep16以降の27 runでBLOCKING確定不能を含むのは2 run(7.4%)。n=27で結論は出せない。
- Prompt変更は行っていない。

## 5. D(報告項目5)
| | 延べ | ユニーク | 率 |
|---|---|---|---|
| K1全体の確定不能 | 42/389 | 20/133 | 10.8% / 15.0% |
| K1・BLOCKING | **35/261** | **13/78** | **13.4% / 16.7%** |
| K1・非BLOCKING | 7/128 | — | 5.5% |
| meta・BLOCKING | 0/44 | 0/13 | 0% |

BLOCKING確定不能35行の記事別: bgroup_B3 21、safety_A4 5、hormuz_run03_standard 3、bgroup_B4 2、neg1_meta_b3prod_a2 2、hormuz_run03_advanced 1、bgroup_B2_hormuz 1。

Human Reviewへの影響(分母=277ファイル):
| 集団 | run数 | BLOCKING確定不能を含む | 率 | 現行の最終結果 |
|---|---|---|---|---|
| 全run | 277 | 32 | 11.6% | Stage 4が10(cycle_limit_exhausted 3、cycle_limit_exhausted_after_recheck 2、ja_deviation_unresolved 5)、解消22(RESOLVED_REWRITE 18、RESOLVED_REWRITE_THEN_DOWNGRADE 4) |
| iter8 s1(29 instance) | 29 | 0 | 0%(補助1=3.4%、Stage 4[ladder_exhausted]) | — |
| iter8全体(38) | 38 | 0 | 0%(補助1) | — |
| rep16以降 | 27 | 2 | 7.4% | 解消2、Stage 4 0 |
| meta全run | 23 | 0 | 0% | — |

- **新方式で増えうる上限**: 現行で解消していた22 run(277のうち7.9%)。現行のStage 4は40件(14.4%)なので、+55%相当。内訳はbgroup_B3 17、safety_A4 3、bgroup_B2_hormuz 1、hormuz_run03_advanced 1。B3は古い固定文が大半で、rep16以降は2 run。metaは0。現行fallbackが直せていた根拠は、確定不能BLOCKINGでRewrite実行34行のうち23行で`all_prior_issues_resolved`が真だったこと。
- **減りうる上限**: 現行Stage 4 40件のうち、現行の対象が新方式の範囲と異なる指摘を含むrunは13件(32.5%)。metaは8件すべて。補助では15件。
- **hint引用で拾える参考値**(採用しない): 確定不能BLOCKING 35行のうち30行(85.7%)、ユニークで9/13、補助で31/36。
- **判定**: meta=不要。全体=あれば有用だが不可欠ではない。理由は、上限影響が7.9%でその大半が古いB3であること、Promptで逐語化できる可能性、新方式で確定不能を人間確認とする、またはChecker返し直し(設計書§2-4のB)という他の選択肢があること。必要性が数字で確認されたとは言いにくいが、拾える上限は大きい。採用はしていない。

## 6. E(報告項目6)
iter8 s1(29 instance)+iter8 s2(9)+rep16以降のStage 4は12件。
| run | stage4_reason | 現行と新方式の差 |
|---|---|---|
| iter8 s1 meta | same_claim_fact_id_reblocked | **あり** |
| iter8 s1 safety_A2A3 | target_not_locatable | なし(補助: 現行は特定不能) |
| iter8 s1 safety_A4 | ladder_exhausted | なし(補助: 拡大、新で確定不能) |
| iter8 s1 safety_A5 | ladder_exhausted | なし(補助: 取りこぼし) |
| iter8 s1 safety_er009_unsupported_new_claim | ladder_exhausted | なし(補助: 縮小・1文以内) |
| iter8 s2 meta | target_not_locatable | **あり** |
| rep16 neg3_hormuz_prodrunner_b1b | ladder_exhausted | なし |
| rep18 safety_A2A3 ×2 | ladder_exhausted | なし(s2の補助: 縮小・1文以内) |
| rep19 meta | cycle_limit_exhausted_after_recheck | **あり** |
| rep20 s2 meta | ladder_exhausted | **あり** |
| rep21 s1 meta | cycle_limit_exhausted | **あり** |

- 機械的に受け渡し起因と言えるのは**5/12(41.7%)、すべてmeta**。補助では7/12(safety_A4・A5が加わる)に、現行が対象特定不能の1件。
- iter8 s1単独では、Stage 4が5件(17.2%)のうち1件(補助3件)。stage4_reason別はladder_exhausted 3、target_not_locatable 1、same_claim_fact_id_reblocked 1。
- rep16以降は6件(ladder_exhausted 4、cycle_limit_exhausted 1、cycle_limit_exhausted_after_recheck 1)のうち3件(すべてmeta)。
- 「範囲が違う」=「それが原因でStage 4」とは限らない(因果の証明ではない)。Safety系ladder_exhaustedは範囲の差だけでは説明できない。

## 7. F(報告項目7)
- 所見: 「受け渡し修正だけでmetaの**主要問題**が解消できそう」は、根拠付きで概ね言える。ただしJA側(rep20 s2型)は別。
- 根拠: (1)取りこぼし型(meta Stage 4 8件中4件)は決定論的に解消する。(2)対照3件は2文の1回Rewriteで3/3がguard成立・再検査で解消(n=3の傍証)。(3)確定不能0/44で、全件が表記差のみ。
- 残る不確実性: 再検査が別事実をいつ指摘するか(LLM次第)、JA側の扱いの設計判断、Stage 2の重大度の揺れ(受け渡し修正の範囲外)。
- STOP条件: (1)多数のケースで確定不能=非該当(meta 0%、全体BLOCKING 13.4%)。(2)Prompt変更なしで構造的に成立しない=非該当(metaは成立。JAは対応設計の問題でPromptの問題ではない)。(3)別AI引用救済が不可欠=非該当。
- 実装する場合の設計論点(参考): JA側で位置比を使うか、delete型の再出現確認(類似度)、複数範囲を渡すときのRewrite呼び出し単位、現行が文全体・段落に広げている拡大型32行をユーザー§4に合わせてどう扱うか。

## 8. 検算・決定論(報告項目8)
- (i)OK: rep21 s1の固定Stage 1 deviations[1]はL1で確定、A2。
- (ii)OK: rep20 s2 cycle2の`“…” and “…”`はL4で2範囲、A3(間に1文)。
- (iii)OK: `Paragraph beginning “People asking Muse to call”`はK1の`claim_in_article`には無く、捨てられた`same_fact_id_locations`要素(rep20 s2 cycle2、s1 cycle2にも同様の2件)として記録にあった。定義を当てると分解されずA4(説明文混在)。
- (iv)OK: meta rep19〜21のK1は23行で付録Aと一致(L1 19・L4 2・L3 2)。
- (v)OK: 無作為10件(seed=41)は定義どおり(A1 6、A2 2、A4説明文混在1、A4不一致1)。明細は`results_01.json`の`sample10`。
- 決定論: 2回実行で`results_01.json`・`claims_detail_01.csv`のmd5が一致した(results `d420a30e…`、csv `0c0e583d…`)。ただしこの後、スクリプトを変えずに再実行はしていない。commitしたのは同じ2ファイル。
- 現行ロケータの再現はmethod文字列と162行中159行(98.1%)一致。

## 9. 限界・未確認(報告項目9)
- 判定不能(本文記録なし)はK1で75行(BLOCKING 11行)。補助集計で補い、併記した。
- 現行の対象範囲は再現値。対ペア98行は検証不能、同cycle複数BLOCKINGの81行は近似。
- 新方式の範囲は照合の結果にすぎず、Checkerが正しい箇所を指しているかは検証していない。
- 「縮小/拡大」は範囲の大きさの比較で、Rewrite結果の良し悪しは見ていない。
- 日本語claimはJA本文の記録がある場合のみ照合した(22行中13行が判定不能)。
- Rewriteが実際に直すか、再検査が何を指摘するかは、決定論的には言えない。傍証はn=24行。rep20 s2 cycle2の全水準guard不成立の真因は記録なし。
- 各stage4_reasonの是正状況は、DECISION_LOG見出しとコードコメントからの照合。各報告全文は読んでいない。
- 補助集計は定義外。同一fixtureのcycle1本文は全run一致(1種類)で借用したが、定義の本流ではない。

## 10. T-0・Git・変更確認(報告項目10)
- T-0: `check_delegation_prompt.py`の結果は**PASS**。warningは「TTSを伴う委任文だが差分再生成/--budget言及なし」のみで、本委任はTTS非該当。保存先は`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md`と同`_41.md_check.json`。
- 既存`*.py`・Prompt・テストは未変更。runner・Trialスクリプト・回帰テストは未実行。LLM/API/TTS/Web Searchも呼んでいない。`git status`のtracked変更に`.py`は無い。
- commit `e0ae8de0c228f1a4bf2a1890fbbce5a6b5b5ed1d`、`git push origin main`成功(c3555de0..e0ae8de0)。
- `git show --stat HEAD`: DECISION_LOG.md +228(ユーザー原文逐語収録を含む)、OPEN_ITEMS.md ±2行(OPEN-233行の次Actionセル末尾に追記、Status他列は不変)、REPORT_LEDGER.md ±2行、委任記録_41.md +324、`_41.md_check.json` +1、`aggregate_01.py` +972、`claims_detail_01.csv` +697、`results_01.json` +17889。計8ファイル。
- 1ファイルずつ明示`git add`し、`git add -A`・stash・amend・force pushは未使用。無関係の既存tracked変更・untrackedは触れていない。
- `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は更新済みで`.gitignore`対象のためaddしていない。ACTIVE_TASKは指定どおりの固定ヘッダ。
- raw URL:
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_handoff_log_aggregation_01/aggregate_01.py
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_handoff_log_aggregation_01/results_01.json
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/REPORT_LEDGER.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md
  - https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41.md_check.json

## 11. 指示どおりにできなかった点・迷った点・追加Read(報告項目11)
- 報告書`docs/pm/report_open233_handoff_log_aggregation_01.md`は、ハーネスの制約で作成できなかった(上記)。この最終メッセージが報告本文。保存するならFableが行ってほしい。SSOT記述は「ファイル」ではなく「最終報告/`results_01.json`」を指している。
- `before_fragment`が記録されていないため、現行の対象範囲は再現値になった(指示は「記録された…`before_fragment`」)。
- 定義の補足2点: L4のつなぎ語に`/`を含めた。断片1つ+説明文を「説明文混在」で確定不能にした。
- 補助集計(cycle1本文の借用)は定義外で、指示にない。cycle1本文なしによる判定不能75行が、E・Dの評価を大きく弱めるため追加し、定義の本流とは分けて併記した。
- 一覧外の追加Read: `er010_ledger_local_rewrite_09.py`の`locate_target_sentence`/`split_sentences`(40〜86行、現行ロケータの再現のため)、runnerの`locate_best_sentence`ほか(2241〜2380)、`check_delegation_prompt.py`の必須見出し部分(30〜70行)、Opusレビュー#5の§5〜6(59〜104行)。
- 事前指定Readで読まなかった箇所: 設計書§4-3(238〜257行)、Opusレビュー§8は§5〜6の読み取り範囲に含まれる行のみ。集計に不要と判断した。
