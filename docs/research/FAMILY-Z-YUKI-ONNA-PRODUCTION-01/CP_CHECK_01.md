# Fable CPチェックリスト(機械生成: yuki_onna、essentials sha 9c77e83ab1cd)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23。narrationを(A)へ追加=案A承認2026-10-25の§1語り口維持・§6 PRODUCTION_WIRED条件との整合): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffs・narration(人称・視点・語り手の立場の変更)のいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | Years after the night in the hut, Minokichi breaks his promise: by the lamp he tells his wife Yuki the whole story of the woman in white, saying she looked very like her. Yuki then reveals that she was that woman, repeats that she told him she would kill him if he ever said a word, and says that only the sleeping children keep her from killing him now; she orders him to take very good care of them. Her voice thins like wind, she melts into white mist and slips away through the smoke-hole, and she is never seen again. She spares him a second time (the first time because he was young, now for the children) but leaves forever. [原作最終文: Never again was she seen.] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the last scene, do not say or hint outright that Yuki is the woman in white and do not tell the listener that Minokichi will break his promise or that Yuki will leave; do not explain the ending, add a moral, or comment on it. The original's quiet clues (her white skin, her fair children, her never growing old) may appear as plain facts without comment. |  |  |  |  |  |
| 3 | 重大 | setup と payoff | In the hut the woman in white spares young Minokichi on one condition: if he ever tells anybody, even his own mother, what he saw this night, she will know it and kill him; afterwards he keeps silent, even about the old man's death  ->  Years later he tells his wife, Yuki, the whole story; she reveals she is that woman, repeats the condition he broke, and spares him only because of the children before she melts away |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Minokichi(名前が維持され他人名が増えていない) | the young woodcutter, eighteen at the start, who is spared in the hut on the condition of silence, later marries Yuki and breaks the promise |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Yuki(名前が維持され他人名が増えていない) | the beautiful girl who joins Minokichi's family, becomes his wife and the mother of his ten children, and is revealed to be the woman in white (the same speaker as the woman in the hut) |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the old woodcutter, Minokichi's master, who is frozen to death in the hut (no spoken lines, no name) |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | Minokichi's widowed mother, who welcomes Yuki and persuades her to stay (no spoken lines, no name) |  |  |  |  |  |
| 8 | 重大 | key_causality | A snowstorm drives the old and the young woodcutter into a hut; a woman in white kills the old man with her breath but spares the young man, because he is young, on the condition that he never tells anybody what he saw; he keeps silent. The next winter a girl called Yuki joins his household and becomes his wife, and they have ten children. Years later, by the lamp, he tells her the story of the hut and says she looks like the woman; she reveals that she was that woman, tells him he has broken the condition and that only the children save him, and melts into mist, never seen again. |  |  |  |  |  |
| 9 | 重大 | narration(人称・語り手の立場が各stageで保たれている) | A calm storyteller in the third person and the past tense (no 'I'), telling an old Japanese ghost story to a listener; the storyteller plainly says when and where each scene happens and who is speaking, keeps a quiet eerie tone, and never explains the ending. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数0、語数0)
- 最終段落: 

### r1(段落数0、語数0)
- 最終段落: 

### r2(段落数0、語数0)
- 最終段落: 

### std_adjust(段落数0、語数0)
- 最終段落: 


## §B 委任_02以降の起動コマンド列案(藪の中 CP_CHECK_01 §Bと同形式。実行は`.venv/Scripts/python.exe`、環境`TTS_EXECUTION_MODE=STANDARD`)
共通引数: `er026_family_z_fiction_production_runner_01.py --story yuki_onna --run run_yo_prod_01 --mode real --approved-budget-jpy <Cap> --tts-execution-mode STANDARD --stages <段>`(Capは案件¥150内。起動引数は1起動ごとの上限で、E2E_APPROVED_BUDGET_MAX_JPY=300以下)。**各起動の直前に** `.venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-YUKI-ONNA-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --out <scratch json>`(rc=3なら新規API呼出をせず停止報告)。
**初回起動前に1回だけ**: Production seed置き場 `er026_output/family_z_production_e2e_01/yuki_onna/seed/` を作成(`seed.json`と`primary_text_excerpt.md`[=`er026_seeds/yuki_onna/story.md`の複製]をsha付き`SEED_PROVENANCE.json`で凍結。形式は`seed_check_dryrun_01.py`と同じ)。Fable Seed CP(SEED_CHECK_DRYRUN_01.txt・本checklist)後に作成する。

| # | `--stages` | 想定 | 備考 |
|---|---|---|---|
| 02-a | `seed_check,writer,std_adjust,plan` | 約4〜6分、約¥15〜20 | **本文確認の停止点**。終了後に原作忠実性CP(上表)とPLAN_REVIEW_01 §3の5項目を本文で再点検(Part境界=3場面、場面頭の時・場所の1文、台詞比率、話者判定、約束の3回提示)。問題があればWriter再生成(明示--regenerate-stage)はFable判断 |
| 02-b | `support,kp` | 約3〜5分、約¥3〜5 | 150秒以上空ける。lint(spoiler=正体・結末)・KP |
| 02-c | `tts_b1b` | 約6〜10分、約¥8〜12 | TTSは直列 |
| 02-d | `tts_a2` | 約6〜10分、約¥8〜12 | 同上 |
| 02-e | `provision_shell,gate,assemble,pages,page_verify`(**1起動**) | 約2〜5分、API 0 | provision_shell欠落でRESTART_STORM(OPEN-480) |
- 見込み合計 約¥40〜55(藪の中¥136.6の約1/3。台詞clip少、再生成リスク低)。案件Cap¥150内。起動間隔は300秒窓内≤2・各起動≥150秒、HR Lock/STOP時は即停止してFableへ。
- 02-a後にFableが本文を確認してから02-b以降へ進める運用を推奨(TTS前に作品適性を本文で確認でき、不適合時の損失をWriter分約¥15-20に限定できる)。
