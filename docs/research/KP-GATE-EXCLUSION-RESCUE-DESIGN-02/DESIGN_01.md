# DESIGN_01: Key Phrase Gate除外「救済」方式の再設計(DEV実証済み)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01 / 2026-10-26 / 到達上限Status=`COMPLETED_PENDING_FABLE_ACCEPTANCE`→Fable受入後`USER_DECISION_REQUIRED`(区分2のみ提示)。
Production(`er105`/`er003_*`/`er119_*`/scaffold)は未変更・未配線。DEV=`er123_kp_rescue_dev_01.py`+test 52件PASS。前回(KP-GATE-EXCLUSION-RESCUE-DESIGN-01/DESIGN_02)の「11件中4件救済可、残り7件不可」は固定せず、11件を再調査して作り直した。

## 0. 前回Opus指摘(M1〜M6/R1〜R4)の反映状況

| ID | 指摘 | 今回の反映 | 証跡 |
|---|---|---|---|
| M1 | 再導出はLLM提案語の部分集合に限る | `rederive_m1`: 各位置を{display語, LLM語}から選ぶだけ。LLM keyがdisplayより長い範囲拡張は、先頭`len(display)`語を窓とし窓外tailを捨てる。副詞前の原形化は**LLM提案語+CMU実在+前方活用生成一致**の三重検査。`hoped→hop`は前方生成不一致で拒否 | test `test_forward_inflection_rejects_wrong_lemma`/`test_adverb_tier_rejects_wrong_lemma_even_if_cmu_registered`/`test_rederive_m1_uses_only_display_or_llm_tokens` |
| M2 | 救済はHR経路限定・既定OFF | 設計に維持(§3 H1/H2、明示引数・既定OFF)。DEVはHR経路に配線しない。**Production実装時の必須test**に固定(§6) | - |
| M3 | gloss再整合を強制 | `make_rescue_record`が`gloss.realign_required`を出力(最終形がLLM提案keyと異なる救済のみ)。再整合不可は`gloss_hr_pending`。`align_glosses(only_ranks=)`はProduction側の新規引数(§3) | `rescue_eval_07.json` `rescue_record` |
| M4 | QA上書き禁止 | `gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`・`auto_eligible=False`・LLMのqa_*欄は触らない | test `test_inventory_invariants` |
| M5 | 外側retry条件は現行維持 | 設計に維持(救済句は`gate_dropped`相当として数え、累積除外リストには入れない)。Production実装時のtestで「救済あり/なしでretry発動回数同一」を固定(§6) | - |
| M6 | 救済内validatorは最終Gateと同一引数 | `gate_check`は`allow_inflection_normalization=True`・`original_span`・`role_ok_poss`を最終Gateと同じに渡す | test `test_gate_check_calls_validator_with_final_gate_arguments` |
| R1 | トリガーを構造違反全般+cmu_post_canonへ | `rescue_structural_revert`(displayへ戻して既存validator+CMUを再検査) | test `test_structural_revert_for_cmu_post_canon_style_violation`(実イベントは未観測=synthetic) |
| R2 | 2c採用条件(否定/程度語・元句併記) | A1/A2に決定論の演算子作用域禁止表を実装・HR表に元句併記 | test `test_subspans_never_drop_scope_operator_and_keep_operand`ほか |
| R3 | 外側retry置換・call1 retryで消えた句を記録 | DEV範囲外(観測のみの項目)。Production実装リストに残置(§3) | - |
| R4 | test 3件 | (1)`hoped→hop`はDEVで実装。(2)(3)はProduction実装時 | §6 |

## 1. 結論(先に)

1. 除外11件のうち**4件(36%)は承認済み規則の意図に反する過剰除外・実装不整合**で、規則是正(区分1)だけで通常フローを通る: `studied separately`(guardが副詞後続を拒否)・`had our eye on`/`have a say`(語彙動詞haveを助動詞と誤判定)・`rang through`(過去形専用表の網羅漏れ)。
2. 残り7件は「規則違反だから不可」ではなかった。**6件は既存Gateを同一引数で通る救済形が実際に作れた**(`too soon`・`rise above`・`hold out`・`can’t be helped`×2・`catches their interest`→`catch their interest`)。これらは受理面の拡大または新しい後処理工程を要するので区分2(ユーザー判断)。1件(`redelivery fee`)はCMU規則の趣旨(未登録語を推測で合格させない)に反するため**救済しない(区分2・非推奨)**。
3. 区分3(救済しない)は、Human NG 3件と、ユーザー例の`too soon to do`(本文に無い語・独立評価でreject)の推奨のみ。**11件内で品質・安全上救済できないものは0**。
4. 救済方式は2種類に整理できる: (1)**Gate自体の是正**(区分1。救済フロー不要)、(2)**救済フロー**(区分2。選定段H1と正規化段H2の後処理。HR経路限定・既定OFF・AUTO不可)。(1)はAPI 0・追加費用0、(2)は救済1件につきgloss再整合約0.53〜0.56円。
5. LLMは候補の**生成に使わない**(決定論)。DEVでは評価に使い(8回、約2.14円)、LLM評価の揺れは多数決で扱った。

## 2. 全体フロー

```
call1/call2(選定) ─▶ [選定gate: 本文連続一致・1〜5語・有限助動詞(←区分1:役割判定)・CMU・重複・NG]
                        │不合格
                        ├─▶ H1 選定段救済(区分2, HR経路・既定OFF)
                        │     A1 連続部分列短縮(語数超過)  D1 本文再アンカー(原形で返された句)  D3 主語除去+慣用句例外(完全文の法助動詞)
                        │     └▶ 救済形を選定gateへ再適用(通れば選定結果に差し替え)
                        ▼
canonicalization(LLM) ─▶ parse ─▶ postprocess_possessor_roles(既存) ─▶ validator [Rule7+原形化(←区分1:guard副詞/量化詞・過去形表)]
                        │INVALID(LLMのkeyが原因)
                        ├─▶ H2 正規化段救済(区分2, HR経路・既定OFF)
                        │     M1窓内再導出(範囲拡張のtail破棄/人称+lemma不整合)  → 通らなければ revert(表層形)
                        │     構造違反/cmu_post_canon → revertのみ(R1)
                        │     └▶ 同一引数でvalidator+CMUを再適用(M6)
                        ▼
gloss再整合(救済は強制, M3) ─▶ Redundancy QA ─▶ HR候補(rescue記録+旗+auto_eligible=False, M4)
```

## 3. 実装設計(Production配線時の差分案。**今回は適用しない**)

### 3-1 区分1(規則是正。通常フローに乗るのでflagなし。A/B/Cはバイト同一)
| # | 変更 | 場所(現行) | 内容 |
|---|---|---|---|
| 1 | 有限助動詞を語形→役割判定へ | `er105:213 _legacy_form_reasons`(fulltext専用)・`er003_key_words_canonicalization.py:627`(共有) | `_contains_finite_auxiliary`の`have/has/had`のみ役割判定(`have_role`)。**共有側は`allow_inflection_normalization=True`のときだけ**新判定(A/B/C=27-7はバイト同一)。法助動詞・be系は不変 |
| 2 | guardに量化詞限定詞 | `er105:614 _GUARD_DET` | `no/each/every/all/both/another/either/neither/several/few/many/much/enough`を追加(閉表の網羅漏れ) |
| 3 | guardに副詞後続(三重検査) | `er105:662 _guard_ok`/`:670 _token_pair_ok` | manner副詞(-ly、-ly形容詞表除く+`again/alone/hard/well/fast/often/always/never/still`)が句末/直後が前置詞・不変化詞・限定詞・接続詞のとき。**この追加経路にだけ**前方活用生成一致(強勢つきCVC重子音)を課す |
| 4 | 過去形/分詞の閉表補完 | `er105:577 _PAST_ONLY_IRREGULAR`・`:584 _AMBIGUOUS_IRREGULAR` | 過去形専用51語・曖昧過去形20語・分詞35語(`irregular_gap_01.json`)。`bound`は除外(OPEN-476=DEFERRED) |

追加test(区分1): 実選定句315種で既受理ペアの取りこぼし0、新規受理は`rang through`・`studied separately`・`thrown into it`のみ(`selection_probe_01.json`)。敵対的な組(`heated debate`等)は拒否のまま。
**副次の不具合候補(同時是正しない)**: 曲線`’`とASCII`'`で有限助動詞判定が食い違う(`can’t`は拒否、`can't`は通過)。是正はGateを厳しくする方向のため、影響測定の後に別委任(§8)。

### 3-2 区分2(救済フロー。HR経路限定・既定OFF・単一flag読取関数)
- 新規module(例`er12x_kp_rescue_01.py`)に、DEVの`subspan_candidates`/`rederive_m1`/`reanchor`/`rescue_structural_revert`/`make_rescue_record`を移す。`er119 generate_candidates`が`select_fn`/`canon_fn`へ**明示引数**(`rescue=True`、既定False)を渡したときだけH1/H2が動く。`is_fulltext`だけでは有効にならない(M2)。flag名は実装時に決め、`OPEN_ITEMS.md`に「承認前・既定OFF」を記録、`PRODUCTION_WIRED`と呼ばない(11-7)。
- 記録: `kp_candidates.json`の候補に`rescue{applied,method,before,after,recheck,gloss}`・`flags.rescued`・`gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`・`auto_eligible=False`。`dropped[]`には救済候補化した場合も元の除外理由と`rescued_as`を残す。
- gloss: `align_glosses(only_ranks=)`(新規引数)で救済rankを強制再整合。失敗は`gloss_hr_pending`。HR表(`render_request_md`)の旗に「修正済み(元: …)」「QA未再判定」「gloss_hr_pending」を追加し、元句・本文の文を併記。
- 外側retry: 救済句は`gate_dropped`相当として数える(トリガー判定は現行維持、M5)。累積除外リスト(DECISION_LOG.md:87)には入れない。
- 辞書資産: 慣用句例外・辞書裏付けguard用に、Wiktionary見出し(`er023_output/key_phrase_db_trial_01/db/wiktionary/{idioms,phrasal_verbs,proverbs}.json`、延べ17,389件、CC BY-SA=`db_licenses.md`)をProduction側の安定パスへvendoringする(現在はtrial出力ディレクトリ)。ライセンス確認が前提。
- 観測の追加(R3): 外側retryの置換・call1選定retryで消えた句を`dropped`/inventoryへ記録(救済はしない)。

## 4. 品質リスクと歯止め

| リスク | 歯止め | 検証 |
|---|---|---|
| 誤った原形(`hoped→hop`)の採用 | LLM提案語∩display窓+CMU+前方活用生成一致(強勢つき) | test(前方生成/adverb tier)・実データ315種で誤受理0 |
| 形容詞化分詞+名詞の誤変換(`heated debate`型) | guard維持(副詞/量化詞のときだけ広げる)+形容詞化分詞除外表維持 | test 8組拒否のまま |
| `bound to→bind to`(OPEN-476) | 表補完から`bound`除外 | selection_probeで誤受理を検出→修正済み |
| 意味反転(`too soon`→`soon`) | 演算子語の作用域を壊す部分列を決定論で禁止(否定・程度語)。動詞句末で目的語欠落も禁止 | test(5句に対し性質検証) |
| 語彙haveと完了形auxの取り違え | 迷えばaux(現行どおり拒否)。倒置/副詞挟み/形容詞化分詞+目的語を検出 | test 25ケース+実本文71窓を人手レビュー |
| 完全文の例外化 | 慣用句例外は主語で始まらない核だけ。完全文は主語除去の連続部分列だけ | test |
| 本文対応の喪失 | H1は元句の連続部分列/本文窓への再アンカー、H2は窓内のみ | final_check: 選定gate PASS |
| gloss・QAが古いまま | gloss再整合強制、QA未再判定表示、AUTO不可 | rescue_record |
| 評価の揺れ | LLM評価は評価のみ・多数決(2/3) | judge 8回 |
| 外部辞書依存 | 区分2として分離、ライセンス確認条件 | §5 |

## 5. 区分1/2/3一覧(委任文⑤の判断分類)

### 区分1(承認済み仕様への準拠修正。Fable判定のうえ別委任でProduction適用)
| # | 内容 | 根拠(承認文との関係) | 対象 | 副作用/リスク | 備考 |
|---|---|---|---|---|---|
| 1-1 | 有限助動詞の役割判定(語彙動詞have) | 承認の意図は「有限助動詞」の排除(`DECISION_LOG.md:7408`、ER-003-P2G)。語形リストの機械適用が過剰。P-04(3)の`has/had→have`が自己矛盾(dead path) | `had our eye on`・`have a say`・(導入前)`have a big moment` | 完了形auxの誤受理→「迷えばaux」で歯止め | **OPEN-152(`USER_DECISION_REQUIRED`/Non-blocking、2026-09-14)が既出**。同OPENは「Production QA変更に当たるためユーザー判断」と記録。本委任の判定(区分1=誤判定の是正)との整合をFableが裁定 |
| 1-2 | guardへ量化詞限定詞 | guardの文言「限定詞」の閉表網羅漏れ | `accepts no responsibility`等(導入前) | 低 | |
| 1-3 | guardへ副詞後続(三重検査) | 承認文に無い内部条件(OPEN-530)。目的(形容詞化分詞の誤変換防止)に当たらない場合の過剰除外 | `studied separately` | 誤原形→三重検査 | **境界はFable判定**(『規則文に無い内部条件の是正』だが受理面が広がる見方もある) |
| 1-4 | 過去形/分詞の閉表補完 | 承認は不規則形一般。表は例示的 | `rang through`・`struck a match` | 曖昧語は`bound`除外 | |

### 区分2(ユーザー判断を要する。検証済み修正例・メリット・リスク・代替・QCD・推奨)
| # | 案 | 検証済み修正例 | メリット | 品質リスク | 代替 | QCD影響 | 推奨 |
|---|---|---|---|---|---|---|---|
| 2-A | **救済フロー本体**(H1/H2の後処理工程、HR経路限定・既定OFF・AUTO不可) | `too soon to wave a flag→too soon`・`rose above→rise above`・`held out→hold out`・`(原形で返された)catch their interest→本文のcatches their interest` | 11件中4件(36%)・導入前25種中約半数を残せる。候補を捨てない | 狭まる/原形でない候補が出る。gloss・QA再判定が要る | 現行(除外のまま)。外側retry | gloss再整合0.53〜0.56円/件、12 level-runで約0.23円/level-run(70円の<1%)。速度影響=gloss 1 call | **採用推奨** |
| 2-B | 慣用句の法助動詞例外(辞書見出しの核のみ)+完全文は主語除去 | `it can’t be helped→can’t be helped` | 「仕方がない」等の高価値表現を残す | 外部辞書依存。例外の範囲 | 現行どおり除外 | API 0。辞書vendoring+ライセンス確認 | **条件付き採用推奨**(ライセンス確認後) |
| 2-C | 辞書裏付けguard(V+名詞の原形化) | `lost touch→lose touch`(導入前) | 原形の見出し語 | 辞書依存 | revert(表層形)で候補に残す | API 0 | **保留推奨**(revertで足りる) |
| 2-D | CMU未登録語の分解合格 | `redelivery fee`(`re`+`delivery`) | 1/12 level-run | TTS発音不良の再来。ユーザー規則(2026-10-22)の趣旨に反する | 非採用。採用するなら実TTS音声のASR一致を必須化 | TTS+ASRの追加費用 | **非推奨** |

### 区分3(救済すべきでない)
| 候補 | 理由(品質・安全根拠) |
|---|---|
| Human NG 3件 | ユーザーの明示NGを覆さない |
| `too soon to do`(A2 スロット一般化) | 本文に無い語を含み出典対応を失う。独立評価で8回中7回reject(不自然/意味changed)。検証は実施済み(検査はPASS) |
| `minaudière(s)`ほか(導入前)・`could not bear`等 | 外来語は分解不能で発音を保証できない。法助動詞/否定が意味の核で、外すと意味が変わる(LLM評価でreject) |

## 6. 実装時の必須test(Production適用時)
1. 区分1: A/B/C出力バイト同一(共有validatorの新判定は`allow_inflection_normalization=True`時のみ)。実選定句の単調性・新規受理リスト。敵対的な組の拒否維持。
2. 救済フロー: (R4-1)`hoped→hop`非採用(DEV済み)。(R4-2)HRを経ない経路(`scaffold:883-888`・`er062:1364-1373`)で救済ONでも出力バイト同一。(R4-3)救済あり/なしで外側retry発動回数が同一。(M6)最終Gateと同一引数。(M4)AUTO不可・QA未再判定。NG復活禁止。
3. DefaultOffIsolation: flag未設定でAPI呼出0・出力不変・副作用ファイル0。

## 7. 追加コスト・期待救済率
- 区分1: 追加0円(API 0)。救済フロー: 決定論部分0円、gloss再整合が救済1件につき約0.526〜0.563円(出典: AI島 a2 `raw_usage_log.jsonl`実測、前回DESIGN_02 §5)。HR導入後12 level-runで救済フロー該当5件→約2.8円/12 level-run=約0.23円/level-run=約0.47円/記事セット(2レベル)=70円目標の約0.7%。A1のLLM評価を本番で使う場合は1呼出約0.05円(DEV実測: 14件で0.145円から見積)。
- 期待救済率: HR導入後11件=区分1が4件(36%)、区分2採用推奨まで含め10件(91%)、非推奨1件(9%)。導入前一意句(現行で通る4件を除く25種)=区分1が5(20%)、区分1+2が17(68%)、区分3が8(32%)。※導入前はouter retryで置換された世代の観測で、現行Gateでの絶対発生率ではない。

## 8. OPEN更新文案・新規不具合候補(SSOT未編集。Fable受入後に転記)
- **OPEN-529更新文案**: 「KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01(2026-10-26): 除外11件を再調査し、パターン別救済方式をDEV実証(`er123_kp_rescue_dev_01.py`、52 test PASS、API 0、LLM評価約2.14円)。区分1=4件(guard副詞/語彙have/過去形表)、区分2=救済フロー本体・慣用句例外・辞書裏付けguard・CMU分解(非推奨)、区分3=Human NG・スロット一般化。Production非配線。Status=`COMPLETED_PENDING_FABLE_ACCEPTANCE`→受入後`USER_DECISION_REQUIRED`(区分2)」。
- **不具合候補(新OPEN番号は発番しない=OPEN-529に追記)**: 有限助動詞判定が曲線`’`とASCII`'`で食い違う(`can’t`拒否/`can't`通過、`isn't`/`won't`/`doesn't`も同様)。分類=**修正へ進む(範囲内・承認済みの助動詞排除との乖離)**。ただしGateを厳しくする方向のため、次委任案=「ASCII縮約を含む実選定句の件数を測る→縮約を助動詞+`not`として判定する是正案の影響測定」(API 0)。
- OPEN-152(語彙動詞have)・OPEN-530(guard文書是正)・OPEN-476(`bound to`)との関係: 区分1-1はOPEN-152の解、区分1-3はOPEN-530の対象、`bound`は表補完から除外してOPEN-476を維持。
- DECISION_LOG文案はFable受入後。

## 9. 前回DESIGN_02との差分
- 「機械的に救済可=4件(`studied separately`/`rose above`/`held out`/`rang through`のrevert中心)」→今回は**11件すべてを個別に原因分析**し、方式を再設計: 区分1(Gate是正)と区分2(救済フロー)に二分。
- 新規: 副詞前の原形化(三重検査)、語彙have役割判定、語数超過の2方式(A1部分列+LLM評価、A2一般化=区分3推奨)、再アンカー(原形で返された句)、慣用句例外(辞書見出しの核+主語除去)、cmu_post_canon/構造違反のrevert、LLM評価(多数決)の品質ゲート化。
- 訂正: 前回「`rose above`/`held out`は再導出でrevert」→ LLM提案の窓内部分(`rise above`/`hold out`)を採る形が通る(DEV実証)。「`it can’t be helped`は不可」→主語除去+辞書見出しの核で救える。「`catch their interest`は不可」→再アンカーで救える。
