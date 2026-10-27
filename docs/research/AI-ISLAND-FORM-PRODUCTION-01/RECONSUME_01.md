# RECONSUME_01 (AI-ISLAND-FORM-PRODUCTION-01 委任_06、AI島Std/Advの新表示仕様への移行、2026-10-27)
run=`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`。ユーザー決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md` §5(AI島に適用)。T-0=`..._DELEGATION_06.md`。
stop_scope_check rc=0(`_stop_scope_check_06.json`)、X runner同時起動なし(tasklist: python=Y runnerのみ)。起動間隔は1回のみ。

## 1. reconsume(API 0)
`py er128_kp_confirmed_content_01.py reconsume --run <run> --level a2|b1b --by sonnet-aif6 --user-ref docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md` 両level rc=0。
| 項目 | a2 (Std) | b1b (Adv) |
|---|---|---|
| revision | 2→3 | 2→3 |
| display_spec | `LEARNING_ITEMS_123_V1` | 同左 |
| confirmation_id | 不変(cf_aec83b8cbf53df86) | 不変(cf_e2fdc0b1f2914fe0) |
| origin(form_payload_sha256/user_ref等) | 不変。ただし`review_selection_signature`のみ更新(reviewにstd_part1が入りsignatureが再計算される仕様) | 完全不変 |
| history hash chain | 3→4件、旧3件逐語保持、全件prev連鎖OK、最新event=`reconsumed` | 同左 |
| items | ①3+**②2が追加**(p_1cf1329364 worth paying attention to / p_d17f8079e3 obstacle、slot=vocab、category=2) | ①3+②2のまま(変更なし) |
| unconsumed | ③5件(reason `CATEGORY3_NO_CONSUMER`→**`CATEGORY3_HIGHLIGHT`**)。Std②2件はunconsumedから消えitemsへ | ③5件 同左 |
| 文法 | 0件維持(grammar sidecar sha不変) | 同左 |
`confirmed_by`は「reconsumeを実行した記録」(by=sonnet-aif6, user_ref=SLOT-23 USER, attestation=cli、時刻更新)に更新される仕様。ユーザーの元の確認(form_submit/USER_02)は`history[0..2]`に逐語保持。actorは`user`のまま。
**不変性diff**(実行前snapshot=`<run>/audit/aif6_pre/`):候補ID集合は前後同一。英語(key_phrase/display_phrase/used_form)・日本語訳(japanese_gloss)・区分(category)は、既存10項目×2level全てで前後差0(差分は`slot`/`reason`のみ+Std②2件の派生フィールド[key_phrase/display_phrase/source_sentence_id/reference/derived/gloss_status]の新規付与=前はunconsumed表記のため未保持)。ユーザー確定の逐語変更0。
成果物の退避: a2の`keywords_canonicalized.json`/`kp_selection_final.json`は`*.RECONSUME_SUPERSEDED_1.json`へ退避(再finalize用)。b1bの成果物・review・音声は不変。

## 2. 確定Redundancy QA(LLM、a2のみ。`scaffold --level a2`の1起動内で実行)
kp集合・vocab集合(①+②)とも`REDUNDANCY_PASS`、duplicate_pairs=[]、model=gpt-6-luna(`a2/key_phrases/final_redundancy_qa/{kp,vocab}/keyphrase_redundancy_qa.json`)。NGなし。`vocab_confirmed.json`は`finalize_kp`により①+②5件で書かれた。`require_final_consistent`/`display_spec_of`は両levelで整合(API 0再確認済み)。

## 3. Std Part 1生成(`--stage scaffold --level a2` 1起動)
注: 指示は`--stage study_text`だったが、同stageは入口の`require_final_consistent`が`KP_FINAL_MISSING`(reconsume直後はvocab未確定)で止まる設計(`er019_family_x_audio_production_runner_01.py:3770-3780`)。確定QAとPart 1生成は`scaffold`が担う(既存Adv Part 1と同じ経路、`:915-945`)ため`--stage scaffold --level a2`を使用(b1bは起動せず=Adv不変)。コマンド: `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug ai_island_temple --run run_form_prod_01 --stage scaffold --level a2`(rc=0、log=`<run>/audit/stage_scaffold_aif6.log`)。
- 費用: 累計36.52→36.94円=**¥0.42**(確定QA 2call+Part 1解説1call[¥0.1045、gpt-6-luna、prompt_template_sha256=df21d3ef…=a2 golden一致]+T1訳)。上限¥10内。全て最新世代(gpt-6-luna)。
- 生成物: `a2/key_phrases/{kp_general_explanations,kp_source_sentence_ja,vocab_confirmed}.json`、`a2/study_text/part1_vocabulary_expressions.{json,md}`。5件(carry over / take a detour / card to play / worth paying attention to / obstacle)、日本語解説・T1日本語訳(translation_status=PROVIDED)、`level:"a2"`。品質検査(日本語本文30字以上・見出し一致・禁止パターン)PASS(生成関数内蔵、OK終了)。
- **Adv不変**: 前後sha256照合(270ファイル)で、b1b配下の差分は`confirmed_selection.json`(2枚、reconsume記録)のみ。`part1_vocabulary_expressions.*`/`kp_general_explanations.json`/`kp_source_sentence_ja.json`/narration/assembled/audio sha全て一致。a2の音声(narration/assembled)も一致(音声再生成0)。

## 4. ハイライト解決の事前確認(API 0、`SLOT-23-CONSUMER-DESIGN-01/tools/offline_resolve_01.py`を実run確定レコードで実行)
| level | 判定 | 項目 | 装飾 | ③訳 | NOTICE | ISSUE |
|---|---|---|---|---|---|---|
| a2 | OK | 10(①3/②2/③5) | 10 | 5 | `HL_OCCURRENCE_RELOCATED:p_31e10e6357`(Std `Strategy`: 元の候補文S2から本文内の別出現S8[full_story_part1]へ再配置) | 0 |
| b1b | OK | 10(①3/②2/③5) | 10 | 5 | 0 | 0 |
全項目の表層形/位置は`SLOT-23-CONSUMER-DESIGN-01/OFFLINE_RESOLVE_01.md`のAI島節と一致(コピー検証時と実run確定後で同一結果)。
