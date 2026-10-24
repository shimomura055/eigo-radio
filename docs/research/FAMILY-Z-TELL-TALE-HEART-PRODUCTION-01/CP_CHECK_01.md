# CP_CHECK_01 / 手順書 (FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_01、2026-10-24、準備段階=有料API 0)

直近の同種制作『猿の手』(FAMILY-Z-MONKEYS-PAW-PRODUCTION-01: `docs/research/FAMILY-Z-MONKEYS-PAW-PRODUCTION-01/{CP_CHECK_01,SOURCE_CHECK_01,BUDGET_PLAN_01,RUNTIME_EVIDENCE_01,CLOSEOUT_01}.md`、`er026_seeds/the_monkeys_paw/seed.json`、`er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/`)の手順を正とし、同じ正式経路・コマンド列・Gate・試聴ページ形式を踏襲する。**本委任では起動しない(次委任で起動)。**

## §A 着手時の整合確認
| # | 確認事項 | 結果(照合箇所) |
|---|---|---|
| 1 | 正式Production経路 | er026 runner `er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_01 --stages ...`(『二十年後』『賢者の贈り物』『猿の手』と同一経路)。E2E_STAGES順=seed_check,writer,std_adjust,plan,support,kp,tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify。作品追加は`STORY_REGISTRY["the_tell_tale_heart"]`・`TELL_TALE_HEART_RIGHTS_BLOCK`(runner)、`STORY_VOICE_ROSTER`/`STORY_SPEAKER_CONFIG`/`STORY_LINT_CONFIG`(er062_structure)、`STORY_MAIN_CHARACTER`(er062_writer)のdata表のみ(ロジック変更0)。登録test 23件+関連294件OK。 |
| 2 | Std/Adv構成・長さ・Voice | 既存3パート構成、本文330-470語(`ACCEPT_WORD_RANGE`)。Voice=正式Voice表+決定的割当規則、pinなし: narrator=Aoede(語り手本人の台詞も)、old_man=Algieba、officer=Schedar(Charon=Adv補助、既存)。登場順はWriter出力確認後にplan前に訂正し得る(data表の順序のみ、『猿の手』と同手順)。会話の少ない一人称ホラーだが構成・速度仕様v2はそのまま適用(仕様変更・効果音・新Prompt禁止を遵守)。 |
| 3 | 原作忠実性基準 | Seedに`source_essentials`(ending_reveal=自白[source_quote `It is the beating of his hideous heart!`]/setups_and_payoffs 2件[鋭い聴覚の主張→最終場面の心臓音、目への執着→8夜目]/key_causality 1件/key_roles 3[全員名なし=keep_name false]/free_to_cut)。維持必須=1+2+1+0=4件(上限5)。`validate_source_essentials`PASS(登録test、`seed_check` stageで再検査)。ユーザー指示の維持項目との対応表=SOURCE_CHECK_01.md。 |
| 4 | Key Phrase | A-1・課題②=PRODUCTION_WIRED。**課題①X2p'はUDR #179 APPROVED_FOR_PRODUCTION・commit `d8fb8f9a4`で配線済み**(XYZ共通のKP gloss新規生成経路、新flagなし)。本作はX2p'配線後の仕様で動く。 |
| 5 | ASR/TTS/retry/fallback/HR | `TTS_EXECUTION_MODE=STANDARD`。OPEN-487/491/494のASR数値・時刻修正(commit d6d17562b/7d4ec5bc4/1d104d711)はHEADに含まれる(`git merge-base --is-ancestor`、下記§D)。HR Lock時はapprove_regenerateしない(Fable/ユーザー承認後のみ)。極短clip速度Gate(SHORT-CLIP-SPEED-GATE-01、OPEN-496)は実装済み・Fable受入待ち(Gate緩和なし)。 |
| 6 | 日次予算 | BUDGET_PLAN_01.md(Z≤70円)。 |
| 7 | STOP確認 | `tools/stop_scope_check_01.py --managed-id FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01` rc=0(`stop_check_00.json`)。 |

## §B 次委任の起動コマンド列(『猿の手』の実績どおり。実行は`.venv/Scripts/python.exe`、環境`TTS_EXECUTION_MODE=STANDARD`)
共通引数: `er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_01 --mode real --approved-budget-jpy 70 --tts-execution-mode STANDARD --stages <段>`。**各起動の直前に** `.venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01 --out docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/_stop_scope_check_<段>.json`(rc=3なら停止報告)。

| # | `--stages` | 想定 | 備考 |
|---|---|---|---|
| 1 | `seed_check,writer,std_adjust` | 約3分、約15〜20円 | seed_checkでSeed承認(source_essentials・rights gate・sha)。Adv r0/r1/r2→Std。語数330-470・段落数Adv/Std一致を確認。**終了後に原作忠実性CP(§C)を記入**。Writer出力の初出順でroster順を確認し、必要ならplan前に訂正 |
| 2 | `plan,support` | 約2分、約1円 | plan=会話話者判定(LLM+決定論のクロスチェック)。support=Preview/Comment(lint)。`DIALOGUE_ATTRIBUTION_MISMATCH`/`SUPPORT_LINT_FAILED`が出たらdata表修正を**まとめて1回**、次起動まで**150秒以上** |
| 3 | `kp` | 約3〜5分、約2円 | KP全文選定+gloss(X2p'配線後の経路) |
| 4 | `tts_b1b` | 約5〜10分、約10〜12円 | **TTSは直列**(b1b→a2を同時に起動しない) |
| 5 | `tts_a2` | 約5〜10分、約10〜12円 | 同上 |
| 6 | `provision_shell,gate,assemble,pages,page_verify`(**1起動**) | 約2〜5分、API 0 | provision_shell欠落でgateがrc=2→再起動でRESTART_STORMを自行発動するため必ず5段を1起動で指定(OPEN-480)。page_verify=公開URLの実再生検証(Playwright) |

- **有料run起動回数**: 基本=1,2,3,4,5,6の6起動(うち有料=1〜5)。例外起動(Fable承認後のみ・各1回): 速度Gate/ASR NGの該当clip再生成(`--stages tts_b1b --only-clips <clip>`、キャッシュ退避方式は『猿の手』RUNTIME_EVIDENCE_01 委任_03)、完成段の再実行(`provision_shell,gate,assemble,pages,page_verify`を1起動)。
- **RESTART_STORM回避**: 同一run起動間隔 **最低150秒**(300秒窓に3起動で自行発動)。`<run>/STOP`・`RESTART_STORM_LOCK.json`は自分で削除・`--clear-stop`しない。
- **TTS直列化**: tts_b1b と tts_a2 は別起動で順に実行(runner内もclip直列、cooldownはrunner待機)。X側audioとのTTS同時実行を避ける。
- **HR Lock時**: 即停止してFableへ報告(Gate緩和・approve_regenerateは自分で行わない)。
- **公開**: `pages`段がrunnerの正式Z試聴ページ生成(`user_test/family_z_tell_tale_heart_01/`、`audio_file_prefix=TellTaleHeart`)を行い、公開(git push)後に`page_verify`が公開URLを検査する。公開は通常のcommit/push(今回変更の対象ファイルのみ`git add <path>`)。

## §C 原作忠実性チェックポイント(次委任で最終稿確定後に記入。8項目の様式は『猿の手』CP_CHECK_01 §Bと同じ)
最低限の項目: ①ending_reveal(自白で終わる・音が現実か妄想か語らない) ②withhold_until_end(自白・音の正体を最終場面前に示唆しない) ③語り手=名なし・一人称・『狂っていない』主張 ④老人の目(淡青色・vulture eye)が動機 ⑤7夜の偵察→8夜目 ⑥心臓音の増大→殺害→床下の隠蔽 ⑦警官の来訪→語り手が真上に座る ⑧音の増大→自白。Adv/Std両本文の引用を`writer/r2.md`/`writer/std.md`へ機械照合(curly quote正規化)。Fable確認事項(質問): SOURCE_CHECK_01の『遺体解体の描写は1文に圧縮可』は原作の重要な出来事の維持と整合するか(Seed内の圧縮指示、新仕様ではない)。

## §D 事前チェック(import graph未commit差分、HEAD=`d8fb8f9a4`、2026-10-24 22:1x JST)
- import graph算出: 静的import+文字列参照の推移閉包(root: `er026_family_z_fiction_production_runner_01`)=**161 module**。`git status --porcelain`でM/D/??のあるもの=`er026_family_z_fiction_production_runner_01.py`・`er062_family_z_structure_01.py`・`er062_family_z_writer_01.py`(いずれも**本委任のdata表追加=自分の変更。commit後に解消**)のみ。他agentのX2p'差分(`er003_key_words_gloss_alignment.py`)は着手時にuncommittedだったが22:05:56にcommit `d8fb8f9a4`として確定済み(作業ツリーclean)。
- 次委任の起動条件: graph内のtracked .pyが全てcommit済みでHEADと一致・STOP/LOCK sentinelなし・`stop_scope_check` rc=0・`origin/main`へpush済み(再現性)。
- 公開先 `user_test/family_z_tell_tale_heart_01/`: 未使用(`ls user_test`/`git ls-files`で0件)。run dir `er026_output/family_z_production_e2e_01/the_tell_tale_heart/`: 未作成(runner `seed_check` stageが作成)。
