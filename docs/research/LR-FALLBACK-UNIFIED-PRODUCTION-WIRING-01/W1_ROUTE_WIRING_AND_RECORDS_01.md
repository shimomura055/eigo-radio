# W1_ROUTE_WIRING_AND_RECORDS_01(LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_01 / Phase A、読取専用・API 0・JPY 0、2026-10-28)

原文: `docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §6・§7・§10。共通事項: `…_委任_00_COMMON.md`。
実施したのは保存データ・コード・docsの読取と、scratchpad上の読取専用json集計のみ(Production code/test/SSOT/script変更なし、API・TTS・ASR 0)。
凡例: 【静的】=コード読解のみ / 【実走】=保存evidence(`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/evidence_runs`等)で観測 / 【未確認】=確認できていない(推測で埋めない)。

---
## 0. 結論(Phase B実装・Fable統合への重要度順)

1. **§7の代表仕様(回数・待機・Fallback Style・LR範囲)と現行Production配線は、49経路すべてでコード上一致。旧仕様のDangling Referenceは「実行コード上は0件」**。旧600秒は`er020.LEGACY_COOLDOWN_SECONDS`(A/B/C専用)にのみ残り、X/Y/Z専用moduleからの参照は0件(Grep)。残るのはコメント/docstring中の「10分」文言のみ(§1-3 DR-1、実害なし)。統一flowの発動判定は単一関数`er127.unified_flow_active()`(`er127_tts_block_policy_01.py:129-134`、`er109_xz_scope_01.current_scope()`がX/Y/Z)。
2. **最終Human報告の“入力記録”は経路ごとに形が違い、そのままでは「最終採用音声のLR/Fallback状態」を一意に読めない**。主因3点(§2-3): (a) Fallbackの記録先が経路ごとに別キー(X Std/Adv英語=`fallback_attempts_log`/`instruction_type`、JA=`instruction`文字列のみ、KP英語=`english_lock_attempts_log`(`fallback_attempts_log`は前段の記録=命名が逆)、KP解説=`fallback_attempts_log`+gate evidence、Z会話=`dialogue_tts.final_mode`、Z narrator=`attempts[].phase/instruction_label`) (b) 採用attemptを示す統一キーが無く、**LR発動時に未採用の③(Fallback)がattempt列に残るため、最終Styleの誤表示リスクが実在**(Z実証: `style.fallback_used=False`なのに③が`minimal_fallback`でNG、採用は①'。Xは旧run `fallback_used=True`だが採用はLR①'のrole Style) (c) LR差分の粒度がX(`changed_span_before/after`あり)とZ(`diff_summary`文字列のみ)で不揃い。→ **統一記録`final_adoption`(採用attempt・採用Style・切替元・LR before/after/span・対象segment/chunk)の追加が必要**(§2-4、設計提案のみ)。
3. **runtime evidenceは既存の承認済みdriver(`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_*.py`)が再利用可能**(判定結果のNG方向のみ注入、Style/Prompt/Voice/速度/回数/待機は不変)。過去実費は1case ¥0.13〜2.5(Y y_voice系のみ¥4.8〜8.6)、全case合計¥86.6(`COST_01.md:7-13`)。Phase Bのrecord伝搬検証は代表10〜12caseの有料最小で足り、見積¥10〜40(§3、Production既定動作は変えない)。「自然発生待ち」に頼る必要はない。
4. **既存実runの再利用**: 最終Human報告の表示検証(赤/濃青)の入力にできる実runは、記録の完全性で分類(§4)。**AI島hr_02・Y run_01は旧コード(F1/F2/OPEN-564是正前)で保存されており記録に既知欠陥あり**(`fallback_used`誤、Std `LR_REWRITTEN`警告欠落、BlockProgress depth1欠落)→表示検証には「LR・Fallbackとも実記録あり」のtru_ev evidence run(X/Y/Z全Family・Lv)が使える。
5. **A/B/C**: 方式置換禁止。leaf関数は共通(scope外=`_blk=None`で従来コード)で、entry直下の`fallback_used`/`instruction_type`/`local_rewrite_recovery`/`attempts_log`は同形。最終Human報告の適用は「entry直下キーの読取のみ」で可、BlockProgress・`final_adoption`(新設)・Z `dialogue_tts`は対象外(§1-4)。

---
## 1. 49経路 × 現行Production配線の照合表

### 1-1. policy実装(正)
- `er127_tts_block_policy_01.py:108-117` `PROFILES`(EN_LR_STD/ADV=3回・待機(3,)・短文EN・LR可・計6/6/待機2、JA_STD=3・短文JA・LR不可・3/3/待機1、KP_EN=4・ENGLISH_LOCK・LR不可・4/4/1、KP_EXPL=3・短文EN・LR不可、Z_DLG_CTX=3・LEGACY_DIALOGUE、Z_DLG_LEGACY=3・SAME、SHELL_EN/NO_TTS=`unified=False`)。`COOLDOWN_SECONDS=180.0`(`:30`)。LR再入禁止=`LocalRewriteReentryError`(`lr_recover` `:626-646`、`blk.depth>=1`)。
- 判定の流れ(全leaf共通): `@er127.with_block(leaf)`(`:509-550`)→`open_block`(`:490-506`)→`block_policy_for`(`:144-171`、冒頭`:149`で`unified_flow_active()`。scope外=None=従来コード、scope内で未解決=`BlockPolicyError`=fail-closed)。
- 安全網: `er020_tts_retry_local_rewrite_01.py:85,173`(scope内で旧600秒関数に到達しても180秒+STOP確認へ)。scope設定=各runnerのTTS段入口decorator `er109_scope.family_scope("X"|"Y"|"Z")`(X:`er019_family_x_audio_production_runner_01.py:1534,1901`/Y:`er121_family_y_audio_01.py:550,639`/Z:`er063_family_z_audio_01.py:1504`)。
- leaf→with_block対応(file:line=decorator行): L1 `er003_v1_sing01_voice01_generate.py:50`(Charon英語)/L2 `er003_v1_sing01_news_tail_fix.py:64`(Adv本文)/L3 `er003_v1_crosslevel_audio_02_common.py:96`(Std英語。Std本文は減速hook付きで同関数)/L5 `er019 runner:1297`(`_kp_explanation_unified`。入口`generate_key_phrase_explanation_en_verified:1281`が`er127.unified_flow_active()`で分岐)/L6 `er003_v1_repro01_main_generate.py:824`・`er019_family_x_kp_en_k2_store_01.py:56`・`er063:1075`(K2二段)/L7 `er003_v1_n3_01_tts_generate.py:762`(a2日本語)・`er003_v1_sing01_voice01_generate.py:526`(固定shell日本語)/L8 `er012_b_family_voices_production_01.py:484`(`z_policy=lambda a:"legacy"`、`skip_when=attempt_hook is not None`)。Std本文の減速+再検証をattempt内へ入れる分岐=`er003_v1_n3_01_tts_generate.py:441`(`er127.unified_flow_active()`)→`_generate_a2_segment_with_slowdown_unified:369-392`。
- Z会話(文脈・感情付き)はer127の`with_block`をskip(`skip_when`)し**独自policy**: `er122_fz_ctx_policy_01.py:29-32`(`MAX_TOTAL_ATTEMPTS=3`、`POLICY_CTX`)・`:43-45`(180秒=`er127.COOLDOWN_SECONDS`参照)・`:97-115`(`resolve_run_policy`: 既存run state有=legacy固定/新規=ctx)。③=従来Dialogue Style=`:291`(`mode="ctx" if n<=CTX_ATTEMPTS else "legacy_fallback"`)。呼出=`er063:915-960`(`generate_dialogue_ctx`)。

### 1-2. 49行の照合(ID網羅=`ROW_MAPPING_01.json`の49 ID)

呼出箇所(file:line)は「経路→leaf」。unified判定は全行が`block_policy_for`(`er127:149`)経由(例外は§1-1記載のZ ctx独自policy・L5入口・Std減速分岐)。`runner`=`er019_family_x_audio_production_runner_01.py`、`er121`=`er121_family_y_audio_01.py`。evidence列=既存`evidence_runs`の実走case(【実走】。「同leaf」は同じleaf・同policyの別caseで実走済み)。

| ID | Family/Lv・部位 | 呼出箇所→leaf | policy(`PROFILES`) | §7一致 | evidence |
|---|---|---|---|---|---|
| X-S01 | X Std topic_intro | `runner:2038-2042`→L3 | EN_LR_STD | 一致 | X-Std-1b/2/3 |
| X-S02 | X Std 日本語(title/preview/comment/KP意味) | `runner:2049-2053,2067-2071,2196-2200`→`n3_tts.generate_a2_japanese_with_reading_safety:901`→L7(`n3_tts:762`) | JA_STD | 一致 | X-Std-6/7 |
| X-S03 | X Std shell固定日本語『ポイント解説』 | `er006_audio_cost_pilot_02_shared_narration.py:236-243`→`voice01.generate_charon_japanese`(L7 `voice01:526`) | JA_STD | 一致(`max_attempts=6`を渡すが関数内で3にclamp。DR-3) | **未実走**(JA title系で同leaf代替) |
| X-S04 | X Std full_story_part1〜3(減速6%) | `runner:2092-2100`→`n3_tts.generate_a2_segment_with_slowdown:394`→(`:441`)→L3+減速hook | EN_LR_STD | 一致 | X-Std-4/5/12 |
| X-S05 | X Std full_story chunk _k{j} | `runner:1478-1495`(`_generate_x_body_part_chunked_a2`)→同上 | EN_LR_STD | 一致 | X-Std-12 |
| X-S06 | X Std in_one_line | `runner:2092-2100`(同loop)→同上 | EN_LR_STD | 一致 | X-Std-5 |
| X-S07 | X Std KP英語 | `runner:2184-2194`→`_kp_english_generate_fn:1767`→L6(K2=`kp_en_k2_store:56`/default=`kp_vote…`→`repro01:824`) | KP_EN | 一致 | X-Std-8/9 |
| X-A01 | X Adv topic_intro | `runner:1612`→L1 | EN_LR_ADV | 一致 | X-Adv-14b |
| X-A02 | X Adv preview | `runner:1629-1637`→L1 | EN_LR_ADV | 一致 | X-Adv-14/14b |
| X-A03 | X Adv comment_1〜4 | `runner:1629`→L1 | EN_LR_ADV | 一致(disfluencyのみNG=NO_NG_SPANで即HR) | X-Adv-1/2/3c/4 |
| X-A04 | X Adv full_story_part1〜3 | `runner:1666-1670`→L2 | EN_LR_ADV | 一致 | X-Adv-12/13 |
| X-A05 | X Adv full_story chunk | `runner:1462-1466`(`_generate_x_body_part_chunked`)→L2 | EN_LR_ADV | 一致 | 同leaf(X-Adv-12) |
| X-A06 | X Adv in_one_line | `runner:1666-1670`→L2 | EN_LR_ADV | 一致 | X-Adv-6/16 |
| X-A07 | X Adv KP英語 | `runner:1829-1841`→L6 | KP_EN | 一致 | X-Adv-10/11 |
| X-A08 | X Adv KP英語解説 | `runner:1867-1870`→`:1281`→`_kp_explanation_unified:1297`(L5) | KP_EXPL | 一致 | X-Adv-7/8/9 |
| X-A09 | X shell固定英語9 | `shared_narration.py:232`→`voice01.generate_charon_english`(`SHELL_EN_ID_RE`で`unified=False`=従来) | SHELL_EN | 一致(既存維持) | 未実走(表外) |
| Y-S-01 | Y Std shell固定英語9 | `er121:674`→同上 | SHELL_EN | 一致 | 未実走(表外) |
| Y-S-01b | Y Std shell固定日本語 | `er121:674`→`shared_narration:243` | JA_STD | 一致(X-S03と同) | 未実走 |
| Y-S-02 | Y Std topic_intro | `er121:684`→L3 | EN_LR_STD | 一致 | Y-Std-1 |
| Y-S-03 | Y Std japanese_title | `er121:695`→L7 | JA_STD | 一致 | Y-Std-2b |
| Y-S-04 | Y Std 日本語 preview/comment | `er121:705`→L7 | JA_STD | 一致 | 同leaf(Y-Std-2b) |
| Y-S-05 | Y Std ナレーター本文5(減速) | `er121:724`→L3+減速hook | EN_LR_STD | 一致 | Y-Std-4/4b |
| Y-S-06 | Y Std Voice本文3 | `er121:724` | EN_LR_STD | 一致 | Y-Std-4/4b |
| Y-S-07 | Y Std 本文chunk | `er121:527`→L3+hook | EN_LR_STD | 一致 | **未実走**(`EVIDENCE_01.md`に「YのE-S3/chunk経路」未観測と明記) |
| Y-S-08 | Y Std KP英語 | `er121:744`→`xr._generate_key_phrase_segments_a2`→L6 | KP_EN | 一致(前段=MINIMAL。U-15別件) | Y-Std-3 |
| Y-S-09 | Y Std KP日本語意味 | 同上→L7 | JA_STD | 一致 | 同leaf |
| Y-B-00 | Y Intro/Notification/Outro固定mp3 | TTS呼出なし | NO_TTS | 一致(生成なし) | — |
| Y-B-01 | Y Adv shell固定英語 | `er121:564` | SHELL_EN | 一致 | 未実走(表外) |
| Y-B-02 | Y Adv topic_intro | `er121:575`→L1 | EN_LR_ADV | 一致 | 同leaf(Y-Adv-1) |
| Y-B-03 | Y Adv preview/comment_1/3 | `er121:587`→L1 | EN_LR_ADV | 一致 | Y-Adv-1 |
| Y-B-04 | Y Adv ナレーター本文5 | `er121:608`→L2 | EN_LR_ADV | 一致 | Y-Adv-4/4b |
| Y-B-05 | Y Adv Voice本文3 | `er121:608`→L2 | EN_LR_ADV | 一致(U-03最頻) | Y-Adv-4b |
| Y-B-06 | Y Adv 本文chunk | `er121:499`→L2 | EN_LR_ADV | 一致 | **未実走**(chunk経路) |
| Y-B-07 | Y Adv KP英語 | `er121:627`→L6 | KP_EN | 一致 | Y-Adv-3 |
| Y-B-08 | Y Adv KP英語解説 | `er121:627`→`runner:1281`→L5 | KP_EXPL | 一致 | Y-Adv-2 |
| Z-A2-NARR | Z Std 地の文(+100語超chunk) | `er063:1021`→`generate_a2_segment_with_slowdown`→L3+hook | EN_LR_STD | 一致 | Z-Std-1 |
| Z-A2-DIALOGUE-CTX | Z Std セリフ(ctx) | `er063:1029`→`generate_dialogue_ctx:915-960`→`er122` policy(L8 skip) | Z_DLG_CTX | 一致(②NG後180秒→③=従来Dialogue Style、LRなし) | Z-Std-2 |
| Z-A2-DIALOGUE-LEGACY | Z Std セリフ(legacy) | `er063:1041`→L8(`er012_b:484`、`z_policy="legacy"`) | Z_DLG_LEGACY | 一致(Style不変) | **未実走**(unit/golden testのみ) |
| Z-A2-TOPIC | Z Std topic_intro_en | `er063:1051`→L3 | EN_LR_STD | 一致(`er020`でU-06: `topic_intro_en`はscope内のみTOPIC_INTRO、`er020:~171-175`) | Z-Std-6 |
| Z-A2-JA | Z Std 日本語(title/preview/comment) | `er063:1059`→L7 | JA_STD | 一致 | Z-Std-4 |
| Z-A2-KPEN | Z Std KP英語 | `er063:1075`(K2二段)→L6 | KP_EN | 一致 | Z-Std-5 |
| Z-A2-KPJA | Z Std KP日本語意味 | `er063:1120`→L7 | JA_STD | 一致 | 同leaf(Z-Std-4) |
| Z-B1B-NARR | Z Adv 地の文(+chunk) | `er063:1017`→L2 | EN_LR_ADV | 一致 | Z-Adv-1 |
| Z-B1B-DIALOGUE-CTX | Z Adv セリフ(ctx) | `er063:960`(外側loopで減速後再検証。通算3回共有) | Z_DLG_CTX | 一致 | Z-Adv-2/3/3b |
| Z-B1B-DIALOGUE-LEGACY | Z Adv セリフ(legacy) | `er063:1035`(外側loop+L8) | Z_DLG_LEGACY | 一致 | **未実走** |
| Z-B1B-TOPIC | Z Adv topic_intro_en | `er063:1044`(`charon_en`)→L1 | EN_LR_ADV | 一致 | Z-Adv-4 |
| Z-B1B-PREVCOM | Z Adv preview/comment | `er063:1044`→L1 | EN_LR_ADV | 一致 | 同leaf(Z-Adv-4) |
| Z-B1B-KPEN | Z Adv KP英語 | `er063:1075`→L6 | KP_EN | 一致 | Z-Adv-6 |
| Z-B1B-KPEXPL | Z Adv KP英語解説 | `er063:1115`→`runner:1281`→L5 | KP_EXPL | 一致 | Z-Adv-5 |

照合結果: 一致49/49(静的)。evidence観測(同leaf含む)=39行、**未実走=9行**(X-S03・X-A09・Y-S-01・Y-S-01b・Y-S-07・Y-B-01・Y-B-06・Z-A2-DIALOGUE-LEGACY・Z-B1B-DIALOGUE-LEGACY。うち表外のSHELL_EN 3行は既存方式維持)、生成なし1行(Y-B-00)。未実走9行の追加evidence案は§3-2。

### 1-3. Dangling Reference候補(列挙のみ・修正しない)
| ID | 箇所 | 内容 | 判定 |
|---|---|---|---|
| DR-1 | `er003_v1_sing01_voice01_generate.py:67,219` `er003_v1_sing01_news_tail_fix.py:202` `er003_v1_repro01_main_generate.py:259` `er020_tts_retry_local_rewrite_01.py:7,10,75-76`(コメント/docstring) | 「10分cool-down」等の旧待機の記述。scope外(A/B/C)の旧挙動の記述としては正しいが、X/Y/Z読者に旧仕様と誤読される | C(実害なし) |
| DR-2 | `er020:62-63` `LEGACY_COOLDOWN_SECONDS=600`と別名`COOLDOWN_SECONDS` | A/B/C専用(byte同一維持)。X/Y/Z専用moduleの参照: Grep 0件(非test)。静的testで固定済み(`er020:61`注記) | 残置が正(撤去不可=A/B/C golden) |
| DR-3 | `shared_narration.py:243` `generate_charon_japanese(..., max_attempts=6)` と `er127.BlockRun.max_attempts`(`:408`) | shell日本語は6を渡すが関数内で`min(max_attempts,3)`(`voice01:~570`)。`BlockRun.max_attempts`は代入のみで参照0(Grep)。実回数は3で§7一致 | C(死んだフィールド) |
| DR-4 | `er063:224-232`のplan "path"文言・`er122:8-9` | 「旧600秒」等は変更履歴の説明として残存 | C(コメントのみ) |
| DR-5 | `er122_fz_ctx_policy_01.py:360,371` `tts_mode_effective="minimal_fallback_in_{ctx\|legacy}_attempt"` | Z会話③で内側ループが短文Styleへ落ちる旧経路の記録名。③は`max_attempts=policy.remaining()=1`(`er063:940`)で内側fallbackに入らない設計のため発火しない想定 | 【静的】のみ・未実走=【未確認】(C) |
| DR-6 | KP_EN記録キーの命名逆転(`er063:1111-1113`) | `fallback_attempts_log`=前段(K2/MINIMAL)の記録、`english_lock_attempts_log`=ENGLISH_LOCK段(実Fallback)。名前と中身が逆(legacy互換) | **最終Human報告が`fallback_attempts_log`を素直に読むと前段Styleを「Fallback」と誤表示する**(§2-3 G-3)。B(Fable判断=読み方の統一規則) |

撤去・残置の旧規則Grep: `unified_flow_active`の呼出(非test)=`er003_v1_n3_01_tts_generate.py:441`・`er019 runner:1281`・`er020:85,173`・`er127:129,149`のみ。

### 1-4. A/B/C Family(対象外=方式置換禁止)の記録構造確認
- A/B/Cは**scope外**(`current_scope()=None`)→`with_block`は`_blk=None`で従来コード(旧600秒・Fallback後LR1回構成=`er003_v1_crosslevel_audio_02_common.py:299,329`等の旧経路)。BlockProgress(`tts_block_progress/*.json`)・`BlockCtx`・Z`dialogue_tts`は**生成されない**。
- entry直下の記録形はX/Yと同一leaf関数のため同形: `fallback_used`・`instruction_type`(`minimal_fallback`)・`style_prefix`・`attempts_log`・`fallback_attempts_log`・`local_rewrite_recovery`・`canonical_text_before_local_rewrite`。保存A/B/C系`tts_generation_results.json` 52件の走査(scratchpad集計、`er013/er012/er003/er014_output`): `local_rewrite_recovery`含有0件・`minimal_fallback`または`fallback_used:true`含有18件。
- 判定: 最終Human報告の「LR=赤/Fallback=濃青」の適用は、entry直下キーを読む限り**追加記録なしで技術的に可能**。ただし(a)`final_adoption`(新設)は載らない=旧キーからの導出縮退ルールが必要 (b) A/B/CのLR採用時`fallback_used`はOPEN-564是正前の挙動(scope外は未変更)→採用attemptは`attempts_log`の`verified`行から導出する。適用範囲は**表示(読取)のみ**とし生成・Gate・待機の変更は含めない(判断候補J-5)。

---
## 2. 発動記録の所在表(経路 × 記録)

### 2-1. 共通の記録ファイル(X/Y/Z)
| 記録 | path/キー | 内容 | 書込元 |
|---|---|---|---|
| segment entry | `<run>/<lv>/audit/tts_generation_results.json` `segments.<seg>` / `key_phrases.<n>.{english,japanese_meaning,explanation}` | 採用音声のtop-level記録+attempt列 | 各leaf return |
| BlockProgress | `<run>/<lv>/audit/tts_block_progress/<seg>.json`(`schema tts_block_progress_v1`) | `blocks["0"].attempts.<n>.{started,finished,verified}`、`cooldown`、`lr.{used,text,text_sha}`、`final_status` | `er127.BlockProgress`(`:239-387`、`save_lr_text :359-362`) |
| chunk evidence | `audit/chunk_tts_evidence_<lv>.json` `parents.<id>.chunks[]` | chunk別`status/voice/local_rewrite_recovery`(全文コピー)。**`instruction_type`/`style_prefix_sha256`/`attempt_count`が実run(AI島)でNone/0**=Fallback採用の識別に使えない | `er019 runner:~1429`系 |
| style gate | `audit/style_profile_gate.json`(X M3)/Y Gate/Z Gate | `blocked[].violations`(`LOCAL_REWRITE_RECOVERY`・`STD_FALLBACK_USED_OR_UNKNOWN`等) | `er019_family_x_style_profile_01.py:685-760`、`er121:895-945` |
| 事後試聴 | `audit/pass_with_warning_listening_list.json` `entries[]` | `segment_id/role/warning_labels/canonical_text/primary_text/secondary_text`(`LR_REWRITTEN`警告で識別) | AUW |
| LR監査コピー | `er011_output/local_rewrite_recovery/<theme>/<lv>/local_rewrite_recovery_<seg>.json`・`er011_output/attempt_history.jsonl`(`action:LOCAL_REWRITE_RECOVERY`) | LR一式 | `er020:757-834` |
| LR重なり記録 | `audit/confirmed_kp_lr_overlap.json` | 確定KPとLR範囲の重なり(記録のみ) | `er128:1262`(`note_lr_fired`) |
| タイムライン | `audit/timeline.json`(assemble成功後のみ) | 区間の時刻。**ユーザー原文§6「時刻の表示不要」→区間はsegment/chunk/本文範囲で足りる** | `er019 runner:2592` |
| Z style記録 | `audit/style_record.json`(role別承認Style)・`segments.<id>.style`・`attempts[]` | role Style承認値/clip実測 | `er063:1154-1185,1985-2035` |

### 2-2. 経路別「(a)LR / (b)最終採用のFallback / (c)非採用試行のFallback」の所在
採用attemptの識別: X/Y(`er127`系)は**merge済み`attempts_log`/`standard_attempts_log`/`fallback_attempts_log`の`verified:true`行**と`local_rewrite_recovery.retts_result`(LR採用時)。HEAD(是正commit `7dab92aba`以降)では`_merge`が`fallback_used`を採用attempt種別に従わせる(`er003_v1_crosslevel_audio_02_common.py:477-480`)。

| 経路(policy) | (a)LR発動・前後英文・差分・区間 | (b)最終採用のFallback有無・採用Style名・切替元 | (c)未採用試行のFallback(区別要) | 欠落/誤読リスク |
|---|---|---|---|---|
| X Std英語 EN_LR_STD(L3/L4: topic/本文/chunk/in_one_line) | segment entry `local_rewrite_recovery.status`・`.selection.selected.{rewritten_segment,changed_span_before,changed_span_after}`・`canonical_text_before_local_rewrite`(元)/`text`(LR後)・`.retts_result`。区間=segment_id(chunkは`_k{j}`)+`ng_span.canonical_span_with_context` | ③採用: `fallback_attempts_log[-1]`の`style_prefix{len,sha256}`+`instruction_label`(flash-lite=`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、`voice01:169`/structured=`MINIMAL_INSTRUCTION_PREFIX`)、切替元=`style_profile.expected_base_sha256`/標準attemptの`style_prefix.sha256`。LR採用時は`retts_result.attempts_log`(①'②'=role Style、③'=Fallback)と`retts_result.fallback_used`で判定 | `standard_attempts_log`(①②)+元③が`fallback_attempts_log`に残る(`merge_logs`で結合)。**採用はLR block内のattempt**=`retts_result` | 旧run(AI島 hr_02)は`fallback_used:true`(OPEN-564是正前)かつ`blocks["1"]`欠落・`LR_REWRITTEN`欠落(是正はHEAD)。chunk evidenceにStyle無し |
| X Adv英語 EN_LR_ADV(L1/L2) | 同上(`instruction_type`は`minimal_fallback`/`english_style_prefix_wide_margin`をentry直下) | entry直下`instruction_type`(`minimal_fallback`=③採用)+`style_prefix`(全文)。切替元=`style_profile.expected_base_sha256` | 未採用③は`attempts_log`の`instruction_type`で識別(entry直下`instruction_type`は最終採用のもの) | LR採用+③NGの元試行が`attempts_log`に混在→「直近行=採用」と仮定すると誤り |
| X/Y/Z 日本語 JA_STD(L7) | LRなし | **entry直下`instruction`文字列**(例`minimal (not JAPANESE_STYLE_PREFIX)`)+`fallback_used`。`fallback_attempts_log`の行に`style_prefix`/`instruction_label`は**無い**(keys: attempt/status/asr_text/…/attempt_audio_path。`x_std_6`で確認) | `standard_attempts_log`(①②)のみ。③NGなら`status`≠OK | JAのFallback Style名はentry直下`instruction`文字列のみ(切替元名は【未確認】) |
| X/Y/Z KP英語 KP_EN(L6) | LRなし | **`english_lock_attempts_log`が実際のENGLISH_LOCK段**(`er063:1111-1113`)。entry直下`fallback_used:true`=ENGLISH_LOCK段へ入った事実、`primary_instruction_type:ENGLISH_LOCK`。採用は`english_lock_attempts_log`の`verified`行 | `fallback_attempts_log`=**前段K2/MINIMAL(②までの記録)**(命名逆転。`x_std_8`で確認: style sha 9d905c…=K2/len 332)。`minimal_attempts_log`も前段 | `fallback_attempts_log`をそのまま「Fallback」と読むと前段Styleを誤表示(DR-6)。Master Audio Store再利用時はkey B(`instruction_path=english_lock_fallback`、`er019_family_x_kp_en_k2_store_01.py:10-12`)で別管理。manifestにkey B 0件(`primary`のみ集計)→再利用音声は常に前段採用 |
| X/Y/Z Adv KP解説 KP_EXPL(L5) | LRなし | `explanation.fallback_used`・`fallback_attempts_log`(③=短文Style)・`style_profile`。Style名は`style_profile`/gate evidence(`MINIMAL_INSTRUCTION_PREFIX`) | `attempts_log`(①②)。③NG時`STOPPED` | **W2 F4: Adv③NG attemptのStyle未記録**(`W2_SIX_ROUTES_01.md`参照)。終端(未採用)のためHR資料にのみ影響。Gate evidence(X-Adv-7: `FINAL_STYLE_SHA_MISMATCH_NO_HINT`)は**正常Fallbackでも発火**=UD-3の対象 |
| Z narrator Std/Adv(L3/L2、chunk含む) | `segments.<id>.audio_text_deviation.{canonical_text_before_local_rewrite,audio_text_after,diff_summary}`・`provenance.audio_text_deviations[]`(`er063:1686-1699`)。`changed_span_*`は無く`diff_summary`文字列(`replace: 'topic' -> 'subject'`)のみ。親行notesは`deviation_chunks`を集約(`er063:2464-2468`) | `attempts[]`(`phase/attempt/instruction_label/instruction_type/verified`、`er063:1154-1185`)。Adv③=`minimal_fallback`。`build_style_actual_record`(`er063:1993-2035`)は「fallback段→標準段の順で最後にstyle記録を持つattempt」を採用attemptとして扱う | `attempts[]`内の`verified:false`の`minimal_fallback`行 | **実証(`run_tru_ev_z_adv_4` topic_intro_en)**: `style.fallback_used=False`・`fallback_attempts=[]`だが`attempts[]`に③`minimal_fallback`(NG)+④採用①'(`english_style_prefix`,verified)。LR採用時に`build_style_actual_record`が未採用③Styleを「実測」とする可能性=【静的】(未実走確認) |
| Z会話 Z_DLG_CTX | LRなし | **`segments.<id>.dialogue_tts.{policy,final_mode,final_attempt_n,n_started,attempts[].{n,mode,effective_mode,verified}}`**(`er063:~950-975`、`er122:361-371`)。`final_mode=legacy_fallback`が③採用=従来Dialogue Styleへ切替 | `dialogue_tts.attempts[]`のverified=false行(mode=ctx) | **`segments.<id>.style.fallback_used`は`False`のまま**(実証`run_tru_ev_z_std_2`: `dialogue_tts.final_mode=legacy_fallback`なのに`style.fallback_used:False`)→`dialogue_tts`を読まないと切替を見落とす |
| Z会話 Z_DLG_LEGACY | LRなし | Style不変(③も同一Style)→**切替なし**(§6-B「Styleが変わらない再試行は表示しない」に該当) | — | 判定は`dialogue_tts`無し/`policy==legacy`かつStyle同一 |
| 共通(全行) | LR後英文=`segments.<id>.text`、元=`canonical_text`/`canonical_text_before_local_rewrite`。**対象音声区間=segment_id/chunk id**(§6は時刻不要) | | | 本文反映(UD-1)用の`changed_span_*`はXのみ。Zは`diff_summary`のみ(span復元は文字列diffのパースが必要) |

### 2-3. 欠落・誤読リスクの一覧(最終Human報告へ伝搬させるうえでの障害)
| ID | 内容 | 根拠 | 区分 |
|---|---|---|---|
| G-1 | 採用attemptを示す統一キーが無い(LR採用時は元ブロックの③とLR blockの①'…が同じ列に並ぶ) | `er127.lr_recover :626-702`が`merge_logs`でstd/fallback logを結合(`crosslevel :477-483`)。`final_adoption`相当は無い | 追加記録が必要(§2-4) |
| G-2 | Z narrator/dialogueのtop-level `style.fallback_used`が実際のFallbackを反映しない | `run_tru_ev_z_adv_4`・`run_tru_ev_z_std_2`(上表) | 追加記録or読取規則 |
| G-3 | KP_EN `fallback_attempts_log`の命名逆転 | `er063:1111-1113` | 読取規則(B) |
| G-4 | W2 F4: Adv KP解説③NG attemptのStyle未記録 | `W2_SIX_ROUTES_01.md` §5 F4。③NG=終端のため最終採用音声には影響せず、終端HR資料のみ | 追加記録候補(重要度低) |
| G-5 | JAのFallback Style名がentry直下`instruction`文字列のみ | `x_std_6` entry | 追加記録 or 名称マップ(C) |
| G-6 | chunk evidenceにStyle/attempt記録なし(`instruction_type:None`、`attempt_count:0`) | AI島a2 `chunk_tts_evidence_a2.json` `parents.full_story_part1.chunks[1]` | chunk単位のFallbackは親segment entryまたはBlockProgressから拾う必要 |
| G-7 | LR差分の粒度がZでは`diff_summary`のみ | `er063:1218-1232`・上表 | 「変更語句」表示に`changed_span_*`同等が必要 |
| G-8 | 旧コード保存runの既知欠陥(`fallback_used`誤、Std `LR_REWRITTEN`欠落、`blocks["1"]`欠落): F1/F2/OPEN-564はHEADで是正済み(`FIX_A_01.md`)、ただし`blocks["1"]`(depth1記録)の復元は未達(W1_LR_DATAFLOW S-3) | 保存AI島runと`FIX_A_01.md` | 旧runは再生成せず読取側で補正(§4) |
| G-9 | 人間承認(HR採用)で音声が原文に置換されたrunのLR記録(Y run_01 `y_voice_1`)は「LR発動」が残るが**最終採用音声は原文** | `er121_e1_hr_adopt_r0_01.py:147`・`er020:852-868`・W4 #37/#38 | 表示で「LR発動履歴あり/最終音声は原文採用」を区別(§6-C) |
| G-10 | Store再利用(KP phrase・固定殻)でFallback採用有無が音声側に保存されない | manifest key `instruction_path`が`primary`のみ(366+118+35+3件) | KP reuse時に元entryの記録を参照できるか【未確認】 |

### 2-4. 最終Human報告へ伝搬させるために追加記録が必要な項目(設計提案のみ・実装しない)
**`final_adoption`(segment/chunk entry直下、全経路共通の1キー)の新設**を提案する。既存キーの意味は変えず追加のみ(既存Gate/Validatorは不変)。
| キー | 内容 | 導出元(既存) |
|---|---|---|
| `final_adoption.adopted_phase` | `standard`/`fallback`/`lr_standard`/`lr_fallback`/`ctx`/`legacy_fallback`/`english_lock` | merge済み`verified:true`行・`retts_result`・`dialogue_tts.final_mode`・`english_lock_attempts_log` |
| `final_adoption.adopted_style` | `{name, sha256, source}`(name=承認済みStyle名 or `ENGLISH_LOCK`/`EN_MINIMAL`/`JA_MINIMAL`/`LEGACY_DIALOGUE`) | 採用attemptの`style_prefix`/`instruction_label`/`instruction`/`dialogue_tts` |
| `final_adoption.switched_from` | `{name, sha256}`(通常Style)。**Styleが同一なら`null`**(§6-B) | `style_profile.expected_base_sha256`/`style_record.json` |
| `final_adoption.fallback_scope` | segment_id/chunk_id/本文範囲 | 親segment/chunk plan |
| `final_adoption.lr` | `{fired, before_text, after_text, spans:[{before,after}], status, adopted(bool。HR採用で原文に戻ったらfalse)}` | `local_rewrite_recovery.selection.selected`(X)・`audio_text_deviation`(Z。spanは`diff_summary`のパース or LR側で`changed_span_*`を併記) |
| `final_adoption.non_adopted_fallback` | 未採用試行のFallback有無(「実行履歴」欄用。表示色の対象外) | NGの③行 |
| `final_adoption.history_ref` | BlockProgressのpath | `tts_block_progress/<seg>.json` |
記録のみで、Gate・停止判定・回数・待機・Styleには一切使わない(UD-3「記録は維持」)。**書込み点**は`er127.BlockRun.finish()`(`:~458-488`)に1箇所(L1〜L7)+Z ctxの`finish`(`er122`)に1箇所が最小(【設計提案】。配置はOpus条件Aレビューの対象)。

---
## 3. runtime evidence手段(Family×Level×Role別)

### 3-1. 既存の承認済み手段の棚卸し
| 手段 | 実体 | 発火の再現力 | 費用 |
|---|---|---|---|
| E1 統一TTS runtime evidence driver | `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_{core,cases,run,aggregate}_01.py`・`EVIDENCE_PLAN_01.md §2`(注入はjudge結果のNG方向のみ。LR駆動にはPrimary転写へ「1語置換」を注入。Style/Prompt/Voice/速度/model/待機/回数は不変。台帳はcase専用dir) | 実TTS・実ASR・**実180秒待機**・実LR(Luna)・実Gate。①②NG→③Fallback、LR発火・LR後PASS/全NG、STOP、resumeをFamily×Level×leaf別に再現 | 1case ¥0.13〜2.5(X・Z)/¥0.22〜8.6(Y。y_voice系のみ¥4.8〜8.6)(`COST_01.md:20-80`)。全case ¥86.6 |
| E2 unit・結合test | `er127_tts_block_policy_01_test_01.py`(104件、実LR経路`test_real_lr_path_third_open_then_lr_block_then_finish_keeps_records`含む)、`er019_family_x_style_profile_01_test_01.py`(51件)、`er008_n8_a2_slowdown_sha256_refresh_22_test_01.py`(`LR_REWRITTEN`)(`FIX_A_01.md`) | record構造・merge・Gate判定をmock注入で再現(API 0) | ¥0 |
| E3 mock runner | `er121_family_y_mock_01.py`(Y `--mode mock`)、`er026_family_z_e2e_integration_test_01.py`(Z mock全stage)、X runner testの`mock.patch.object` | 全stage通しの形式確認。ただしfake TTSは`status=OK`のentryを返すため**LR/Fallbackの発火そのものは再現できない**(NG注入が別途必要) | ¥0 |
| E4 保存run再判定 | `er019_family_x_validation_inheritance_01.py:256 rejudge_with_current_judge`(新規Secondary呼出0、保存転写でAND gate再判定。LR済みはLR後文を正解にする) | 判定結果の再現(発動の再現ではない) | ¥0 |
| E5 resume | `BlockProgress`(`er127:239-387`)。kill→同一args再起動で①②再生成0・LR LLM再実行0・待機は残り時間のみ(X-Adv-12/16、X-Std-10。`EVIDENCE_01.md` #12) | resume挙動 | evidenceの一部 |
| E6 KP DB由来の`forced_fallback` | `docs/pm/kpx1_evidence_forced_fallback_rerun.log`・`er030/er035_*evidence*` | **TTS Fallbackとは別概念**(KP DB source fallback)。**流用不可**(名称衝突に注意) | — |
| E7 保存evidence runの再利用 | §4 | 表示検証の入力 | ¥0 |

### 3-2. Family×Level×Role別の発火再現手段
区分: ◎=有料0で記録形まで再現(E2/E3+保存run)/○=有料最小(E1、見積=過去実費、`COST_01.md`)/△=自然発生待ち(再現不可)。
| Family/Lv | Role(policy) | LR発火 | Fallback発火 | 有料0 | 有料最小(見積¥) | 未観測/再現不可 |
|---|---|---|---|---|---|---|
| X Std | 英語EN_LR_STD(L3 topic/L4本文・in_one_line・chunk) | E1: X-Std-2(LR PASS ¥1.14)/3(LR全NG ¥2.2)/5(¥1.87) | E1: X-Std-1b(③採用 ¥0.47)/X-Std-4(¥0.80)/X-Std-12 | ◎E2 | ○ ¥1〜2.5/case | なし |
| X Std | JA_STD(L7) | — | E1: X-Std-6(¥0.24)/7(終端) | ◎E2 | ○ ¥0.3 | shell日本語(X-S03)未実走(同leaf) |
| X Std | KP_EN(L6) | — | E1: X-Std-8(¥0.39)/9(¥0.52) | ◎E2 | ○ ¥0.4〜0.5 | なし |
| X Adv | EN_LR_ADV(L1 topic/preview/comment、L2本文/in_one_line) | E1: X-Adv-2(¥1.30)/3c(¥2.0)/6(¥1.79)/16(R-5 resume ¥1.85) | E1: X-Adv-1(¥0.76)/14b(¥1.67) | ◎E2 | ○ ¥1〜2/case | なし |
| X Adv | KP_EXPL(L5) | — | E1: X-Adv-7(¥0.68)/8(終端) | ◎E2 | ○ ¥0.7 | なし |
| X Adv | KP_EN(L6) | — | E1: X-Adv-10(¥0.32)/11(¥0.41) | ◎E2 | ○ ¥0.4 | なし |
| X | SHELL_EN/固定mp3 | 対象外 | 対象外(既存方式維持) | — | — | — |
| Y Std | EN_LR_STD(L3 topic・L4 Voice本文) | E1: Y-Std-1(¥1.32)/Y-Std-4(+Y Gate、¥4.8〜6.5) | E1: Y-Std-4b(¥6.5) | ◎E2/E3 | ○ ¥1.3〜6.5 | **Y chunk(Y-S-07)未観測**(追加case要。見積¥1〜3) |
| Y Std | JA_STD/KP_EN/KP意味 | — | E1: Y-Std-2b(¥0.49)/3(¥0.32) | ◎ | ○ ¥0.5 | なし |
| Y Adv | EN_LR_ADV(L1/L2、y_voice) | E1: Y-Adv-1(¥1.15)/4b(+Y Gate、¥8.56) | LR経由(③単独caseはY-Adv-4=自然逸脱) | ◎ | ○ ¥1.2〜8.6 | **Y chunk(Y-B-06)未観測** |
| Y Adv | KP_EXPL/KP_EN | — | E1: Y-Adv-2(¥0.41)/3(¥0.41) | ◎ | ○ ¥0.4 | なし |
| Z Std | EN_LR_STD(L3 topic_intro_en・L4 narrator chunk) | E1: Z-Std-1(¥2.5)/Z-Std-6(¥0.70) | LR経路込み | ◎E3 | ○ ¥0.7〜2.5 | なし |
| Z Std | Z会話(Z_DLG_CTX) | — | E1: Z-Std-2(¥1.51。③=legacy_fallback) | ◎(`er122` unit) | ○ ¥1.5 | **Z_DLG_LEGACY実走未観測**(unit/golden testのみ) |
| Z Std | JA_STD/KP_EN/KP日本語 | — | E1: Z-Std-4(¥0.20)/5(¥0.38) | ◎ | ○ ¥0.4 | なし |
| Z Adv | EN_LR_ADV(L2 narrator・L1 topic/preview/comment) | E1: Z-Adv-1(¥1.07)/4(¥0.63) | LR経路込み | ◎ | ○ ¥0.6〜1.1 | なし |
| Z Adv | Z会話(ctx+外側loop減速) | — | E1: Z-Adv-2(¥1.22)/3/3b(¥1.3〜1.5) | ◎ | ○ ¥1.2〜1.5 | Z_DLG_LEGACY Adv未観測 |
| Z Adv | KP_EXPL/KP_EN | — | E1: Z-Adv-5(¥0.46)/6(¥0.45) | ◎ | ○ ¥0.5 | なし |
- **表示検証(赤・濃青)の入力は有料0で足りる**: 保存のtru_ev evidence run(§4)から作る。Phase Bの**正式runtime evidence**(原文§10-11)=最終Human報告が`final_adoption`を読み、X/Y/Z・Std/Adv・LR/Fallback各1経路以上で赤/濃青が出ることの確認分は、E1の既存caseを再実行(代表例: X Std LR PASS 1.1+X Std Fallback 0.5+X Adv LR 1.3+X Adv KP解説 0.7+X KP_EN 0.4+X JA 0.25+Y Std LR 1.3+Y Adv LR 1.2+Z Std会話 1.5+Z Adv LR 0.6+Z narrator Std LR 0.7 ≒ ¥10〜15、Y Gate同時確認+¥8.6を足しても≒¥25〜40)。**案件見積300円以下に収まる見込み**(見積は過去実費ベース。実際のcase選定・再実行回数はPhase Bで確定)。未実走9行のうち実走が要るのはZ legacy会話・Y chunk・shell JAのみ(各¥0.3〜3)。
- **Production既定動作を変える手段は提案しない**。E1は判定結果の上書きをdriver側monkeypatchのみで行い(Production code不変)、台帳はcase専用dirに隔離(`tru_ev_core_01.py`冒頭、`EVIDENCE_PLAN_01.md §2`)。Phase Bで`final_adoption`を入れた後のevidenceも「driver実走での新記録確認」であり、Gate/回数/待機/Styleは変わらない。

---
## 4. 既存evidenceの再利用候補(最終Human報告の表示検証入力)

走査: `er019_output/family_x_audio_production_wiring_01`・`er121_output/family_y_production_01`・`er026_output/family_z_production_e2e_01`の`tts_generation_results.json`(LR=`local_rewrite_recovery`/`audio_text_deviation`、Fallback=`fallback_attempts_log`非空 or `instruction_type=minimal_fallback` or `dialogue_tts.attempts[].mode=legacy_fallback`)。実行=scratchpad上の読取専用json集計(API 0)。公開/LR一覧は`W4_ROLE_COVERAGE_01.md` §5(#1〜#43)と整合。

### 4-1. 実Production公開物(記録の完全性は旧コードで保存された分に欠陥あり)
| run(segment) | 内容 | 記録の完全性 | 表示検証の入力に使えるか |
|---|---|---|---|
| X AI島 `ai_island_temple__run_form_prod_01` a2 `full_story_part1_k2`(L3/L4) | LR(AIs→AI agents)+Fallback(③)+LR①'採用(role Style) | LR全記録・`style_prefix.sha`・`instruction_label`・`cooldown_events`あり。**旧コード保存**: トップ`fallback_used:true`(採用はLR①'のrole Style=誤)、`LR_REWRITTEN`警告なし、`blocks["1"]`欠落(HEADで是正、runは再生成しない) | ○ `retts_result.fallback_used=false`から採用attemptを再導出する前提で可。UD-2是正の最終Human報告にも使う実データ |
| X AI島 b1b `full_story_part1_k2`(L2) | LR(AIs→AI systems)。`instruction_type:minimal_fallback`はLR前の③=未採用 | LR全記録あり。`LR_REWRITTEN`警告あり | ○ **「未採用③のFallbackを採用Styleと誤表示しない」検証の最良データ** |
| X Word Gacha Adv `word_gacha__run_wg_01` b1b part3 | LR(you've→you have。UDR #183(a)承認、ページ注記なし) | LR記録あり(旧コード、Fallbackなし) | ○ 赤(span)表示の単純データ |
| Z メロス Adv `melos/run_e2e_02`(公開)・同系`run_e2e_04/kga3/kgcpw*` | LR(`Melos→He` `full_story_part3_c1`) | `audio_text_deviation`(`diff_summary`のみ、`changed_span_*`なし)。FB記録0(統一前flow) | △ spanのパース要(G-7)。chunk→親notes集約も検証可 |
| Z 猿の手 Std `the_monkeys_paw/run_sf_prod_01`(公開)a2 `full_story_part1_c10` | LR(`guest→visitor`) | 同上`audio_text_deviation` | △ 同上 |
| Y Redelivery fee `redelivery_fee/run_01` a2/b1b `y_voice_1` | LR発火+HR採用で**音声は原文**(G-9)。a2は`preview`/`y_voice_1`のFallbackも記録 | LR全記録+Fallback記録+`HUMAN_APPROVAL_SUPERSEDES…`旗 | ○ **「実行履歴(LR発動)と最終採用音声(原文)の区別」の検証に必須**。Y Fallback(a2)も含む |
| X Coffee m2p0 `coffee_prices__run_m2p0_n01_01` b1b comment_2 | LR(Brazil entered→reached)。公開音声は原文(派生) | 派生run(validation_state_rebuilt)で記録整合性未確認 | △ 【未確認】 |

### 4-2. tru_ev evidence run(X/Y/Z全Family・Std/Adv・LR/Fallback・Z会話ctx→legacy切替)
`er019_output/…/coffee_prices__run_tru_ev_*`(X Std/Adv)・`er121_output/…/redelivery_fee/run_tru_ev_*`(Y)・`er026_output/…/the_monkeys_paw/run_tru_ev_*`(Z)。**LR記録あり**: X-Std-2(topic_intro)・X-Adv-2(comment_1)・X-Adv-16(in_one_line)・Y-Adv-1/4b・Z-Adv-4/Z-Std-6。**Fallback記録あり**: EN短文(X-Std-1/1b/4/5、X-Adv-1/14b)・JA短文(X-Std-6/7、Y-Std-2/2b)・ENGLISH_LOCK(X-Std-8/9、X-Adv-10/11、Y-Std-3、Y-Adv-3)・KP解説(X-Adv-7/8、Y-Adv-2)・Z会話ctx→legacy(`run_tru_ev_z_std_2`・`z_adv_2/3/3b`)。**LR+Fallback同居**: X-Adv-16(`in_one_line`)・X-Std-2・AI島a2。強制NG由来(`evidence_only_ledger`)で公開記事ではないが、**表示仕様(赤=LR差分、濃青=Fallback全体)の検証入力としては3種のFallback・Z会話切替・LR/Fallback重複がすべて揃い、API 0で読める**。
- AI島の人間確認資料入力: `audit/hr_packet_data_01.json`(`canon`/`spoken`/`changed_after`)。Y HR試聴節`user_test/family_y_production_redelivery_fee_03`・X`user_test/family_x_ai_island_form_01`は既存の人間確認資料の形(W2/W4で確認。本委任では内容未再確認=【未確認】)。
- A/B/C保存run(`er013/er012/er003/er014_output` 52件): Fallback記録18件・LR 0件=濃青の「旧形式入力」としては使える、赤は不可。

---
## 5. 判断候補(区分付き。原文で決定済みのUD-1/2/3・色仕様・試行回数不変は再質問しない)
| ID | 内容 | 区分 | 根拠・推奨 |
|---|---|---|---|
| J-1 | `final_adoption`記録(§2-4)を新設して最終Human報告の入力に統一する(既存キーは変更せず追加のみ・Gate判定には使わない) | **B**(Fable判断。Opus条件A対象) | 承認済み仕様内の記録拡張(UD-3「記録は維持」、§6の表示要件を満たす手段)。仕様の意味的変更ではない。推奨=採用 |
| J-2 | KP_EN `fallback_attempts_log`の命名逆転(DR-6/G-3)は旧キー名を変えず、`final_adoption`側でENGLISH_LOCK段を明示する(読取規則) | B | 旧キー名変更は既存Gate/test/Y・Z互換に波及。推奨=読取規則で吸収 |
| J-3 | Zの`style.fallback_used`/`fallback_attempts`(G-2)を直すか(記録)、`dialogue_tts`/`attempts[]`から導出して表示するか | B | 表示は導出で足りる。記録修正は不整合記録の是正(PM_GOVERNANCE 11-8)だが、Z Gate`build_style_actual_record`の採用attempt判定変更はGate挙動に触れうる→Opus条件Aで確認 |
| J-4 | Z narrator LR時の`build_style_actual_record`が未採用③Styleを「実測」とする可能性(【静的】、未実走)の再現確認と是正 | B(再現してから) | `style.fallback_used=False`は観測済みだが、`kind=measured`の`sha256`が③か①'かは未確認。evidence runの再計算(API 0)で確認可 |
| J-5 | A/B/Cへの適用範囲=表示(読取)のみ・entry直下旧キーから導出(§1-4)、生成/Gate/待機は変更しない | B | 原文§1「方式を無断でX/Y/Z方式へ置換しない」「適用可能な最終Human報告仕様」。推奨=読取のみ |
| J-6 | 旧コード保存の既公開run(AI島・Y run_01等)の記録欠陥(G-8)は再生成せず、読取側で`retts_result`/`verified`から再導出 | A | 承認済み(UD-2「不要な再TTSは行わない」)。推奨=再導出 |
| J-7 | DR-1/DR-3/DR-4/DR-5(コメント・死んだフィールド) | C(実害なし、Phase Bで触れる場合のみ) | 任意 |
| J-8 | Z legacy会話・Y chunk・shell JAの追加runtime evidence(§3-2、各¥0.3〜3) | A | 承認済みScope内・案件見積300円以下(7-7) |
| J-9 | W2 F4(Adv KP解説③NG時Style未記録)の記録追加 | C(終端HR資料にのみ影響) | `final_adoption`と一緒に載せるなら追加コスト小 |
D(ユーザー判断要)に該当する新規事項: **なし**(決定済みのUD-1/2/3・表示仕様・§7維持の範囲内で自己解決/Fable判断に収まる)。

## 6. 未確認事項(推測で埋めていない)
- Z narrator LR採用時の`build_style_actual_record`出力(未採用③のsha/採用①'のsha、J-4)。Y chunk・Z legacy会話・shell JA・SHELL_ENの実走。JAのFallback切替元Style名のentry内復元。KP phrase reuse時のFallback記録継承(G-10)。W2 F4の再現条件。Y/Zの`timeline.json`相当の所在(区間の時刻は§6で不要と整理)。
- 本ファイルの`~`付きfile:lineはgrep/先頭行確認ベースの近似。Phase Bで使う際は再Grepで確定すること。
