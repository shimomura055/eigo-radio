# FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_01B(2026-10-15、成果物側。委任文保存・T-0)

## 管理ID
`FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01`(略称CFSA)委任_01B(成果物側: 実artifactの観測=原稿構成・KP・Voice/TTS Prompt・Style・音声品質・validation・再利用由来)。委任_01A(仕様側)が並列。成果物は別ファイル(本委任は`B_`接頭辞)。並行する他管理ID: KGCPW 委任_02(`er003*/er019*/er026*`コード・`er071_output/.../gloss_alignment_production_wiring_01/`・OPUS台帳・REPORT_LEDGER・ACTIVE_TASKを編集中)、Day3 委任_E(`docs/research/.../day3/`)。本委任はRead-only調査。コードは読取のみ可、行番号は`git show 64d3ec975:<path>`のHEAD固定版で引用。git index.lock衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項
- Read-only監査。Production実装・音声再生成・有料API(LLM/TTS/ASR)・Trial・SSOT編集・Open Item起票は禁止。到達上限Status: `AUDIT_PART_B_COMPLETE`。
- 禁止: 有料API 0(JPY0)。SSOT/ACTIVE_TASK/REPORT_LEDGER/コード/Prompt/profile/音声/user_test編集禁止。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。音声再生成・変換禁止(既存ASR結果・validation記録・WPM測定結果の読取のみ。ローカル無料の音声長測定は可)。新Validator・新管理制度の提案禁止。
- Opus独立技術レビューGate: 非該当。時間見込み約2.5h。

## 固定ブロック
E-1(同一task内で同一ファイル再読しない)/D-1(Grep→該当行範囲Read)/G-1(git出力最小化)/F-1(transcript退避不要)/T-0(本ファイル保存+check_delegation_prompt.py実行、結果をRESULT_PACKETへ1行)/T-2(TTSなし)/T-3(JPY0のためGuardrail文不要)。

## ユーザー指示(原文、要点。全文は01A保存ファイル参照)
> 「### B. Key Phrase: M2候補供給・P0選定/Source span／canonicalization／Rule7/Key Phraseの選定数・難易度・意味整合/英語KPと日本語glossの一致/Standard：英語KP→日本語意味→英語KP/Advanced：英語KP→英語解説→英語KP/日本語gloss再整合工程の実際の適用版/retry／fallback／regeneration／Validation Gate。現時点で正式採用済みのcorrected gloss再整合工程と、旧Coffee音声で使った処理を混同しないこと。」
> 「### C. Voice／TTS Prompt・Style: 各音声segmentについて、期待されるStyleと実際に生成に使用されたStyleを照合する。特に、Intro／固定Master phrase/Standard日本語Preview／Comment：R2/Advanced Preview：E1/Standard／Advanced KP英語：K2/KP日本語意味：M2/Advanced英英解説：P3/Full Story：N01/Standard Full Story：N01＋既存6%減速/In One Line：既存承認Styleと新しい構成方針/その他の承認済み役割別Style。P8／PD8／N01など、過去の採用判断が上書きされた経緯も整理すること。Style名が設定ファイルに存在するだけで反映済みとは判定しない。可能な限り、実際の生成Prompt全文またはhash、生成時のprofile、actual model_id、出力音声、validation記録を照合する。seed音声・cache再利用・fallback takeについても、由来を確認する。」
> 「### D. 音声品質・完成状態: WPM、文末ポーズ、長い無音/Standardの6%減速後の品質/ASR検証結果/不自然な日本語読み/Audio Validation GateとM3 Style Gate/再利用音声のValidation継承/完成MP3と試聴ページの内容一致/最新仕様の反映漏れによる品質リスク。参考値と正式合否基準を混同しないこと。」
> 「### A. 記事構成・原稿: Intro／Welcome／Preview／Full Story／Comment／Key Phrase／In One Line／Outro/Storyの構成・分割数・記事内容/各Commentの役割と本文との接続/In One Lineの文数・内容・長さ・生成Prompt/Standard／Advancedの難易度と原稿の整合」
> 「推測をPASS扱いしないこと。証拠がなければ『未確認』と記録する。」「監査後の修正で音声再生成が必要な場合は、変更対象segmentを特定し、全記事を無条件に再生成しない最小対応案を提示する。」「今回の作業範囲：Read-only調査・分析・報告まで。」

## KPI provenance
すべて`reuse`(既存artifact・ログ・validation記録の読取)。新規測定は音声長のみ`fresh`(ローカル無料)。

## 対象artifact/事前指定Read/Grep一覧(要約)
完成版run dir `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/`(a2=Standard, b1b=Advanced)、試聴ページ`user_test/coffee_m2p0_n01_final_03/`、前版`user_test/coffee_final_v3/`・`er057_output/coffee_final_audio_assembly_01/`・`er057_output/coffee_final_listening_tone_trial_01/`(WPM_MEASUREMENT_01.md)・`er057_output/pace_trial_02/`、完成時チェック`er071_output/m2p0_n01_production_wiring_01/completion_04/CHECKLIST_05.md`(+completion_03/CHECKLIST_04.md)、Style/profile定義、Master Audio Store manifest、ASR/validation(tts_generation_results.json, er021 telemetry)。事前指定Read: CHECKLIST_05 / scaffold_run_summary / parts.json / segment_plan / keywords_canonicalized / tts_generation_results / raw_usage_log / index.html / WPM_MEASUREMENT_01 / Style定義 / Master Store manifest / Audio Validation Gate(`git show 64d3ec975:er003_v1_n3_01_assemble.py`) / M3 Style Gate。3者(segment_planのstyle・実使用prompt hash・Style定義本文sha256)一致で初めて「反映済み」。

## 成果物(`er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/`)
- `B_ARTIFACT_OBSERVATION_01.md`: §0超サマリ(10行)/§1原稿構成表(In One Line実文と文数、生成Prompt所在)/§2 KP表(gloss再整合の実際の適用版=旧legacyの証拠行)/§3 Voice/Style照合表(全segment、Intro/固定Master phraseはMaster Store由来とGate走査対象外の根拠明記)/§4音声品質・完成状態/§5未反映・部分反映・証拠不足候補/§6再生成最小範囲案/§7確認できなかった事項。
- `B_SEGMENT_PROVENANCE_01.csv`(level,segment_id,role,expected_style,used_prompt_hash,style_def_hash,match,profile,model_id,speed,origin,validation_status,asr_status,notes)。

## SSOT追記文/Git
SSOT編集権なし。ACTIVE_TASK・REPORT_LEDGERも編集しない。明示add: B_2ファイル+本ファイル+`_check.json`。RESULT_PACKET_CFSA1Bはgitignoreならforce addしない。音声・user_test・run dir配下は一切addしない。コミットメッセージ: 「FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_01B: Coffee完成版(final_03)の実artifact観測(原稿構成・In One Line実文数・KP/gloss適用版・全segmentのStyle/Prompt hash/由来/validation照合・音声品質・ページ一致)。Read-only、JPY0」。push to origin/main。

## 報告(RESULT_PACKET_CFSA1B項目)
(1)T-0 (2)§0超サマリ転記 (3)In One Line実文数(Std/Adv、実文引用) (4)Style照合集計 (5)gloss再整合適用版の証拠(ファイル:行) (6)由来集計 (7)Gate・validation・ページ一致 (8)未反映・証拠不足候補 (9)最小再生成範囲案 (10)commit hash・push・raw URL (11)確認できなかった事項 (12)逸脱。

## 事前指定Grep一覧+追記位置・更新位置の手順
- 各segmentの「期待Style vs 実際Style」: segment_planのstyle/profile名 → tts_generation_resultsの実使用prompt/hash → Style定義本文のsha256。3者一致で「反映済み」。不一致/記録なし→「未反映」または「証拠不足(未確認)」。
- 再利用・seed・fallback由来: `reused_from`/`validation_inheritance`/`take`/`cascade`欄とMaster Store manifest → 各segmentの由来(fresh/REUSED_VALIDATED/seed/Secondary cascade)。
- gloss再整合の適用版: keywords_canonicalized.jsonの`version`(`ER-003-KP-GLOSS-ALIGN-01`=旧legacy)・`mode`・`gloss_alignment_status`・HR有無をCHECKLIST_05と照合。
- 完成MP3と試聴ページの一致: index.htmlが参照するmp3のファイル名・サイズ・音声長 vs assemble出力。音声長はローカル無料測定。
- 成果物は`er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/`(`B_`接頭辞)。追記先: 新規作成のみ(既存ファイルの追記・更新なし)。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01B.md --json-out docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01B_check.json`
- 音声長: `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 <mp3>`(無ければ`.venv\Scripts\python.exe -c "import soundfile as sf,sys;f=sf.SoundFile(sys.argv[1]);print(f.frames/f.samplerate)" <wav>`)
- sha256: `.venv\Scripts\python.exe -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <path>`
- git: `git status --porcelain -- er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01 docs/pm/delegation_log`、`git log --oneline -3`
- 有料API・runner・TTS・ASRの実行は一切しない。
- 注記(実行層): 委任文本体は実行層が受領した全文を要点保存したもの(上記ユーザー指示は逐語)。
