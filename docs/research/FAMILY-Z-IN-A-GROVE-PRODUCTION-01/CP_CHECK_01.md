# CP_CHECK_01 / 手順書 (FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_01、2026-10-28、準備段階=有料API 0)

直近の同種制作『告げ口心臓』(`docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/{CP_CHECK_01,SOURCE_CHECK_01,BUDGET_PLAN_01}.md`)・『猿の手』の手順を正とし、同じ正式経路・コマンド列・Gate・試聴ページ形式を踏襲する。**本委任では起動しない(Fable Seed CP後の委任_02で起動)。**

## §A 着手時の整合確認
| # | 確認事項 | 結果(照合箇所) |
|---|---|---|
| 1 | 正式Production経路 | er026 runner `er026_family_z_fiction_production_runner_01.py --story in_a_grove --run run_sf_prod_01 --stages ...`(『告げ口心臓』『猿の手』等と同一経路)。E2E_STAGES順=seed_check,writer,std_adjust,plan,support,kp,tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify。作品追加は`STORY_REGISTRY["in_a_grove"]`・`IN_A_GROVE_RIGHTS_BLOCK`(runner)、`STORY_VOICE_ROSTER`/`STORY_SPEAKER_CONFIG`/`STORY_LINT_CONFIG`(er062_structure)、`STORY_MAIN_CHARACTER`(er062_writer)のdata表のみ(ロジック変更0。`git diff`はrunner/structure/writerとも挿入のみ+writerの1行置換)。 |
| 2 | Std/Adv構成・長さ・Voice | 既存3パート構成、本文330-470語(`ACCEPT_WORD_RANGE`、CURRENT_SPEC 2026-10-19④)。Voice=正式Voice表(FAMILY-Z-VOICE-PRODUCTION-WIRING-01 2026-10-23)+決定的割当規則、pinなし(下記§E)。速度仕様v2(2026-10-23)・Std/Adv会話の扱いは仕様どおり適用。**証言構造は新Gate/Validatorを置かず、Seed(conversion_plan/essentials)のWriter Prompt指示のみで担保**(ユーザー原文§2末尾「既存品質基準を引き上げない・新Validator/Gate禁止」を遵守)。 |
| 3 | 原作忠実性基準 | Seedに`source_essentials`(ending_reveal[source_quote逐語・原作最終文]/setups_and_payoffs 0件/key_causality 1件/key_roles 3名keep_name[Tajomaru・Masago・Takehiro]+役割4/free_to_cut 1/narration_voice)。維持必須=1+0+1+3=**5件=上限ちょうど**(`ESSENTIALS_MAX_ITEMS=5`)。`validate_source_essentials`PASS(下記§D dry run、登録test)。essentials削除でfail-closed(`FamilyZSeedEssentialsStop`)も確認。ユーザー原文§2の5重点との対応=SOURCE_CHECK_01.md §3およびSeed。 |
| 4 | Key Phrase | A-1・課題②=PRODUCTION_WIRED、課題①X2p'(KP日本語意味の新経路、UDR #179承認・commit d8fb8f9a4)配線済み=『告げ口心臓』と同じ。本作固有の変更なし。 |
| 5 | ASR/TTS/retry/fallback/HR | `TTS_EXECUTION_MODE=STANDARD`。HR Lock時はapprove_regenerateしない(Fable/ユーザー承認後のみ)。極短clip速度Gate(SHORT-CLIP-SPEED-GATE-01、OPEN-496)は仕様どおり(Gate緩和なし)。**本作は全編ほぼ台詞=Adv会話速度(atempo 1.06)の対象が本文の大半**(承認済み仕様v2どおり。極短clipが少ない長い独白中心のため、『猿の手』のc5型停止の可能性は低いが、短い引用[`Kill me.`等]が生じ得る=Gate停止時は『猿の手』前例[該当clipのみ再生成、Fable許可後]に倣う)。 |
| 6 | 日次予算 | BUDGET_PLAN_01.md(Z≤70円)。当日(2026-10-28)把握分は起動直前に再集計(本委任では未集計=委任_02の起動条件)。 |
| 7 | STOP確認 | `tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01` rc=0(`stop_check_01.json`、`stop:false`)。run dir(`er026_output/family_z_production_e2e_01/in_a_grove/`)は未作成。 |

## §B 次委任の起動コマンド列(『告げ口心臓』の実績どおり。実行は`.venv/Scripts/python.exe`、環境`TTS_EXECUTION_MODE=STANDARD`)
共通引数: `er026_family_z_fiction_production_runner_01.py --story in_a_grove --run run_sf_prod_01 --mode real --approved-budget-jpy 70 --tts-execution-mode STANDARD --stages <段>`。**各起動の直前に** `.venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --out docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/_stop_scope_check_<段>.json`(rc=3なら新規API呼出をせず停止報告)。

**初回起動前に1回だけ**: Production seed置き場 `er026_output/family_z_production_e2e_01/in_a_grove/seed/` を作成(『告げ口心臓』『猿の手』と同形式。`seed.json`と`primary_text_excerpt.md`[=`er026_seeds/in_a_grove/story.md`の複製]をsha付き`SEED_PROVENANCE.json`で凍結。`ctx.seed_dir`=この置き場。本委任では未作成=Fable Seed CP前に確定させないため)。dry runの手順は§D(同じ形式)。

| # | `--stages` | 想定 | 備考 |
|---|---|---|---|
| 1 | `seed_check,writer,std_adjust` | 約3〜4分、約15〜20円 | seed_checkでSeed承認(source_essentials・rights gate・sha)。Adv r0/r1/r2→Std。語数330-470・段落数Adv/Std一致を確認。**終了後に原作忠実性CP(§C)を記入**。Writer出力の証言者の初出順・省略有無を見て、必要ならplan前にroster(order/話者)を訂正 |
| 2 | `plan,support` | 約2分、約1円 | plan=会話話者判定(LLM+決定論のクロスチェック)。support=Preview/Comment(lint)。`DIALOGUE_ATTRIBUTION_MISMATCH`/`SUPPORT_LINT_FAILED`が出たらdata表修正を**まとめて1回**、次起動まで**150秒以上** |
| 3 | `kp` | 約3〜5分、約2円 | KP全文選定+gloss(X2p'配線後の経路) |
| 4 | `tts_b1b` | 約6〜12分、約12〜16円 | **TTSは直列**(b1b→a2を同時に起動しない) |
| 5 | `tts_a2` | 約6〜12分、約12〜16円 | 同上 |
| 6 | `provision_shell,gate,assemble,pages,page_verify`(**1起動**) | 約2〜5分、API 0 | provision_shell欠落でgateがrc=2→再起動でRESTART_STORMを自行発動するため必ず5段を1起動で指定(OPEN-480)。page_verify=公開URLの実再生検証(Playwright) |

- 起動回数: 基本6起動(有料=1〜5)。例外起動(Fable承認後のみ・各1回): 速度Gate/ASR NGの該当clip再生成(`--stages tts_b1b --only-clips <clip>`、wav退避方式は『猿の手』RUNTIME_EVIDENCE_01 委任_03)、完成段の再実行(5段を1起動)。
- RESTART_STORM回避: 同一run起動間隔**最低150秒**。`<run>/STOP`・`RESTART_STORM_LOCK.json`は自分で削除・`--clear-stop`しない。HR Lock時は即停止してFableへ。
- 公開: `pages`段がrunnerの正式Z試聴ページ(`user_test/family_z_in_a_grove_01/`、`audio_file_prefix=InAGrove`)を生成。公開(git push)後に`page_verify`が公開URLを検査。

## §C 原作忠実性チェックポイント(機械生成チェックリスト、Writer後に記入)
`writer/cp_checklist.md`はWriter段で`write_cp_checklist`が生成する。以下は**本作Seedから`build_cp_checklist`で生成した書式(本文欄は空)**。処置規則(A重大/B軽微)は`CP_TREATMENT_RULE`(2026-10-23承認、narration行=2026-10-25案A)。ユーザー原文§2・§5に固有の確認観点を、チェックリストの各行に加え下記「追加観点」として記入する(新Gateではない=CP担当[Fable/Sonnet記入→Fable確認]の目視)。

追加観点(各stage本文を逐語引用して記入): (a)7証言(または省略時はどれを省いたか)が原作順にあり、当事者3証言が全て「自分が(死因を)担った」と語る (b)3証言の食い違い(多襄丸=太刀の決闘/真砂=小刀で自分が刺した/武弘=自害+見えない手)が残り、本文が真相を決めつけない (c)各証言者が聞き分けられる(speech tagが話者名、証言者ごとの関心・口調が違う) (d)語り手(narrator)が紹介以上の判断をしていない(誰が本当かを言わない) (e)性的暴行が非グラフィックな1句か (f)Preview/Commentが後の証言内容を先取りしない・解釈を断定しない (g)最終文が死霊の最後の言葉で終わり、評決・説明・教訓・追加文がない。

<!-- ここから機械生成 -->
# Fable CPチェックリスト(機械生成: in_a_grove、essentials sha a931dbcde7fe)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23。narrationを(A)へ追加=案A承認2026-10-25の§1語り口維持・§6 PRODUCTION_WIRED条件との整合): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffs・narration(人称・視点・語り手の立場の変更)のいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | The last testimony, spoken by the dead man's spirit through a medium, says that after the bandit left and his wife fled, he rose from the cedar, took up the small dagger she had dropped and stabbed himself in the chest; the thicket fell silent, then someone crept up to him and an unseen hand quietly drew the dagger out of his chest, and he sank for ever into the darkness. The story ends on that last scene, with no verdict, no word on which of the three accounts is true, and no explanation of who the unseen person was or what really happened. [原作最終文: おれはそれぎり永久に、中有の闇へ沈んでしまった。] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the last testimony, do not say or hint what the dead man will tell (that he stabbed himself, or that an unseen hand drew the dagger from his chest), and do not preview, in the introductions or anywhere else, what any later testimony will say; never tell the listener who the real killer is or which account is true, never say that the accounts will be settled or explained, and never add a verdict, a solution, a moral or a comment. |  |  |  |  |  |
| 3 | 重大 | key_role keep_name=Tajomaru(名前が維持され他人名が増えていない) | the famous bandit, caught by the constable, who confesses with pride that he killed the man in a fair sword fight |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Masago(名前が維持され他人名が増えていない) | the wife, who says in her account at the temple that she herself stabbed her helpless husband with the dagger |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Takehiro(名前が維持され他人名が増えていない) | the dead husband, a samurai, whose spirit speaks through a medium and says he killed himself with the dagger |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the woodcutter who found the body, a brief outside witness |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | the traveling monk who met the couple the day before, a brief outside witness |  |  |  |  |  |
| 8 | 重大 | key_role(役割・関係で表され名前が付いていない) | the constable who caught the bandit and blames him |  |  |  |  |  |
| 9 | 重大 | key_role(役割・関係で表され名前が付いていない) | the old woman, Masago's mother, who begs the magistrate to find her daughter |  |  |  |  |  |
| 10 | 重大 | key_causality | One man is found dead in a thicket, and seven people speak about it in turn: four outsiders set the scene (no sword found, only a rope and a comb; the man had been travelling with his wife; the bandit Tajomaru was caught with his bow; the wife is missing), and then each of the three people who were there claims the death for himself or herself, for reasons that fit their own pride, shame or bitterness: Tajomaru says he killed the husband fairly after the wife begged one of the two men to die, Masago says she stabbed her helpless husband because of the cold contempt in his eyes, and Takehiro says he killed himself after his wife asked the bandit to kill him; the accounts clash on who did what, and no one, in or out of the story, resolves the clash. |  |  |  |  |  |
| 11 | 重大 | narration(人称・語り手の立場が各stageで保たれている) | The story has no narrator of its own: it is a series of spoken testimonies, each told in the first person ('I') by the person who gives it, in that person's own voice and self-interest; a short, neutral outside narrator may only say who is speaking (for example 'The woodcutter was questioned first.'), never judges, comments or says which account is true, and is never the one who knows what happened; the police magistrate who questions the witnesses stays silent, and the dead man speaks through a medium but in his own first-person voice. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数0、語数0)
- 最終段落: 

### r1(段落数0、語数0)
- 最終段落: 

### r2(段落数0、語数0)
- 最終段落: 

### std_adjust(段落数0、語数0)
- 最終段落:
<!-- ここまで機械生成 -->

## §D Seed承認の事前確認(dry run、API 0・書込0)
`stage_seed_check(ctx)`をtempdirのseed置き場(`seed.json`+`primary_text_excerpt.md`[story.md複製]+`SEED_PROVENANCE.json`)で実行(`E2E_RUN_ROOT`をtempdirへ差替え。コード変更なし、実Productionの置き場には触れない)。結果:
- `source_essentials`: present=true, exempt=false, **items=5**, keep_names=[Tajomaru, Masago, Takehiro], **source_quote_checked_vs_last_paragraph=true**, essentials_sha256=`a931dbcde7fe02202741a055db148d1d40b868d006c8f2bc5ef7c66877f091d3`(seed内容修正のたび変わる。次委任では`seed_check`の出力で再確認)
- routing_models: Writer r0/r1/r2/std_adjust=`gpt-6.1-sol`、story_split/dialogue_attribution=`gpt-6-luna`。style_table 11キー整合、er020 full_story clip pattern=true。
- dialogue_voices: narrator=Aoede / woodcutter=Algieba / monk=Schedar / constable=Fenrir / old_woman=Zephyr / tajomaru=Orus / masago=Kore / takehiro=Puck。
- fail-closed: Seedから`source_essentials`を除くと`FamilyZSeedEssentialsStop`(FAMILY_Z_SEED_ESSENTIALS_MISSING)。上限(setups_and_payoffs 1件追加で6件)・source_quote誤りでも同Stop(登録testで固定)。
- 再現: `.venv/Scripts/python.exe docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/seed_check_dryrun_01.py <出力md>`(出力=`SEED_CHECK_DRYRUN_01.txt`、rc=0、API 0・書込はtempdirと出力mdのみ)。登録test `er026_family_z_story_registry_in_a_grove_test_01.py`(27 tests)。

## §E Fable CP用の照合点
1. **source_quote vs 原作最終段**: Seed `source_essentials.ending_reveal.source_quote`=「おれはそれぎり永久に、中有の闇へ沈んでしまった。」。原作最終段落(SOURCE_CHECK_01 §4)の最終文に逐語一致(testで`paras[-2].endswith(q+"………")`を検査、`validate_source_essentials`が`primary_text_excerpt.md`最終段落への包含を検査)。**意味の妥当性(meaning文と原作最終段)はFableが照合**: meaningは「死霊が小刀で自分の胸を刺す→誰かが忍び寄り見えない手が小刀を抜く→永久の闇へ沈む。評決なし・3証言のどれが本当かを言わず、誰が抜いたかの説明なし」。
2. **真相を一本化していないか**: ending_reveal.meaning/withhold_until_end/key_causality/conversion_planの文言(「no verdict」「never tell the listener ... which account is true」「no one, in or out of the story, resolves the clash」「do not decide which one is true / do not call anyone a liar」)をFableが読む(testで文字列を固定済み)。
3. **essentials 5件の構成(判断B=承認範囲内で自己解決、Fable確認)**: 上限5件に対し、事件当事者3名のkeep_name(Tajomaru・Masago・Takehiro)を優先し`setups_and_payoffs`を0件にした。理由: (i)結末(見えない手が小刀を抜く)は先行setupが無くても成立する (ii)3名は3証言の語り手そのもの(中心人物=現行固有名詞ルール(b)) (iii)代替案(keep_nameを2名[Tajomaru・Masago]に減らしsetup「現場に太刀も小刀も無く縄と櫛だけ→死霊の語りで小刀が抜かれる」を1件入れる)は、短編化で最も削られやすい細部を守る一方、Takehiroを役割名(the husband/the samurai)にする。**Fableが代替案を望む場合はSeed再編のみ(data)**。
4. **視点設計の確認(判断B)**: `narration_voice`=「語り手なしの証言集。短い中立のnarratorは話者の紹介のみ、各証言は当該証言者の一人称」。narrator(Aoede)枠=紹介のみ、各証言=speech tagで話者名を付けた引用(同一証言内の長い独白は複数quoteに分かれ得る)、検非違使の質問は書かない(質問は答えから暗示)。万一Writerが検非違使の質問を台詞化した場合の話者はnarrator枠(attr_roster_text明記)。**この設計(新Voice不要・新Gate不要)がFable意図に沿うか確認**。
5. **STORY_MAIN_CHARACTER="Tajomaru"**: 単一の主人公はいないため、名前可の枠(REVISE prompt「only <値> and the people marked keep the name ...」)に3名を入れる目的の名目値。Writer R0のPromptには主人公名は入らない(「main character」一般語+keep_name表)。
6. **Comment/Preview lint**(`STORY_LINT_CONFIG["in_a_grove"]`、既存機構のdata値): spoiler_ja/en=死霊の最後の証言(自害・見えない手・小刀を抜く)と真相断定(真犯人・the real killer・the truth is等)に限定。「どれが本当か分からない」型の記述と、多襄丸・真砂の語りの内容自体(後半Commentで既に聞いた部分)は禁止しない(『猿の手』起動3の教訓)。ユーザー原文§5「後から明らかになる証言内容を先取りしない」の最終防衛はPrompt側(Seed withhold)+本lint+CP目視。
7. **既存仕様の未変更**: Prompt本文・正規表現・閾値・辞書の直接編集0、新flag 0、Gate/Validator追加0、`ESSENTIALS_EXEMPT_STORIES==("melos",)`のまま。

## §F 事前チェック(import graph未commit差分、HEAD=`01c949d33`、2026-10-28 21:26 JST)
- Z runnerのimport graphに含まれる`er019_family_x_audio_production_runner_01.py`(`er026...runner.py:1277`の費用読み取り、`er063_family_z_audio_01.py:1127`のKP英語解説TTS)が**他workerのX Std Comment3委任で未commit変更(` M`)**。本委任の変更ではない。**委任_02の起動条件「graph内の.pyがcommit済みでHEADと一致」を満たすには、このX側差分がcommitされるまで待つ(またはFableが可否判断)**。併せて`er019_family_x_audio_plan_01.py`(M)も同worker。
- 本委任の変更(3 py: runner/structure/writer、いずれもdata表追加)は本commitで解消。無関係な未追跡.py(`er003_v1_p2*`、`er008_n8_*`、`er009_*`等)はZ graph外(静的import/文字列参照なし)。

## §G テスト結果(2026-10-28、API 0)
- 登録test `er026_family_z_story_registry_in_a_grove_test_01.py`: **27 tests OK**。
- 関連回帰(`er062*test*.py er026*test*.py er063*test*.py` 25ファイル): **640 tests、errors=1、skipped=2**。唯一のerror=`er063_family_z_audio_01_test_01.WiringTest.test_preview_comment_kp_styles`(`m.call_args`がNone=kp_en生成経路のmock不発)。**本委任の変更が原因ではない**: (i)HEADの清潔なworktreeで同testはOK (ii)HEAD+本委任の3ファイル差分+Seed(同worktree)でも同testはOK (iii)共有作業ツリーでのみ失敗=他workerの未commit変更(`er019_family_x_*`のX Std Comment3委任。kp_en経路が`er019_family_x_audio_production_runner_01`をimport)が原因と推定。§F参照。
