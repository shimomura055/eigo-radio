# FABLE_ACCEPTANCE_01 — FZ-DIALOGUE-LR-ADOPTION-01 受入検証(委任_04B、API 0・実装編集0。D1: 検証のみ)

## 受入記録:
### (1) ユーザー原文の逐語引用(`docs/pm/delegation_log/2026-10-29_FZ-DIALOGUE-LR-ADOPTION-01_USER.md`)
- L15 「ZセリフにもLRを正式導入し、最大TTS6回の共通フローへ統一する。」
- L36 「最大TTS6回、LR最大1回、180秒待機最大2回。」
- L58 「今回は#1〜#3を再実行せず、LR段階から再開してください。」
- L72 「原作の意味・事実関係を変更しない。」
- L76 「確定済みKey Phrase・Word・文法・日本語訳等を保護する。」
- L100 「正式Production仕様の一覧から「Zセリフ従来方式」の独立行を削除してください。」
- L104 「独立行を削除することと、従来Dialogue Styleそのものを撤去することを混同しないでください。」
- L181 「正式runtime evidenceを取得し、DEV／Trial専用経路の動作だけでPRODUCTION_WIREDと判定しないでください。」
- L232 「最終目標は、Family Zのセリフ音声も他の英語本文・Voiceと同じ最大6回＋LR方式に統一し、今回の『藪の中』を既存3試行の続きから最短で完成候補に戻すことです。」

### (2) 最終成果物・失敗経路
- 配線: Profile `Z_DLG_CTX`(`er127_tts_block_policy_01.py:114`)、state v2(`er122_fz_ctx_policy_01.py` phase B1/LR/B2)、移行tool(`docs/research/FZ-DIALOGUE-LR-ADOPTION-01/tools/fz_dialogue_lr_resume_01.py`)、確定内容保護/表示(`er129_lr_display_reflection_01.py`)。commit d989a6445(実装)/daeee530b(runtime evidence・SSOT)。
- c6(藪の中Adv part3_c6・Puck): state `status=TERMINAL_NG`(`er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/b1b/audit/dialogue_ctx_attempt_state.json:10203`)、Lock=HUMAN_REVIEW_REQUIRED(`er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/b1b/audit/review_lock_state.json:5909`付近)、⑥最終wav=`b1b/narration/full_story_part3_c6.wav`。候補ページv1(`user_test/family_z_in_a_grove_01/`)は据置(c6未決着のため完成stage・v2未実施)。HR試聴ページ=`user_test/family_z_in_a_grove_hr_03/`(委任_04A)。
- 失敗経路: LR不可(入力なし/確定内容と重なる)→TTS追加0でLock+HRQ(E3-C: EVIDENCE_01.md:77)、LR候補全滅→Lock+HRQ(E3-D: :92)、技術STOP→IN_PROGRESS再開可(LR/HRに入れない: CURRENT_SPEC「終端NG1件=HRQ1行」節)。

### (3) 証拠(実測値)
| # | 項目 | 値(file:line) | 判定 |
|---|---|---|---|
| 1 | E1 state v2 | phase=B2(`dialogue_ctx_attempt_state.json:11308`)、n_started=6(:10204)、cycle=2(:11306)、LR UNRESOLVED(:11385)、通算TTS6(Lock `cumulative_tts_attempts=6` review_lock_state.json:5919)。attempts n=1..6のうちn=4〜6が本委任(ctx/ctx/legacy)、LR(An→Some)1回 | OK |
| 1 | Lock/HRQ | Lock state=HUMAN_REVIEW_REQUIRED/final_status=STOPPED。HRQ c6行=1(`human_review_queue.jsonl:151`、grep -c=1) | OK |
| 1 | Gate値 | ①NG_BOTH ②減速後NG ③ASR PASS+d' 0.73s>0.6 ④PASS_WITH_WARNING+d' 0.68s>0.6 ⑤NG_BOTH(sunk) ⑥NG_BOTH(he)。state内 repetition_qa d'値: n=2 0.5 / n=3 0.73 / n=4 0.68 | 記録一致 |
| 1 | LR採用台帳 | LR Before/After: An→Some、7Gate全PASS(EVIDENCE_01.md:39)。最終採用なし(HR) | OK |
| 1 | 180秒待機 | n<3: 179.941s(state:11363)、n<6: 179.944s(:11286/:11377)。process_starts=1(:11288) | 実測180秒 |
| 1 | 起動1回 | E1 18:23:46の1起動のみ(`docs/research/FZ-DIALOGUE-LR-ADOPTION-01/_launch_times.txt:2`)、①〜③の再実行0(EVIDENCE_01.md:22) | OK |
| 2 | E3 4ケース | A Std6スロット(:43)/B Adv途中PASS+kill→resume(:61、待機28.6s・resumed=True・process_starts=2:73)/C LR不可(:77)/D LR候補全滅(:92)。全ケース注入記録の全行 INJECTED=true(:59/:75/:90/:105) | OK |
| 2 | 共有台帳汚染 | 共有`human_review_queue.jsonl`・`er011_output/attempt_history.jsonl`の`fzlr_ev`行=0、`INJECTED`行=0(grep -c実測) | 汚染0 |
| 3 | test | lr 17 + lr2 27 = 44 passed(本受入で再実行) | OK |
| 3 | 既知失敗 | 6件を本受入で再実行: er020 fullseg corpus / er063 test_preview_comment_kp_styles / er063_fz_ctx w11b / er129 u8 / er131 layer4 / er132 public_page_scan = 委任_02時点の集合と同一(EVIDENCE_01.md:117)。+order依存flake1は単独PASS(同:118) | 同一集合 |
| 3 | er127 golden | `git diff d989a6445^ HEAD -- er127_test_golden_01.json er127_test_golden_01.py`=空(byte同一)。er127_tts_block_policy/final_adoption_b1 test PASS(126 passed内) | OK |
| 3 | OPEN-607/608 | `er122_fz_ctx_policy_lr2_test_01.py:460`(level_facts偽T2)、`:491`(二重引用符unwrap)、`:299`(m6隔離) 4 passed | OK |
| 4 | 8区分 | CURRENT_SPEC.md:3183-3193の表(#3=:3186)(#1 Std/#2 Adv/#3 Zセリフ・文脈感情方式[LR○・6回]/#4 JA/#5 KP英語/#6 Adv KP解説/#7 英語固定案内/#8 固定MP3)。「Zセリフ従来方式」独立行なし(grepは3179履歴注記のみ)。`Z_DLG_LEGACY`は:3163で「履歴・独立行なし」と残置注記 | OK |
| 5 | X/Y/narrator/KP/JA不変 | `er063_fz_ctx_wiring_test_01.py::test_w11_x_y_runners_do_not_reference_new_modules_or_hook`(:494)・`test_w11c_style_text_for_and_non_dialogue_keys_unchanged`(:537)・w15・w16 PASS、`er122 test_m6_inject_harness_is_isolated`(:299)PASS。注意: `test_w11b_non_dialogue_generators_source_unchanged_vs_baseline_commit`(:505)は既知失敗(assert set(b)==set(c)、HEAD単独でも失敗=baseline集合差で本委任差分と無関係) | 注意点あり(既知) |
| 6 | 費用 | 藪の中累計¥136.40/Cap145(E1 ¥14.38)。E3 ¥9.03(copy-run別枠、うち不具合再走¥2.07)(EVIDENCE_01.md:9,28) | Cap内 |

### (4) 項目ごとの一致
- フロー ①ctx②ctx→180秒→③従来→LR→④⑤→180秒→⑥→HR: 一致(E1+E3-A)。上限(TTS6/LR1/待機2): 一致(n_started=6、LR1回、待機2回実測)。
- LR段階再開・#1〜#3不再実行: 一致(移行tool→phase=LR、①〜③ cost/attempt_history再実行0)。
- KP保護(sank for ever・on soft feet不変): 一致(LR候補はAn→Someの1語のみ、skip n=2はOVERLAPS_CONFIRMED_CONTENT)。「原作の意味・事実関係不変」: 一致(1語・意味不変)。
- 一覧8区分・独立行削除≠撤去: 一致(表から独立行削除、従来Dialogue Styleは③⑥のFallbackとして現役、Z_DLG_LEGACY履歴残置)。
- 自然evidence=E1(Adv c6)・注入=E3(Std/Adv): 一致、混同なし(E3は全記録INJECTED、品質根拠にしない)。X/Y不変: 上記テスト一致(既知失敗w11bを除く)。
- 表示§6(候補ページのLR Before/After赤字・Fallback濃い青): **未確認**(候補ページ未生成のため。採用後のページ生成時に確認)。
- OPEN-608(二重引用符`""…""`)の④〜⑥入力への影響: **未観測**(④の読み誤りは別原因、音声への影響は観測されず)。
- 目的「藪の中を既存3試行の続きから最短で完成候補に戻す」: **未達**(c6はHR)。

### (5) 判定
- **配線: ACCEPTED(PRODUCTION_WIRED)可。** Fable基準(上記1〜5が成立、本件起因の失敗なし)を満たす: 正式経路でE1自然発火+E3注入の双方で6回フロー/LR1回/待機2回/Lock+HRQ1行/resume/失敗経路を実測。c6のHRは仕様どおりの正常通過(区分A)で配線不具合ではない。既知失敗6件は本件差分と無関係かつ同一集合。w11bは既知失敗(留意、OPEN化済み既存事項としてFableが扱う)。表示§6はc6決着後の候補ページ生成で確認する条件付き残件(受入阻害でない)。
- **記事目的: 部分達成(配線達成・c6未達)。** 完成候補への復帰はユーザー判断(UDR #220: ③/④試聴採用 or 再生成承認[¥15〜19、累計¥160に接近]、OPEN-594閾値)待ち。
判定整合: 重大NG=なし / 主因=ASR/repetition QA(③④はd'のみ超過、⑤⑥は読み誤り) / 是正対象=OPEN-607/608(FIXED) / STOP理由=なし / 提示=可
