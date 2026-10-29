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

