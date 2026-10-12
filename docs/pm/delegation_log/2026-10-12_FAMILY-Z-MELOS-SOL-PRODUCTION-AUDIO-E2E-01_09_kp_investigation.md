# 委任_09 kp_a2 CANONICALIZATION_INVALID 調査(read-only、課金0、コード・SSOT無変更) 2026-10-12

## 1. 該当コードと現行挙動(事実)
- Rule7判定: er003_key_words_canonicalization.py:375-416 `validate_canonicalization_item`。key==display なら常に可、そうでなければ source_span 内の連続部分文字列、または (normalization_reason=="generalize_person_dependent_reference" かつ `_is_valid_person_generalization`) のみ可。
- 閉じた語彙集合: 同:304-322 `_PERSON_DEPENDENT_TO_GENERIC`(キー=display側トークン、値=許可されるkey側トークン)。
  - my -> {one's} のみ / our -> {one's} / its -> {one's}
  - your, his, her, their -> {one's, someone's, somebody's}
  - you/they/he/she -> {someone, somebody, one}、再帰代名詞 -> oneself、yours/theirs -> {one's}
  - 一人称 I / me は集合に無い(別Trialで既知)。
  - よって "take my place" -> "take someone's place" は集合外(my->someone's が無い)で不可。"take one's place" なら通る。
- 原因(事実): promptと検証の不整合。canonicalization prompt template (er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt) 規則3(11行目)は「my/your/…等を one's/someone's/somebody's 等の標準一般形へ置換せよ」と指示し、例も "catch their attention"->"catch someone's attention"。ただし「決まった一人称・二人称の慣用句等は機械的に変換しない、迷えばreasoningで説明」の除外句もある。LLMは規則3に従い my->someone's とし、QAは全PASS自己申告(evidence_08 attempt1: normalization_reason=generalize_person_dependent_reference)。しかし検証側は my->one's のみ許可。"辞書形へ"と明示指示している=一般化は仕様どおりの動作。
- 無変更 "take my place" のまま出していれば key==display で無条件に通る(LLMが一般化を選んだことだけが原因)。
- CANONICALIZATION_INVALID時: er003_key_words_canonicalization.py:507 MAX_CANONICALIZATION_RETRY_ATTEMPTS=2(同一入力でprompt同一の再呼出し1回)、:560-566 で2回目もINVALIDなら終了。er003_v1_n3_01_scaffold_generate.py:731-733 run_key_phrases は canonicalization 失敗時に selection へ自動retryせずそのまま {"canonicalization": canon(INVALID)} を返す(Redundancy retryは別ループ:710)。fallback/Human Reviewは無い。Z側 er026_family_z_fiction_production_runner_01.py:1212 が FAMILY_Z_KP_CANONICALIZED_MISSING でSTOP(1230はNG_REVIEW_REQUIRED時のSTOP)。
  - 補足: 今回の selection 2回は --regenerate-stage による別実行であり、共有コード内の自動selection retryではない。

## 2. 過去の同種記録
- er030_output/kp_backend_telemetry_01/telemetry.jsonl: 141行。final_statusは STRUCTURE_PASS 87 / FALLBACK 26 / STOP 26 / STRUCTURE_INVALID 2。selection段のtelemetryであり canonicalization 結果は記録されない -> Canonicalization INVALID の頻度はここでは測れない(推測不可、事実: 未記録)。
- 同種STOPの過去事例: EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-PERSON-CHECK-01_REPORT.md:70-88(一人称記事で "give me distance"->"give someone distance"、me が集合に無くINVALID。Voices Production採用時に I/me を集合へ入れるかはUSER_DECISION_REQUIREDと記載)。解決は Production関数無変更で選定を独立再実行(2回目で me 含む候補が避けられPASS)。同種の外側retryは er012_b_voices_3v_a2_kp_fix_ai_hiring_01.py:200-222 (OUTER_RETRY_MAX=4) と free_address版にもある(Trial/個別script側、共有moduleには無い)。
- 関連既存修正: DECISION_LOG(KEYPHRASE-PERSON-DEPENDENT-REFERENCE-GENERALIZATION-WIRING-FIX-01、2026-09-27): qa_traceable_contiguous_span のみ集合に整合させた。集合自体は無変更。
- OPEN_ITEMS.md:813 OPEN-310 が本件。X Production(Family X/C)でのCANONICALIZATION_INVALID STOP記録はDECISION_LOG/OPEN_ITEMSからは確認できず(Voices Trialの上記事例のみ)。er019 meta__run_regen_01 のX a2 canonicalizationはPASS。

## 3. 設定/引数だけで可能な手段(既存機構)
- 除外リスト/過去phrase dedupe/human_confirmed入力/seed/temperature: KP選定・canonicalization経路(scaffold_generate.py:293-,349-,589-、er003_key_words_strategy_compare)に該当する引数は確認できず(temperatureのgrep0件)。dedupeは同一記事内候補のみ(er030_core:365)。
- 唯一の注入点: `diagnostic_note`(scaffold_generate.py:293-296, 349-360)。自由文をselection promptへ追記する。公開関数 run_key_phrase_selection は受け付けるが、run_key_phrases はこれを引数で受けず内部のRedundancy QA結果でのみ設定(:760-765)。したがって利用するにはZ側がrun_key_phrases(共有)を使わず、run_key_phrase_selection -> run_key_phrase_canonicalization -> redundancy QA を自前で組む必要がある(共有moduleは無改変で可、Zの追加コードのみ)。
- run_kp_stage(er062_family_z_writer_01.py:918-928)の kp_fn フックは差し替え口として存在(runner:1229の ctx.hooks["kp_fn"]。本番引数は text, kp_dir, article_id, source_level, process)。

## 4. Z側から渡せるもの
- 渡せる: 選定対象 text(Std/Advそれぞれの本文全体、canonical_article_text)、level、out_dir、slug、process(A2_SUPPORT/B1_SUPPORT)、kp_fn。候補数(5)・本文範囲・除外リストの引数は無い(Strategy L固定)。kp_backend="db_hybrid" は Family X専用で、Z未配線・Z採用は未承認なので使わない。

## 5. 選択肢整理
(a) Z側選定promptへ所有格phrase回避: 変更=Z所有のkp_fn内でdiagnostic_note注入(共有module無改変)。Production影響=Zのみ(Z自体Trial/E2E隔離中)。承認=Z仕様追加のため要Fable判断+Zのみなら軽い。費用≒1 run(<JPY1〜2)。再発防止=中。所有格だけ避けても me/I 等の別形が残る可能性。OPEN-310には"回避側"で効くがLLM遵守は非決定的。
(b) Fable指示の別rank1を人間確定: 変更=Z側にhuman確定入力の追加(現状無い)。人為修正禁止(OPEN-310記載)との整合が必要。再発防止=なし(個別対処)。費用ほぼ0。承認=ユーザー/Fableの明示判断。OPEN-310には効かない(症状回避)。
(c) Rule7集合に my/our/its -> someone's/somebody's を追加: 変更=共有module 1箇所(:305,309,311)。Production影響=全Family(X/C等)に及ぶ(許可が広がる方向、QAの意味判断・他検査は不変)。承認=要(共有module変更、人間のProduction承認)。要Opusレビュー(重要変更のProduction採用提案条件C)。費用=実装+unit test(既存er003_test_key_words_canonicalization.py)+Z再実行 ≒ <JPY2。再発防止=最も高い(prompt規則3と検証の不整合を根治、your/his系と対称化)。I/me追加は別論点(Voices)。
(d) 除外/dedupe機構で除外: 該当機構なし。(a)のdiagnostic_noteで「take my place を選ぶな」と記すのと実質同じ(個別phrase名を入れるのは記事固有ハードコードで、既存の「記事固有ハードコード禁止」思想に反する)。非推奨。
(e) canonicalization prompt修正(共有): 規則3に「my等の所有格は one's に限る」または「物語中の特定人物を指す一人称は無変更でよい」と明記。変更=共有template(全Family影響、promptなので挙動確率的)。承認=要(共有)。再発防止=中(LLM遵守に依存)。(c)と二者択一の整合策(検証側を広げるか、promptを検証に合わせるか)。
(f) その他: (f1) Z側kp_fnでselectionのみ外側retry(OUTER_RETRY_MAX相当、Trial scriptにprecedentあり、共有無改変、各retry≒selection+canon <JPY1)。ただし今回は同一rank1が4回連続のため効果は不確実。(f2) INVALIDの項目だけ key=display(無変更)に落とす決定論的fallback(Z側kp_fn後処理)は「Gate回避」にあたる恐れがあり不可寄り、Fable/ユーザー判断要。

## 6. "take my place" のKP適切性
- A2 KPとしては妥当(平易で、メロスの身代わり=身代わりになる意味を持つ汎用句)。canonical形 "take my place" 無変更なら通る(key==display)。LLMが変形したのは上記のとおり規則3(一般化指示)に従ったため。ただし "take someone's place" 自体は辞書形として自然で、集合側の欠落(my->someone's)が不整合の本質。物語特定の一人称慣用で一般化不要とみなす除外句もpromptにあるが、LLMは今回採らなかった。なお "take one's place" だと不自然になりうる(学習用途で劣る)。

## Fable推奨案の材料(最小変更で安全な順)
1. (f1)+(a)軽量版: Z側kp_fn(共有無改変)でselectionのみ外側retry(上限をFableが固定、例2回)し、diagnostic_noteに汎用ルール文(個別phrase名を含めず「所有格を含むphraseは可能な限り避ける」等)を付ける。Z隔離内、費用<JPY3。効果は確率的で、OPEN-310の根治にはならない。
2. (b) 人間確定: ユーザーが明示承認する場合に限り別rank1/または take my place 無変更を人間確定。E2E進行のみ目的、費用ほぼ0。OPEN-310は未解決のまま残す。
3. (c) 集合に my/our/its->someone's/somebody's を追加(my->someone's は(e)プロンプトと整合):根治案。共有module変更のため要Opusレビュー+人間承認、既存unit test拡張+全Family回帰確認が必要。X/C記事の既存PASS結果を再判定して誤PASS化がないか確認(過去の14件再判定と同様の手順)。1か3かは、OPEN-310をStd頻発リスクとして根治するか次第。
