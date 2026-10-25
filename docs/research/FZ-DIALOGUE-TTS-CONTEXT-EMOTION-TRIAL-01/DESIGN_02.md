# DESIGN_02 — 追加2作品の追加比較Trial: Round 1 DESIGN_01(+§9)からの差分のみ(委任_04、2026-10-26)

方式・事前登録・検査は **Round 1(DESIGN_01 §1〜§9 / `PREREGISTERED_CRITERIA_02.md` / `OPUS_REVIEW_01.md`)と同一**。本書は差分だけを書く。新しい構造・処理フローは追加していないため、Opus独立レビュー(条件A)は既存 `OPUS_REVIEW_01.md` を再利用する(PM_GOVERNANCE 11-3、内容が変われば再レビュー)。到達上限=VALIDATED(限定)。Production file / Prompt / 閾値 / reuse key / Gate / flag の変更は0(DEV専用経路)。

## 1. 差分一覧

| 項目 | Round 1 | Round 2(追加2作品) |
|---|---|---|
| 対象作品 | 賢者の贈り物(Adv 8件) | 開いた窓(8件)・猿の手(8件)。`SELECTION_02.md` |
| 出力dir | `er118_output/fz_dialogue_context_tts_trial_01/` | `er118_output/fz_dialogue_context_tts_trial_02/{open_window,monkeys_paw}/`(作品別: phase0/llm/gen)。**GO・cost log・Cap(30円)は親 `…_trial_02/` で2作品共有** |
| 試聴ページ | `user_test/fz_dialogue_context_trial_01/` | `user_test/fz_dialogue_context_trial_02/index.html`(2作品を1ページに束ねる。各作品の単独ページ `…/<work>/index.html` と `dev_details.html` も生成)。前回ページ `../fz_dialogue_context_trial_01/index.html` へのリンクと「3作品を続けて聴く」案内、A/B各2take(A・A'・B・B')、本文+日本語の場面・感情説明+折りたたみの前後文脈、「B=改善方式」を明示 |
| 感情LLM | 1 call/8件 | 作品別に1 call(計2 call)。EMOTION_DEVELOPER は作品名のみ置換(rule 1〜10は無変更、test `test_round2_emotion_prompt_only_title_differs`) |
| Cap | 個別Cap 30円(Round 1分) | 個別Cap 30円(追加2作品の合計、別枠・分離) |

## 2. er118 script の変更(`er118_fz_dialogue_context_tts_trial_01.py`、+284/−32行、test +203行。生成関数・Style追記方式・CONTEXT書式・leakage検査・ASR検査・分離条件は**無変更**)

1. **作品パラメータ化**: `WORKS` dict と `configure(work)`(module globalsの差替え)。既定は `magi` で、Round 1の値・EMOTION_DEVELOPER sha・出力先は不変(test `test_default_is_round1_magi_and_prompt_sha_unchanged`)。CLIに `--work {magi,open_window,monkeys_paw}`。
2. **共有Cap/cost log**: `GROUP_DIR`・`COST_LOG`・`PHASE1_GO_FILE` を作品dirから分離(Round 1はOUT_DIR自身)。
3. **default引数の遅延評価**: `run_emotion_llm`/`build_page`/`build_dev_details`/`analyze_all` の既定出力先を呼出時に解決(configure後に正しいdirへ書くため)。
4. **試聴ページ**: `build_page` を `_cards_html` に分割(Round 1出力は不変)。`build_combined_page`(親ページ)と `page-all` サブコマンド、`page_manifest.json`(各作品の音声path)。カードの話者表示は `_speaker_label`(Round 1の `Della/Madame/Jim` は不変)。
5. **感情候補の出力**: `_candidate_body`/`render_emotion_candidates_multi`/`candidates-all`(2作品を `EMOTION_CANDIDATES_02.md` へ)。
6. **新規固有名詞検査の許可語**: `ALLOWED_NAMES`(作品別)。Round 1は`{della, jim, christmas}`をコードに直書きしていた(入力に与えた話者名がLLMの文に出るのを許すため)。同じ趣旨で、開いた窓=`vera, framton, bertie, india`、猿の手=`herbert, mr, mrs, white` を許可(入力に無い名前は従来どおり破棄、test `test_round2_speaker_names_allowed_in_emotion_validation`)。**検査の緩和ではなく、入力に与えた固有名詞への対応を作品別にしたもの。** 結果、猿の手 `part2_c6` の `Whites`(家族名の複数形)は規則どおりDISCARDEDになった(規則は結果を見て変えない)。
7. **Cap先読み**(安全側の強化): 既存の `実績≥Cap` 停止に加え、`実績+次clipの見積>Cap` でも開始しない(`est_next_clip_jpy`)。
8. **①記録の補足**: `existing_audio_record` に `original_attempt_index`(採用原音がProductionのどのattemptか。既存keyは不変、読取のみ)。
9. 副作用の隔離: Round 1の旧test `test_page_has_noindex_and_no_dummy_audio_for_missing_arm` が実phase0を上書きしていたため、tmp dirへ向けた。

test: 54件PASS(Round 1の43件は無変更で全PASS + 追加11件)。遮断harness(`netblock_harness_01`)下で実行、接続試行0。

## 3. 事前登録(PREREGISTERED_CRITERIA_02)の適用 — **TTS観測前に固定(2026-10-26、LLM感情情報の観測後・TTS未観測)**

`PREREGISTERED_CRITERIA_02` の閾値・Status写像・成立条件(a)(b)(c)(e)(f)(g)・完全分離・「5件中3件以上=効果あり(機械的)/1件以下=効果なし/2件=保留」・逆向き記録・leakage定義は**一切変更しない**。Round 1の§5「clipごとの主指標」表と同じ作り方で、新作品のclipごとの主指標を、地の文の手がかり語から**次の対応則で割り当てて固定**する(Round 1の4種の対応を踏襲):

| 手がかり | 主指標 | 期待方向(ctx) | Round 1の対応 |
|---|---|---|---|
| hushed / murmured(ささやき・つぶやき) | 揃える前RMS(rms_dbfs) | ↓ | part2_c7 `she whispered` |
| 涙・震え声・落ち着いた(calmly)など、ゆっくり/抑えた話し方 | 調音話速(articulation_wpm_300) | ↓ | part3_c4 `smiling through tears`、part3_c8 `smiled gently` |
| hurried / rushed(急ぎ) | 調音話速 | ↑ | part3_c2 `rushed` |
| laughed / smile / brightened(明るい喜び) | F0中央値(f0_median_hz) | ↑ | part3_c6 喜び |
| 手がかりが弱い・混在 | 方向なし=過剰演技の監視(②両takeのF0幅>1.5×max(①,base)なら疑い) | — | part2_c2 / part2_c5 |
| 感情・演出の明記なし | 安定監視(長さ・調音話速・F0幅・RMS線形が①・baseの±20%内) | — | part2_c4 |

**割当(各作品: 方向あり5・監視2・安定1。`WORKS`のtargetsに`role`/`metric`/`direction`としてコード固定、test `test_round2_selection_rules`)**

| 作品 | clip | 役割 | 主指標・方向 | 根拠(地の文) |
|---|---|---|---|---|
| 開いた窓 | part1_c10 | 方向あり | RMS ↓ | `Framton murmured.` |
| | part2_c4 | 方向あり | 調音話速 ↑ | `her aunt hurried into the room.` |
| | part2_c6 | 方向あり | F0中央値 ↑ | `Then her face brightened.` |
| | part3_c9 | 方向あり | 調音話速 ↓ | `Vera said calmly.`(直後) |
| | part3_c11 | 方向あり | 調音話速 ↓ | `Vera said calmly.`(直前) |
| | part1_c7 / part1_c12 | 過剰演技の監視 | — | 窓を見る動作 / `Vera's voice grew quieter.`(直後) |
| | part3_c8 | 安定監視(9語) | — | 明記なし |
| 猿の手 | part1_c13 | 方向あり | F0中央値 ↑ | `Herbert laughed.` |
| | part1_c15 | 方向あり | F0中央値 ↑ | `Mr. White raised the paw with a smile.`(**注: 直後に`He cried out`が混在**) |
| | part2_c8 | 方向あり | 調音話速 ↓ | `Her face was wet with tears.`(**注: `shook her husband awake`の切迫が混在。Round 1の涙=話速↓の対応則を機械的に適用**) |
| | part2_c10 | 方向あり | RMS ↓ | `He turned away.`(内にこもった話し方=弱い手がかり) |
| | part3_c1 | 方向あり | 調音話速 ↓ | `His voice shook.` |
| | part1_c4 / part2_c2 | 過剰演技の監視 | — | 会話タグのみ / 明記なし |
| | part2_c6 | 安定監視(13語) | — | 明記なし(感情情報はDISCARDEDで決定論文脈のみ) |

- 判定の単位は**作品ごと**(方向あり5件のうち完全分離3件以上/1件以下/2件)。Round 1の判定(5件中1件)は書換えない。
- **追加分析(事前登録外)**として、3作品を合算した「方向あり15件中の完全分離件数」と、期待方向を問わない効果量(clipごとの② vs ①側の差の符号)は、元の判定と区別した別節に載せる(委任_05)。これは判定の代替にしない。
- 機械指標だけで主観的な音声品質を最終決定せず、ユーザー試聴による比較判断を残す(ページはこのため)。

## 4. 無変更の確認事項

生成関数(`generate_voice_body_wide_margin(style_prefix_override=…)`)/Style追記(①の文字列+空行+CONTEXTブロック、`CONTEXT_HEAD`/`CONTEXT_TAIL`)/EMOTION_SCHEMA/強度語deny/根拠引用の逐語一致検査/Fableレビューgate(`emotion_review.json` 全件 accept|discard 設定が無いとctx armを起動しない)/`leakage_check`(difflib方式)/`comparison_validity`/protected snapshot・repo mtime走査/sink隔離/`SESSION_ORDER`/最終相当音声(atempo=1.06、`er008.apply_a2_slowdown`)/target_rms統一(**作品ごとの実組立 `timeline.json gain_report`**: 開いた窓0.08116、猿の手0.08307 — Round 1が「その作品の実組立」を使った方式を踏襲)。

## 5. Phase 1a(感情情報LLM)の結果(委任_04で実行済み)

- 各作品1 call、`gpt-6-luna`、実費 0.095円/0.0988円(計0.1938円)。結果 `EMOTION_CANDIDATES_02.md`(英文・前後文脈・LLM出力・根拠引用[出どころ付き]・実際に送られるCONTEXTブロック)。件数: 開いた窓 ACCEPTED 6 / NO_EXPLICIT_CUE 2 / DISCARDED 0、猿の手 ACCEPTED 6 / NO_EXPLICIT_CUE 1 / DISCARDED 1(`part2_c6`、`new_proper_noun:scene:Whites`)。合計 ACCEPTED 12 / NO_EXPLICIT_CUE 3 / DISCARDED 1。
- Fableレビュー枠 `…/<work>/llm/emotion_review.json`(`fable_decision` 全件null、`summary_ja`はSonnet下書き)。**全16件に decision が付くまでctx armは起動しない**(M6)。
- レビュー時の注視点(Sonnetの所見。判断はFable): (i) 猿の手 `part1_c15` の `scene` が "At home" と書く(原文に場所の明記なし。軽微な推測)、(ii) 猿の手 `part2_c8` の state に "distressed"(強度語denyには該当しないが感情語)、(iii) 開いた窓 `part3_c11` の evidence に直後の地の文 `Inventing convincing stories …`(作り話だと明かす文)が入っており、CONTEXTにも直後の地の文として入る(Round 1と同じ抽出規則の帰結)、(iv) NO_EXPLICIT_CUEの3件(開いた窓`part1_c7`/`part3_c8`、猿の手`part2_c2`)は規則どおり state行を出さない。

## 6. 既知のリスク・限界(結果を見て基準を動かさないため、先に記録)

1. **文脈の抽出規則がRound 1と同一のため、隣接する別人の動作が手がかり語になる**: 猿の手 `part1_c13`(`laughed`+`smile`[次の文]),`part1_c15`(`smile`+`cried`[直後]),`part2_c8`(`tears`)。混在clip(`part1_c15`,`part2_c8`)は方向あり予測が外れやすい。これは文脈方式の実装上の弱点でもあり、結果の解釈に使う(基準は動かさない)。
2. 猿の手 `part2_c6`(安定監視)は感情情報がDISCARDEDのため、ctxとbaseの差は決定論の前後文脈だけになる(安定監視としては妥当だが、LLM由来情報の影響は見えない)。
3. 開いた窓 `part1_c10` は2語で、Round 1の教訓どおり計測が不安定になり得る(方向ありの1件のみ。安定監視には使っていない)。
4. 怒りの明示が両作品のAdv地の文に無く、怒りは網羅できない。
5. 速度加工後のProduction ASR再検証は行わない(Round 1と同じ限界、`PREREGISTERED_CRITERIA_02` §6-5)。
6. N=16セリフ×2 take、F0は粗い自己相関推定。機械指標は聴感の代替ではない。

## 7. 委任_05(Phase 1b〜公開〜3作品整理)の実行案

1. Fable: `EMOTION_CANDIDATES_02.md` をレビューし、各作品の `emotion_review.json` に `fable_decision`(accept|discard)と`summary_ja`確定を設定。`PHASE1_GO.json` の `arms` を `["ctx","base"]`、scopeをPhase 1bへ更新。
2. Sonnet(各作品を**直列**、cost log共有のため): `py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 --run-dir er118_output/fz_dialogue_context_tts_trial_02 --out …/stop_check_委任_05.json` → `PYTHONUTF8=1 .venv\Scripts\python.exe er118_fz_dialogue_context_tts_trial_01.py --work open_window gen-session` → 同 `--work monkeys_paw gen-session`(各 約5分、計48 call)。
3. API 0: `… --work open_window analyze` / `--work monkeys_paw analyze`(最終相当音声・mp3[target_rms統一]・`analysis.json`[evaluation: 完全分離・監視・条件(a)(b)(c)(e)(f)(g)・leakage]・単独ページ・`page_manifest.json`)→ `… page-all`(親ページ)。
4. Fable独立評価(leakageのflagged/needs_listenは転写と音声長を確認)、追加分析(3作品合算・事前登録外)の別節作成、`py docs/pm/tools/user_test_page_e2e_check.py`等の既存ページ検査、公開(`user_test/fz_dialogue_context_trial_02/` のみ。wavは不追跡)。
5. 3作品横断整理(効果の有無・傾向、改善/非改善セリフの特徴)→ TRIAL_RESULT_02.md、Status(REJECTED/VALIDATED[限定]/USER_DECISION_REQUIRED)、SSOT(CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS[OPEN-516更新]・REPORT_LEDGER・USER_DECISION_REGISTER)とGit反映。
- 所要見込み: 生成約10分 + 解析・ページ約10分 + Fable評価・文書化・公開約30〜40分 = 約1時間。クリティカルパスは「Fableの感情レビュー → 生成」。解析・ページ・文書の雛形は本委任で用意済み。
