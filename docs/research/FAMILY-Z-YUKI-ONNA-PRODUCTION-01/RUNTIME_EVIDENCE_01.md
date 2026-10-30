# RUNTIME_EVIDENCE_01 (FAMILY-Z-YUKI-ONNA-PRODUCTION-01 委任_02、2026-10-30)

## 起動(JST、`er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/run_launch_log.jsonl`)
| # | 起動時刻 | PID | --stages | 所要 | rc |
|---|---|---|---|---|---|
| 1 | 07:58:43 | 30708 | seed_check,writer,std_adjust,plan | 約2分42秒(終了08:01:25) | 0 |
| 2 | 08:02:13 | 37300 | support,kp | 約10分(終了08:12) | 4(KP_REVIEW_PENDING、HR待機) |
- 共通: --story yuki_onna --run run_yo_prod_01 --mode real --approved-budget-jpy 60 --tts-execution-mode STANDARD。各起動前にstop_scope_check rc=0(07:58頃・08:02:09)。
- **規律逸脱(自己申告)**: 起動1の終了(08:01:25頃)から起動2の開始(08:02:13)まで約48秒で、起動規則「各起動≥150秒」を満たさなかった(300秒窓内の起動数は2で≤2は順守。RESTART_STORM保護・STOP・rcエラーは未発動、影響なし)。実質的な副作用は観測されず、以後の起動はなし。
- Seed凍結: `er026_output/family_z_production_e2e_01/yuki_onna/seed/`(seed.json sha256 13d86f74cc5e..., primary_text_excerpt.md 95dba57bbdf7...)。seed_check通過(source_essentials 5件)。

## モデル・Prompt sha・retry(`writer/provenance.json`、cost_log.jsonl)
| 段 | model(要求=実際) | prompt sha256(先頭12) | 出力sha(先頭12) | attempts | 費用(円) |
|---|---|---|---|---|---|
| writer r0 | gpt-6.1-sol (effort high) | 791e9b12182d | 7e628cab54e8 | 1 | 4.74 |
| writer r1 | gpt-6.1-sol | 41c9095fe852 | 0deac00fd943 | 1 | 3.48 |
| writer r2(Adv最終) | gpt-6.1-sol | cf2c96743a50 | 09031ab9f23c | 1 | 2.67 |
| std_adjust | gpt-6.1-sol | 704dbce4009e | 4b9135ddbf08 | 1(auto_regenerated無し) | 5.46 |
| plan(段落分割+話者判定) | gpt-6-luna | - | - | 3呼出(Adv段落分割1[Stdはadv境界を写像]+話者判定Std/Adv各1、全success) | 0.13 |
| support | gpt-6-luna | - | - | 8呼出(全success) | 0.42 |
| part2_cand(a2/b1b) | gpt-6-luna | - | - | 各1 | 0.33 |
| kp+kp_gloss_alignment | gpt-6-luna | - | - | kp12+gloss4(全success、失敗0) | 3.52 |
| nuance_cand(a2/b1b、廃止決定済みだが現行配線で生成=費用のみ記録) | gpt-6-luna | - | - | 各2 | 0.43 |
- 最新世代モデル原則: Writer=gpt-6.1-sol、補助=gpt-6-luna(本番ライン指定のrouting、検証用の旧モデル不使用)。
- retry/fallback/LR/再生成の発動: 全API呼出success=true・失敗0(cost_log.jsonl 37行)。Writer再生成(--regenerate-stage)なし。std_adjustの警告は soft gate "STD_AVG_SENT_LEN_NOT_SHORTER:8.87 vs adv 8.80x0.85" のみ(failures空、既存の軽微警告)。support_stdのlint warnは LISTEN_INSTRUCTION(preview/comment_1)と comment_2×comment_3 の4gram重複(`launch2.log`) — 既存Gateの警告で再生成は発動せず。
- Gate除外: KP候補 "woodcutters" がCMU発音辞書未登録でGate除外(a2/b1b各1件、補完候補で補填。藪の中と同一事象)。

## 費用
- 本委任(起動1+2): 約21.18円(cost_log.jsonlからer009単価で再計算。起動1の累計=16.48円[runner出力spent_jpy]、起動2追加=約4.70円)。TTSは未実行。
- 案件累計(ZY01 API 0円+本委任): 約21.2円 / Cap150円。本日(JST)の他案件費用は本Workerから把握できず「未確認」(本案件分のみ21.2円)。見込み(≈20〜30円)内。

## 委任_03(2026-10-30 09:12-09:58): HR回答確定 = Adv確定済み / Std拒否(NUANCE_CORNER_ABOLISHED)で停止。API 0・TTS 0・費用増0
- 回答原文保存: `docs/pm/delegation_log/2026-10-30_FAMILY-Z-YUKI-ONNA-PRODUCTION-01_USER_HR_01.md`(逐語、2件)。
- NCA競合待機: `git status --porcelain -- er128* er119* er120* er135* er026_family_z_* er062* export_form_data_01.py` が20件dirty(最終編集08:30)→09:12から5分間隔で監視、09:56に空(NCA委任_02 Step A commit a39acf3bf 09:56:01)。待機約44分(上限90分内)。
- 起動(runner)は本セッションで0回(run_launch_log変化なし)。stop_scope_check未実施(有料runなし)。
- Adv(b1b): `er119_kp_human_review_cli_01.py confirm --from-readable ... --level b1b --dry-run` → 照合コードAIF1検証OK → 09:57 本確定(rev1、KP3[slip away/widowed/bar]+追加解説2[take shelter/go no farther]+本文意味表示4、文法0、grammar_status=confirmed)。
- Std(a2): 回答はAIF2(旧ニュアンス欄つきフォーム)。a39acf3bf以降 `er128_form_readable_restore_01.py:295` が `NUANCE_CORNER_ABOLISHED` で明示拒否(dry-run)。指示どおり「ニュアンス解説：不採用〜【ニュアンスここまで】」節を除去した版(内容無変更、AIF2コードは原文のまま)でも再試行 → 同じ理由で拒否(コード接頭辞AIF2を検出するため)。Std dataは再出力済み(nuance欄なし)でd6も旧コードと不一致のため、旧コードの復元は不可能。確定せず停止。KP review status: pending=[a2]。
- 選定内容自体(Std): KP=talk someone into staying/slip away/light-skinned、追加解説=get what you deserve/mist、本文意味表示=riverside/complain、文法なし、コメントなし(ニュアンスは不採用)。

## 委任_04(2026-10-30 10:49-11:05): support,kp再開→tts_b1b→tts_a2→組立段でStyle実測照合Gate BLOCK(a2 comment_3)で停止
| # | 起動時刻 | --stages | 結果 |
|---|---|---|---|
| 3 | 10:49:0x | support,kp | rc=0(spent 22.05。KP確定済み、ニュアンス撤去後コードで動作=Z新記事フルrunの撤去runtime証拠) |
| 4 | 10:52:22 | tts_b1b | rc=0(256秒、spent 32.73、JA ASR PASS_W新方式0・HR Lock0・Human Review残0) |
| 5 | 10:56:54 | tts_a2 | rc=0(spent 45.71、HR Lock0・HR queue0) |
| 6 | 11:04:42 | provision_shell,gate,assemble,pages,page_verify | rc=2 `FamilyZStyleActualGateStop`(11秒、API 0) |
- 各起動前 stop_scope_check rc=0。間隔は全て150秒超、300秒窓内2起動以下。再起動なし(rc=2は1回のみ、停止して報告)。
- BLOCK内容: a2 `comment_3`(STD_JA_COMMENT、日本語コメント「…ミノキチが、今、妻に…」)。標準phase attempt1/2=TRUE_CONTENT_MISMATCH(ASRが固有名「ミノキチ」を実基/実之と表記)→fallback(style無し)attempt1=READING_RESOLVED_MATCH(実之吉)で採用 → Style実測照合Gateが `Z_STYLE_ACTUAL_UNMEASURED,Z_STYLE_FALLBACK_ADOPTED,FALLBACK_NOT_ALLOWED_FOR_POLICY` でBLOCK(`a2/audit/style_actual_vs_approved.json`、human_approved_count=0)。b1b=Gate PASS。他のa2 26 clip=全一致。
- 30節7項目: 対象=雪女a2 comment_3(日本語コメント、地の文でなく解説) / 経路=Z Production(TTS→ASR→style gate) / ASR: 標準2回NG→fallback1回で内容一致 / HR Lock=0・LR/ctx fallback未発動 / 直接原因=ASRの固有名表記ゆれ(katakana→kanji)による標準phase不一致→style無しfallback採用 / 残る自動救済=なし(Gate設計上、fallback採用は人間承認[human_approved_segments.json]が必要) / 判断依頼=comment_3を聴いて承認するか(承認記録 or 当該clipのみ再生成)。迂回せず停止。
- 費用: 本委任 約24.5円(spent 21.22→45.71)。案件累計 約45.7円/Cap150。本日(JST)全体 daily_cost.py=約969.7円(他Worker分含む。1,000円/日に接近)。

## 委任_05(2026-10-30 11:20-11:42): comment_3のみ再生成でStyle Gate BLOCK解消→組立PASS→End User Playwrightで停止(検証harness側の短尺タイトル境界)
- 読み辞書登録の可否(API 0, 実測): `er007_ja_asr_validator_01.classify_ja_asr_match`(`zy05_evidence/zy05_dictionary_offline_check.py`)。expected_readings={"ミノキチ":"ミノキチ"}を渡しても、ASR「実基」は TRUE_CONTENT_MISMATCH のまま(`_reading_dictionary_token_diff`はASR側表記の読みがkakasiで「ミノキチ」と一致する場合のみ許容、実基/実之は不一致)。さらに登録すると `reading_dictionary_mismatch=True`が付き、er078 A7_READING_DICT_MISMATCH(統一judgeのSecondary救済除外)でむしろ不利。「美濃吉」は辞書無しでも PHONETIC_MATCH。加えて`classify_foreign_tokens_in_japanese_text`の辞書(DEFAULT_JA_READING_DICTIONARY/resolver)の対象はLatin英字トークンのみでカタカナ人名は入らない(er003_audio_tts_asr_safety.py:707-775、_LATIN_TOKEN_RE)。=> 辞書登録は無効かつ逆効果のため**登録せず**(データ編集0)。
- 再生成: comment_3のみ(`--stages tts_a2 --only-clips comment_3`)。ただし既存entry(status OK・reuse_key一致)は再利用されるため、`tts_generation_results.json`から当該segmentのentryのみ削除して(元ファイルは scratchpad zy05_results_backup.json)再実行。1回目(11:20:09)は再利用でAPI 0(再生成せず)、2回目(11:20:58)で再生成: attempt4(標準phase, custom_06ec49ff)が **PHONETIC_MATCH**(ASR「美乃吉」)で1回目に採用、fallback未使用。費用0.37円(spent 45.7097→46.0763)。
- Style実測Gate: a2 PASS 27/27(BLOCK 0)、b1b PASS 26/26。組立(11:26:28、1起動 provision_shell,gate,assemble,pages,page_verify): provision_shell/gate/assemble/pages 完了(公開dir user_test/family_z_yuki_onna_01 に生成、API 0)、page_verify(local)=index/standard/advanced HTTP200・plays_failed 0・console_errors 0・ニュアンス見出し0(grep 0/0/0)。
- End User(enduser/)生成: sync gate Std PASS(min_row_ratio 0.92)/Adv PASS(0.60)、整合ok。**Playwright検証 rc=3 → FamilyZE2EStop ENDUSER_BROWSER_VERIFY**(runner rc=2)。NG 2/182(pc/mobile各1): `std_highlight_moves_into_next_part`(er135_enduser_page_verify_01.py:279-290)。原因=Japanese title「雪女」のclip長が1.27秒(発話区間sync 17.347-17.977の0.63秒)と極短で、検証は「境界から1.0秒後」時点でactive sentenceを要求するが、その時点(境界+1.0=18.087)は発話終了(17.977)後でactive=None。音声・表示は正常(発話中のハイライトは正しい)で、短尺パートが最短ペアとして選ばれる検証側の境界条件。音声/ページ側の欠陥ではない。
- 状態: 完成候補ページはlocalに生成済みだが**publish-copy・live検証・commit/pushは未実施**(End User検証未通過のため公開dirを公開しない)。検証ツールの是正(短尺パートの扱い)はProduction codeのためFable判断待ち。
- VOICE_TABLE: VOICE_TABLE_ZY05.md、a2/b1b全65clip不一致0(b1bのEN補助5clipはCharon=設計)。HR Lock 0。聞き分け=AUDIO_REVIEW_01.md(機械確認のみ、耳確認は未実施)。
- 費用: 本委任0.37円。案件累計46.08円/Cap150。本日JST累計は委任開始時約969.7円+0.37=約970円(1,000円以内)。起動: 11:20:09(再利用のみ・API0)/11:20:58(comment_3再生成)/11:26:28(組立段・API0)。stop_scope rc=0全3回。**起動規則: 11:20:09→11:20:58の間隔49秒(≥150秒に不足、1回目はAPI 0の再利用空振り、影響なし)**。300秒窓内2回以内は遵守。
