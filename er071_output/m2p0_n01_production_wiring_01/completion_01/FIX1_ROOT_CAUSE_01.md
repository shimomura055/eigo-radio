# FIX1_ROOT_CAUSE_01: Coffee Std KP『based on』CANONICALIZATION_INVALID の根本原因と是正(2026-10-13、JPY0)

管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_01 / Status: FIXED_PENDING_PRODUCTION_RUN(unit/regression/dry-runで確認、正式経路完走は委任_02)

## 1. 事実(既存記録のみで確認)
- 現象: 2 job x 内部2 attempt = 4回すべてで rank5 の key_phrase=`based on interviews`(normalization_reason=`restore_semantic_complement`)が Rule7 違反。reason=「display_phraseと一致せず、source_span('based on')内の連続部分文字列でもない」。
  証跡: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2/key_phrases/canonicalization_runtime_metadata.json`、`a2/key_phrases_d02_attempt_invalid/canonicalization_runtime_metadata.json`。
- 『based on』の出所: selection段(M2P0)の通常DB照合候補 C1(Wiktionary phrasal_verb survivor、`m2_supply_report.json` rank5 `source_candidate_id=C1`、`reserved_slot_candidate=false`・`fragment_risk=false`)。(a)(b2)予約枠・所有格3-gram・placeholder由来ではない。M2供給は仕様どおり動作しており、供給段の不具合ではない。
- canonicalizationへの入力(`canonicalization_prompt.txt` L100-103): `display_phrase="based on"`, `source_span="based on"`, `source_sentence="However, \"about nine months\" is an estimate based on interviews"`。

## 2. 根本原因
候補ID方式(Source Reference Contract)では `source_span` = 候補の `surface_form`(DB照合した短いn-gram。`er030_key_phrase_db_hybrid_source_reference_contract_01.py` の `restore_source_fields` で `source_span = surface_form`)であり、Strategy Lの選定LLMが文脈込みで書いたspanとは性質が違う。
一方 canonicalization Prompt(`restore_semantic_complement`、qa_not_over_minimized、qa_context_sufficiency)は「単独で意味が欠ける場合は **source_span から** 必要最小限の語を復元する」と指示する(Promptの例: source_span `the urge to watch`、display `the urge to` -> `urge to watch`)。
『based on』は前置詞で終わり単独では意味が閉じないため、LLMはPromptどおり補語の復元を試みる。しかし補語『interviews』は source_span の外(source_sentence側)にしかなく、LLMは source_sentence から取って `based on interviews` を返す。これは Rule7(source_span内の連続部分文字列)に違反する。
すなわち: Prompt(復元せよ)と入力(復元元が無い)の食い違い。LLMの出力自体は意味的に妥当(reasoningに「source_spanは『based on』のみなので文字列追跡の条件は満たしません」と自己認識している)。

## 3. 責任範囲
| 工程 | 役割 | 今回の関与 |
|---|---|---|
| selection/M2供給 | DB候補を選ぶ | 仕様どおり。『based on』はDB上正当な候補。変更しない(Parity Gate維持) |
| canonicalization入力(source_span) | 復元元を与える | **原因工程**: 候補ID方式でspanが短いn-gramのまま渡される |
| canonicalization Prompt | 復元を指示 | 正しい(承認済み、変更不可) |
| Rule7 Validator | key_phraseがspan内連続部分文字列か検査 | 正しい(緩和不可) |

## 4. retryで同一になる理由
`run_canonicalization_gate` の再試行は「同一条件で最大1回」(入力・Prompt同一)。入力に復元元が無い限りLLMは同じ判断(補語復元)を再現する。実測で4/4回同一。決定論的な構造不整合であり、再生成を繰り返しても解消しない。

## 5. 修正(原因工程で、Rule7/Prompt/Validatorは無変更)
`er003_key_words_canonicalization.py`:
- `expand_dangling_source_span(item)` / `canonicalization_view_items(items)` を追加。**候補ID方式のitem(`source_reference_contract`を持つ)に限り**、source_spanが機能語(前置詞・冠詞・限定詞・接続詞等、`_DANGLING_TAIL_WORDS`)で終わる場合に、source_sentence内の実出現位置の直後から「内容語を1語含むところまで(最大3語)」を原文どおり連結した拡張spanを作る。句読点・文末・sentence内に見つからない場合は拡張しない。
- 拡張spanは `build_user_message`(LLM入力)と `validate_canonicalization_response`(Rule7判定のsource_span)にのみ使う(同一関数 `canonicalization_view_items` で両者一貫)。選定結果の `source_span`(Source Consistency Gate等が参照)は書き換えず、`merge_canonicalization_result` が監査用に `canonicalization_source_span` を追記するのみ。
- Rule7の判定式(`_is_contiguous_substring(key_phrase, source_span)`)は無変更。拡張spanは原文の連続部分文字列なので、原文に存在しない語の捏造は従来どおりINVALID(test: `based on the interviews` / `based on interviews with experts` / `relying on interviews` はINVALIDのまま)。
- 一般化: 『based on』個別のpatchではなく、「機能語で終わる候補ID方式span」全般(`urge to` -> `urge to watch`、`look at` -> `look at the data` 等)に効く共通機構。Strategy L(source_reference_contractなし)は入力がバイト同一(test済み)。

M2P0仕様範囲: M2供給(er030_*m2_supply)・P0 Prompt(template/static/guidance sha)・KP canonicalization Prompt文面・Rule7は一切変更していない。変更したのはcanonicalizationへの入力データ(復元元の提示範囲)のみで、Prompt自身が規定する「source_spanから復元」契約を、候補ID方式でも成立させる修正。

## 6. OPEN-310との関係
OPEN-310はRule7の**人称代名詞一般化表**(`my->someone's`等がINVALID)で、同じRule7でも別枝。本修正は「補語復元がspan外」の枝で、OPEN-310の恒久策(person表とPrompt案内の不一致解消)とは**別修正**。OPEN-310は未解決のまま(本修正で変化しない)。OPEN-346①(Rule7 fragment起因INVALID監視)とは同種(語追加系Rule7)で、本修正がその主要因を解消。`loan against the future`型(span外の辞書形)は別論点のまま。

## 7. 検証(API 0円)
- 新規test `er003_test_key_words_canonicalization_dangling_span.py` 12件PASS(再現ケース+同種表現+Strategy L無影響+Rule7厳格性維持+merge監査項目)。
- 既存: er003_test_*.py 1479件中1475 PASS(4件failは `er003_test_p2j_investigate.py` のtest件数照合で、本変更前から失敗=既存。新規testファイルを退避しても同じ4件失敗を確認)、er030 108/108、`er003_v1_n3_01*_test*` 55/55、er019 378/378(新規21含む)。
- Parity Gate(`er071_m2p0_parity_report_01.py` を出力先だけ変えて再実行): `completion_01/parity_after_fix1_01.json` all_pass=True、既存`parity_02.json`と完全一致(10記事rows sha・final prompt sha不変。selector側を触っていないため当然)。
- dry-run(`er071_completion_01_fix1_dryrun.py` -> `completion_01/fix1_dryrun_01.json`): 既存INVALID 2 job x 2 attempt の記録済みLLM出力を修正後validatorへ再投入 -> 全4 attemptで構造INVALID解消(job1: PASS/PASS、job2: 1回目REVIEW_REQUIRED[LLM自身のQA FAIL]/2回目PASS)。入力spanは `based on` -> `based on interviews`。

## 8. 残存リスク(委任_02で確認)
- 修正後入力でLLMが実際に何を返すかはdry-runでは確認できない(記録済み出力の再投入のみ)。正式経路のStd KP再生成(約JPY1)で確認する。LLMが『based on』のまま返す場合もPASS(unchanged)。
- 拡張windowは単純規則(機能語リスト+最大3語)。`in the` -> `in the old` のように内容語1語で止まるため学習単位として最適でない場合があるが、LLMに選択肢を与えるだけで、最終key_phraseはLLMがQA基準で決める。
- 『based on interviews』が学習単位として適切かは別論点(Rule7整合のみ保証)。
