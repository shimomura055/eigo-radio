# WIRING_DESIGN_03: Std gloss改善(G2/G3) + A-1 のProduction配線差分(設計のみ、Production編集0・API 0)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_08 / 2026-10-23 / 前版=`WIRING_DESIGN_02.md`(Adv案E1/E4を含む旧版。Adv Promptは現行維持と判断したため**Adv関連の変更は全て不要になった**)・`WIRING_DESIGN_01.md`(A-1)
採否: G2/G3は**未承認**(採否は人間ユーザー。`TRIAL_RESULT_03.md` §7、Fable盲検後に確定)。A-1は`APPROVED_FOR_PRODUCTION`(UDR #169)だが配線は未実施。本書は採用された場合の差分設計。**採用前にProductionの既存Promptを直接編集しない**(11-7限定例外は既存Prompt直接編集には適用されない=Offline Trial→VALIDATED→ユーザー採用→実装の順)。

## 0. 要点
1. 変更範囲は**Std新規生成Prompt(`er003_key_words_gloss_alignment.py`のgloss生成)のみ**+A-1(`WIRING_DESIGN_01.md`)。**Adv Prompt・Adv schema・`PROMPT_SHA256`は不変**(`er019_family_x_kp_explanation_01.py:142`)。
2. Std gloss変更時のAdv説明の再生成は**既存のsignatureで自動的に起きる**(X `gloss_signature`、Z `sig_payload["gloss"]`)=仕様ID/version追加は不要(§3)。
3. flagは新設しない(承認されたProduction仕様として配線)。既存kill switch `EIGO_KP_GLOSS_ALIGNMENT`(`er003...:38`付近)のままで、OFFでもgloss未生成の全文選定itemは通さない既存挙動を維持。
4. 既存完成記事は**自動では変わらない**(KP stageを再実行したときだけ新glossになる。記事Bは別委任で手順実行、§6)。
5. G2/G3どちらを採っても差分は小さい(差は定数2つ=`NEW_GENERATION_GLOSS_BLOCK`とschema1つ)。

## 1. 変更箇所(file:line、現行HEADで確認)
| # | file:line | 現状 | 変更 |
|---|---|---|---|
| S1 | `er003_key_words_gloss_alignment.py:315-321` `NEW_GENERATION_TEXT` | 新規生成(current_japanese_gloss=null)の規則 | **直後に1定数**: G3案=`NEW_GEN_GLOSS_BLOCK_G3`(Trial `er112_kp_gm_trial_02.py G3_BLOCK`逐語)、G2案=`..._G2`(`G2_BLOCK`逐語)。選ぶのは1つだけ |
| S2 | 同:549-609 `build_user_message_corrected` の`new_gen_block`(:576)・組立(:605-607) | `person_block + new_gen_block + prior_block + "【日本語グロスの規則(承認済み選定Promptと同一)】"…` | `new_gen_block`が非空のとき**だけ**、`prior_block`の後・`【日本語グロスの規則…】`の**直前**にS1定数を挿入(Trialと同じ位置=`er112_kp_gm_trial_02.py gloss_call`のanchor置換)。`new_gen_block`が空(A/B/C・既存gloss判定・Z人称修復)のときは挿入しない=**メッセージはバイト同一** |
| S3 | 同:81-111 `GLOSS_ALIGNMENT_JSON_SCHEMA`(base、:81) | itemのproperties: rank, current_gloss_consistent, japanese_gloss, qa…, reasoning, added_word_mappings | **baseは不変**。新定数`GLOSS_ALIGNMENT_JSON_SCHEMA_NEWGEN`を追加(G3案=`candidates`[string 2〜3件]をrankの直後・japanese_glossの前に置く、G2案=`usage_sentence`,`usage_type`,`core_sense_en`を同位置)。Trial `g3_schema()/g2_schema()`と同形(strict structured outputでは**propertiesの順=生成順**のためfieldを前置する) |
| S4 | 同:382-415 `make_alignment_fn`(schema引数:383、:395) | `schema if schema is not None else GLOSS_ALIGNMENT_JSON_SCHEMA` | `schema is None`のとき、`user_message`にS1定数の識別行(例 `【日本語グロスの作り方(新規生成の項目`)が含まれるならNEWGENを、含まなければbaseを使う。呼出元(X/Z共通の`_align_factory`)は無変更。**メッセージとschemaが1つの条件(S2のnew_gen_block)で常にそろう**ので、不整合な組(G block有+base schema)は構造的に作れない |
| S5 | 同:612-672 `validate_item_corrected`・:752-790 `apply_alignment_corrected` | resp.get(known keys)のみ読む | **変更不要**(余分なfield=candidates/usage_*は無視される)。監査用に`candidates`/`core_sense_en`を`item["gloss_alignment"]`に保存するのは任意(下流は不使用)。保存する場合は`attempts_detail`への追加のみで、消費側が参照する`japanese_gloss`/`gloss_alignment_status`は不変 |
| S6 | 同:38 `GLOSS_ALIGNMENT_VERSION="ER-003-KP-GLOSS-ALIGN-02"` | 版文字列(artifact provenance。reuse判定には**使われない**: Grep `GLOSS_ALIGNMENT_VERSION`の参照はer003本体とtestのみ) | 版は**bumpしない**(testの`==...-02`固定[er003_test_key_words_gloss_alignment.py:487,826]を壊さない)。代わりにgloss生成仕様ID定数 `GLOSS_GENERATION_SPEC="STD-GLOSS-G3-01"`(またはG2)を追加し、`gloss_alignment_runtime_metadata.json`(:~827)と新規生成itemの`gloss_alignment`に記録(provenanceのみ、reuse条件には入れない) |
| A-1 | `WIRING_DESIGN_01.md` §1(T1〜T7、K1〜K5、G1) | — | **そのまま**。Std gloss変更とA-1は同じ`er003_key_words_gloss_alignment.py`のG1(`person_generalization_pairs`)で交差するため、同一委任で実装・同一回帰で確認する。Opus条件C must-fix **W-01〜04**の本文はrepo内(`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/`、`docs/pm/delegation_log/…KP…`)をGrepしても見つからず**未確認**。Fableが配線委任文でW-01〜04を転記すること(本書は反映済みとは言わない) |

## 2. X/Z共通であることの確認(コード照合)
- X・Z共通のgloss生成経路: `er003_v1_n3_01_scaffold_generate.py:524-532`(`_align_factory`→`gloss_align.make_alignment_fn`→`align_glosses`)。fulltext選定itemはJapanese glossが未生成=`is_fulltext_gloss_missing`(`er003...:253`)で`new_gen_block`が有効になる。
- Zのみ: `er026_family_z_fiction_production_runner_01.py:1347 ga.make_alignment_fn(msg, model=model)` は**永続化済みartifactの人称整合修復**(`only_ranks`、既存gloss有)=`new_gen_block`空→S1挿入なし・base schema=**挙動不変**。
- mapping_gate: Production呼出元は未指定(既定False)。新規生成itemはmapping必須語0(`RULE_CONSISTENCY_01.md`)。

## 3. Std gloss変更時のAdv説明の再生成(signature)
- X: `er019_family_x_audio_production_runner_01.py:1073-1086` `_resolve_kp_explanations_text`。`_has_status = any(it.get("gloss_alignment_status"))`(:1075)。fulltext新規生成itemは`apply_alignment_corrected`が`gloss_alignment_status=ALIGNED`を付ける(`er003...:778`)ため`_has_status`=True → **`gloss_signature`(display_phrase/key_phrase/japanese_glossの並び)の一致が必須**。gloss文字列が変われば5件まとめて再生成。
- Z: `er026...:1517-1528` `sig_payload`は、statusを持つitemがあれば`{"display":…,"gloss":[japanese_gloss…]}`にglossを含める → glossが変われば`ensure_stage("kp_expl_b1b", sig,…)`が再生成。
- よって**Adv説明の再生成条件に新しい仕様ID/versionの追加は不要**(Adv Prompt/PROMPT_SHA256が不変であるため)。glossが同一文字列なら従来どおりreuse。部分変更時は5件一括再生成の既存仕様のまま。
- A-1(used_form変更)は`explanation_phrase(it)=used_form`基準のsignature(`WIRING_DESIGN_01.md` §4)で別途再生成される。

## 4. Store reuse・retry/fallback
- retry: item単位retry上限2(`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2`、:39)。各attemptは`build_user_message_corrected`を再呼出するため、S2によりS1ブロックは**各attemptのmessageに入る**。`prior`(前回却下理由)も従来どおり渡す。2回失敗は`FAILED_HUMAN_REVIEW_REQUIRED`(既存fallback不変、KPを短い候補へ戻さない)。独自の回避・無効化はしない。
- 費用: Trial_03実測のgloss 1call平均 G0 0.070円、G3 0.104円(+0.034)、G2 0.130円(+0.060)(`paid_calls.jsonl`)。1記事セット(gloss call 2回)で+0.07/+0.12円。
- Store reuse(`master_audio_store`のStd日本語意味音声): gloss文字列が同じなら既存のText+Style一致でreuseされ、変われば新規TTS(従来のreuse機構のまま)。reuse_keyの具体は配線委任で実測確認(`WIRING_DESIGN_01.md` §4と同じ要確認事項)。
- 既存完成記事: `select_consumer_unevaluated`はstatus付きitemを評価済みとして扱う → **KP stageを再実行しない限り旧glossのまま**(強制再生成なし)。再実行手順はZ `--regenerate-stage kp_<lv>`、X はKP成果物削除後に再生成(`UNEVALUATED_REASON` `er003...:444`)。

## 5. test計画・撤去対象
| 区分 | 内容 |
|---|---|
| **維持(陳腐化しない)** | `er003_test_kp_fulltext_wiring_01.py:466,469,470` A/B/C msgのsha(`df113b44…`)・base schema sha(`c41959bd…`)・gloss規則sha(`447e07cb…`)= S1〜S4が条件付きのため**変更不要**。golden request(`er003_test_kp_gloss_alignment_wiring.py` `GoldenRequestBytes`、std_a2/adv_b1b、既存gloss有=`new_gen_block`空)も無変更で維持 |
| 追加 | (1)新規生成messageにS1が`【日本語グロスの規則…】`の直前に1回だけ入る (2)A/B/C・既存gloss判定・Z人称修復のmessageにS1が入らない(バイト同一) (3)`make_alignment_fn`のschema選択がmessage条件と連動し、不整合組が作れない (4)応答にcandidates/usage_*が有っても`validate_item_corrected`が従来どおり採用 (5)`GLOSS_GENERATION_SPEC`がmetadataに記録され、reuse判定に使われない (6)DefaultOff型は不要(flag新設なし、承認後の正規配線)だが、`EIGO_KP_GLOSS_ALIGNMENT=0`の既存挙動が不変 (7)全回帰 |
| 撤去対象 | **無し**(Std/Adv Prompt・schema・`PROMPT_SHA256`の既存assertはいずれも変わらない)。確認: Grep `er041_`(Trial-02履歴module、編集しない)・Trial-02逐語test(`PROMPT_SHA256`固定、`er019_family_x_kp_structure_wiring_01_test_01.py`)は**Adv Prompt不変のため対象外**。A-1側の撤去(`WIRING_DESIGN_01.md` §5: template:11旧文、`test_object_pronoun_kept_accepted_but_generalized_rejected`反転)は従来どおり |
| 残置 | 承認済みgloss規則(平易・括弧禁止・漢数字・数値穴埋め禁止)、`PERSON_CONSTRAINT_TEXT`、mapping record-only、人称決定論検査、語数/新規Fact検査(Adv)、`rules_sha256` |

## 6. 記事B(`uk_train_speaker_playback`)への反映手順(別委任、配線・回帰PASS後)
現状(`er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/{a2,b1b}/key_phrases/keywords_canonicalized.json`): a2=`sound no one asked for`/`reach for one's wallet`(自分の財布に手を伸ばす)/`draw that line`(その線を引く)、b1b=`a blanket ban`/`reach for one's wallet`/`draw that line`(その境界線を引く)。`user_test/uk_train_speaker_playback_e2e_02`はOPEN-467どおり保全。
1. 前提: STOP確認(`stop_scope_check_01.py`、run-dir付き)rc=0、Production差分commit済み、全回帰0/0。
2. 別out-dir(新run_id)でFamily X runnerの`--scaffold-only kp`(正式入口、`WIRING_DESIGN_01.md` §7)をa2・b1bで実行。Std gloss(S1〜S4)とA-1が同時に効く。
3. **KP段を再実行すると、Prompt 2の全文選定が3件を選び直す**(選定はLLM確率出力)。`draw that line`が`draw a line`になることに加え、`sound no one asked for`や`reach for one's wallet`が**入れ替わる可能性がある**。既存の3 KPをそのまま維持して`draw that line`の1件だけを差し替える経路はProductionに無い。→ 配線委任では(a)再選定を許容して新3 KPで再生成するか、(b)現3 KPに固定して個別に直すか、をFableが選ぶ(個別対策は禁止方針のため(a)を推奨)。
4. Adv説明は§3のsignatureで自動再生成、KP英語・Std日本語・Adv解説の音声は新text分のみ新規生成(≤5円見込み。X KP段0.8〜1.5円+KP音声の実績)。
5. 新成果物でStd日本語・Adv説明・音声を確認し、ユーザー再試聴用ページを作る(記事Bのユーザー最終承認はOPEN-467で保留中)。
6. 本番成果物を上書きしない(別out-dir)。評価はFable盲検+Gold(draw a line=区別をはっきりさせる等)で行う。

## 7. G2案とG3案の差分(どちらを採っても小さい)
| 項目 | G2(用法先決め) | G3(定訳・慣用句優先+自己選択) |
|---|---|---|
| S1定数 | 4ステップ(usage_sentence→usage_type→core_sense_en→japanese_gloss) | 2ステップ(candidates 2〜3案→japanese_gloss) |
| S3 schema追加field | usage_sentence、usage_type(enum 4値)、core_sense_en | candidates(string 2〜3件) |
| 1call費用 | +0.060円 | +0.034円 |
| 規則文・検査変更 | なし | なし |
| 差分行数 | 定数約8行+schema約10行 | 定数約6行+schema約6行 |
| 判断は`TRIAL_RESULT_03.md` §7(採否はユーザー、G0維持も選択肢) | | |

## 8. 見積
実装+test: Sonnet 1委任(A-1と同一委任で半日程度)、API 0。runtime evidence: X≤5円+Z≤5円(`WIRING_DESIGN_01.md` §7に従う)。待機は採否判断(ユーザー)とOpus条件Cレビューのみ。
