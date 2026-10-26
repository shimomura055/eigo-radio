# DESIGN_01: Key Phrase候補「除外→修正救済」方式の設計(X/Y/Z共通・調査設計のみ・API 0)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01 / 到達上限Status=`USER_DECISION_REQUIRED`(Sonnetは`判断候補`と表記、ラベル付与はFable)。Productionコード・Prompt・Gateは変更していない。
設計の中心(ユーザー指示): 解決したいのは「8件に届かないこと」ではなく「適切に修正できる候補まで捨ててしまうこと」。よって**候補数の補充(数合わせ)は目的としない**。救済は「既に選ばれた候補を、承認済みGateを変えずに残す」ことだけを行う。

## 0. 結論(先に)

1. 実データ(HR導入後のGate除外11件)のうち、**承認済み規則内で機械的(API 0)に救済できるのは4件(36%)**。残りは新規則(ユーザー承認)が必要な3件(27%)と救済困難4件(36%)。HR導入前の一意句29では同12件(41%)/2件(7%)/11件(38%)/現行で既に通る4件(14%)(RESCUE_ANALYSIS_01 §1)。
2. 救済の部品は既に承認済みの先例がある。`postprocess_possessor_roles`(`er105_kp_fulltext_selector_01.py:927`、UDR #173②・2026-10-24承認)が「canonicalization応答のparse直後・validate前に、決定論で『revertのみ』行い、validatorを通ることを確認できなければ無変更」を実装済み(hook=`er003_v1_n3_01_scaffold_generate.py:502-507`)。**救済は同型の後処理を「基本形化の失敗」へ広げるだけで足りる**(新Gate・新Promptなし)。
3. ただし救済フロー自体は11-8の「新しい処理方式」に当たるため、採否はユーザー判断(段階1)。受理面を広げる項目(段階2: 副詞後の原形化・限定詞`no`等・`rang`等・lexical have・短縮提案・スロット一般化)は項目ごとにユーザー承認が要る。
4. AI島 `studied separately` は段階1で**表層形のまま**HR候補に残せる(既存validator通過を机上確認)。原形`study separately`は新規則(W2)。`too soon to wave a flag` は段階1では救済できず(段階2c)、ユーザー例`too soon to do`は現行規則でも段階2の範囲でも通らない別種の新規則(本文に無い語の生成)になる。

## 1. 救済フロー(候補抽出 → Gate検査 → 違反検出 → 修正可能性判断 → 修正 → 再検査 → HR候補登録)

```
[既存] call1(Prompt 2)/call2(Prompt 2-V) -> 選定gate(validate/重複/NG/CMU)
                                          \-> 違反検出(1): 語数>5 = 救済点B(段階2c)
[既存] canonicalization(LLM) -> parse
   [新: 救済点A] postprocess_lemma_repair(parse直後・validate前, API 0)
        違反検出: 各itemを既存validatorに通し Rule7(基本形化) で落ちるものを抽出
        修正可能性判断(決定論の2段):
          (1) 再導出: spanの各tokenを「現行の許可表の1対1置換」へ置換した全組合せのうち、
              既存validator+CMU通過のもの。LLM案に最も近い(一致token数最大)案を採用
          (2) revert: key_phrase = display_phrase(無変更。Rule7の『無変更』)
        修正: item.key_phrase / normalization_reason / changed_from_display_phrase を更新し lemma_repair を記録
        再検査: 同じ validate_canonicalization_response を全体に再適用(M-7(a)「全体PASSのみ受理」を維持)
        失敗: 無変更のまま(現行どおり INVALID -> item除外 -> 残りで再実行 -> dropped記録)
[既存] gloss再整合 -> CMU post-canon -> 記号 -> (Z: 人称整合/SRC D1) -> NG(used_form) -> 候補ID -> Redundancy QA
[新] 候補に rescue 記録と flags.rescued を付けて HR候補(kp_candidates.json)へ登録
```

(a) **機械的修正で足りるものとAI(追加LLM call)が必要なもの**

| 区分 | 内容 | 方式 | LLM call | 段階 |
|---|---|---|---|---|
| 機械(決定論) | 表層形revert、現行表での再導出、人称一般化のみ残す再導出 | `postprocess_lemma_repair` | 0 | 1 |
| 機械(決定論・表の拡張) | W1 guard限定詞追加(`no`,`each`…)、W2 guard副詞追加、W3 過去形専用表の補完(`rang`…) | 閉表/guardの拡張(新規則) | 0 | 2a/2b |
| 機械(検査精緻化) | lexical `have`を有限助動詞扱いしない | `_contains_finite_auxiliary`の精緻化(新規則) | 0 | 2e |
| **AI判断要** | 6語以上の短縮(どの部分列が意味を保つか。`too`を落とすと意味が反転する実例あり) | 新規「短縮提案」1 call(Prompt 2/2-Vはsha固定のため新Promptが必要=Opus条件A/ユーザー承認) | 1/該当句 | 2c |
| 不可 | 本文に無い語の生成(`too soon to do`)、CMU未登録、modal/進行形auxを核とする句、本文不一致、Human NG | 救済しない(2d: スロット一般化は非推奨) | - | - |

2c(AI短縮提案)の呼出条件・回数上限: 選定段で語数>5のみ・1句につき最大1回・1レベル最大2句まで・候補は元句の連続部分列に限る(本文対応保持)。提案は**`dropped[].rescue_options`に記録するだけ**とし、候補にするかは(i)出た部分列を既存パイプライン(canonicalization→gloss→…)に通す、(ii)通過したものだけ`rescued`旗付きで候補化、の順。費用は§4。**推奨は2cを今回は採用せず保留**(発生率が低い=HR導入後14イベント中1件、かつ意味反転リスクのため)。

(b) **再検査**: 新Gateは作らない。救済点Aは既存`validate_canonicalization_item`/`validate_canonicalization_response`をそのまま呼ぶ(`postprocess_possessor_roles`が`er105:976-978`で同関数を呼ぶ先例)。修正後の候補はその後の全段(CMU post-canon・記号・gloss・Z限定SRC D1/人称整合・NG・Redundancy QA)を通常候補と同条件で通る。選定段で句を差し替える場合(2c)は差替え句を**選定gateの先頭**(語数→重複→NG→CMU)から再適用する。

(c) **記録形式**(`kp_candidates.json`の候補に追加するフィールド案):

```json
"rescue": {"applied": true, "method": "mechanical_revert|mechanical_rederive|llm_shorten",
           "rule": "revert_to_surface|rederive_current_tables|...",
           "before": {"selection_phrase": "studied separately", "llm_key_phrase": "study separately",
                      "stage": "canonicalization", "reasons": ["Rule7 ..."]},
           "after":  {"used_form": "studied separately"},
           "recheck": {"validator": "PASS", "cmu": "PASS", "words": 2},
           "scope": "S1"},
"flags": {"rescued": true},
"auto_eligible": false
```

`dropped[]`には救済で候補化した場合も元の除外理由を残し`rescued_as`(candidate_id)を付ける(監査性)。HR依頼書(`render_request_md` `er119_kp_human_review_01.py:1193-1213`)の「旗」列に `修正済み(元: studied separately / 原形化不可: 動詞+副詞)` を出し、元形はその行に常に見える。「Gateで除外された候補(参考)」節(`:1214-1218`)には「→候補Nへ救済」を追記。`candidates_sha256`は救済込みの文書全体に対して従来どおり固定される(既存の仕組みのまま)。

(d) **既存仕様との整合**
- 順位: 救済候補は元のLLM順位(call1の順/call2の`raw_rank`)の位置にそのまま戻る。`ai_rank`の付番(`er119_kp_candidates_01.py:308-310`)は無変更で、AIが順位を付け直さない。
- 重複排除: 救済後の句も`_containment`(`:30-33,81-83`)とRedundancy QA(`:312-327`)にかかる。実測: AI島の救済案は現行a2の5候補と包含/同一にならない。
- 最大8・数合わせ禁止: 救済は元から選ばれていた句を残すだけで、補充ではない。call2の最大5件(`p2v.SELECTOR_2V_MAX_ITEMS`)は救済後に再適用(超過は下位をoverflow)。shortfallの定義(`:353`)は無変更。
- AUTO/NG: 救済候補は**`auto_eligible=False`(Human選択のみ)を既定**(LLMのQAは救済前のkeyに対する判定のため。既存の`qa_fail`旗と同じ扱い)。NGは「元の選定句」と「救済後の句」の両方に`match_ng`を適用(NG復活禁止を救済で迂回させない)。ユーザーが将来AUTO可に緩めるかは別判断。
- 外側retryとF1累積除外: 救済に成功した句は`dropped`に入らないので累積除外リスト(DECISION_LOG.md:87)にも入らない。救済に失敗した句は現行どおりdropped+累積。除外リストにある句は選定gate(LLM前)で落ちるため救済は試みない。外側retryは「AUTO可<3 かつGate除外あり」のまま(救済候補は`n_auto`に数えないので条件を緩めも厳しくもしない)。
- OPUS R-1「vocabのshortfall受容・数合わせretryなし」(`OPUS_REVIEW_01.md:54`。`OPUS_FINDINGS_LEDGER.md`でKP HR関連行はGrepで特定できず=未確認): 救済は補充ではないので矛盾しない。

(e) **X/Y/Z共通核での位置**: `er119_kp_candidates_01.py generate_candidates`が呼ぶ`sc.run_key_phrase_canonicalization`内の`run_canonicalization_gate(postprocess=)`(`fulltext_p2`のときのみ設定、`er003_v1_n3_01_scaffold_generate.py:502-507`)。X・Y・Zは同じ経路で、差はZ限定のSRC D1・人称整合(救済後のitemにも既存どおり適用)のみ。Z全文選定の決定論validatorが別にあるわけではなく、同一の`is_valid_inflection_normalization`系。A/B/C旧経路は`fulltext_source_ref`が無く`_is_ft=False`のため無影響(27-7)。

## 2. 制作速度への影響

段階1は決定論のみ(ミリ秒)で待ち時間を足さない。むしろ現行の「INVALID→item除外→canonicalization LLM再実行(1 callあたり実測約27秒、AI島raw_usage_log scaffold行の最終行elapsed_seconds)」を避けられる。実測: 外側retryが発動したのはHR導入前の`fulltext_p2` outer_retry_log 78件中25(32%、tell-tale heart等の再実行を含み過大評価)、HR導入後は13 level-run中0。段階2cのみ該当句で+1 call(10〜30秒)。

## 3. 品質リスクと歯止め

| リスク | 歯止め |
|---|---|
| 表層形(非原形)の候補が増える | `rescue.method`と旗で明示、`auto_eligible=False`、HRがユーザー判断 |
| 再導出で意味が変わる(例: 名詞化した語を動詞原形に) | 既存の閉表・除外表(`_PLURAL_EXCLUDE`、`_PARTICIPIAL_ADJ_EXCLUDE`)とguardをそのまま使う。新しい許容を作らない。CMU辞書登録で`studi`のような非語を排除(実装済みの検証を再利用) |
| 所有格のrole(self/other_person)を無視した人称一般化 | 再導出は`postprocess_possessor_roles`の後に置き、roles検証結果(`person_role_repair`)を尊重。未検証ならrevertを選ぶ |
| 本文対応の喪失 | 救済は元span内のtoken置換またはrevertのみ。選定段の短縮(2c)は元句の連続部分列に限る |
| 意味反転(`too soon to wave…`→`soon to wave…`) | 機械の左削り・右削りは行わない。短縮は2c(LLM提案+HR選択)に限り、`auto_eligible=False` |
| 救済でGate基準が実質緩む | 段階1は「受理面を広げない」(revert=Rule7の『無変更』、再導出=現行validator通過のみ)。受理面を広げる項目は段階2で個別にユーザー承認 |

## 4. 追加コスト(70円/記事セット目標に対して)

単価の出典: `er009_n1_routing_governance_10_actual_model_cost.py:30`(gpt-6-luna 入力0.10/キャッシュ0.01/出力0.50 USD per 1M token)、`:21`(1USD=160円)、AI島`raw_usage_log.jsonl`実測3行(gloss再整合0.563円・同0.526円・part2_cand 0.322円)。

| 案 | 追加LLM call | 追加コスト/記事セット(2レベル) | 備考 |
|---|---|---|---|
| 段階1(機械のみ) | 0 | **0円**(救済が成立した場合は現行の再実行1回分を節約=約-0.3〜-0.6円) | 70円目標への影響は無視できる(<1%) |
| 段階2a/2b/2e(表・検査の拡張) | 0 | 0円 | 判定が変わるだけ |
| 段階2c(AI短縮提案) | 該当句ごとに1 call+通過句のcanonicalization/gloss | 発生率8%(HR導入後13 level-runで1件)として期待値約+0.03〜0.05円/レベル、発生時約+0.8〜1.7円(提案0.3〜0.6+canon/gloss0.5〜1.1) | 保留推奨 |
| AI島a2の今回分を救済して再発行する場合 | gloss再整合 1 call | 約0.5〜0.6円(a2のみ、実測0.526〜0.563円) | §7 |

費用承認区分: 本設計はJPY0。実装後の運用増は上表のとおり0円〜1.7円/発生時で、7-7の案件300円閾値には遠い。

## 5. 推奨する必要十分な実装案(段階化。ユーザーが段階ごとに採否を決められる)

| 段階 | 内容 | 受理面 | 11-8分類 | 実装規模 | 推奨 |
|---|---|---|---|---|---|
| **1** | 救済点A: `postprocess_lemma_repair`(再導出→revert)+`rescue`記録+HR表の旗+`auto_eligible=False`。LLM案が範囲拡張した場合も決定論で直せる | **広げない** | 新しい処理方式=ユーザー判断(11-8)。部品は承認済み先例(UDR #173②)と同型 | `er105`に1関数+`er119_kp_candidates_01.py`の旗付け+`render_request_md`の旗1種 | **採用推奨** |
| 2a | guard限定詞に`no`/`each`/`every`/`all`/`both`/`another`等を追加(`accepts no responsibility`等) | 広がる(閉表網羅の是正の側面もあり、Fableが範囲内/拡大を判定) | 範囲内の可能性/拡大 | 表1行 | 判断(影響小) |
| 2a' | 過去形専用表の補完(`rang`等) | 広がる | 同上 | 表数行 | 判断(影響小) |
| 2b | guardに副詞追加(`studied separately→study separately`) | 広がる(`er105:575`の設計意図=V+名詞等は基本形化しない、との関係を整理要) | 拡大(ユーザー承認) | guard関数1行+副詞判定(語尾`ly`等) | 判断 |
| 2c | 6語以上のAI短縮提案(新Prompt/新1 call) | 広がる(新Prompt=Opus条件A) | 拡大 | 中 | **保留**(発生率低・意味反転リスク) |
| 2d | スロット一般化(`wave a flag`→`do`) | Rule7原則の変更 | 拡大 | - | **非推奨**(本文に無い語を生成。承認済み一般化の閉集合の外) |
| 2e | lexical `have`を有限助動詞から区別(`have a say`・`had our eye on`) | 広がる | 拡大 | 検査関数の精緻化 | 判断(HR導入後14中2件=X1・Y1) |

段階1だけで、HR導入後のGate除外の36%(4/11)、HR導入前の一意句の41%を残せる。段階2は個別に効果が小さい(各1〜2件)ため、**ユーザーが「原形で見たい」を重視するなら2b、`have`系を重視するなら2eを選ぶ**、という選び方を推奨する。

## 6. 検証計画(実装する場合)

DefaultOffIsolation型testは段階1が「受理面を広げない」ことの確認に使う: (1)既存の除外全件(`inventory_01.json`)に対し、修正後keyが既存validatorで通ること (2)rescue OFF相当の入力で出力がバイト同一 (3)A/B/Cが無影響 (4)NG/累積除外/重複/overflowとの結合test。runtime evidenceは既存記事の保存済みparsed応答を使うofflineで可能(新規有料run不要)。実装前にOpus条件A(新しい処理フロー)を実施。

## 7. AI島 run_ai_01 のHR候補へ救済分を追加する場合(今回は実施しない)

HR状態はa2/b1bともPENDING_REVIEW・round 1・選択なし。救済を加えるとa2の`candidates_sha256`(`b030652528b0…`)が変わり、`kp_human_review.json`・`kp_human_review_request.md`の再発行が必要。既存CLI(`status/show/select/reselect/ng/…`、`er119_kp_human_review_cli_01.py:64-121`)に再発行コマンドは無く、`reselect`は選び直し(round+1・NG付き)用。したがって追加するなら(1)段階1の採否→(2)実装→(3)再発行手順の新設(sha再固定・`--accept-ai`のsha一致・round扱いの確認)が必要で、**現時点では候補は未確定のまま保全**している。a2に追加できる救済は`studied separately`(表層形)の1件のみ(b1bは除外0)で、gloss再整合1 callが必要(約0.5〜0.6円)。

## 8. 残るOpen Item

| # | 内容 | 分類 |
|---|---|---|
| OI-1 | 救済方式(段階1)の採否 | ユーザー判断要(新方式) |
| OI-2 | guardの記録漏れ(CURRENT_SPEC.md:1997に次トークン条件・閉表を追記) | 修正へ進む(範囲内・文書是正。次委任案: SSOT追記のみ) |
| OI-3 | guard限定詞の網羅(2a)・過去形専用表(2a') | Fable判定(範囲内是正/拡大) |
| OI-4 | 2b/2c/2e各項目の採否 | ユーザー判断要 |
| OI-5 | AI島a2への救済追加の要否と再発行手順 | ユーザー判断要+実装確認 |
| OI-6 | lexical `have`の扱い(現行は語形リストでhave/has/had/is/was等を一律拒否) | ユーザー判断要(2eに含む) |
