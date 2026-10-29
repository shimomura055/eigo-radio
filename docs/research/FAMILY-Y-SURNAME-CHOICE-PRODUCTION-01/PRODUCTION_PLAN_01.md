# PRODUCTION_PLAN_01 (FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_01)

作成: 2026-10-29 / 範囲: 制作前の経路確認・費用見積。LLM/TTS API 0円、Production実行なし、コード変更なし。
ユーザー原文: `docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER.md` (制作実行承認。記事内容・最終公開の承認は未取得)。
STOP確認: `tools/stop_scope_check_01.py --managed-id FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01` rc=0 (stop=false)。

## A-1. 承認済みの制作経路(復元結果)

入口 runner = `er121_family_y_runner_01.py`(音声層 `er121_family_y_audio_01.py`、構造 `er121_family_y_structure_01.py`、本文 `er121_family_y_text_core_01.py`)。手順書 = `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/OPERATIONS_01.md` (§1〜§8)。

先例(直近のY制作):
- 『SNS年齢制限』 `er121_output/family_y_production_01/sns_age_limit/run_01`。argv(`run_launch_log.jsonl`): `er121_family_y_runner_01.py --mode real --slug sns_age_limit --run run_01 --theme-package docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/sns_age_limit_package_01.json --approved-budget-jpy 170 --stage all`。実費 82.72円(`cost_by_stage.json`)。公開 `user_test/family_y_production_sns_age_limit_01`。
- 『再配達』 `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01` (argv: `--theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest .../redelivery_fee_reuse_01.json --approved-budget-jpy 60 --tts-execution-mode STANDARD --stages ...`)。公開 `user_test/family_y_production_redelivery_fee_03`(ユーザー最終試聴PASS、CURRENT_SPEC.md:3198)。
- 注意: `er110_output/family_y_*`(opinion_based_03 / closing_general_02)は**DEV/Trial経路**(`er110_family_y_*.py`)。今回の正式経路は er121 であり er110 は使わない。Theme Packageの原型は er110 の WORLD_FRAME/SHEETS/WHO_JA を転記したもの(新テーマの人物シート作成は手作業、下記)。

### stage 一覧とコマンド
STAGES(`er121_family_y_runner_01.py:34`) = `seed_check → text → translate → support → kp → tts_b1b → tts_a2 → gate → assemble → pages → page_verify`。b1b=Advanced、a2=Standard。

| # | stage | 内容 | 要点 |
|---|---|---|---|
| 0 | (前) STOP確認 | `py tools/stop_scope_check_01.py --managed-id <ID> --run-dir er121_output/family_y_production_01/<slug>/<run> --out <json>` | rc=3で新規API停止 |
| 1 | seed_check | routing・Voice割当・Theme Package検証(読取のみ) | dry-run既定でも確認可 |
| 2 | text | Voice 1-3 / Lead / 紹介 / Closing(Tension)+Gate。タイトルもここで決定 | 本文を手で直さない。Closing Gate=案B承認+`leak_discovery_syntax`補足(CURRENT_SPEC.md:3120-3123) |
| 3 | translate | 日本語本文→英訳(Std=a2 / Adv=b1b) | 契約違反の英訳は残さない |
| 4 | support | Preview / Comment 1 / Comment 3 等(Adv=Comment 2なし CURRENT_SPEC.md:3127-3131、Std=4種) | |
| 5 | kp | Key Phrase/Word候補生成。**rc=4=Human Review待機(失敗ではない)** | 有料の後続へ進まない |
| 6-7 | tts_b1b / tts_a2 | TTS+ASR(日本語音声はa2のみ)+Local Rewrite/retry(OPEN-540統一仕様) | Voice 1=Puck / 2=Zephyr / 3=Schedar固定 |
| 8-11 | gate / assemble / pages / page_verify | 音声品質Gate→組立→試聴ページ→検査 | **完成段は1起動で** `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify`(OPEN-480 RESTART_STORM回避。OPERATIONS_01 §3) |

推奨起動(実行はまだしない・Fable承認後): `py er121_family_y_runner_01.py --mode real --slug surname_choice --run run_01 --theme-package <新規 theme_packages/surname_choice_package_01.json> --approved-budget-jpy <N> --stages seed_check,text,translate,support,kp`(KPでrc=4)→HR→同一`--stages`後半を1起動で再開。`--approved-budget-jpy`の上限は `APPROVED_BUDGET_MAX_JPY=170`(runner:32)、警告閾値100円(runner:33。超過見込みで新規API前にSTOP。`--ack-warn-threshold`はFable確認後のみ)。再開=同じコマンドの再実行(各stageは入力shaが一致すれば再利用・API 0)。

### 必須入力: Theme Package(最大の未整備事項)
- 形式=`er121_family_y_text_core_01.validate_theme_package`(text_core:1150-1175)。必須キー: `theme_id, world_frame(distinctions含む), who_ja, sheets{voice_1..3}(gender, age_label, role_ja, daily_life_ja, contact_point_ja, persona_sketch_ja, stake_ja, arc_ja, experiences[{id, kind=E/O, source_ids非空, text_ja}], speech_style, opening_type, identity_cue_ja, claim_core_ja, known_fact_id, ...)`, `restricted_voice_ids`, 任意 `source_dir`(出典との連続一致検査用。無いと `verbatim_report` が not_checked、text_core:1745-1751)。
- 先例の作り方: er110 DEV Trial の定数を機械転記(SNS package の`note`欄)。**新テーマで出典→人物シートへ落とす正式の収集・抽出ツールは存在しない**(CURRENT_SPEC.md:3255「収集経路=未配線・未検証」)。よって Package は手作業(Fable/Sonnet)で作成し、各experienceに実在コメント番号を`source_ids`で紐づける。Voice説明文(承認文言)は全Voiceの全experienceにsource_idsが非空のときだけ自動表示(`ys.theme_package_is_post_based`、structure:117-)。
- 出典の保存: ガルちゃんは逐語転載を避ける条件(CURRENT_SPEC.md:3255)。`source_dir`に生コメントを置くとrepo内に逐語が残るため、置くなら要約のみか、連続一致検査の方式をFableが決める(判断候補)。
- 出典表示方式(音声ラジオ)は未設計(CURRENT_SPEC.md:3255、UDR #213の設計部分は残)。

### Human Review と最終成果物
- KP/Word/文法(Top1/Top2)/ニュアンス候補は**学習項目選定フォームv3**で採否(X/Y/Z×Std/Adv PRODUCTION_WIRED、CURRENT_SPEC.md:3215-3223)。コマンド: `py er119_kp_human_review_cli_01.py select|reselect|declare-absent ...`、フォーム回答の確定は `confirm --from-readable <paste.txt> --run <run> --level a2|b1b --by <名> --user-ref <path>`(CURRENT_SPEC.md:3219)。統合依頼書は `<run>/review_request.md`。先例では不在宣言(Fable代行・user_ref付き)で通した例があるが、**今回のユーザー原文は「必要なHuman Reviewを実施」**なので、不在宣言で通すか人間確認を取るかはFable判断(判断候補)。
- TTS 1 segmentが3回に達するとER-011 HR Lockになり、再起動では解除されない。解除は `er011_human_review_lock_01.approve_regenerate()`(ユーザー承認)のみ(OPERATIONS_01 §8)。Take承認の流用はVoice一致が条件(`er121_family_y_hr_approval_guard_test_01.py`)。
- 照合コード方式: Y専用のコードは無く、X/Y/Z共通フォーム(`er128_form_readable_restore_01.py` restore/confirm、fail-closed)。**これらer120/er128は現在未commit差分あり**(A-4)。

### 試聴ページ出力先
- runner出力 = `<run>/pages/index.html`(+`audio/`)。公開は別手順で `user_test/family_y_production_<slug>_NN/` へ配置(先例: `family_y_production_sns_age_limit_01`、`..._redelivery_fee_03`)。配置前に `py -I tools/user_test_page_standard_check_01.py --page <index.html>` と `py -I tools/y_page_notice_check_01.py --page <index.html>` が共にrc=0(OPERATIONS_01 §6)。到達目標=公開URL(`https://shimomura055.github.io/eigo-radio/user_test/...`)。ユーザー最終試聴前は公開完了扱いにしない(ユーザー原文§6)。
- Chunk境界マーカー`⏸`は開発用で既定publicでは出さない(CURRENT_SPEC.md:3201)。

## A-2. 機能Status表(SSOT照合。断定できないものは「未配線扱い」)

| 機能 | Status(Y) | 根拠 | 本記事での扱い |
|---|---|---|---|
| Y正式runner(text〜page_verify) | `FAMILY_Y_PRODUCTION`(OPERATIONS_01冒頭)。Style継承=PRODUCTION_WIRED(CURRENT_SPEC.md:3192) | OPERATIONS_01:5 | 使用可 |
| Y Voice map | Voice 1=Puck(男) / 2=Zephyr(女) / 3=Schedar(男)固定。PRODUCTION_WIRED | CURRENT_SPEC.md:3143、structure:60-64 | 下記「性別とスロット」要判断 |
| KP/Word(Part 1、Std+Adv) | Y配線済み(SLOT-23 commit 331474a9f、Std Part 1は新規記事から) | CURRENT_SPEC.md:2091 | 使用。HR必須(rc=4) |
| 文法 Part 2(Top1/Top2事前生成、HR採否) | X/Y/Z×Std/Adv 仕様確定・配線済み(GRAMMAR-PREGEN commit c3b83a3e0) | CURRENT_SPEC.md:2109-2110 | 「0件=コーナー非表示」(2026-10-29承認)のrunner対応は**未commit差分の中** |
| ニュアンス解説(OPEN-586) | ユーザー2026-10-29 `APPROVED_FOR_PRODUCTION`、到達目標PRODUCTION_WIRED、**配線作業中=未配線扱い**。`er134_nuance_explanation_01.py`はcommit 09716c352「未配線」。runner(er121)への接続は未commit差分のみ(`nuance_for_display`/`FAMILY_Y_NUANCE_OUTPUT_MISMATCH`追加中) | `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md`、OPEN_ITEMS.md:1102 | **配線済みと扱わない**。接続完了(Fable受入)まで生成・HRを前提にしない |
| JA-ASR v2+β | commit afc63717d でX/Y/Z配線(R-1 OFF)。OPEN-515本文に「目的達成度=未達」注記が残る | `git log -- er121_family_y_runner_01.py`、OPEN_ITEMS.md:1030 | 配線済みとして使用可。PRODUCTION_WIRED最終判定はFable |
| TTS retry/Fallback/Local Rewrite統一 | PRODUCTION_WIRED(限定)(OPEN-540) | CURRENT_SPEC.md:3156- | 使用。Local Rewrite経由はStyle Gate/人承認が必須 |
| Chunk TTS(Y) | `WIRED_NOT_FIRING`(本文契約=段落5固定・Voice本文1行で不発火)。**PRODUCTION_WIREDではない** | CURRENT_SPEC.md:3019,3134 | 本文契約を変えない |
| Advanced Comment 2削除 | PRODUCTION_WIRED(限定: 初回生成stage[導入文3 call]は次のY新規記事で確認) | CURRENT_SPEC.md:3127 | 今回が初回確認の機会 |
| Voice説明文(承認文言) | `APPROVED_FOR_PRODUCTION`(実投稿ベース記事のみ) | CURRENT_SPEC.md:3201 | 全Voiceのexperienceにsource_ids必須 |
| 新しい情報源の収集方式 | 19サイト承認済みだが**収集経路=未配線・未検証、PRODUCTION_WIREDではない** | CURRENT_SPEC.md:3255 | Package手作業作成。ガルちゃんは単発・robots遵守のみ |
| Fact確認工程(Y) | Y runnerに専用のFact確認stageは見当たらない(text_core:1241は「知っている事実はない」制約、`world_frame.fact_scopes`/`known_fact_id`のみ) | grep結果 | 制度の事実を入れるならPackage作成時に一次情報で裏付けて`distinctions`/`fact_scopes`に固定。Voice本文は制度に触れない設計が既定 |

### 要判断: Voice性別とスロットの整合(重要な発見)
- `FIXED_VOICE_SLOTS = {voice_1: Puck(male), voice_2: Zephyr(female), voice_3: Schedar(male)}`(structure:60-64)。Package検証(`validate_theme_package`)には**sheetの`gender`とスロットの整合検査がない**。
- 実例: SNS package は `voice_1.gender=女性` だが `voice_assignment.json` は voice_1=Algieba(男性声)(`er121_output/family_y_production_01/sns_age_limit/run_01/voice_assignment.json`)。再配達は男/女/男でスロットと一致。つまり先例SNSは**本文は女性の一人称・音声は男性声**の不整合が既にある可能性(聞き取り評価の有無は未確認)。
- 本記事: ユーザー原文の3軸候補(V1=寂しい親=トピ主は夫を「旦那」と呼ぶ女性、V3=自分の姓を選んだ女性)は**Voice 1=男声・Voice 3=男声のスロットと衝突**。解決案は`VOICE_SOURCE_01.md`参照。分類: スロット変更はユーザー承認事項(CURRENT_SPEC.md:3143で固定)、人物設計での整合は承認範囲内。SNSの不整合は11-8(承認済み設計原則「性別はVoice Cardの明示項目」[DESIGN_PROPOSAL_02.md:345]との矛盾)に当たる可能性があり、本件と独立に是正対象かをFableが判断。

## A-3. 費用見積(Std+Adv 1セット)

先例の実費(`cost_by_stage.json`):

| 区分 | SNS run_01 (本文を新規生成) | 再配達 run_01 (本文固定・再利用) |
|---|---|---|
| 本文(yp_voice[Sol 27.9] + closing[Sol 22.0] + intro[Sol 4.8] + lead[2.6] + vmap/vstruct 約1.9) | 約59.4円 | 約0.12円 |
| 英訳 | 0.64 | 0.47 |
| support | 0.34 | 0.42 |
| KP + gloss整合 | 3.35 | 2.81 |
| TTS(Gemini flash-lite) | 14.68 | 18.01 |
| ASR(Azure STT + gpt-4o-mini-transcribe) | 4.58 | 10.19(Azure 5.41は再試行込み) |
| 合計 | **82.72円** | 32.07円 |

本記事の見積(新規本文生成なのでSNS型):
- 基準 約83円。追加要素: 文法Top1/Top2事前生成(Std/Adv両level)・ニュアンス解説(+約0.10〜0.14円/set、OPEN_ITEMS.md:1102)・JA-ASR β。合計で+数円。TTS/ASR retry・Local Rewrite・Take再生成を見込み、**通常 85〜110円、悪化時〜130円**。
- 判定: **案件300円(7-7)・日次1,000円内**。ただしrunner警告閾値100円(runner:33)を超える可能性があり`--ack-warn-threshold`はFable確認後。個別Cap 170円(runner:32、BUDGET_PLAN_03)内に収まる見込み。Package作成(手作業)・追加取材・Human Review・ページ公開は追加費用0。
- 量産単価70円/セット目標との差: 新規本文生成は本文(Sol)だけで約59円で、合計は70円を超える(SNS 82.72円)。固定本文の再配達型のみ32円。原価低減余地=Sol本文生成の削減(別判断。本タスクで承認済みPromptは変えない)。
- 本文を再生成すると1回あたり約+60円(本文生成が主コスト)。Package品質を事前に固めてから1回で通すのが費用効率的。

## A-4. 未commit差分のY経路への影響

`git status`(2026-10-29 10:4x JST)で、Y経路が直接importするfileに未commit変更あり:
- `er121_family_y_runner_01.py`(53行差分): `_blocks_in_page_order` / `FAMILY_Y_NUANCE_OUTPUT_MISMATCH` / `nuance_for_display` / 文法0件期待の追加。**`stage_pages`関数が`_y_pww_aux_html`の後ろへ移動する途中状態**(diff上、元の定義が削除され後方で再定義)。
- `er120_part2_wiring_01.py`(130行)、`er120_part2_grammar_production_01.py`(175行)、`er128_kp_confirmed_content_01.py`(245行)、`er019_family_x_audio_production_runner_01.py`(4行)。runnerのimport: `import er120_part2_wiring_01 as p2w`(runner:709)、`import er119_kp_wiring_01 as kw`(runner:573)。
- 結論: **Y正式経路(kp / pages / page_verify)に影響する**。他案件(ACTIVE_TASK (H)Z IN-A-GROVE、(A)月Std)も同じ差分で待機中。**有料run(特にkp以降)は、この差分がcommitされFable受入されるまで開始しない**ことを推奨(OPERATIONS_01 §8「有料run前に`git status`でer121_*が未commit変更でないことを確認」)。textもrunnerを通るため同様に待機が安全。Package作成・出典整理(API 0)は並行可能。
- 作業中に見えた未commit新規`er128_nuance_hr_test_01.py` / `er120_nuance_display_test_01.py`は別Workerのもの。触っていない。

## A-5. 実行前のクリティカルパス(提案)
1. (並行・API 0) Theme Package作成: Voice設計確定(`VOICE_SOURCE_01.md`)→world_frame・人物シート・experienceのsource_ids→`seed_check`(dry-run)で検証。
2. (並行・API 0) 追加取材: 妻の姓を選んだ男性当事者など(note等、承認済み情報源、各5ページ以内)。
3. NUANCE配線差分のcommit確認→Fable承認→text〜kp(rc=4)→HR→tts〜page_verify(1起動)→公開前検査→試聴URL。
