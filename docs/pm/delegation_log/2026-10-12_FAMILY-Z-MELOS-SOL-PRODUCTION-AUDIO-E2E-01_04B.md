# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04B(2026-10-12)

範囲: er062 Writer鎖・Standard調整・Story分割・Dialogue話者判定・Preview/Comment/KP・lint・来歴。実装+mock tests+最小smoke。PRODUCTION_WIRED未達(er026統合は後続)。SSOT編集なし。

## 実装概要
- `er062_family_z_structure_01.py`(純粋関数・課金0): 段落整形、分割候補の決定論全列挙(各Part20〜45%)、話者の決定論判定(Family C keyword窓)と突合、Family C `plan_story_segments(force_split_before_paragraphs={b1,b2})` 全文1回呼出+`full_story_part{n}_c{k}`改名(Part跨ぎclipはSTOP)、Comment挿入位置、Std/Adv同一本文率、Preview/Comment決定論lint。
- `er062_family_z_writer_01.py`: routing key経由のLLM呼出(actual model_id/usage/費用記録、返却model不一致STOP、費用上限)、Writer鎖R0->R1->R2(Trial②のPrompt/effort=high/developer文を正式化、B3Zなし。差分=A2->Advanced化・400-560語・原作保持条件・Story Type・タイトル行)、Std調整(X共有ブロック`STANDARD_A2_NEW_VOCAB_BLOCK`/`STANDARD_A2_DEVELOPER`をimport、In one line要求なし、段落数・順序一致契約・同一本文禁止)、分割選択(LLM=候補ペアの選択のみ、候補外は1回再提案->STOP、理由日本語)、話者判定(全引用1call、不一致STOP+`dialogue_override.json`)、Preview/Comment(Std=Z既存Preview role+Family C Comment生成、Adv=X B1の`COMMENT_1_ROLE`/`COMMENT_2_ROLE`/`PREVIEW_ROLE`無改変、Comment3は`COMMENT_2_ROLE`再利用、Comment4/COMMENT_3_ROLEは呼ばない)、KP(Strategy L、両レベル別々)、provenance(sha chain、resume時sha一致のみ再利用、不一致STOP、`--regenerate-stage`のみ再生成、子孫はstale化し自動再生成しない)。
- `er062_family_z_writer_01_test_01.py`: 55 tests(mock、課金0)。

## smoke結果(実呼出、gpt-6-luna、実費 約0.12円、model_id=gpt-6-luna)
証跡: `er060_output/melos_production_e2e_01/er062_smoke_01/`(smoke_result.json/.md、raw_usage_log.jsonl)。入力=Trial②R2(39段落・364語、Adv下限400語未満のためWARN相当だが分割検証には使用)。
- 分割: 候補69ペアから Part2=段落10〜、Part3=段落25〜 を選択(Part1=99語27.2%、Part2=142語39.0%、Part3=123語33.8%)。理由(日本語)は「第1部=約束と人質、第2部=帰路の苦難と諦めかけの危機、第3部=友の顔を思い出す転機から再会」。候補内、再提案不要。
- 話者判定(全18引用、1call): 決定論との一致 agree 7件、llm_only 11件(決定論=キーワード該当なしで判定不能)、mismatch 0。計画: 37 clip、Comment2挿入=`full_story_part1_c16`の後、Comment3=`full_story_part2_c6`の後。
- 要人間確認の所見: q26_1(`*"I will wait."*` イタリック回想の友の台詞)をLLMはmelosと判定(文脈上は友の台詞の回想の可能性)。決定論は判定不能のためllm_onlyで採用された。
- lint(¥0): OK文はOK、NG文(news/Point/構造ラベル/聴取指示/ネタバレ/In One Line)は全て検出、期待通り。

## 設計判断(要確認)
1. 決定論が判定不能(キーワード該当なし、「he said」等)の引用は不一致でなく`llm_only`としてLLM判定を採用(これを不一致扱いにすると「he said」だけで全件STOPするため)。決定論とLLMが異なる値を出した場合のみSTOP。
2. EN Comment/Previewのlintは聴取指示を検査しない(X B1のCOMMENT_1_ROLEが「Listening Focus」で注目点を示す設計のため)。news/In One Line/Point/構造ラベル/ネタバレ/名前/言語は両言語で検査。
3. X B1の`PREVIEW_ROLE`/`COMMENT_*_ROLE`は「ニュース」前提文言を含むため、無改変のまま文脈側で「ニュースではなく物語」と打ち消し、出力をlintで検査。lint NG -> retry1回 -> STOP。E2Eで実出力により初めて確認される(未実行)。
4. Std Comment n の`content_facts`は「これから聞くPart n本文に書かれた事実のみ」と指示し、contextにも対象Part(+直前Partを参考)だけを渡す。Part外の事実は渡さない。事実性の検証は決定論lint(名前・ネタバレ語)まで。

## er026統合時のstage定義・CLI
stage名(provenanceのキー): `r0,r1,r2,std_adjust,plan_b1b,plan_a2,support_b1b,support_a2,kp_b1b,kp_a2`。依存: r0->r1->r2->{std_adjust,plan_b1b,kp_b1b}、std_adjust->{plan_a2,kp_a2}、plan_b1b->{plan_a2,support_b1b}、plan_a2->support_a2。
CLI: `python er062_family_z_writer_01.py --run <run> --stage {writer|std_adjust|plan|support|kp} [--level a2|b1b|both] --mode {dry-run|mock|real} [--regenerate-stage <名前>] [--approved-budget-jpy N]`。dry-runは副作用ゼロ。smokeは `... smoke --text <path> --out <dir> --mode real --approved-budget-jpy N`。
出力: `<run>/writer/{r0,r1,r2,std}.md`+`*_prompt.txt`+`provenance.json`、`<run>/segment_plan_{a2|b1b}.json`(データ契約4-2。追加欄: split_origin, paragraph_count, source_text_sha256, clips[].speaker/voice_role/text)、`dialogue_attribution_{level}.json`、`support/{level}_support.json`、`key_phrases/`。
注意: Std調整は`--stage std_adjust`、Adv鎖は`--stage writer`(r0-r2)。本文は`level_text_path`(Adv=r2.md、Std=std.md)。Melos/王/友の台詞clipは`voice_role=dialogue:<speaker>`(melos/king/friend/other)。STORY_REGISTRYにMelos用Voice割当は無い点は04C確認事項。

## 残リスク
- Family C B1 assembly未実行(OPEN-305)。Advancedのaudio側は04C/E2Eで初実行。
- news文言lintは実LLM出力で未確認(E2E)。Writer鎖R0->R2とStd調整の実呼出は未実施(E2Eで実施)。
- Adv Promptは400-560語・B1-B2に変更(Trial②はA2約350語)=Trialと同じ品質になる保証は無い。Std調整のPromptもTrial未検証(要試聴)。
- 語数Guardrail(OPEN-302)は未承認のためWARN。
- 事故: CLI mockの動作確認中に`kp`段階が実API(gpt-6-luna、KP選定)を呼んでしまった(mockのkp_fn未設定が原因、修正済み)。概算 約0.1〜0.5円、記録は`kp_backend_telemetry`へ書かれたが私の2行は削除済み。smokeとは別で、合計でも¥5に遠く及ばない。
