# WIRING_DESIGN_07: 課題① X2p'(本文での語義を選び、表すのはkey_phraseの範囲だけ)のProduction配線設計 改訂案(OPUS_REVIEW_08 OF-KP2-04/05/06/07反映。**実装しない**)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_30 / 2026-10-24 / 設計のみ(Production .py・template・既存test変更0、API 0) / 前版=`WIRING_DESIGN_06.md`(本書が優先。変更表G-1〜G-9の番号を引き継ぐ) / 根拠=`OPUS_REVIEW_08.md`(論点4・5・6)
承認状態: **未承認**(VALIDATED候補[補強検証待ち]。採否は人間ユーザー)。11-7の限定例外は**適用しない**(既存Prompt周辺領域)。**ユーザー`APPROVED_FOR_PRODUCTION`の後にのみ実装**。補強検証(`TRIAL_DESIGN_07.md`)がPASSしない限り提案もしない。
行番号は作業ツリー現行(2026-10-24)基準。並行の課題②(possessor_roles、canonicalization段)・委任_27(`er105`/`er003` test)とは別責務。本書作成中、`er003_key_words_gloss_alignment.py` は**読むだけ**。

## 0. WIRING_DESIGN_06 からの変更点(要点)
| 論点 | 06 | 07(改訂) | 根拠 |
|---|---|---|---|
| 混在batch | call全体を現行builderへ戻す(記録のみ) | **2 callに分割**(null itemは新builder、glossありitemは旧builder) | OF-KP2-04。06では未生成itemを旧Promptで書く=今回直す不具合が戻る |
| 経路選択 | 選択肢P: message冒頭マーカーで`make_alignment_fn`が切替(推奨) | **方式P'**: `str`継承型に新経路情報を持たせ、`make_alignment_fn`が型を見て切替。**Promptにマーカーを入れない** | OF-KP2-05 |
| 新builderの正しさ | Trialとの一致は設計書上の対応のみ | **Trial harnessの`build_x_message06`とのgolden一致test**(差分=prior/rules_fulltext/マーカー無し) | OF-KP2-05 |
| 撤退手段 | 「`EIGO_KP_GLOSS_ALIGNMENT` OFFがkill switch」 | **単一commitの`git revert`が撤退手段**。flag OFFは**本番停止**(撤退ではない)と明記 | OF-KP2-06 |
| validator | 合否は既存検査+新3欄の存在 | 加えて**記録のみ**の持ち込み検出(`neg_in_gloss_not_in_kp`・`past_tense_ending`) | OPUS論点2 |
| Z repair | 非適用(推奨) | 非適用+**repair件数とgloss変化の監視項目1つ** | OPUS論点5 |
| 単価・所要時間 | +0.1〜0.3円/記事セット | **KP単位 約+0.05円/KP(Opus試算)→ +約0.5円/記事セット**。実測(補強検証(e))で確定、監視指標の基準を引き直す | OF-KP2-07 |
| 設計原則 | 「本文での用法に合わせた訳」へ変更(二択) | **「本文での語義を選び、表すのはkey_phraseの範囲だけ」**(新造比喩=指す意味、通常表現=従来どおり再利用できる訳が残る) | OPUS論点3 |

## 1. 設計の骨格
1. **新規生成経路専用の別builder + 別schema + 別developer message を新設**し、既存の `build_user_message_corrected`・`NEW_GENERATION_TEXT`・`PERSON_CONSTRAINT_TEXT`・`DEVELOPER_MESSAGE`・`GLOSS_ALIGNMENT_JSON_SCHEMA` は**一字も変えない**(A/B/C・Z repair・混在batchのlegacy側の出力はbyte-identical)。
2. 追加LLM call: 通常の新規生成は**0**(従来と同じ1 call/level)。**混在batchのときだけ+1 call**。retry上限(`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2`)・item単位retry・`prior`再提示は維持。
3. 新経路のpromptの正は、**DEV harness `er112_kp_gm_trial_06.build_x_message06`**(補強検証で実測した文面)。Production側新builderはこれと**byte一致**(golden test WC-12)。
4. revert単位=本件の単一commit(§6)。

## 2. 変更表(Production側。採用後にのみ実装)
| # | 場所(現行行) | 変更 | 備考 |
|---|---|---|---|
| G-1 | `er003_key_words_gloss_alignment.py` 新定数 `NEWGEN_DEVELOPER_MESSAGE`(:79付近) | 「英語学習教材のKey Phraseに付ける日本語グロスを書いてください。」(DEVの`M_DEVELOPER`) | 現行`DEVELOPER_MESSAGE`は不変。**developer文の差もX2p'の効果に含まれる**(§8限界) |
| G-2 | 同 新関数 `build_user_message_newgen_meaning(targets, article_text, rules, prior)`(:566-627の直後)。戻り値は **`NewGenMessage(str)`**(§4) | DEV `build_x_message06` を移植: `X_HEAD`+(人称項目あれば)`PERSON_CONSTRAINT_TEXT`の文脈限定句置換版+`X_NEWGEN`+**`X2PP_SCOPE`**+**`X2PP_MEANING`**+`X_OUTRULES`+**`prior_block`**+承認済みgloss規則(**`rules_fulltext`**)+対象項目(`previous_attempt_rejected`含む)+記事本文 | 06でTrialが省略した`prior_block`を含める。マーカー文字列は**入れない** |
| G-3 | 参考例「fall into」 | 新builderには含めない。既存builderは不変 | 既存builderの字義寄りfew-shotはZ repair・混在batchのlegacy側に残る(§7) |
| G-4 | 同 `NEWGEN_JSON_SCHEMA`(新規) | `GLOSS_ALIGNMENT_JSON_SCHEMA`をdeepcopyし`current_gloss_consistent`の後・`japanese_gloss`の前に `meaning_in_text_en`(string)・`naive_ja`(string)・`naive_ja_conveys`(enum yes/partly/no)を挿入、`required`に追加。name=`key_phrase_gloss_alignment_corrected_newgen` | DEV `x06_schema()`と同一(golden) |
| G-5 | 同 `validate_item_corrected`(:629-686)に `newgen: bool=False` | newgen時のみ: (a) 新3欄が非空文字列・enum内でなければ `reasons`に `meaning_stage_fields_invalid`。(b) **記録のみ**: `gloss==naive_ja`・`naive_ja_conveys`値・**持ち込み検出**(下記)を`out`へ。既存検査は不変 | **`newgen`は『gateが新builderを選んだか』で決める**(messageの型ではない)。型が失われても新欄欠落→INVALID→安全側(§4) |
| G-6 | 同 `run_alignment_gate_corrected`(:696-)と `make_alignment_fn`(:399) | §3(混在batchの2 call分割)と§4(P'): pendingをnewgen集合/legacy集合に分け、attemptごとに最大2 call。`make_factory_for(msg)`の契約は不変 | |
| G-7 | 同 `apply_alignment_corrected`(:766-) | `gloss_alignment`記録に `meaning_stage`(`applied`/`mixed_split_newgen`/`legacy`、`meaning_in_text_en`・`naive_ja`・`naive_ja_conveys`・`import_flags`)を追記のみ | TTS/表示へは出さない |
| G-8 | 同 `align_glosses`(:813-)の `gloss_alignment_runtime_metadata.json` | `meaning_stage`・`n_newgen_calls`・`n_legacy_calls`・schema/developerのsha・`rules_sha256`(既存)・`n_import_flags`・**repair時**の`n_realigned`/`n_already_consistent`(§7) | |
| G-9 | 承認済みgloss規則 | **変更0**(rules sha不変)。Production全文選定itemは`rules_fulltext`を使う(DEVも同一) | 補強検証(c)で実測(次委任) |

### 持ち込み検出(記録のみ。合否に使わない。G-5(b))
- 実装候補=DEV `er112_kp_gm_trial_06.detect_import`: (1) key_phraseに否定語(`not/no/never/without/none/nothing/nobody/cannot/neither/nor/hardly/barely/unable`・`n't`・`un-`で始まる語)が無いのにglossに否定(「ない」「なかっ」「ません」「ぬ」「ずに」「ず」)がある → `neg_in_gloss_not_in_kp`、(2) glossが過去形(「た」「だった」)で終わる → `past_tense_ending`。
- 実測(API 0、Trial_05 Stage 2の既存文字列): B0 108出力で2件(`off the hook`→「責任を問われずに済む」×2)、X2p 54出力で3件(`add up`→「つじつまが合わない」[真の持ち込み]、`move in the other direction`→「売れ行きは逆に下がった」[真]、`fill in`→「足りない部分を補う」[誤検出: 形容詞「足りない」])。Opusが挙げた持ち込み6件(THIN 2+PASSで見えるもの4)のうち**2件を検出(recall 2/6)、誤検出1/54**(B0側の`off the hook`は定訳的な訳で誤検出に近い)。主語・対象・場面の持ち込み(`step out`→「人が姿を現す」・`supply chain`→「店」)は検出できない。**=補助指標であり、品質判定の代わりにしない**(合否に使わない理由)。記録の目的は『量産で持ち込みが増えていないか』の傾向監視。再現=`er112_output/kp_gm_trial_06/import_detect_stage2_06.py`。

## 3. 混在batch(OF-KP2-04)
- 起きる場面: `select_generation_targets`(:278-288)は『再整合対象・人称一般化item(`is_person_generalized`)・人称不整合・全文選定でgloss未生成』を同一callにまとめる。全文選定の新規生成では通常全itemが`fulltext_source_ref`付き・gloss=nullで始まる(全件new)。**混在が起きうるのは再実行/resumeでglossが既にあるitemが対象に入るとき**(人称一般化itemなど)。
- 設計: `run_alignment_gate_corrected` の各attemptで `pending` を `newgen_pending = [t for t in pending if is_fulltext_gloss_missing(t)]` と `legacy_pending = それ以外` に分け、**非空の集合ごとにそれぞれ1 call**(newgen→新builder/新schema/新developer、legacy→現行builder/現行schema/現行developer)。`item_log`・`prior`・`adopted`は共通、attempt番号は共有(1 attemptで最大2 call)。`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2`を超えない。
- 費用: **混在した記事のlevelだけ+1 call**(legacy側は件数が少なく単価は現行並み)。新規生成のみのlevelは追加0。混在率は本番ログ(`n_legacy_calls`)で測る。
- **06案(call全体をlegacyへ戻す)は採用しない**: nullのitemを黙って字義訳しやすい旧Promptで書くことになる(今回直す不具合そのもの)。
- test WC-04(改訂): 混在入力でAPI callが2回、newgen call内に「他の文脈でも再利用できる」「辞書に複数の語義がある表現で」が**含まれない**、legacy call内のmessageが**現行builderの同入力出力とbyte一致**、結果は両集合のitemが共通の`adopted`に入る。

## 4. 経路選択: 方式P'(OF-KP2-05)
- `class NewGenMessage(str)`(`str`継承。属性 `path="newgen_meaning_v1"`)。新builderはこれを返す。**Promptに余計な文字列[マーカー]は入らない**ので、DEV Trialと文面が一致する(P案の欠点を解消)。
- `make_alignment_fn(user_message, ..., developer_message=DEVELOPER_MESSAGE, schema=None)`: `isinstance(user_message, NewGenMessage)` かつ **呼出側が`developer_message`/`schema`を明示していない**ときだけ `NEWGEN_DEVELOPER_MESSAGE`/`NEWGEN_JSON_SCHEMA` に切替。呼出側が明示した場合は明示を優先(既存test・golden・hookの契約不変)。factory契約(`factory(msg)`)は**変更なし**。
- 通る経路の確認(Grep): 本番の`make_alignment_fn`呼出は `er003_v1_n3_01_scaffold_generate.py:525-531 _align_factory(msg)` と `er026_family_z_fiction_production_runner_01.py:1447-1461 _person_repair_factory`(msg素通し、`msg + x`等の加工なし)のみ。gateは`messages.append(msg)`・`out_dir`への`f.write(msg)`のみで、strのままファイルへ書ける。
- **型が失われた場合の安全側**: strメソッド(`+`・`.replace`)を通ると型が戻り旧schemaで呼ばれる。この場合、応答に新3欄が無く、gate側が`newgen=True`で検証するため**INVALID**(`meaning_stage_fields_invalid`)→retry(同じ結果)→上限2で`FAILED_HUMAN_REVIEW_REQUIRED`(従来のHRフロー)で**安全側に停止**。黙って旧Promptの結果を採用することは無い(WC-07で固定)。`NewGenMessage`は`__add__`等を上書きしない(上書きして型を保つと意図しない伝播が起きる)。DEV harnessでは同じ構造を検証済み(`test_x2pp_invalid_when_new_fields_missing`: 新欄なし応答→全item INVALID→UNRESOLVED)。
- **Trialとのgolden一致test(WC-12)**: 同じ入力(代表KP群: 人称あり/なし、prior有/無)で、(a) DEV harness `er112_kp_gm_trial_06.build_x_message06` の出力、(b) Production新builder `build_user_message_newgen_meaning` の出力が**byte一致**(DEV側の出力をfixtureとしてProduction testにcommit。Productionコードは`er112`をimportしない)。さらにDEV側で、宣言した差分(rules_fulltext/prior/X2PP_SCOPE/X2PP_MEANING)を戻すとTrial_05 `build_x_message("X2p")`と一致することを確認済み(`er112_kp_gm_trial_06_test_01.py::test_golden_x2pp_builder_matches_trial05_x2p_except_declared_diffs` PASS)。**テストした組み合わせ以外を本番に出さない**。
- **方式Q**(factory契約の拡張)は不採用(全caller・test・hookの改修が必要)。

## 5. prior再提示・rules_fulltext(WC-06/Trial差分)
- Trial_05のX2pは`prior`を省略し`rules`(非fulltext)だった。新builderは`prior_block`・`previous_attempt_rejected`・`rules_fulltext`を含む。**DEV harnessで実装済み・API 0でtest済み**(`test_prior_block_matches_production_item_form`、`test_x2pp_message_contents`、fake clientによるretry経路`test_run_group_x2pp_with_fake_client_and_retry_prior`)。**質への影響は補強検証(c)で実測**(`rules_fulltext`+`prior`込みで54KP)。
- WC-06(改訂): retry時に`prior`が新messageに再掲され、attempt上限2不変、unresolvedはHR、新経路失敗が旧builderへ**暗黙フォールバックしない**。

## 6. flagと撤退手段(OF-KP2-06)
- 新規flagは設けない(同意)。ただし**説明を訂正**: 「`EIGO_KP_GLOSS_ALIGNMENT` OFFが撤退手段」は**不正確**。X/Zの全文選定itemはgloss=nullで始まり、`EIGO_KP_GLOSS_ALIGNMENT`がOFFだとglossが作られず、消費側`select_consumer_unevaluated`(:297-308、fail-closed)がTTS/組立を止める(`UNEVALUATED_REASON` :461-463に「kill switch=0のままだとglossが作られない」と明記)。**OFFは「gloss生成の全停止=本番停止」であり、元の挙動へ戻る手段ではない。**
- **実際の撤退手段 = 本件の単一commitの`git revert`**。既存builder/schema/定数は不変のため、revertで現行(byte-identical)に戻る。revertの検証手順(実装後のruntime evidenceに含める): 作業branchで`git revert --no-commit <commit>` → WC-01(不変性golden)とgloss alignment関連test群が全PASS → `git revert --abort`。commitには「Production挙動変更を含む単一commit」であることを明記し、他の変更(課題②等)と混ぜない。
- 起動script・`.env`等で暗黙にOFF/ONを切替えない。Trial中のProduction到達性: 現状`er112_kp_gm_trial_05.py`/`er112_kp_gm_trial_06.py`はDEV専用でProductionからimportされない。Production moduleは未編集(`TRIAL_05/production_hash_start.txt`・`er112_output/kp_gm_trial_06/production_hash_start.txt`と`git diff HEAD`で確認)。採用までflag/配線は**存在しない**(未承認機能のProduction既定値=「経路なし」)。

## 7. Z repair・A/B/C・Y(OPUS_REVIEW_08 論点5・6)
- **Z repair(`er026_family_z_fiction_production_runner_01.py:1552`)は非適用**: current glossありの人称修復で、旧builderの手順2(一致していれば書き換えない)が働くため字義寄りへ書き戻すリスクは低い(Opus見解)。意味欄を足す案は不要。
- **追加する監視項目は1つだけ**: repair呼出(`only_ranks`指定)のときの「repairされたitemの件数と、glossが変化した件数(`GLOSS_REALIGNED`対`GLOSS_ALREADY_CONSISTENT`)」を`gloss_alignment_runtime_metadata.json`へ記録(`n_repaired`・`n_realigned`)。既存の`GLOSS_REALIGNED比率`監視(CURRENT_SPEC.md:2793)の補助。
- A/B/Cの凍結ラインは`fulltext_source_ref`なし(`is_fulltext_gloss_missing`が偽)で新経路に入らない(WC-05)。**Yは共通moduleのため自動波及**するが、Yの量産Production経路は未存在(DEV/Trial)で、`PRODUCTION_WIRED`と呼ばない。
- 変更後の状態の開示: 旧builderの「key_phrase単体で他の文脈でも再利用できる自然な訳」の句がZ repair・混在batchのlegacy側・A/B/Cに**残る**。本番に2つの原則が併存する。CURRENT_SPECには**適用範囲つき**で書く(§11)。

## 8. 単価・所要時間・監視指標(OF-KP2-07)
- 単価の訂正: ADOPTION_PROPOSAL_01の「+0.1〜0.3円/記事セット」は、1.9KP/callのTrialでの値。本番は1 callに約5件で、増分の大半は出力token(KP数に比例)。Opus試算=**+約0.05円/KP × 10KP/記事セット ≒ +0.5円/記事セット(70円の約0.7%)**。DEV実測fitによる私の見積(`BUDGET_PLAN_T6_01.md`、Trial_05台帳の最小二乗): X2p b≈0.079円/KP(harnessは+10%余裕で0.087)、B0 b≈0.001円/KP(n≤2のため過小の可能性)→ **KP単位の増分は0.05〜0.09円/KP**(Opus試算の上限〜やや上)。**補強検証(e)の実測で書き直す**。
- 所要時間: 出力tokenが約3.5倍(447→1,561/call、KP単位でX2p 約1,621 token/KP)。1 level 5KPで約8,000出力token → 数十秒の増の見込み(Opus)。実測(e)で確定。
- **監視指標の基準見直し計画**(CURRENT_SPEC.md:2793の記録のみ指標): 「align費用[記事セット0.6円超]」は、B0で約0.06円/call(level)に対しX2p'の見積は約0.47円/level(a≈0.035+b≈0.087×5KP)で、**2 level/記事セットなら約0.9〜1.0円となり常時発火する**。「level単位align所要[60秒超]」も出力token増で常時発火の見込み。→ **(e)の実測後**に基準を引き直す: 費用=実測p95×1.3(記事セット単位)、所要=実測p95×1.5(level単位)。実測前に「発火しない値」へ緩めない(=アラートの意味を失わせない)ため、**採用提案には実測値と新基準案をセットで載せる**。その他の指標(attempt≥2[基準0/145、1件でも報告]・HR[1件で即時]・REALIGNED比率・DISABLED run)は不変。
- 新規監視(記録のみ): `meaning_stage`適用率、`n_import_flags`(持ち込み検出)、混在batch率(`n_legacy_calls`)、repair時のgloss変化率。
- 限界(開示): developer文(`M_DEVELOPER`対`DEVELOPER_MESSAGE`)・`rules`対`rules_fulltext`・`include_numeric_rule`差の影響はX2p'の効果と分離されない。補強検証(c)はB0p(現行Production)対X2pp(新経路全体)の比較で「新経路全体」の効果を見る。

## 9. test計画(WC。実装時。新規 `er003_test_kp_gloss_meaning_stage_01.py`)
既存 `er003_test_key_words_gloss_alignment.py`・`er003_test_kp_gloss_alignment_wiring.py`・`er003_test_kp_gloss_alignment_stop_paths.py`・`er003_test_kp_gloss_person_alignment.py` は変更せず回帰として全PASS確認。
| ID | 内容 |
|---|---|
| WC-01 | **不変性**: 全itemが`fulltext_source_ref`なし/current gloss有のとき、生成messageが現行とbyte-identical(`er071_output/.../golden/make_alignment_request_golden_01.py`のgolden)、schema/developer=現行 |
| WC-02 | 新規生成(全件null+`fulltext_source_ref`)で新builder・`NewGenMessage`・新schema・新developerが選ばれ、欄順=`current_gloss_consistent`→新3欄→`japanese_gloss`、Production必須欄が全部schemaにある |
| WC-03 | 新messageに「他の文脈でも再利用できる」「辞書に複数の語義がある表現で」が**含まれない**、「範囲の規則」「定訳」が含まれる、`rules_fulltext`の抽出文がそのまま含まれる、**マーカー文字列が含まれない** |
| WC-04 | 混在batchが2 call(§3)。legacy側messageは現行builderとbyte一致、newgen側に旧制約句なし |
| WC-05 | A/B/C形のitem(`fulltext_source_ref`なし)で新経路が一切呼ばれない(builder/schema呼出回数0) |
| WC-06 | retry時の`prior`再掲、attempt上限2不変、unresolvedはHR、新経路失敗が旧builderへ暗黙フォールバックしない |
| WC-07 | validate: 新欄欠落/enum外→INVALID、**新経路messageが旧schemaで呼ばれる(型喪失)とINVALID→HR(安全停止)**、`gloss==naive_ja`/conveys/持ち込み検出はrecord-onlyで合否不変、既存検査(括弧・算用数字・人称整合・qa・mapping)が新経路でも同一に働く |
| WC-08 | Z repair(`only_ranks`、current有)は現行builder(新経路0回)、repair件数メタデータが出る |
| WC-09 | `EIGO_KP_GLOSS_ALIGNMENT` OFFで従来どおり`DISABLED`・API呼出0(**挙動の確認であり、撤退手段ではない**ことをtestのdocstringに明記) |
| WC-10 | `make_alignment_fn`: `NewGenMessage`でない/呼出側がschema・developerを明示した場合は現行のまま |
| WC-11 | 回帰: 既存gloss alignment関連test群全PASS、全回帰 failed 0/errors 0の維持を実行時に記録 |
| WC-12 | **golden**: DEV `build_x_message06` の出力(fixture)と新builderがbyte一致(人称有無×prior有無) |

## 10. runtime evidence計画(実装後。X/Z正式KP段、新規TTS 0)
1. DEV注入text(過去Production記事の本文+`original_items`)で、X経路(`scaffold.run_key_phrase_canonicalization`)・Z経路(`er026` stage_kp)の正式KP段を`rules_fulltext`で実測。API費用は2経路×記事数(gloss callのみ)。
2. 確認項目: 新経路選択(`meaning_stage`)、validate通過率、HR率、混在batchの再現(current gloss有+null itemの合成入力で2 call)、型喪失の安全停止、A/B/C形入力で新経路0、Z repairは現行builder、所要時間・reasoning_tokens・単価(補強検証(e)の再測定)、revert手順の予行。
3. 失敗時の最終成果物: gate unresolvedは従来どおり`FAILED_HUMAN_REVIEW_REQUIRED`(KP維持・旧gloss維持・HR報告)。新経路固有の失敗(空応答等)も既存のTECHNICAL_FAILED/PARSE_FAILEDとしてattemptを消費し上限2後HR。

## 11. CURRENT_SPEC更新箇所(採用後。適用範囲つき)
`CURRENT_SPEC.md`のKP gloss再整合節(1970-1979行付近[承認済みgloss規則]、2785-2793行付近)に: 「**新規生成(全文選定由来・gloss未生成)のglossは、本文での語義を選び(字義か比喩か)、表すのはkey_phraseの範囲だけとする。`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`を先に出力して本文での意味を確定してから書く。key_phraseに含まれない本文側の否定・主語・時制・具体的な対象・場面は持ち込まない。定訳があれば定訳を優先する。**」を追記し、**適用範囲**を明記: 「Z repair・混在batchのlegacy側・A/B/C凍結ラインは従来の『key_phrase単体で他の文脈でも再利用できる訳』のまま(2原則が併存)」。承認済みgloss規則(`b1_p2_keywords_l_prompt_template.txt`抽出文)自体は不変。OPEN-474・DECISION_LOGも更新。

## 12. 本設計が決めていない事項(Fable/ユーザーへ)
①設計原則変更の採否(承認事項。`ADOPTION_PROPOSAL_02.md`の選択肢)、②補強検証(b)(c)(d)の結果次第でX2p'を見送りCp最適化版へ切替える場合の本設計の再利用範囲、③`meaning_in_text_en`の後段(Adv説明等)活用(仕様候補)、④A/B/C・Z repair・混在batchに残るfew-shot「fall into」(原因候補)の扱い(別Trial)、⑤`NewGenMessage`方式の細部(型継承の実装)を実装時にOpus再確認するかの要否(Fable判断)。
