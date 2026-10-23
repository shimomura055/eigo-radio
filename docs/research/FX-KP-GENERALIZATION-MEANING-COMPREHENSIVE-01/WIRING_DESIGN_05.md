# WIRING_DESIGN_05: ②possessor_roles + A-1 の統合Production配線設計(Opus条件C[OPUS_REVIEW_06.md]の必須修正WC-01〜07・推奨WC-08〜12・情報WC-13〜15を全て反映)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_18 / 2026-10-23 / 設計のみ(Production .py・template・test・er112コード変更0、API 0)
前版: `WIRING_DESIGN_01.md`(A-1)・`WIRING_DESIGN_03.md`(Std gloss G2/G3+A-1)・`WIRING_DESIGN_04.md`(②/①)。**本書は②+A-1の単一変更表であり、WIRING_DESIGN_04の②-1〜②-5を置き換える**(①は今回提案から外す。WC-15)。
承認状態: A-1=`APPROVED_FOR_PRODUCTION`(UDR #169、配線は未実施)。**②=未承認**(VALIDATED候補。採否は人間ユーザー)。11-7の限定例外は既存template/validator/schemaの直接編集を伴うため**適用しない**=ユーザー採否の後にのみ実装する。flagは作らない。
根拠データ: `TRIAL_RESULT_04.md` §4・§8、`TRIAL_04/POSS_RESCORE_01.md`(本委任の再採点)。rep2(再現性)は委任_17が別途実施中で、本書は結果を含まない(§7の事前宣言で判定する)。

## 0. 要点
1. 骨格は変えない: role先行判定(`possessor_roles`をkey_phraseより先に生成)・追加call 0・fulltext専用schema・X/Z共有moduleの単一経路・既存記事は自動再生成しない。Opusも同意(総合判定「必須修正を反映すれば配線可、作り直し不要」)。
2. 修正の中心は3点: (i)許可表を共有のまま広げない=**role条件付き受理**(A/B/C凍結経路を変えない、WC-01) (ii)後処理は**`postprocess=None`引数のhook**でfulltextのみ・記録をparsed itemとmergeに通す(WC-03) (iii)修復は**revertのみ・表外置換先は触らない**、窓特定はer105に1本化しA-1と統合(WC-04/08)。
3. 結果の表現を正確化(WC-06): 「誤り9→0」ではなく**意味関係の誤り7→0、加えて辞書的に許容できる一般化2件+擬人化2件が無変更(its)へ後退**(`POSS_RESCORE_01.md`で全42件再採点、Opus所見と一致)。
4. 同梱順: A-1 `_EDITS` → `_POSS_EDITS`(同一templateに連結、anchorは各1回だけ存在することをdrift guardで確認)。②は別commitにし`git revert` 1手順で戻せる(WC-11)。
5. 費用: canonicalization +0.015円/回=**+0.03円/記事**(出力トークン増のみ、X/Z差なし)。A-1は+0.05円/記事(別計上)。追加callは0。

## 1. 統合変更表(単一。A-1→②の順で適用)
凡例: 場所の行番号は現行HEADで確認済み(2026-10-23)。「W-0n」はA-1に対するOpus条件C必須修正だが、**W-01/03/04の本文はrepo内に無く未確認**(`WIRING_DESIGN_03.md` §1 A-1行と同じ)。W-02のみ、委任_18のWC-04が「`reference_pair_ok`はer105」と引用している。Fableは配線委任文でW-01〜04の本文を転記すること(本書は未転記分を反映済みとは言わない)。

### A. A-1(`WIRING_DESIGN_01.md` §1をそのまま採用し、下記を統合)
| # | 場所 | 変更 | 本書での統合・修正 |
|---|---|---|---|
| T1〜T7 | fulltext template :7,:11,:12直後,:14,:20,:32,:39,:41 | `WIRING_DESIGN_01.md` §1のとおり(規則5新設、T2で規則3の「him/her/me/us…そのまま残してください」を差替え) | **T2は規則3の同じ文を編集する**ため、②のP-T2と**1つの編集に統合**する(旧文を2段階で書換えない) |
| K1 | `er003_key_words_canonicalization.py`:113-136 | fulltext enumのみに`generalize_reference_word`追加(`NORMALIZATION_REASONS`不変) | 変更なし |
| K2/K5(W-02で統合) | 窓判定の新関数 | `WIRING_DESIGN_01.md`ではK2「kcへ新関数`reference_pair_ok`」+K5「er105の窓判定へ`or`」と分かれていた | **er105に一本化**: `er105_kp_fulltext_selector_01.py`に(a)`reference_pair_ok(kt,dt,idx,key_tokens,window)`(this/that→a/an、him/me/us→someone/somebody、her→someone/somebodyは直後語が`_OBJ_HER_FOLLOW`のとき)と(b)開始indexを返す`find_inflection_window(key,display,role_ok_poss=frozenset())`を新設。`is_valid_inflection_normalization`は`find_inflection_window(...) is not None`と等価化(従来の真偽は不変)。validator(kc経由)と②の後処理は**同じ関数**を使う(窓特定の二重実装を作らない)。kcに`reference_pair_ok`は作らない。a/an判定は既存のer108 CMU資産を再利用。er105は既にkcを遅延import済み(:675)かつscaffold・kc以外から参照されないため、`er105_kp_fulltext_selector_01_test_01.py:294`の`ALLOWED`は変更不要(②の後処理もer105内に置く。新moduleを作るとALLOWED更新が必要になるため作らない) |
| K3 | kc:502 `_is_valid_fulltext_normalization` | reasonゲートに`generalize_reference_word`追加 | 変更なし。②のP-A1で`role_ok_poss`引数を同じ関数へ追加 |
| K4 | kc:650 | enum所属検査は自動追随 | 変更なし |
| G1 | `er003_key_words_gloss_alignment.py`:236-243 | `person_generalization_pairs`にhim/her/me/us→someone系を追加 | **②追加(G1')**: `person_role_repair`が記録された(role=other_personで`my/our→someone's`を受理した)itemでは、`my/our→someone's/somebody's`のペアも返す(表は拡張しないため、gloss側が「私の」残りを人称不一致として検出できるようにする)。実測対象(§11: person gate再整合件数) |

### B. ②possessor_roles(WIRING_DESIGN_04の②-1〜②-5を置換)
| # | 場所 | 変更 | Opus対応 |
|---|---|---|---|
| P-S1 | kc `_fulltext_item_properties()`(:134)/`CANONICALIZATION_JSON_SCHEMA_FULLTEXT` | `rank`直後に`possessor_roles`(array of {token:string, role:enum[self,other_person,non_person,none]}、required、additionalProperties false)。properties順=生成順なので`key_phrase`より前。**共有`_ITEM_SCHEMA_PROPERTIES`・`CANONICALIZATION_JSON_SCHEMA`は不変**(fulltext専用) | OF-KPFT-P-02(1)の方針維持 |
| P-T1 | fulltext template規則3(:11) | `ROLE_BLOCK`(role判定の問い2つ・self→one's/other_person→someone's/non_person・none→置換しない・置換しないことは常に許可・再帰代名詞はoneself) | DESIGN_06 §2-4 |
| P-T2(**WC-02**) | 同:11「変換すべきかどうか迷う場合は、reasoningでその判断根拠を説明した上で、より自然だと判断する側を選んでください。」 | **旧文を同じ編集で置換**: 「迷う場合は、reasoningで根拠を説明した上で、置換せずdisplay_phraseの語のまま残してください(所有格はこの後のrole判定の規則に従います)。」。`ROLE_BLOCK`の「迷う場合は置換しない」と自己矛盾しない。A-1のT2と同じ文のため1編集に統合。drift guard対象に旧文を追加(oldが各1回だけ存在することを両方で確認) | WC-02 / 原則8 |
| P-T3 | 規則3例示・規則4例示 | 規則3: 旧(`catch their attention`→`catch someone's attention`等、すべてsomeone's)→新(self=`lost his temper`→`lose one's temper`/other_person=`praised their effort`→`praise someone's effort`/non_person=`challenged its conclusions`→`challenge its conclusions`)。規則4: `pumps its fist`→`pump its fist`→`lost his temper`→`lose his temper`(併用時はroleに従い`lose one's temper`) | DESIGN_06 §2-4 |
| P-T4 | `qa_person_reference_generalized`(:39) | 「possessor_rolesに従って一般化しなかった場合[non_person・none、または置換しない選択]もPASS」を追記 | **QAのblocking意味の変更=ユーザー判断(§10 b)** |
| P-K1(**WC-03**) | kc `run_canonicalization_gate`(:693-) | 引数`postprocess: Optional[Callable]=None`を追加。parse成功直後・`validate_canonicalization_response`の前に`if postprocess: parsed = postprocess(parsed, original_items)`。**None(既定)では従来と完全に同じ**。attemptsの`raw_text`は従来どおり生応答のまま保持 | WC-03 |
| P-S2 | `er003_v1_n3_01_scaffold_generate.py`:499 | `run_canonicalization_gate(make_factory, original_items, sleep_fn=..., postprocess=(er105.postprocess_possessor_roles if is_fulltext else None))`。**A/B/Cの約10呼出点(例`er003_v1_a2_kp_select_generate.py:131`、`er003_v1_b1_scaffold_01_generate.py:297`)は無変更=hookを渡さない** | WC-03 |
| P-R1(**WC-03/04/05/08**) | er105(新)`postprocess_possessor_roles(parsed, original_items)` | 各itemについて: (1)`possessor_roles`検証(個数=displayの所有格数、tokenが出現順に一致、roleがenum内)→不成立は`status=UNVERIFIED_ROLES`でkey無変更 (2)`find_inflection_window(key, display, role_ok_poss)`で窓特定(validatorと共用) (3)窓内の所有格slotについて、keyが一般形(one's/someone's/somebody's)で、role(self→one's、other_person→someone's/somebody's)に**合致しない**場合のみ**revert(displayの語へ戻す)**。role=non_person/noneの一般形も同様にrevert。**置換先の追加(role modeでone's→someone's等への書換え)はしない**(WC-08) (4)revert後keyがvalidatorを通ることを確認できない場合はrevertを中止し`REVERT_SKIPPED`でkey無変更(WC-04: INVALID→retry消費を新たに作らない。revertはdisplayの語へ戻すのでWRONGを作らない) (5)recompute(P-R2) (6)parsed itemに`possessor_roles`と`person_role_repair`={status, roles_ok, roles_reason, repairs[{ordinal, display_token, role, before, after, rule}], key_before, role_ok_poss}を**残す**(validatorは余分項目を無視。旧DEVの`it.pop("possessor_roles")`は行わない) | WC-03/04/05/08 |
| P-R2(**WC-05**) | 同 再計算(旧DEV `recompute_fields`) | (i)`person_sub`の「不定人称語」集合を`_GENERIC_TOKENS`相当(one's/someone's/somebody's/one/someone/somebody/oneself)へ拡張(旧DEVはone's/someone's/somebody's/oneselfのみ=A-1で`him→someone`になった句で所有格をrevertすると`lemma_normalization`へ付け替わり、`gloss_alignment.is_person_generalized`[:224-233]のreason判定が外れる)。(ii)LLMの`normalization_reason`が新key側(`generalize_person_dependent_reference`/`generalize_reference_word`)で検査を通る場合は**変更しない**(A-1の`generalize_reference_word`記録を消さない)。(iii)`qa_person_reference_generalized`の**無条件PASS上書きはしない**: 全所有格slotがroleと整合する(revert後を含む)場合のみPASS、それ以外は元値を維持 | WC-05 |
| P-A1(**WC-01**) | 受理条件 | §2のとおり**role条件付き受理**を採用(共有表`_PERSON_DEPENDENT_TO_GENERIC`は不変) | WC-01 |
| P-M1(**WC-03**) | kc `merge_canonicalization_result`(:773-) | 現行の引き継ぎ(:837-)は**選定側`original`**のフィールドを読むだけで、**canon側(LLM出力)の未知項目は引き継がない**。新規に`FULLTEXT_CANON_PASSTHROUGH_FIELDS=("possessor_roles","person_role_repair")`を定義し、`is_fulltext_item(original)`のときだけcanon側から`merged_item`へ複写(A/B/Cの出力はバイト同一) | WC-03(「既存passthroughで引き継ぐ」は不正確=canon側の新passthrough節が必要) |
| P-M2 | scaffold:505 `_canon_meta` | `attempts_detail`のうち`raw_text`だけ除く現行処理は維持(`parsed`にroles/repairが入るので追加変更不要) | — |
| P-E1 | 件数記録 | run summary/outer_retry_logに`UNVERIFIED_ROLES`/`NO_WINDOW`/`REVERT_SKIPPED`/`REPAIRED`件数を出す(reuse判定・signatureには使わない) | WC-13/14 |

## 2. WC-01: 許可表拡張のA/B/C漏れの回避(採用案=(b) role条件付き受理、Fable推奨)
問題: 共有表`_PERSON_DEPENDENT_TO_GENERIC`(kc:431-449)は`_is_valid_person_generalization`(:452-469)経由で`validate_canonicalization_item`(:570-573)と`_qa_field_effective_verdict`(:512-513)から**fulltext非依存で**使われる。`my`/`our`→someone'sを表に足すとA/B/C凍結経路の受理範囲が広がる(`er064_kp_idiom_trial_01_test_01.py:55-56`は現状その経路で拒否を`assertFalse`固定している)。
- **採用(b)**: 表は不変。`find_inflection_window`/`is_valid_inflection_normalization`/`_is_valid_fulltext_normalization`/`_qa_field_effective_verdict`/`validate_canonicalization_item`に**キーワード専用引数`role_ok_poss: frozenset=frozenset()`**を追加(既定空=現行とバイト同一)。postprocessが`person_role_repair.role_ok_poss`に「roles_ok=trueかつrole=other_personのdisplay内token index(my/our)」を記録し、fulltext経路のvalidatorだけがそれを渡す。受理されるのは「display token∈{my, our}、key token∈{someone's, somebody's}、そのslotのroleがother_person(検証済み)」の場合のみ。roles未検証・role≠other_personなら従来どおり拒否(INVALID→外側retry)。**ER-011-NO18の承認済み表そのものは無変更**だが、fulltext経路の新しい受理条件なのでユーザー判断(§10 d)。
- (a)併記: 共有表を触らず、fulltext専用のer105 `_token_pair_ok`側に`my/our→someone's`を全itemで無条件追加する案。実装は小さいが、rolesが無効(`UNVERIFIED_ROLES`)でも`lose my job→lose someone's job`のような誤変換を受理する。Fableは(b)を推奨。
- いずれの案でも`er064:55-56`は**維持**(A/B/C不変の固定test)。fulltext受理は別testを追加(§8)。**反転しない**。
- 影響: A/B/Cの`validate_canonicalization_item`呼出は`role_ok_poss`を渡さない=出力不変(A/B/C経路でhook不呼出も機械的に確認、§8)。

## 3. WC-04: 窓特定・修復先の一元化
- 窓特定はer105の`find_inflection_window`に一本化(A-1の`reference_pair_ok`・②の`role_ok_poss`・従来の`_token_pair_ok`を同じ走査で判定)。DEVの独自`_pair_ok`+`er112_kp_gm_trial_01._ref_pair_ok`はProductionへ移植しない(Production→er112 importは既存test `test_no_production_module_imports_er112`が禁止)。
- 修復はrevertのみ(§5)。revert先はdisplayの語=必ず表内。revert後keyがvalidatorを通らない場合は`REVERT_SKIPPED`で元keyを維持し、INVALID→retry消費を新たに作らない。
- `its→someone's`は表に無い(kc:436)。旧DEVのrole modeがother_personへ一律someone'sに書換える場合、itsだとINVALIDになる問題は、role mode不採用により生じない。

## 4. WC-06: 「物が動作主のits」の扱い(ユーザー判断あり)
再採点(`POSS_RESCORE_01.md`、42件、Fable基準=辞書慣例)の内訳:

| 区分 | C0A(現行+A-1) → C1A(本案) |
|---|---|
| 意味関係の誤り | **7 → 0**(3件は正しいone's/someone'sへ、4件はits/their無変更へ) |
| 辞書的に許容できる一般化の後退(`keeps its promise`, `finding its way back`) | one's=許容 → its(無変更)。意味は壊れない |
| 擬人化の後退(`wallet pumps its fist` 2unit) | one's=許容 → its(無変更)。意味は壊れない |
| 不変 | 31 |

旧表現「誤り9→0」は、うち2件(`keep one's promise`, `find one's way back`)が辞書上one'sが見出し形の定型句であるため不正確。**採用提案では「意味関係の誤り7→0、許容できる一般化の後退4件[無変更形]」と書く**。後退4件はいずれも無変更(its)形でWRONG化はない。境界注記: `compete through its presence`/`questioned its methods`は自己参照読みも可能で、その読みなら許容側に回り「誤り5→0・後退6」となる(方向は不変)。
- **選択肢A(現設計・Fable推奨)**: DESIGN_06 §2-2のとおり、動作主自身が物でもnon_personとして一般形をrevert(itsを強制で残す)。安全で、一般化は減る。先行OF-D5-09は「現状維持[its]を許容」であって強制ではなかった点、およびtemplate規則4の例(`pumps its fist`→`pump one's fist`)・test(`er003_test_kp_fulltext_wiring_01.py:152,255`、`er064:40-42`)の考え方との差は**§10 aとしてユーザーに明示**する。
- **選択肢B(将来候補)**: non_personを`non_person_agent`(物・擬人化が動作主自身)と`non_person_other`(動作主ではない物・組織)に分ける。agentはone's・無変更とも許可、someone'sはrevert(追加call 0、enum追加+小規模Trial要、`run its course`の過剰変換確認)。実装・Trialは今回行わない。**OPEN候補として記録**(`OPEN_ITEMS.md` OPEN-481)。
- Opus推奨=Aで採用可。Bは実データが溜まってから再評価。

## 5. WC-08: 食い違い時の修復はrevertのみ
role mode(roleに合わせてone's↔someone'sを書換える)は不採用: Trialで発火0/42で未検証、revertはWRONGを作らず「迷えば置換しない」(ROLE_BLOCK)と一致し、コード最小。role modeは実データで食い違いが溜まってから再評価(OPEN-481に併記)。

## 6. WC-09: runtime evidence・PRODUCTION_WIRED定義
採取対象(X/Z各々、正式入口からのKP段実行): 所有格を含むitemが1件以上あり、記録に`possessor_roles`と`person_role_repair.roles_ok=true`、keyとroleの整合、request schemaに`possessor_roles`、新template sha、`UNVERIFIED_ROLES`件数、canon_status、外側retry回数、gloss person gate結果。
- 候補X: `uk_train_speaker_playback`の`reach for your wallet`(self、`--scaffold-only kp`、**別out-dir**)。
- 候補Z: Melosの`gave my word`(self、`--regenerate-stage kp_<lv>`必須[er026:1542の本文sha鍵])。Z完成段の再実行は`--stages provision_shell,gate,assemble,pages,page_verify`を1起動で指定(OPEN-480)。
- 修復(revert)経路は単体testで担保し、evidence対象外と明記(自然発火しないため。mockをruntime evidenceと呼ばない)。
- A-1のevidence(`WIRING_DESIGN_01.md` §7)と**同一run**で採取可。費用≤10円(X≤5+Z≤5)。
- `PRODUCTION_WIRED`の定義: X/Z両方で上記evidenceが揃い、全回帰(基準=OPEN-456 F6、failed 0/errors 0)がPASSした時点。片方だけでは`PRODUCTION_WIRED`と呼ばない。

## 7. WC-10: rep2で採用提案に必要な最小条件(**事前宣言**。結果を見る前に固定)
1. 所有格42件でWRONG合計≤1、実データ29件では0。
2. 所有格なしitemのkey同一率(C0A対C1A)がC0A反復間ノイズ以内(rep1のC0A対C1A差3/102に対し、C0A rep1対rep2のノイズ幅で比較)。
3. `CANONICALIZATION_INVALID`+`REVIEW_REQUIRED`の件数がC0A以下。
4. `UNVERIFIED_ROLES`≤2/42。
5. 後退は無変更(its)形に限り、WRONG化0。

満たせば2回分(rep1+rep2)で採用提案に足る。満たさない条件があれば提案せず原因を再検討する。WC-06の内訳再採点はrep1分を`POSS_RESCORE_01.md`で完了(API 0)。

## 8. WC-07: test計画
| 区分 | 内容 |
|---|---|
| 修正(必須) | `er003_test_kp_fulltext_wiring_01.py:216-225` `test_fulltext_schema_adds_only_lemma_normalization`: 配線後は**必ずFAIL**(enum以外が共有schemaと同一でなくなる)→**差分許可リスト方式**へ変更: 許可差分=(1)`normalization_reason`のenum(`lemma_normalization`+`generalize_reference_word`)(2)itemsの`possessor_roles`(rank直後・required・要素{token,role}・role enum 4値)。許可差分以外は共有schemaと同一 |
| 不変固定 | :210-214 共有schema sha(`1daac908…`)・`NORMALIZATION_REASONS` sha(`fd341920…`)、:292 A/B/C template blob sha1(`6e19a905…`)。`er064:55-56`(`pull my leg→pull someone's leg`はINVALID)は維持=A/B/Cの受理範囲が広がっていない固定test |
| 実測後に更新 | :287-289のtemplate内容assert(`目的格`・`そのまま残してください`)は、A-1のT2と今回(P-T2)の編集後に実測して確定(両語が残るか確認) |
| 書換え(A-1) | `test_object_pronoun_kept_accepted_but_generalized_rejected`(:261-267付近)→受理2ケース(`WIRING_DESIGN_01.md` §5) |
| 新規(②) | role要素数/token/enum照合(不一致→`UNVERIFIED_ROLES`かつkey無変更)/再帰self/二重所有(`put herself in their shoes`)/物動作主定型句(`run its course`維持)/revert(role=non_personで一般形→displayの語)/revert後にvalidatorを通らない場合の`REVERT_SKIPPED`/表外置換先へ書換えない(role mode不在)/A-1同居(`gave him his word`→`give someone one's word`、`told her the truth`[role=none]でA-1のsomeoneをrevertしない)/reason保持(`generalize_reference_word`を消さない)/A/B/C経路で`postprocess`が呼ばれない・`role_ok_poss`が渡らない/mergeでroles・person_role_repairが引き継がれる(fulltextのみ、A/B/Cはバイト同一)/roles欠落・破損でkey無変更/`my→someone's`受理はrole=other_person(検証済み)のみ・それ以外は拒否/QA実効値(無条件PASS上書きをしない) |
| 全回帰 | `run_project_regression.py`、基準=OPEN-456 F6(failed 0/errors 0) |
| 環境 | 本環境は`wordfreq`未導入のため`er064`/`er003_test_kp_fulltext_wiring_01`/`er064_kp_opt_01_upstream_test_01`はcollect不可(`DESIGN_06.md` §6)=配線委任で導入環境にて実行して確定 |

## 9. WC-11: rollback
11-7例外が適用されないためflagによるOFFは無い。**②のtemplate・schema・後処理(hook呼出含む)・受理条件・testを1 commitにまとめ、`git revert <hash>` 1手順で戻せる**ようにする(A-1とは別commit、同梱順A-1→②)。後処理はrolesが無ければ何もしない(`UNVERIFIED_ROLES`でkey無変更)ため、templateだけを戻しても安全。既存記事はKP段を再実行しない限り変わらないので、戻した後の後始末は無い。

## 10. WC-12: ユーザー判断表(②のみ。①関連の#1/#4/#5は除外)
| # | 事項 | 区分(27-3) | 備考/推奨 |
|---|---|---|---|
| a | 物が動作主のitsの扱い(WC-06): A=itsを強制で残す / B=`non_person_agent`を分ける(将来) | D | Fable推奨A。後退4件の内訳を正確に提示済み。Bが必要ならOPEN-481 |
| b | `qa_person_reference_generalized`定義の変更(P-T4: 一般化しなかった場合もPASS=QAのblocking意味の変更) | D | 承認済みQA定義の変更 |
| c | LLM出力を書き換える決定論後処理という新方式(revertのみ・API 0・roles検証不能なら無変更) | D | 書換えはdisplayの語へ戻すだけ |
| d | 受理条件: (b)role条件付き受理(推奨)か(a)fulltext専用の無条件追加か。共有表を拡張する案はA/B/Cに漏れるため不採用(拡張する場合はER-011-NO18の表変更+A/B/Cの受理範囲拡大としてユーザー判断) | D | (b)ならER-011-NO18の表は無変更 |
| e | 承認済みPromptの変更(規則3の追記・例示均等化・迷う場合の1文置換[P-T2]・schema欄追加) | D | **P-T2はTrial未検証の1文**。配線前に36 unit×1 repのDEV確認(約10〜11円、実測0.28〜0.29円/call)をFable判断で推奨(7-7内) |
| f | 既存完成記事を自動再生成しない方針の確認 | B(既定方針) | KP段再実行時のみ変わる。再実行は記事ごとの判断 |

採用の入口はユーザー判断(UDR)。実装は採否の後に1委任。

## 11. WC-13/14: 監視項目・費用
- 件数を記録・報告: `UNVERIFIED_ROLES`、`NO_WINDOW`(規則2[source_spanから復元]でdisplay外の所有格を取り込んだkeyはroles対象外=現行どおり、`yours/theirs`もslot対象外)、`REVERT_SKIPPED`、`REPAIRED`(revert発火)、person gate再整合件数(`my→someone's`化で「私の」が残るgloss再整合が増えうる)、外側retry試行数(baseline比)、INVALID/REVIEW_REQUIRED件数。
- 費用: canonicalization +0.015円/回(0.279→0.294円、+5%)=**+0.03円/記事**。X/Z差なし。追加call 0。
- Store reuse: KP段を再実行した記事に限りused_formが変わりうる→既存仕組み(`gloss_signature`/`explanation_phrase`)でAdv/TTSが再生成。自動再生成はしない。

## 12. WC-15: ①との関係
①(Std字義訳の独立検査)は今回の提案から外す。将来同梱する場合は**②の確定key(後処理後)を入力にする**ことで干渉しない(順序: ②→①)。

## 13. 撤去・残置の確認(原則8)
- 撤去(同時編集): template規則3の旧文「迷う場合は…より自然だと判断する側を選んでください」(P-T2)、規則3の旧例示・規則4の旧例示(P-T3)、A-1側の旧文(`WIRING_DESIGN_01.md` §5)。配線後Grepで旧文0件を確認。
- 変更しない: 共有schema・`NORMALIZATION_REASONS`・`_PERSON_DEPENDENT_TO_GENERIC`・A/B/C template(sha1 `6e19a905…`)・`er064:55-56`。
- 新規ファイルは作らない(後処理はer105)。`ALLOWED`(er105 isolation test)変更不要。

## 14. 費用・時間・クリティカルパス
実装+test: Sonnet 1委任(A-1と同一委任、②は別commit)。API 0(evidenceは≤10円)。待機はユーザー採否のみ。rep2(委任_17)は並行実施中。依存: ユーザー採否→配線委任→test/全回帰→evidence(X/Z並列可)→SSOT。

## 15. 限界・未確認
- ②のgold自体は実行層の目視(Opus WC-06指摘)。`POSS_RESCORE_01.md`も同一gold+Fable基準の適用で、独立盲検ではない。
- P-T2(迷う場合の1文置換)はTrial未検証。rep2は旧template(Trial版)で実施中。
- W-01/03/04の本文は未確認(§1冒頭)。
- `wordfreq`未導入のため一部testは本環境で未実行。
- (b)のplumbing(`role_ok_poss`引数の貫通)は設計のみ。実装時にA/B/C出力のバイト同一をtestで確認する。
