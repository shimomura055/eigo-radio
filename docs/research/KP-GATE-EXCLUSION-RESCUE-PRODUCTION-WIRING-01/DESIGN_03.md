# DESIGN_03: Key Phrase Gate除外救済方式のProduction確定設計(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01)

2026-10-26 / Status=DESIGN_FINAL+DEV_IMPLEMENTED(`er125_kp_rescue_production_01.py`+test 53件PASS。Production未配線=委任_02)。API 0。
前提文書: DESIGN-01 `DESIGN_02.md`(M1〜M6/R1〜R4)、DESIGN-02 `DESIGN_02.md`/`OPUS_REVIEW_02.md`、`SPEC_LEDGER_01.md`(採用表との対応・Opus台帳反映)。

## 1. 全体フロー(X/Y/Z共通・Standard/Advanced共通。入口=`er119_kp_candidates_01.generate_candidates`)

```
call1(Prompt 2) / call2(Prompt 2-V) -> er105.validate_and_resolve                    [H2: 選定段の救済]
     除外理由が 本文に連続一致しない -> D1再アンカー(合法な正規化関係にある一意の本文表層へ)
     除外理由が 有限助動詞(先頭it)  -> 慣用句の主語除去(核が辞書見出し+構造条件に一致)
     それ以外(語数>5・文境界・数値placeholder…) -> 救済しない(従来どおり除外->外側retry)
   助動詞始まりの慣用句そのもの(can't be helped / might as well)は有限助動詞guardの例外  [H1: contains_finite_aux_role_based]
-> canonicalization(LLM) -> parse -> postprocess[roles -> rescue]                     [H3-a: gate内hook、validate前]
     最終Gateと同一引数のvalidator(+CMU)で不合格のitemだけ: M1窓内再導出 -> revert(表層形)。成功すれば validate が通り INVALID/retry を消費しない
-> merge -> gloss再整合(既存。対象は表示候補に無い語を含むitem)
-> 救済rank: gloss強制再整合 + QA 12項目再判定(1 call/level-run, バッチ)              [H3-b: finalize_rescued_items]
-> CMU post-canon -> 記号 -> (Z: 人称整合/SRC D1) -> NG(used_form) -> 候補ID
-> 候補へ rescue メタ・旗・gates・auto_eligible を付与                                 [H4: annotate_candidate]
-> Redundancy QA -> 外側retry判定 -> kp_candidates.json 永続化(rescueメタ込み, candidates_sha256)
```
A/B/C旧経路(`_is_ft=False`)・`sc.run_key_phrases`系(旧候補なし経路)はhookを受け取らず挙動不変(golden 1002件バイト一致を確認済み)。

## 2. 慣用句の一般機構: QCD比較と選定理由

| 案 | 品質(Q) | 速度(D) | 単価(C) | 保守性 | 判定 |
|---|---|---|---|---|---|
| 旧: 27件閉表(DESIGN-02) | 高(人手レビュー) | 済 | 0 | 追加ごとに再レビュー・個別例外の積み上げ(ユーザー要件『一般的な仕組み』に反する) | **廃止** |
| (i) 辞書見出し照合+構造条件(採用) | 高(見出し一致+主語なし助動詞始まり+中身語あり+疑問文/名詞主語/断片除外+除外表) | 実行時はset照会のみ | API 0 | 辞書はsha固定・更新は取得script+差分レビュー | **採用** |
| (ii) 規則のみ(法助動詞+be+過去分詞等) | 低(`will be missed`/`could not bear`を通す) | - | 0 | - | 不採用 |
| (iii) LLM判定 | 中(非決定論) | +1 call | 約0.05〜0.5円/件 | 結果の再現性なし(決定論Gateの原則に反する) | 不採用 |

採用機構の条件(`idiom_exception`): (1)2〜5語 (2)先頭=法助動詞/助動詞(`can/could/should/may/might/must/will/would/shall`+縮約形+`have/has/had`系。**be系は含めない**=完全文化)、または先頭`come`+wh語+助動詞(`come what may`) (3)助動詞直後が主格代名詞/指示詞でない(倒置の疑問文を除く。have系は`it`を目的語として許可) (4)助動詞以外の中身語が1語以上 (5)見出しに一致(核そのもの、または`it`+核。所有格スロットは`one's/someone's`へ、`has/had`は`have`へ正規化。曲線/ASCII引用符両対応) (6)除外表(`denylist.txt` 10件: 侮蔑・スラング・方言・出来事特定の決まり文句)に無い。先頭が`it`の句は主語`it`のみ除去(that/there/名詞主語は除去しない=Opus M3)。

実測: 辞書10,661見出しのうち構造条件に合う116、そのうち**現行guardが実際に拒否している(=例外が判断を変える)25件**(`idiom_exception_listing_01.json`)。旧27件閉表の27件すべてを包含(`can't be helped`は見出し`it can't be helped`の核として一致)。fail-closed: 辞書・メタ・除外表のsha256(コード固定値と二重ピン)不一致/欠落/件数不一致は空表=例外なし。

## 3. 配線インターフェース(委任_02で実施。4箇所。Fable委任文の想定『er105とer119から1箇所ずつ』より多い=設計上の発見)

| # | 場所 | 追加する呼出 | 理由 |
|---|---|---|---|
| H1 | `er105_kp_fulltext_selector_01.py:941 contains_finite_aux_role_based` | 戻り値を `any(role=="aux" ...) and not _rescue().idiom_aux_exception_applies(text)` にする(`_rescue()`は関数内の遅延import=循環回避。er125はer105をtop-levelでimportする) | 有限助動詞guardは選定段(`_legacy_form_reasons`)とcanonicalization validator(`er003:627`)の**両方**がこの1関数を使うため、1箇所で足りる |
| H2 | `er105 validate_and_resolve:225`の項目ループ(`r.extend(_legacy_form_reasons(phrase))`の後) | `res = _rescue().rescue_selection_item(phrase, r, units)`。成功なら`phrase=res["phrase"]`で再`locate_phrase`し、recへ`selection_rescue`メタを保持。`build_original_items`(:266)が`selection_rescue`を原itemへ複写 | call1(`run_selection_gate`)とcall2(`run_vocab_selection`)の**共通choke point**。再帰はer125側の遮断flagで防止済み |
| H3 | `er003_v1_n3_01_scaffold_generate.py:475 run_key_phrase_canonicalization(..., rescue: bool=False)` | `rescue`が真かつ`is_fulltext`のとき `_postprocess = er125.chain_postprocess(_ft_pp.postprocess_possessor_roles)`(:502-507)。merge+既存gloss整合(:522-540)の後・`keywords_canonicalized.json`書込(:551)の前に `merged = er125.finalize_rescued_items(merged, parsed, original_items, text, gloss_realign_fn=..., qa_call_fn=...)`。`gloss_realign_fn`=`partial(er125.force_gloss_realign, make_factory_for=_align_factory, out_dir=..., article_id=...)`を(merged, ranks)で呼べる形に、`qa_call_fn`=`kc.make_canonicalization_fn(msg, model=routing.require_model(process, routing.SUPPORT_MODEL), schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)`の呼出しラッパ | 『rolesの後にrescue』(Opus論点5(i))、gate内でINVALIDを作らない |
| H3' | `er119_kp_candidates_01.py:162` | `canon_fn = canon_fn or functools.partial(sc.run_key_phrase_canonicalization, rescue=er125.rescue_enabled())`(test注入のcanon_fnは影響を受けない) | 明示引数方式(M2)。HRなし旧経路には渡らない |
| H4 | `er119_kp_candidates_01.py:305`直後 / `er119_kp_human_review_01.py:829` | 候補組立直後に `er125.annotate_candidate(cand)`(`auto_eligible`はANDのみ=緩めない)。`resolve_gloss`後の`auto_eligible`再計算(rv:829)にも `and er125.rescue_auto_ok(c.get("rescue"))`。HR依頼書の旗列(`render_request_md`:1193)に`cand["rescue_note"]`を表示 | 候補への旗・メタ付与と、HRでgloss解決後にauto不可の救済候補がauto可に戻らないため |

er119のimportはer125側に作らない(`er119_isolation_test_01`の方針維持)ため、Human NG照合は呼出側が`match_ng`/`candidate_id_for`を`ng_blocked`へ注入する(H4で`ng_blocked(cand, ng_entries, rv.match_ng, rv.candidate_id_for)`をNG再照合に追加)。

テスト側の更新(委任_02): `er105_kp_rule_compliance_test_01.py::test_rescue_flow_not_wired_in_er105`(禁止トークン検査は旧設計の名残。`reanchor`/`idiom`の語を許可する形へ改訂=旧規則の撤去)。`er105_kp_fulltext_selector_01_test_01.py::TestIsolation.ALLOWED`への`er125`追加は本委任で実施済み。

## 4. HRあり/なし両経路の扱い(既定)

- (α) **HR経路**: 救済候補は`flags.rescued=true`・`rescue_note`(元句・救済コード・QA再判定状態)付きで候補表に表示。人間が選ぶ。Human NG(`match_ng`)は原句・救済形の両方を照合(`ng_blocked`)し、既存の`auto_eligible_now`のNG判定も通る。
- (β) **HRなし(自動採用)経路の既定=QA再判定あり(品質優先)**: canonicalization段の救済(revert/M1)は、gloss強制再整合が`REALIGNED`かつQA 12項目再判定が`PASS`のときだけ`auto_eligible`を維持(それ以外はFalse=HRなしでは採用されない)。選定段の救済(D1/慣用句の核)は、救済後に通常のcanonicalization(gloss・QA込み)を通るので追加条件なし。順位は救済候補が`live`から外れないため元の`raw_rank`位置のまま(AIが順位を付け直さない)。
- QA再判定の方式: **新Promptを作らない**。承認済みfulltext canonicalization prompt/schemaを無変更で使い、救済後keyを`display_phrase`として渡して12項目を判定させる(`build_qa_rejudge_message`)。返却keyが救済後keyと一致しない/欄不正/例外のときは`NOT_REJUDGED`(auto不可・新しいINVALID/retryは作らない)。`qa_traceable_contiguous_span`は実際の(key, display)組で承認済みの有効判定へ再計算。1 call/level-run(該当itemをバッチ)。
- 費用: 該当0件ならAPI 0(従来と同一)。該当時は gloss強制再整合 約0.5〜0.6円/件 + QA再判定 約0.5〜1円/level-run。

## 5. retry/fallback/regeneration/resume の一貫性

- **永続化**: 救済は`item["rescue"]`(codes・selection/canonicalization別メタ・gloss/qa状態・`validator_args_sha256`)として`kp_candidates.json`の候補に保存。`candidates_sha256`は文書全体のsha=救済メタ込み(HR候補の不変性保証は従来の仕組みのまま)。resume(`ensure_kp_review`が保存済み候補を読む)は**再計算せず読み戻す**。`verify_persisted_rescue`で自己整合を確認(手編集は検出->fail-closed)。
- **決定論**: 救済は同一入力で同一出力(set/dict反復順に非依存。test: 3回同一JSON)。
- **外側retry(M-7c)**: 救済成功itemはdropped[]に入らない=`gate_dropped`に数えない(Fable指示)。結果、救済で`n_auto>=3`に届けばretryしない。救済失敗(M1/revert不能・D1窓なし・辞書なし)は従来どおりINVALID/除外->dropped->F1累積除外(OPEN-456)。
- **gate内retry**: 救済はparse直後・validate前なので、救済可能なitemのためにINVALID->再試行(`MAX_CANONICALIZATION_RETRY_ATTEMPTS`)を消費しない(test: 呼出1回)。
- **AI島`run_ai_01`の既存HR候補は不変**: 本moduleは候補ファイルを書かない・読み戻した既存候補への`annotate_candidate`は無変化(test: a2/b1bの全候補、ファイルsha不変、`candidates_sha256`再計算一致)。新フローは今後の生成runにのみ適用。

## 6. 既定ON・kill switch・適用経路

- 既定ON(ユーザー正式採用)。`rescue_enabled()`が唯一の読取点。`EIGO_KP_RESCUE=0`のときだけ全hook無効(従来動作。gloss整合の`EIGO_KP_GLOSS_ALIGNMENT`と同型の安全停止)。起動script/.envでONにする必要はなく、暗黙にOFFにもしない。
- 適用: `fulltext_p2`経路(X/Y/Z共通の`generate_candidates`)。YはX/Zと同じ`generate_candidates`を呼ぶ(`er121_family_y_runner_01.py:540-569`)ため同時に適用(OPEN-484=Yの正式初回経路との関係: 共通moduleのため追加配線不要。Y runner側の変更はなし)。Z限定のSRC D1・人称整合は救済後itemにも通常どおり適用(H3後段の既存処理)。
- 本委任の隔離確認: Productionファイルは`er125`をimportしない(test `TestUnwiredInProduction`)。承認済み機能の配線前状態であり、11-7の限定例外(未承認機能の既定OFF)は不要。PRODUCTION_WIREDと呼ぶのはFableが委任_02の正式runtime evidenceで判定するまで不可。

## 7. 非採用・残リスク(開示)

- 短縮(A1)・スロット一般化(A2)・CMU分解は実装しない。`too soon to wave a flag`は除外のまま。
- 辞書はWiktionaryの見出しのみ。スラング/侮蔑語は除外表(10件)で手当てしたが閉表であり、辞書更新時は差分レビューが必要(更新手順=`data/kp_idiom_lexicon_01/ATTRIBUTION.md`)。
- 縮約形(`can't`ASCIIはすり抜け/curlyは拒否)の既存不整合(R5)は未是正。慣用句例外はcurly/ASCII両対応で影響を受けない。
- QA再判定の実LLM挙動(承認済みpromptに`display_phrase=救済後key`を渡した場合のkey一致率)は未実測=委任_02のevidenceで確認。一致しなければ`NOT_REJUDGED`で安全側(HRでのみ採用)に倒れる。
- 救済で候補が増える方向の変更であり、Redundancy QA・最大件数(8)・数合わせ禁止・shortfall定義は無変更。
