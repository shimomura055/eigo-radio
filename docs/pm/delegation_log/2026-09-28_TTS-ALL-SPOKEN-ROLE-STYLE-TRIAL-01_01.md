# Delegation Prompt — TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 (回1)

日時: 2026-09-28
委任元: Fable (sandwich-pm)
委任先: Sonnet (実行層)

## 管理ID

TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_RS1.md` / `docs/pm/RESULT_PACKET_RS1.md`(commitしない)。並行衝突: 別Sonnetが `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01`(`er037_*`、`er037_output/`、`FAMILY-XY-*_REPORT.md`、`docs/pm/design_family_xy_*`)と KP 4+1 修正(`er003_key_words_*`、`er030_*`、`er035_*`、`er003_v1_n3_01_scaffold_generate.py`、SSOT 4点)を実行中 → これらに触れない。本タスクの所有: 新規 `er038_tts_all_spoken_role_style_trial_01*.py`(+test)、`er038_output/tts_all_spoken_role_style_trial_01/`、`user_test/tts_all_role_style_trial_01/`(試聴ページ)、新規 `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`、`docs/pm/design_tts_all_spoken_role_style_trial_01.md`、delegation_log。**Production code(`er0*.py`既存ファイル、`er033_tts_flash_lite_family_x_styles_01.py` 含む)・CURRENT_SPEC・正式Promptは一切変更しない**(import/呼び出しによる流用のみ。style上書きはTrial script側の引数渡し/`style_prefix_override` 等の既存パラメータで行う)。SSOT 4点は**編集権なし**(追記文案をRESULT_PACKETへ)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Production実装なし)。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(Sonnetは判定案のみ、`VALIDATED` でもProductionへ実装しない)。
- 費用: 上限¥45(Guardrail。Flash-Lite TTS+ASR、Hormuz 1記事×Standard/Advanced×全発話、実測前例: 1レベル約¥10.8)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止(ユーザー明示): Production正式path変更/Production default routing変更(既定 `tts_backend`・style定数の変更)/CURRENT_SPECをProduction採用済みとして更新/retry・fallbackの正式仕様変更/新しい仕様候補の勝手な追加実装/記事生成・Key Phrase再選定(既存テキストartifactを再利用)/長い演技Promptの新設/Trial専用別実装でProduction挙動と乖離させること(既存Flash-Lite Production関数を可能な限り呼ぶ)/既存日本語fallback・pronunciation safetyを壊すこと/`Now the full story.` 等の共有ナレーションを本文Roleへ雑に含めること/Advancedの英語解説を日本語意味として扱うこと。`git add -A` 禁止、履歴書き換え禁止、APIキー本文表示禁止。ユーザー向け試聴リンクは GitHub Pages(`file:///`・raw URL不可)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_01.md_check.json`、結果1行記録。
T-2: TTSを伴う実行は `TTS_EXECUTION_MODE=STANDARD` を明示(同期実行)。実行前に(1)差分再生成の可否(既存テキストartifact再利用、TTSのみ新規)、(2)Master Audio Store再利用の有無(Trialは別out-dir・別style文字列のためkeyが変わり再利用されない=意図どおり。**Production Master Audio StoreへTrial資産を登録しない**: Storeへの書込みを無効化できる引数/経路があればそれを使い、無ければTrial用の別Store pathを指定。不可ならSTOP)、(3)`--budget-jpy` 明示、(4)想定外の全再生成ならAPI実行前STOP、の4点を確認。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「Task B — 全TTS Role Style Trial。目的: 現在のFlash-Lite 6-roleを拡張し、TTSで実際に発話するものすべてに、その発話目的に対応するRoleを明示するTrialを行う。まだProduction仕様ではない。
基本方針: Standard/Advanced — Role style自体は原則共通にする。現在Standard英語に付いている自然言語の『Speak at a slightly slower...』系の「少し遅く読む」instructionは、このTrialでは外す。Standardの速度差は既存の機械的6% slowdownのみで作る。Advancedにはslowdownなし。比較したいのは、同じRole style+Standardのみ機械的速度調整で自然にレベル差を作れるか。日本語 — 現在は既存の日本語共通instructionを使用しているが、今回のTrialでは日本語にも英語と意味的に対応するRole styleを与える(PreviewならPreview、CommentならComment、TitleならTitle)。言語が違っても「発話の役割」は同じという設計で試す。既存日本語fallback/pronunciation safety等は壊さないこと。
Role inventory: 既存6-roleだけに限定せず、ProductionでTTSされる発話を全件棚卸しして、Role漏れをゼロにすること。最低限: PROGRAM / SECTION INTRO(Welcome、セクション導入等)/TOPIC INTRO(Today's topic等)/JAPANESE TITLE / TITLE(タイトル読み)/PREVIEW/COMMENT(Comment 1〜4)/FULL STORY(本文)/HEADING(本文内見出し)/IN ONE LINE(最終要約)/FULL STORY INTRO(Now the full story.等)/KEY PHRASE INTRO/KEY PHRASE EN/KEY PHRASE JA(Standardの日本語意味)/KEY PHRASE EXPLANATION EN(Advancedの英語解説)/NUMBER / LABEL(One/Two等)/その他(実際にTTSされるものがあれば棚卸しして分類)。重要: Now the full story. はFULL STORY本文ではなく導入Role。共有ナレーションを本文Roleへ雑に含めない。
Key Phrase: レベル差を正しく反映。Standard=英語Key Phrase+日本語意味の両方に適切なRole style。Advanced=英語Key Phrase+英語での解説。Advancedの英語解説を日本語意味として扱わない。Trial Role体系に KEY_PHRASE_EXPLANATION_EN を明示的に含める。既存のAdvanced Key Phrase仕様・コードを先に確認し、二重実装しない。
Role style作成方針: 現在の6-roleと同じく短く単純なdescriptorを基本。長い演技Promptを新たに作らない。例: Topic Intro: brief, clear, engaging/Preview: calm, conversational/Comment: calm, conversational/Full Story: calm, steady, engaging narration/Heading: brief, clear/In One Line: concise, clear。盲目的に固定せず各Roleの目的に合う最小限の表現を設計してよい。日本語も英語の直訳が不自然なら、同じ発話意図を保った自然な日本語style instructionにする。
Trial音声: 既存の記事を使い、無駄な記事生成・Key Phrase再選定等はしない。可能な限り既存テキストartifactを再利用してTTS比較だけに集中。Standard/Advanced双方を生成し、ユーザーが比較試聴できるページを用意。ページでは最低限、Standard全体/Advanced全体/Role別segment/どのRole・styleを使ったか、が確認できるようにする。
評価観点: Roleごとの声色・テンポが自然か/Role差が過剰でないか/日本語Role styleが不自然でないか/Standardで自然言語のslow instructionを外しても問題ないか/Standardの6% slowdownだけで聞き取りやすさが確保できるか/AdvancedとStandardで不要な演技差がないか/Key Phraseが明瞭か/Advanced英語解説が自然か/共有ナレーションまで含めRole漏れがないか/instruction leakage等のRegressionがないか。
実装・安全条件: Production正式pathは変更しない/Trial専用script・artifactで実施/Production default routing変更禁止/CURRENT_SPECをProduction採用済みとして更新しない/retry・fallbackの正式仕様を変更しない/新しい仕様候補が出たら勝手に追加実装せず報告/コスト最小化・既存artifact最大限再利用/Trialのためだけの再生成を必要以上に行わない。音声側では既存Flash-Lite Production関数を可能な限り呼び出して比較。Trial専用別実装でProduction挙動と乖離させない。
Closeout報告(12項目): 1 Existing Spec/Prior Trial確認結果 2 実施Pattern 3 Baselineとの差 4 成果物 5 定量結果 6 品質評価 7 Regression 8 コスト 9 新しく判明した問題 10 REJECTED/VALIDATED/USER_DECISION_REQUIRED 11 ユーザー判断が必要な事項 12 Production変更が一切入っていない証拠。Closeout時に未報告Trial/未処理USER_DECISION_REQUIRED/TrialからProductionへ誤って入った変更/Dangling Reference/SSOT・Open Item記録漏れがないことも確認。」

## Fable補足(Existing Spec Check の入口・実施計画)

- 既存6-role: `er033_tts_flash_lite_family_x_styles_01.py`(TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/HEADING_READOUT/IN_ONE_LINE、`FAMILY_X_ROLE_STYLE_EN_FALLBACK`)。Family X runnerのstyle合成: `er019_family_x_audio_production_runner_01.py`(`_role_style`/`_role_style_slower`、A2 `A2_SLOWER_PACE_INSTRUCTION` 連結、6% post-process `apply_a2_slowdown_postprocess`)、shell短style(修正3回目 commit `ee280e76`、`er006_audio_cost_pilot_02_shared_narration.py`)、JA既存共通instruction(Grep `JAPANESE|JA_STYLE|ja_style` -i in `er019_*.py`/`er003_v1_*.py`/`er033_*`)、Key Phrase音声経路(Standard: EN phrase+JA meaning[kp_ja_charon等]、Advanced: EN phrase+EN explanation。Grep `meaning|explanation|kp_` -i in `er019_family_x_audio_production_runner_01.py`/`er003_v1_n3_01_tts_generate.py`)。Baseline = 現行Production(Flash-Lite、Hormuz `hormuz__run_06_flashlite_full_kp` の既存音声=修正3回目後のもの。**再生成しない**、試聴ページで比較対象として参照)。
- 棚卸し: Family X runnerのStandard/Advanced実行で実際にTTSされる全segment(主記事各role、見出しsub-segment、KP関連[intro/EN/JA/EN explanation]、共有ナレーション[welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five/point_explanation(JA)等]、JA title等)を `tts_generation_results.json`・`shared_narration`記録・runnerコードから列挙し、Role表(segment_id→Trial Role→EN style→JA style)を設計書に作る。Role漏れゼロを確認するtestを書く(runner側の全segment種別がRole表に載っていること)。
- Trial Role style(短いdescriptor、EN/JA対応): 既存6-roleの文言は据え置き、追加Role(PROGRAM_INTRO/SECTION_INTRO、TITLE、FULL_STORY_INTRO、KEY_PHRASE_INTRO、KEY_PHRASE_EN、KEY_PHRASE_JA、KEY_PHRASE_EXPLANATION_EN、NUMBER_LABEL、その他)は各Roleの目的に合う最小限で設計(設計書に一覧と根拠)。Standard: `A2_SLOWER_PACE_INSTRUCTION` を**付けない**(6% post-processのみ)。Advanced: slowdownなし。
- 実装: Trial script `er038_tts_all_spoken_role_style_trial_01.py` は、既存Flash-Lite Production関数(er033 backend call_fn、`resolve_tts_call_and_prompt`、voice01/repro01/news_tail_fix/point_headings/KP/shared narrationの各生成関数)を **style上書き引数付きで呼ぶ**(既存パラメータが無い関数はその旨を記録し、最下層のTTS call関数を同じ引数で呼ぶ)。Trial用out-dir `er038_output/tts_all_spoken_role_style_trial_01/hormuz/{a2,b1b}/`、Master Audio StoreはTrial専用path(Production Storeを汚さない)。ASR検証・retry cascadeはProductionと同じ関数を通す(retry上限は既定3のまま、仕様変更なし)。
- 入力: Hormuz run_06 の既存テキストartifact(本文/見出し/KP/JA訳/共有ナレーションcanonical text)を再利用。Assembly(既存 `--stage assembly` 相当関数をTrial out-dirに対して呼ぶ、不可なら既存結合関数を直接呼ぶ)。
- 試聴ページ: `user_test/tts_all_role_style_trial_01/index.html`(mp3、`imageio_ffmpeg` 同梱バイナリで変換、前例 `docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_03.md` の方式)。内容: Standard全体/Advanced全体(Trial)+現行Production(Baseline、`user_test/flash_lite_family_x_02_hormuz/` の既存mp3へ相対リンクで参照、再変換不要)/Role別segment(Trial、各segmentにRole・EN/JA style文字列・attempt・ASR結果・duration表示)。合計サイズ50MB超見込みならcommit前STOP。push後 `curl -sI https://shimomura055.github.io/eigo-radio/user_test/tts_all_role_style_trial_01/index.html` で200確認(最大15分)。
- 評価: 定量=segment別status/attempt/ASR一致/duration(Baseline比)、instruction leakage検出(既存検出器流用)、Role漏れ0の検証、cost。品質=Sonnetの試聴不可のため主観評価はユーザー(評価観点10項目の表を用意し、機械的に判定できる項目のみ記入、残りは「ユーザー試聴待ち」と明記)。判定案は `USER_DECISION_REQUIRED`(試聴待ち)を基本とし、Regression/leakage/Role漏れがあれば `REJECTED` 候補として明記。

## 事前指定Read一覧

- `er033_tts_flash_lite_family_x_styles_01.py` 全文(短い)
- `er019_family_x_audio_production_runner_01.py`: `_role_style`/`_role_style_slower`(Grep → 範囲)、segment生成ループ(Grep `segment_id` → 範囲)、KP音声生成(Grep `kp_` → 範囲)、shared narration呼び出し(Grep `ensure_all_shared_narration`)、assembly stage(Grep `assembly`)
- `er006_audio_cost_pilot_02_shared_narration.py`:40-150(shell定義・style override・Store key)
- `er006_master_audio_store_01.py`: Store pathの指定方法(Grep `STORE_DIR|store_dir|manifest`)
- `er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/{a2,b1b}/audit/tts_generation_results.json`(segment一覧)
- `CURRENT_SPEC.md` Flash-Lite節(Grep `FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02` → 範囲)、Key Phrase音声仕様(Grep `Key Phrase` `Advanced` `英語解説|explanation` → 該当範囲)
- `DECISION_LOG.md`/`OPEN_ITEMS.md`: Grep `role style|6-role|slower|slowdown|日本語.*style` -i(過去Trial・既存決定の重複確認)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記Grep群 → 設計書 §1(Existing Spec/Prior Trial Check、既存Advanced KP仕様の確認、二重実装なしの根拠)、§2(棚卸しRole表)、§3(Trial style表 EN/JA)。
- Dangling Reference Check: Grep `er038_|tts_all_spoken_role_style` 全体。
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er038`(空)を逐語記録。

## 実行コマンド全文

- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er038_tts_all_spoken_role_style_trial_01.py --source-run "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --level b1b --out-dir "er038_output/tts_all_spoken_role_style_trial_01/hormuz" --tts-backend speech_metadata_flash_lite --budget-jpy 22`
- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er038_tts_all_spoken_role_style_trial_01.py --source-run "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --level a2 --out-dir "er038_output/tts_all_spoken_role_style_trial_01/hormuz" --tts-backend speech_metadata_flash_lite --budget-jpy 22`(引数名は実装に合わせ、実行したコマンドを逐語記録)
- 単体test(¥0、mock): `.venv\Scripts\python.exe -m pytest er038_tts_all_spoken_role_style_trial_01_test_01.py -q`(Role漏れ0、Standard styleに `A2_SLOWER_PACE_INSTRUCTION` が含まれないこと、Advancedにslowdownなし、Production style定数が不変[hash]、Production Store未使用、`assert_no_wpm_specification` 適用)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er038*_test_*.py"`
- 変換例: `.venv\Scripts\python.exe -c "import imageio_ffmpeg,subprocess;subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-i','er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/episode.wav','-codec:a','libmp3lame','-b:a','128k','user_test/tts_all_role_style_trial_01/hormuz_advanced_trial.mp3'])"`(実ファイル名に置換、逐語記録)

## SSOT追記文

RESULT_PACKETへ文案のみ: REPORT_LEDGER新行(Trial、Status案)、DECISION_LOG(Trial実施記録、ユーザー指示要旨、Role表の所在、Status案、Production採用未決)、OPEN_ITEMS候補(Role漏れ・leakage等の新発見のみ)。CURRENT_SPEC変更なし。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `er038_*`、`er038_output/tts_all_spoken_role_style_trial_01/`(json/md、wavは非commit)、`user_test/tts_all_role_style_trial_01/`(mp3/html)、REPORT、設計書、delegation_log+`_check.json`。他Agent差分・SSOT・Production Store(`er006_output/master_audio_store_01/`)は一切addしない。SSOT編集権: なし。
- メッセージ: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: 全TTS発話のRole棚卸し+Role style(EN/JA)Trial、Standard slow instruction除去比較、Hormuz Standard/Advanced試聴ページ`、trailer `Management-ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

ユーザー指定12項目(1 Existing Spec/Prior Trial確認結果[既存Advanced KP仕様の確認含む] 2 実施Pattern[Role表・style表 EN/JA逐語] 3 Baselineとの差[style差分、Standard slow instruction除去] 4 成果物[試聴URL、out-dir] 5 定量結果[segment別status/attempt/ASR/duration Baseline比、cost] 6 品質評価[機械判定分+ユーザー試聴待ち項目] 7 Regression[leakage・Role漏れ・test] 8 コスト実測 9 新しく判明した問題 10 Status案 11 ユーザー判断が必要な事項 12 Production変更が一切入っていない証拠[git diff結果、Production Store未汚染])+STOP該当有無+SSOT文案+commit hash+raw URL。ユーザー向け表記はStandard/Advanced、同期実行/バッチ実行。
