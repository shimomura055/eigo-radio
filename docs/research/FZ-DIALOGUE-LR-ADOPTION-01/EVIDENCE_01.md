# EVIDENCE_01 — ZセリフLR正式採用の正式経路runtime evidence(FZ-DIALOGUE-LR-ADOPTION-01 委任_03、2026-10-29)

区別: **E1=自然発火**(正式runner `er026 --stages tts_b1b --only-clips full_story_part3_c6 --mode real`、注入0、実TTS/実ASR/実Azure/実LR[gpt-6-luna]/実180秒)。**E3=注入**(正式runnerを同一processで起動し、`fzlr_inject_harness_01.NgInjector`で指定attemptの**ASR判定のみ**NG化[全記録`INJECTED`]、`tru_ev_core_01.installed(空Plan)`で台帳を隔離。TTS・LR LLM・Style・Voice・180秒待機・Gate実装は実物。copy-run=`run_fzlr_ev_*`、品質根拠にしない)。表は`tools/fzlr_e3_aggregate_01.py`が実run記録(state/sidecar/cost_log/隔離台帳)から機械生成。

## 0. 主要結論
- 6回フロー(①②→180秒→③→LR→④⑤→180秒→⑥→終端Lock/HRQ1行)は**E1(自然)・E3-A(Std注入)の両方**で、回数・待機(実測179.9秒×2)・LR1回・Style/Voice維持のとおり動作。
- 藪の中Adv c6はE1で④⑤⑥NG→**HR**(LRは発動、③④はASR合格・repetition QA d'のみflag、⑤⑥は読み誤り)。新形式HR報告=`HR_ROUTE_PART3_C6_02.md`。Status据置(完成候補は未達)。
- 実走で**不具合2件**を発見し同一委任内で是正(§4)。
- 合計費用: E1 ¥14.38 + E3 ¥9.03(うち不具合起因の再走[a2_02/03]¥2.07)= ¥23.41。

## 1. 原文§7(検証項目)↔ evidence
| 原文§7 | 自然(E1) | 注入(E3) | test(API 0) |
|---|---|---|---|
| ①②→180秒→③→LR→④⑤→180秒→⑥ | ④⑤⑥まで(①〜③は消費済み引継ぎ、待機2回目=実測179.944秒) | E3-A: ①〜⑥全実走、待機2回(179.954/179.95秒)、LR 1回、終端Lock+HRQ1行 | S1 |
| 最大6回の安全上限 | n_started=6で停止、cumulative_tts=6 | E3-A: 6で停止 | S4/P3 |
| LR最大1回・再入禁止 | LR 1回(`lr.state`UNRESOLVED後に再LRなし) | E3-A/B/D: LR 1回のみ | S3 |
| 途中PASSで即終了 | (④NG) | E3-B: ④実判定PASS→⑤⑥のTTS 0・待機なし | S2 |
| LR適用不可時の安全処理 | (c6では入力あり) | E3-C: LR不可(NO_USABLE_LR_INPUT)→TTS 3・LR LLM 0→Lock+HRQ1行。E3-D: LR発動・7Gate全不合格(NO_CANDIDATE_PASSED_QA)→TTS 3→Lock+HRQ1行 | L1/L2 |
| LR後の元Style・Voice維持 | ④⑤ctx style sha 3eb5d8ba=①②と同一、Voice=Puck、model不変 | E3-A: ①②④⑤ style 44b10035同一、Voice Schedar同一。E3-B: ①②④ c4320ff5同一、Orus同一。③⑥はctx除外(style=-) | L3 |
| ASR・反復検査・減速後再検証 | ④: ASR合格→repetition QA d'短lag 0.68s flag。⑤⑥: ASR(OpenAI+Azure)NG_BOTH | E3-B④実ASR+repetition QA PASS(Advの減速後再検証経路) | L7 |
| HR Lock・終端NG | Lock=HUMAN_REVIEW_REQUIRED、cumulative_tts=6、HRQ 1行(+重複抑止行) | E3-A/C/D: Lock+隔離HRQ各1行 | L4 |
| retry/fallback/regeneration/resume | **移行tool→正規resume**: ①〜③再実行0(cost_log・attempt_history・sidecar件数で確認)、Lock承認1回消費、`cumulative_tts_attempts` 3→6 | E3-B: ①②後に自processをkill→再起動: ①②再実行0、待機は残り28.6秒のみ(resumed=True、process_starts=2) | S4/S5/S8/M4 |
| 最終本文・音声・学習項目の整合 | c6はHRのため最終採用なし(確定「sank for ever」「on soft feet」はLRで不変) | E3-B: LR After=`"Yes, I did him in,"` を④がPASS | R3/R4 |
| X/Y/Z既存共通経路Regression | §5 | - | D1〜D4 |

## 2. 表(機械生成)
### E1 自然(藪の中Adv c6・実再開) — `run_sf_prod_01/b1b/full_story_part3_c6`
status=TERMINAL_NG / phase=B2 / n_started=6 / LR.state=UNRESOLVED (HUMAN_REVIEW_LOCKED_RETTS_FAILED) / Lock=HUMAN_REVIEW_REQUIRED cumulative_tts=6 / 費用(この run の cost_log)=¥136.399

| n | block/ordinal | mode | 開始-終了 | verified | ASR判定 | 備考(Style sha/Voice/model) |
|---|---|---|---|---|---|---|
| 1 | 0/1 | ctx | 14:55:44-14:56:43 | False | NG_BOTH | style=3eb5d8ba voice=Puck model=gemini-2.5-pro-preview-tts |
| 2 | 0/2 | ctx | 14:56:43-14:57:41 | True | PASS | style=3eb5d8ba voice=Puck model=gemini-2.5-pro-preview-tts rep_flag=False |
| 3 | 0/3 | legacy_fallback | 15:01:06-15:01:54 | False | PASS | style=- voice=Puck model=gemini-2.5-pro-preview-tts rep_flag=True |
| 4 | 1/1 | ctx | 18:24:45-18:25:42 | False | PASS_WITH_WARNING | style=3eb5d8ba voice=Puck model=gemini-2.5-pro-preview-tts rep_flag=True |
| 5 | 1/2 | ctx | 18:25:42-18:26:34 | False | NG_BOTH | style=3eb5d8ba voice=Puck model=gemini-2.5-pro-preview-tts |
| 6 | 1/3 | legacy_fallback | 18:29:34-18:30:25 | False | NG_BOTH | style=- voice=Puck model=gemini-2.5-pro-preview-tts |

LR Before→After: `An` → `Some` / 7Gate全PASS=True / 入力=#1 pre_slowdown / skipped=[{"n": 2, "source": "post_slowdown", "reason": "OVERLAPS_CONFIRMED_CONTENT", "stops": ["T1", "T2"], "ng_span": "my chest i sank for ever into the darkness"}]

待機(`cooldowns`): n<3: 要求180.0s / 開始14:58:06 終了15:01:06 / このprocess内待機179.941s / resumed=False / process_starts=1; n<6: 要求180.0s / 開始18:26:34 終了18:29:34 / このprocess内待機179.944s / resumed=False / process_starts=1

### E3-A Std 6スロット全NG注入(LR実走) — `run_fzlr_ev_a2_05/a2/full_story_part1_c6` (全判定注入=INJECTED、品質根拠にしない)
status=TERMINAL_NG / phase=B2 / n_started=6 / LR.state=UNRESOLVED (HUMAN_REVIEW_LOCKED_RETTS_FAILED) / Lock=HUMAN_REVIEW_REQUIRED cumulative_tts=6 / 費用(この run の cost_log)=¥3.213

| n | block/ordinal | mode | 開始-終了 | verified | ASR判定 | 備考(Style sha/Voice/model) |
|---|---|---|---|---|---|---|
| 1 | 0/1 | ctx | 19:02:20-19:02:26 | False | NG_BOTH | style=44b10035 voice=Schedar model=gemini-2.5-pro-preview-tts |
| 2 | 0/2 | ctx | 19:02:26-19:02:31 | False | NG_BOTH | style=44b10035 voice=Schedar model=gemini-2.5-pro-preview-tts |
| 3 | 0/3 | legacy_fallback | 19:05:31-19:05:38 | False | NG_BOTH | style=- voice=Schedar model=gemini-2.5-pro-preview-tts |
| 4 | 1/1 | ctx | 19:06:21-19:06:26 | False | NG_BOTH | style=44b10035 voice=Schedar model=gemini-2.5-pro-preview-tts |
| 5 | 1/2 | ctx | 19:06:26-19:06:33 | False | NG_BOTH | style=44b10035 voice=Schedar model=gemini-2.5-pro-preview-tts |
| 6 | 1/3 | legacy_fallback | 19:09:33-19:09:39 | False | NG_BOTH | style=- voice=Schedar model=gemini-2.5-pro-preview-tts |

LR Before→After: `He carried a sword and` → `He bore a sword and` / 7Gate全PASS=True / 入力=#3 pre_slowdown / skipped=[]

待機(`cooldowns`): n<3: 要求180.0s / 開始19:02:31 終了19:05:31 / このprocess内待機179.954s / resumed=False / process_starts=1; n<6: 要求180.0s / 開始19:06:33 終了19:09:33 / このprocess内待機179.95s / resumed=False / process_starts=1
HRQ行(隔離台帳)=1 / 隔離attempt_history行=5
注入記録=12行(うちINJECTED=true 12行) / kill記録=[]

### E3-B Adv ①〜③NG注入→LR→④実判定PASS(+kill/resume) — `run_fzlr_ev_b1b_01/b1b/full_story_part2_c1` (全判定注入=INJECTED、品質根拠にしない)
status=DONE_OK / phase=B2 / n_started=4 / LR.state=RESOLVED (None) / Lock=RESOLVED cumulative_tts=4 / 費用(この run の cost_log)=¥1.612

| n | block/ordinal | mode | 開始-終了 | verified | ASR判定 | 備考(Style sha/Voice/model) |
|---|---|---|---|---|---|---|
| 1 | 0/1 | ctx | 18:38:56-18:39:00 | False | NG_BOTH | style=c4320ff5 voice=Orus model=gemini-2.5-pro-preview-tts |
| 2 | 0/2 | ctx | 18:39:00-18:39:05 | False | NG_BOTH | style=c4320ff5 voice=Orus model=gemini-2.5-pro-preview-tts |
| 3 | 0/3 | legacy_fallback | 18:42:05-18:42:10 | False | NG_BOTH | style=- voice=Orus model=gemini-2.5-pro-preview-tts |
| 4 | 1/1 | ctx | 18:42:40-18:42:50 | True | PASS_WITH_WARNING | style=c4320ff5 voice=Orus model=gemini-2.5-pro-preview-tts rep_flag=False |

LR Before→After: `killed him` → `did him in` / 7Gate全PASS=True / 入力=#3 pre_slowdown / skipped=[]

待機(`cooldowns`): n<3: 要求180.0s / 開始18:39:05 終了18:42:05 / このprocess内待機28.636s / resumed=True / process_starts=2
HRQ行(隔離台帳)=0 / 隔離attempt_history行=5
注入記録=6行(うちINJECTED=true 6行) / kill記録=['kill_L1.json']

### E3-C Std LR不可(偽T2・是正前) — `run_fzlr_ev_a2_01/a2/full_story_part2_c1` (全判定注入=INJECTED、品質根拠にしない)
status=TERMINAL_NG / phase=LR / n_started=3 / LR.state=NOT_APPLICABLE (NO_USABLE_LR_INPUT) / Lock=HUMAN_REVIEW_REQUIRED cumulative_tts=3 / 費用(この run の cost_log)=¥0.916

| n | block/ordinal | mode | 開始-終了 | verified | ASR判定 | 備考(Style sha/Voice/model) |
|---|---|---|---|---|---|---|
| 1 | 0/1 | ctx | 18:36:01-18:36:05 | False | NG_BOTH | style=4ef87f8e voice=Orus model=gemini-2.5-pro-preview-tts |
| 2 | 0/2 | ctx | 18:36:05-18:36:09 | False | NG_BOTH | style=4ef87f8e voice=Orus model=gemini-2.5-pro-preview-tts |
| 3 | 0/3 | legacy_fallback | 18:39:10-18:39:14 | False | NG_BOTH | style=- voice=Orus model=gemini-2.5-pro-preview-tts |

LR入力: {"n": null, "source": null, "asr_text": null, "skipped": [{"n": 3, "source": "pre_slowdown", "reason": "OVERLAPS_CONFIRMED_CONTENT", "stops": ["T2"], "ng_span": "i killed him fairly"}, {"n": 2, "source": "pre_slowdown", "reason": "OVERLAPS_CONFIRMED_CONTENT", "stops": ["T2"], "ng_span": "i killed him fairly"}, {"n": 1, "source": "pre_slowdown", "reason": "OVERLAPS_CONFIRMED_CONTENT", "stops": ["T2"], "ng_span": "i killed him fairly"}], "reason": "NO_USABLE_LR_INPUT"}

待機(`cooldowns`): n<3: 要求180.0s / 開始18:36:09 終了18:39:09 / このprocess内待機179.954s / resumed=False / process_starts=1
HRQ行(隔離台帳)=1 / 隔離attempt_history行=3
注入記録=6行(うちINJECTED=true 6行) / kill記録=[]

### E3-D Std LR候補全滅(LR発動・7Gate全不合格) — `run_fzlr_ev_a2_04/a2/full_story_part1_c1` (全判定注入=INJECTED、品質根拠にしない)
status=TERMINAL_NG / phase=LR / n_started=3 / LR.state=NOT_APPLICABLE (HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA) / Lock=HUMAN_REVIEW_REQUIRED cumulative_tts=3 / 費用(この run の cost_log)=¥1.212

| n | block/ordinal | mode | 開始-終了 | verified | ASR判定 | 備考(Style sha/Voice/model) |
|---|---|---|---|---|---|---|
| 1 | 0/1 | ctx | 18:57:26-18:57:30 | False | NG_BOTH | style=71079f35 voice=Algieba model=gemini-2.5-pro-preview-tts |
| 2 | 0/2 | ctx | 18:57:30-18:57:35 | False | NG_BOTH | style=71079f35 voice=Algieba model=gemini-2.5-pro-preview-tts |
| 3 | 0/3 | legacy_fallback | 19:00:35-19:00:39 | False | NG_BOTH | style=- voice=Algieba model=gemini-2.5-pro-preview-tts |

LR入力: {"n": 3, "source": "pre_slowdown", "asr_text": "\"I foune him in the bushes this morning,\"", "ng_changed_words": ["found"], "skipped": []}

待機(`cooldowns`): n<3: 要求180.0s / 開始18:57:35 終了19:00:35 / このprocess内待機179.956s / resumed=False / process_starts=1
HRQ行(隔離台帳)=1 / 隔離attempt_history行=4
注入記録=6行(うちINJECTED=true 6行) / kill記録=[]


## 3. 起動時刻一覧(RESTART_STORM規則: 300秒内2回・間隔150秒以上、toolも計上)
`_launch_times.txt`参照。E1=18:23:46(c6 run、1起動のみ)。E3は別run dir(copy-run)で、18:35:55(Std旧)→18:38:44(Adv L1, 自processをkill)→18:41:30(Adv L2 resume)→18:47:08→18:51:19→18:57:20→19:02:13。任意の300秒窓で2起動以内・間隔≥150秒(18:38:44と18:41:30は166秒)。kill(18:40:06)は自分が起動したPIDの意図的終了(`kill_L1.json`)で外部停止ではない。

## 4. 実走で発見・是正した不具合(11-8: 承認済み仕様[確定内容の保護/LR品質条件]との矛盾=不具合、同一委任内で是正)
1. **偽T2による『LR不可』**(E3-C/旧a2_02/a2_03で再現): `er129.level_facts`がLR対象clip本文を文末記号なしでlevel_textへ足し、KP一覧entryと1文に結合 → 確定語句を含む偽の『出典文』と重なり判定 → Std dialogue 8/8 clip(Adv一部)が『確定内容と重なる』でLR不可。是正=台帳と事前保護が**同一関数**`_level_text_from`でlevel_textを組み、群(segments/KP等entry/parts)の境界を文境界化(`er129_lr_display_reflection_01.py`)。test=`test_level_facts_unfinished_quote_clip_is_not_merged_into_kp_list_sentence`(是正前に失敗・是正後PASSを確認)。E3-A(是正後)でLRが実走。藪の中c6(文末`."`)はE1で非該当。
2. **LR候補の二重引用符**(E1 c6・E3-B実測): LR候補生成Prompt(共有・無変更)が原文を`"…"`で囲むため、引用符で囲まれたZセリフでは候補が`""…""`。Z限定の`make_candidate_filter`で原文と同形へ(語列不変)。test=`test_candidate_filter_unwraps_prompt_quote_doubling_only_for_quoted_segments`。E3-A(是正後)でLR Afterが単一引用符。E1 c6の④〜⑥は是正前のため`""…""`のTTS入力(音声への影響は観測されず)。

## 5. Regression(API 0。ログ=`_regression_03.log`)
- 広域: er011/er012_b/er012_e/er012_editorial/er020/er063/er122/er127/er129/er130/er131/er132/er133 = **1393 passed / 7 failed**。
  - 既知6件(委任_02時点と同一集合): er020 fullseg corpus・er063 test_preview_comment_kp_styles・er063_fz_ctx w11b・er129 u8・er131 layer4・er132 public_page_scan(いずれも本委任の差分と無関係。HEAD単独でも失敗/作業木の他者data差)。
  - 追加1件: `er122_fzcw_runtime_evidence_test_01.py::test_e2_forced_ng_1_2_then_cooldown_then_real_legacy_attempt` = バッチ内のみ`RuntimeError: init_logger()が呼ばれていません`(テスト順序依存のlogger状態。単独実行=20 passed、HEAD単独でもPASS)。本委任の差分とは無関係の順序依存flake。
- 新規test(委任_03): `er122_fz_ctx_policy_lr2_test_01.py` +2(level_text文境界/二重引用符) → lr2=27、lr=17、計44 PASS。
- golden: er127 golden(80ケース)・final_adoption_b1 は上記バッチ内でPASS(byte同一)。
- 試験副作用の注意: テスト実行は共有台帳`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`へpytest一時path行(`Are you sure?`)を追記する既存挙動がある(本委任の変更ではない)。E3のHRQ/attempt_historyは隔離台帳(`e3_evidence/*/ledgers`)で、共有台帳を汚していない。
