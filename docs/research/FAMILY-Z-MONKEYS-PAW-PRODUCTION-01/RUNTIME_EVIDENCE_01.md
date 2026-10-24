# RUNTIME_EVIDENCE_01 (FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01〜03、2026-10-24) 【完成: 委任_03で当該1clip再生成→Gate PASS→完成段・公開page_verify PASS】

run dir: `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/`。実行は `.venv/Scripts/python.exe`、`TTS_EXECUTION_MODE=STANDARD`、Production経路のCLI。各起動前に `tools/stop_scope_check_01.py --managed-id FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 --run-dir <run>` rc=0(`_stop_scope_check_*.json`)。HEAD(着手時)=00815e4d8。

## 起動履歴(run_launch_log.jsonl)
| # | JST(2026-10-24) | stages | 結果 |
|---|---|---|---|
| 1 | 17:54:40 | seed_check,writer,std_adjust | OK 19.37円(Adv r0/r1/r2 + Std、Adv 434語/Std 443語、段落32/32) |
| 2 | 17:59:15 | plan,support | **plan STOP**: `DIALOGUE_ATTRIBUTION_MISMATCH(a2): q24_1`(`"It's Herbert!"`: 決定論=mr_white[窓内にMr. Whiteが'caught her arm'で出る]、LLM=mrs_white[正]) |
| 3 | 18:01:20 | plan,support | **support STOP**: `SUPPORT_LINT_FAILED`(retry 1回NG): Comment3候補が`died`/`second wish`でSPOILER判定 |
| 4 | 18:04:25 | plan,support | OK(+0.86円、累計20.23円)。plan mismatch 0、support lint_warn=LISTEN_INSTRUCTION(Std日本語、WARNのみ・既存仕様) |
| 5 | 18:06:13 | kp | **RESTART_STORM STOP**(300秒に3起動[18:01:20,18:04:25,18:06:13=293秒]。`<run>/STOP`を自行発動。APIは呼んでいない) |

### 原因と是正(起動2・3は自分起因のdata誤り。起動5は自分の起動間隔の見誤り)
- 起動2: 決定論話者判定の窓キーワードに人名単体(`mr. white`,`herbert`等)を入れたため、`"It's Herbert!" She ran...pulling free when Mr. White caught her arm.`で誤判定(mismatch)。是正=キーワードを会話タグ型(`said mr. white`,`mrs. white asked`等、動詞×主語の組合せ)に変更(`STORY_SPEAKER_CONFIG[...]["z_voice_keywords"]/["dialogue_voice_keywords"]`と runner `voice_keywords`、いずれも本作entryのdata表のみ)。LLM判定は不変(LLMがtruth、決定論はクロスチェック)。
- 起動3: `STORY_LINT_CONFIG["the_monkeys_paw"]`のspoiler語が過広(`died`,`second wish`等)でCommentに出る『すでに聞いた部分』の事実をNG判定。Commentの設計(Comment2/3は聞いた部分を踏まえる、run_support_*)に合わせ、先回りを禁じる語を結末(第三の最後の願い・戻ってきたもの・無人の道・種明かし語)に限定。承認済みのlint機構は無変更、本作entryの値のみ。
- 起動5: 起動2〜4の間隔が短く、3起動が300秒窓(293秒)に入り`FAMILY_Z_RESTART_STORM`を発動。**`<run>/STOP`は自分で削除・`--clear-stop`していない**(解除はFable/ユーザーのみ)。

## Voice配役(`voice_assignment.json`、pinなし・決定的割当規則)
narrator=Aoede / 軍曹(morris)=Algieba / Mr. White=Schedar / Herbert=Fenrir / 使者(visitor)=Orus / Mrs. White=Zephyr / Adv補助=Charon。登場順はAdv/Std両本文の初出順(CP_CHECK_01.md §A#2)。Rosterは原作の発話者のみ。当初rosterは原作順(Mr. Whiteが1番)で登録し、Writer出力の初出順確認後にplan前に『初出順』へ訂正(data表の順序のみ、plan前のため音声への影響なし)。

## 構成・語数
Adv r2 434語・32段落、Std 443語・32段落(330-470内)。Std/Adv段落数一致。

## 費用(実績、cost_log.jsonl)
途中累計 **20.23円**(plan/support時点。最終累計は末尾『費用(最終)』): seed_check 0 + Writer(r0/r1/r2/std_adjust)19.37 + plan/support 0.86。plan/support再実行分(起動2・3)の追加費用は約0.4円。

## モデル
Writer=`gpt-6.1-sol`、plan/support/kp=`gpt-6-luna`(最新世代、本番ライン既定)。TTSは未実行。

## 登録test・全回帰
- 登録test `er026_family_z_story_registry_monkeys_paw_test_01.py` 22 tests OK。既存 `..._after_twenty_years_test_01`(21)・`..._gift_of_the_magi_test_01`(22) OK。
- 全回帰 `run_project_regression.py`(既定pattern): collected=7102 passed=7091 failed=1 skipped=10。failed 1件=`er064_kp_int_01_test_01.ProductionUnchanged.test_no_tracked_py_or_template_modified`(`REGRESSION_BASELINE_2026-10-24.md`既知の『未commitのtracked .py変更があると必ず失敗』。未commit tracked .pyは本作の3 .py[commit後に解消]+Family Yの`er110_family_y_opinion_based_03.py`・`build_theme_data_02.py`等、実行時)。`er003_test_bad`のFAILはrunner自身の意図的fixture出力(失敗に数えない)。他の失敗0。


## RESTART_STORM自己発動(事故記録、PM_GOVERNANCE 26節)
- 経緯: 起動3(18:01:20)・起動4(18:04:25)・起動5(18:06:13)が293秒に入り、runner が `<run>/STOP`+`RESTART_STORM_LOCK.json` を作成(audit_stop_sentinel.jsonl 18:06:13.96)。起動5(kp)はAPI呼出前に停止。
- 原因: 実行層(Sonnet)が data 誤り(起動2・3)を1つずつ直しては再起動し、起動間隔を見誤った。暴走・監視ループ・自動再起動ではない。
- 影響: 起動3・4は plan/support の小LLM呼出あり(合計約0.4〜0.9円、cost_log.jsonl に記録済み・累計20.23円に含む)。起動5はAPI 0。音声・公開物・副作用なし。(委任_02冒頭の「API呼出なし」は起動5のみ正確)
- 解除: Fable が 2026-10-24 に明示許可。`--clear-stop --reason "FABLE_RELEASE ..."` で STOP と LOCK を runner 経由で除去(18:11頃、手動削除なし)。
- 再発防止: データ修正は起動前にまとめて行い、同一runの起動は最低150秒空ける。

## 委任_02 実行記録(2026-10-24 JST)
| 起動 | 開始 | stage | 結果 | 累計費用 |
|---|---|---|---|---|
| 6 | 18:12:15 | kp | OK | 21.64円 |
| 7 | 18:15:05 | tts_b1b | OK(HR 0、固有名詞アラーム0) | 33.41円 |
| 8 | 18:20:29 | tts_a2 | OK(HR 0、固有名詞アラーム0) | 46.65円 |
| 9 | 18:36:12 | provision_shell,gate,assemble,pages,page_verify | **gate で FamilyZSlowdownGateStop**(rc=2) | 46.65円 |

### Gate停止の内容(速度仕様v2 verify_z_speed_profile、er063_family_z_audio_01.py:1589)
- 対象: Adv(b1b) `full_story_part3_c5`(会話、原音0.771秒)。wav/original長さ比=0.9670(許容0.93〜0.96)。他の会話16clipは全て範囲内(次点0.9588[0.961秒clip]、0.9528[1.37秒])。
- 推定原因: atempo=1.06(WSOLA)の約19msの固定誤差が0.77秒の極短clipで比率に大きく出る(期待0.9434→実測0.9670)。Gate/しきい値は変更していない(承認済み仕様)。
- 状態: STOP/LOCK sentinel は作成されていない。gate以降(assemble/pages/page_verify)は未実行、公開物なし。Fable判断待ち。

## 委任_03 実行記録(速度仕様v2 Gate停止 -> Fable許可の1clip再生成 -> 完成)
- Fable判断: 該当1 clipの再生成を**1回だけ許可**(Gate緩和・仕様変更なし)。起動前確認: `stop_scope_check_01.py --managed-id FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 --run-dir <run>` rc=0(`_stop_scope_check_regen.json`/`_fin2.json`)、`git status`でZ経路import graphのtracked .py変更なし(未追跡の無関係.pyのみ)、STOP/LOCK sentinelなし。起動間隔: 18:36:14(旧完成段)->18:39:46(再生成)->18:42:33(完成段)、いずれも150秒以上。
- 再生成方法(既存のresume/`--only-clips`機構、コード変更0): 既存の再利用判定(`generate_or_reuse_z`)は『cached entryがOKかつwav実在かつsha一致』で再利用するため、`--only-clips`のみでは再生成されない。該当clipの `full_story_part3_c5.wav` と `_original.wav` を `<run>/_regen_backup_part3_c5_20261024/` へ退避(旧`tts_generation_results.json`も同所にcopy)して実体を無くし、`--stages tts_b1b --only-clips full_story_part3_c5` を**1起動**(18:39:46、rc=0、約9秒、`console_t8_regen_c5.txt`)。他clipは `_store` でcached entryをそのまま維持(再生成0)。
- **再生成されたclip=1件**(`full_story_part3_c5`のみ。cost_log: TTS 1呼出[gemini-2.5-pro-preview-tts]+ASR 2呼出[gpt-4o-mini-transcribe]、`tts_generations_used`=1相当)。費用=0.164円(46.653->46.8174円)。
- 結果: 旧テイク 原音0.771秒/比0.9670(Gate停止) -> **新テイク 原音1.051秒/処理後1.002秒/比0.9534(範囲0.93〜0.96内)**、ASR=`Wait!`(OK)。tempo=1.06 applied、HR 0。Gate・しきい値は無変更。(新テイクの原音が長くなったことで通過。極短clipの比の感度は構造的な問題でありOPEN-496/`OPEN496_ANALYSIS_01.md`に整理)
- 完成段(18:42:33、`provision_shell,gate,assemble,pages,page_verify`を**1起動**、rc=0、`console_t9_finalize2.txt`): provision_shell 1.0秒 / gate 0.6秒(Adv/Std shared_gate=PASS) / assemble 1.7秒 / pages 10.5秒 / page_verify(local) 157秒。再起動0回(各stage 1起動、再生成後の追加起動なし)。
- 公開: commit 8cf1f7726(pages+run証跡を push)、GitHub Pages反映後 JST 18:50:17-18:53:48 に公開page_verifyを実施。

## HEAD・モデル
着手時HEAD=00815e4d8(委任_01)、委任_03公開時HEAD=cd829a290->8cf1f7726。モデル: Writer(r0/r1/r2/std_adjust)=`gpt-6.1-sol`、plan/support/kp/kp gloss alignment/RET NER=`gpt-6-luna`、TTS=`gemini-3.8-flash-lite-tts`(地の文・KP・案内)+`gemini-2.5-pro-preview-tts`(会話台詞clip=Z既定)、ASR=`gpt-4o-mini-transcribe`、二次ASR=`azure-speech-stt`。いずれも最新世代/本番ライン既定。

## Voice(最終、`voice_assignment.json`)
narrator=Aoede / 軍曹=Algieba / Mr. White=Schedar / Herbert=Fenrir / 使者=Orus / Mrs. White=Zephyr / Adv補助=Charon。clip数(story): Adv narrator17・Algieba5・Schedar5・Fenrir1・Orus3・Zephyr3 = 34、Std narrator15・Algieba4・Schedar5・Fenrir1・Orus2・Zephyr3 = 30。

## 構成・再生時間
- Adv(b1b): 3part(story clip 16/12/6=34、ASR語数 154/120/155=36%/28%/36%)、通し **291.23秒**(`MonkeysPaw_b1b_full.mp3`)。本文434語。
- Std(a2): 3part(story clip 14/10/6=30、ASR語数 155/132/149=36%/30%/34%)、通し **301.85秒**(`MonkeysPaw_a2_full.mp3`)。本文443語。段落32/32一致。

## ASR/TTS/retry/fallback/HR
- Adv(b1b、52 segment、全OK): attempt>1は`full_story_part3_c1`(`I wish Herbert alive again.`、attempt1 ASR=`were alive`でUNCERTAIN -> attempt2 NORMALIZED_MATCH採用)の1件。fallback 0、local rewrite 0、HR 0、固有名詞アラーム 0。pass理由: primary_pass 41、dual_agreed 3(KP)、secondary_confirmed 1(comment_3)、その他(非ASR clip/KP日本語)。TTS呼出 flash-lite 28 + pro 19(再生成1を含む)、Azure二次ASR 5。
- Std(a2、49 segment、全OK): attempt>1は`full_story_part1_c10`の1件=**Local Rewrite発火**(下記)。HR 0、固有名詞アラーム 0。pass理由: primary_pass 32、`primary_pass_approved_equivalence:READING_MATCH` 6(日本語clipの同音)、dual_agreed 3、secondary_confirmed 1。TTS呼出 flash-lite 30 + pro 15、Azure二次ASR 8。
- **Local Rewrite(Std `full_story_part1_c10`、audio_text_deviation 1件)**: 原稿 `After their guest left` をASRが3回(standard 2 + minimal fallback 1)とも `guests` と転写(=TTSが複数形風に発音)。minimal fallback採択時のLocal Rewriteで音声側の語を `guest`->`visitor` に置換して採択(`asr_text`=`After their visitor left`)。意味は同じ。**ページのスクリプト表示は原稿のまま `guest`(音声は `visitor`)**。provenance.audio_text_deviationsに記録(canonicalは原稿のまま)。2026-10-12ユーザー決定の既存仕様(再検証フック撤去・監査記録のみ)に従った正規動作。耳確認候補(音声とスクリプトの差1語)。
  - 前版の本書は『Std HR 0・TTS OK』のみ記載で、このLocal Rewriteを書いていなかった。今回の完成物集計で判明したため追記。
- approved equivalence: Std `READING_MATCH` 6件(日本語clipの同音: preview、comment_1、comment_3、KP日本語3件。例: KP1 `曹長`->ASR`総長`[そうちょう])。Adv approved equivalence 0。数詞/時刻の equivalence 0(本文に該当なし)。
- RET: 実体表 `audit/entity_table.json`(person/confirmed 1、person/weak 2、place/weak 1[India]、work_title/weak 1。証拠として使用可1件、`Mr. White`/`Mrs. White`/`The Monkey's Paw`/`India`は証拠にならない[weak])。Perplexity発音調査 0。PNAP/UKUS=発火なし(供給対象なし)。固有名詞アラーム 0。
- speed v2: Adv narrator none/dialogue fast6(会話17clip、比0.946〜0.9588)、Std narrator slow6/dialogue none。

## PASS_WITH_WARNING(耳確認候補) 計2件 + Local Rewrite 1件
- Adv `comment_3`('Mr. **White feared** what might return...' 一次ASR=`Mr. Whitebeard`、二次azure=`Mr. White feared`で`SECONDARY_CONFIRMED`)
- Std `full_story_part1_c14`('The **paw** twisted in his hand...' 一次ASR=`pot`、二次azure=`paw`で`SECONDARY_CONFIRMED`)
- (上記Local Rewrite) Std `full_story_part1_c10` 音声=`visitor` / スクリプト=`guest`

## Gate
`gate_result_04C.json`: Adv/Std とも `shared_gate=PASS`、`m2_complete=True`、`kp_vote_audit` checked 3 / blocking=false / missing_vote_evidence []、`article_text_source=canonical`。

## KP(現行Production: A-1+課題②、課題①X2p'等の未承認案は不適用・gloss整合flagは既定ON)
Adv: `interferes with fate`(運命に干渉する)/`in compensation`(補償として)/`wail of loss`(失った悲しみの叫び)。Std: `sergeant-major`(曹長)/`took hold of`(～をつかむ)/`rose into the night`(夜の中へと響き渡る)。gloss整合 ALIGNED 6/6、source gate PASS(3/3)、possessive repair=NO_POSSESSIVE。`[GLOSS-ALIGN] 実効flag=ON (source=default)`。

## 題名の確認
ページ(`<title>猿の手 試聴(Standard / Advanced)`・`猿の手 Advanced 試聴`)、音声ファイル名(`MonkeysPaw_*_full.mp3`)、KP(英題はSTORY_REGISTRYの`The Monkey's Paw`)、SSOT(`STORY_REGISTRY["the_monkeys_paw"]`)とも『猿の手 / The Monkey's Paw』。Writerが付けた本文題 "The Last Wish" は表示題に使われない(CP_CHECK_01.md §B)。

## 試聴ページ・検査
`user_test/family_z_monkeys_paw_01/`(index/standard/advanced、Std/Adv切替、通し・パート別再生、全スクリプト、KP2列、開発者向け情報なし)。
- local page_verify(`page_verify_local.json`): index audio35 / standard 50 / advanced 53 全再生OK、http>=400 0、console error 0、file://なし、A2/B1ラベルなし(localの簡易serverはRange非対応のためseek_ok_all=false、公開側で再検証)。
- **公開page_verify**(`er026_fz_play_verify_17.py`、Playwright実再生、JST 18:50-18:53、証跡=`page_verify_public.json`/`console_t10_public_verify.txt`): URL=https://shimomura055.github.io/eigo-radio/user_test/family_z_monkeys_paw_01/index.html 。index audio35 / standard 50 / advanced 53 すべて plays_ok(plays_failed 0)、seek_ok_all=True(3ページ)、http>=400 0、console error 0、file://なし、level label漏れなし、KP表 index6/standard3/advanced3、通し長 Std 301.85秒/Adv 291.23秒。

## 費用(最終、`cost_log.jsonl` / `e2e_stage_log.jsonl`)
累計 **46.82円**(上限100円・目標70円内): Writer(r0/r1/r2/std_adjust)19.37 + plan/support 0.86 + kp 1.41 + tts_b1b(Adv)11.78 + tts_a2(Std)13.24 + c5再生成0.16 = 46.82円。(RESTART_STORM事故による追加費用は約0.4円で上記plan/supportに含む。)再生成1clipは0.16円。
所要時間: 制作各段の実行 Writer 108+110秒、plan/support 約1分、kp 112秒、TTS Adv 315秒・Std 930秒、再生成9秒、完成段(page_verify local含む)約3分、公開page_verify 約3.5分。制作run全体は JST 17:54〜18:54 の約1時間(RESTART_STORM事故の停止待ち・Fable判断待ちを含む。作品登録・原作取得・Seed・test・全回帰は別途)。

## 経路・Production境界
正式Production CLI(`er026_family_z_fiction_production_runner_01.py`)のみ。未承認機能のflag変更なし(`EIGO_KP_GLOSS_ALIGNMENT`既定ON=既存Production既定)。DEV/Trial経路の混入なし。Gate・しきい値・コード(.py)の変更0(登録時のdata表追加[commit 33565584a]を除く)。再生成は既存の`--only-clips`機構とwav退避のみ。
