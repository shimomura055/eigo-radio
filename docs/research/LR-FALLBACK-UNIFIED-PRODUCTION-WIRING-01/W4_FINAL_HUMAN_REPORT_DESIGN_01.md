# W4_FINAL_HUMAN_REPORT_DESIGN_01(LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_04、Phase A 設計のみ、API 0、2026-10-28)

原文: `docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §2・§6・§10(7〜9)。共通: `…_委任_00_COMMON.md`。
本書は**設計のみ**。Productionコード・test・SSOTは未変更(作成物=本書と`W4_SAMPLE_01.html`のみ)。実施したのは保存データ・コードの読取と、in-memoryのsha256照合だけ。有料API・TTS・ASR 0、費用0円。
表示サンプル=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/W4_SAMPLE_01.html`(静的。ブラウザで開く。公開dir`user_test/`には置いていない)。
W1(委任_01)の棚卸しは本書作成時点で未着手のため、本書のデータ源は**私が保存データから直接読んだ事実**で書く。W1結果と食い違えばW1側を正とし、§3の読取規則を差し替える。

---
## 0. 結論(先に)

1. **新設**する。既存の人間確認資料はすべて目的が違う(HR依頼=承認前の止まった状態の確認、公開試聴ページ=学習者向け)。拡張すると「学習者向け本文へ注記が混入しない」ことを構造では保証できない。新設の読取専用生成器`er_final_human_report_01.py`(仮名)を1本置き、X/Y/Z共通の描画+Family別の読取アダプタとする。1 run=1資料(Std・Adv両方)。
2. **生成タイミング**=assemble・pages・page_verify完了後の読取専用後処理。出力は`user_test/`の外(提案: `final_human_report/<family>/<slug>/<run>/index.html`)。URLはGitHub Pagesの`https://shimomura055.github.io/eigo-radio/final_human_report/…`で確認でき、学習者向けindexからはリンクしない。stage一覧(`E2E_STAGES` `er026:1130`、Y `er121_family_y_runner_01.py:34`)には**入れない**(resume・RESTART_STORM判定に触れないため)。既存の`er078_pass_with_warning_registry`の生成完了hookと同形の「失敗しても生成を止めない・ただし資料未生成は完了報告に明記」とする。
3. **最大の設計論点は「最終採用attemptの確定」**。実データで3種の落とし穴を確認した(§3-3)。(a)X AI島Stdは`fallback_used=True`が残るが、最終採用音声は通常Style(LR後の再生成)。entry単位のflagをそのまま読むとFallbackを誤表示する。(b)Zの既存`style_actual`(`er063_family_z_audio_01.py:1996-2036`)は「fallback段の最後のattempt」を採用attemptとみなす経験則で、告げ口心臓Adv KP2では**実際の採用音声(ENGLISH_LOCK)と違うStyle(K2)を「採用」と記録**している。(c)Z猿の手StdのLR後再生成はStyle記録が保存されていない。→ 読取規則は**最終wavのsha256とattemptファイルのsha256の一致**を最優先の根拠にし、一致しない場合は「記録なし」と明示して推測しない(§3)。
4. **委任文の前提と異なる実データ**: 告げ口心臓は「LR 0/Fallback 0」ではなく、**Adv KP2「mock」にENGLISH_LOCK採用が1件**(最終kp2_en.wavのsha256=attempt3のsha256、attempt3のinstruction sha=`dcd08dca…`=ENGLISH_LOCK、attempt1・2はK2 `9d905cfe…`で未検証)。LRは0件(音声単位 Std20・Adv19を走査)。サンプルHTML§8に青で表示した。
5. 赤=LR変更語句(変更後=赤・太字・二重下線、変更前=赤・取消線、前後英文併記)、濃青=Fallback対象テキスト全体+注記(左に青い太線)。色だけに頼らず文字ラベル(LR/Fallback/発動なし/記録なし)を併記。重複時は「青の区間の中に赤の語句」。実行履歴は灰色枠に分離し、**採用されなかった試行は色を付けない**。
6. 混入防止は(i)生成器が公開ページ・TTS・ASR・KP・Promptの各コードを**import しない/されない**(AST test)、(ii)出力先分離、(iii)専用class接頭辞`fhr-`と判別コメント`<!--FINAL_HUMAN_REPORT-->`の**逆向き混入検知test**(公開HTML・TTS入力・ASR正解・Style Prompt・KP表示・study_text・parts.json に出ない)、(iv)run dirを書換えないこと(前後sha一致)で構造的に保証する(§5)。
7. A/B/C等の既存Familyは、保存データに`attempts_log`/`fallback_used`はあるが**Style名・LR記録がない**(§6)。「適用可能(Fallbackの有無のみ)/記録不足で表示不可」をrun単位で判定し、不可は資料に明記する。音声生成方式は変えない。
8. 追加のAPI費用は0円(読取専用)。量産単価への影響なし(後処理のCPU時間のみ)。
9. Phase Bに入る前にFableが決める点(`判断候補`、§10): Z記録の補強方式(読取のみで足りるか/採用時に`final_adoption_record`を追記するか)、Z公開ページの既存LR注記の扱い、出力先dir。**ユーザー判断(D)は無し**(色・注記・混入禁止は原文で決定済み)。

---
## 1. 既存の人間確認資料の棚卸し

| # | Family | 資料 | 生成器(file:line) | 目的・時点 | 最終Human報告として使えるか | 判定 |
|---|---|---|---|---|---|---|
| 1 | X | 公開試聴ページ `user_test/<slug>/index.html` | `er019_family_x_listening_page_01.py`(全体238行。`pass_with_warning_listening_list`と「制作情報」を同ページに出す=:150-175) | 学習者向け試聴ページ+事後試聴リスト | **不可**(学習者向け。UDは混入禁止) | 非拡張。**ここへ赤/青を出さない**(混入検知testの対象) |
| 2 | X | HR試聴ページ `user_test/family_x_ai_island_form_01/hr_01.html`/`hr_02.html` | `tools/build_hr_packet_aif3_01.py:134`(`build_v2`=AIF5)。per-article専用 | 止まったHR(承認前)の試聴材料 | 不可(承認前の依頼書。M3停止時の補助。UD-3で「正常なLR/Fallbackだけの停止」は解除) | 非拡張。参考(前後差分表示`diff_rows`:36 の考え方は流用可) |
| 3 | X/Y/Z共通 | `audit/pass_with_warning_listening_list.json` | X runner `er019_family_x_audio_production_runner_01.py:1721,2136`、Y/Z同hook(`er078_pass_with_warning_registry_01`) | ASR PASS_WITH_WARNINGの事後試聴リスト | **不可**(LR/Fallbackとは別概念。LR・Fallbackは載らない) | 非拡張。別枠のまま。本資料から「関連資料」としてリンクだけ |
| 4 | Y | HR試聴節 `user_test/family_y_production_redelivery_fee_03/hr_preview_01.html`、`…/index.html` | `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_hr_packet_01.py:25`、`er121_e1_hr_listening_page_01.py`(120行。「書換え前の最終判定対象attempt」を聴かせる=:1-10) | HR(承認前)の試聴 | 不可(同上) | 非拡張 |
| 5 | Z | `review_request.md`(run直下) | `er119_*`のKP/文法HR依頼書(`er119_grammar_review_01.py:594,630`)。例=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01/review_request.md` | KP・文法選定の依頼(音声前) | **不可**(音声・LR・Fallbackと無関係) | 非拡張 |
| 6 | Z | 試聴ページ `user_test/family_z_<slug>/{standard,advanced,index}.html` | `er063_family_z_audio_01.py:2440-2475`(行ごとにvoice/style/script/注記)、`er063_family_z_page_verify_01.py` | ユーザー試聴ページ。**既にstyle名とLR注記(`Local Rewrite採用(音声は原稿から変更…)` :2464-2468、chunk分 :2468-2471)を出している** | 部分的(情報はあるが、学習者向け公開本文と同居・赤青なし・採用attempt判定なし) | 非拡張。UD-1後は本文=音声となるためこの注記は不要になり撤去が必要(§10 B-2) |
| 7 | Z | HR試聴ページ `user_test/family_z_melos_01/hr_review_01.html` ほか | `tools/build_family_z_hr_review_page.py`(v2、per-run) | HR(承認前) | 不可 | 非拡張 |
| 8 | 汎用 | `user_test/human_review.html` | (静的HTML。生成器未特定) | 汎用のHuman Review案内ページ | 不可 | 非拡張 |
| 9 | 各Family | 最終報告テンプレ | 無し(各委任のRESULT_PACKETに散在) | — | — | **新設が必要**(本設計) |

**判定理由**: 「最終Human報告用資料」の要件(原文§6)は①全Family・全Level・全Roleを1資料で網羅 ②LR=赤/Fallback=濃青の固定表示 ③学習者向けに混入しない ④採用されなかった試行を最終状態と混同しない。既存資料はどれも①(Role網羅)と④(採用attempt判定)を持たず、1・6は③の混入側にいる。拡張は不採用、新設+既存への混入防止検査追加(§5)とする。

### 1-2. 新設する資料の構成(1 run = 1資料、Std/Adv別セクション)

資料=`final_human_report/<family>/<slug>/<run>/index.html`(+必要なら`audio/`に採用attemptのmp3。後処理で変換、既存`to_mp3`同方式)。ページ構成:

1. ヘッダ: 記事名・family・run・生成日時(技術時刻ではなく資料の作成日のみ)・凡例(LR=赤/Fallback=濃青/発動なし/記録なし)・読取元の完全性(§3-6のカバレッジ表)。
2. 要約表: Level × Role別に LR件数 / Fallback件数 / 記録なし件数。0件は「発動なし」を明示(隠さない=原文§12の趣旨)。
3. Level別セクション(Std→Adv)× Role別の音声単位カード。**全Roleを網羅**(下表)。各カードに: Role名・範囲(chunk/part)・最終本文・LR表示・Fallback表示・実行履歴(灰色)・採用音声プレーヤー。
4. 照合表: 最終表示本文=TTS入力=ASR正解原稿(LR後)の一致、確定内容(KP/KW/文法/Fact)との重なり(`confirmed_kp_lr_overlap`相当の既存記録があれば表示。`er020:837-846`、無ければ「記録なし」)。
5. 末尾: 注記は読み上げ対象ではない旨と、この資料が学習者向けページ・TTS・ASR・Style Promptに使われないことの明記。

**Role網羅表(X/Y/Z。LR対象は`er127_tts_block_policy_01.py:123 LR_ROLES`の英語5roleのみ、Fallbackは全policyで発生しうる)**

| Role | 単位の取り方 | LR表示 | Fallback表示(切替の種類) | 読取元(代表) |
|---|---|---|---|---|
| 本文(Full Story) | part/chunk(X `*_kN`、Y `y_voice_N`+chunk、Z `*_cN`) | 赤(前後英文) | 英語短文Style(Minimal)/Z Dialogueは別行(下) | X/Y `tts_generation_results.json segments[*]`、Z `entry.attempts[]`+`audio_text_deviation` |
| topic_intro(英語) | 1単位 | 赤 | EN短文 | 同上(Zは`topic_intro_en`) |
| Preview(英語/日本語) | 1単位 | 英語Advのみ赤。日本語はLRなし | Adv=EN短文、Std日本語=日本語短文(Minimal) | 同上 |
| Comment 1〜4 | 1単位ずつ | Advのみ赤 | Adv=EN短文、Std日本語=日本語短文 | 同上 |
| in_one_line | 1単位(Xのみ) | 赤 | EN短文 | 同上 |
| KP英語 `kpN_en` | 1単位 | LRなし(表示しない) | ENGLISH_LOCK | `key_phrases[N].english` |
| KP英語解説(Adv) | 1単位 | LRなし | EN短文 | `key_phrases[N].explanation` |
| KP日本語意味・日本語音声・日本語タイトル | 1単位 | LRなし | 日本語短文(Minimal) | `key_phrases[N].japanese_meaning`・`segments` |
| Z Dialogue(セリフ) | chunk(`clip_kind=dialogue`) | LRなし | 3回目=従来Dialogue Style(`LEGACY_DIALOGUE`) | Z `entry.attempts[]` |
| shell固定英語 | 1単位 | LRなし | 発動時のみ(通常は再利用) | shell entries |
| 固定mp3 | — | — | — | 対象外(TTS生成なし=「対象外」と表示) |

---
## 2. 資料生成器の位置づけ(構造)

- モジュール(新設): `er_final_human_report_01.py`。入力=run dir(read-only)、出力=`final_human_report/<family>/<slug>/<run>/`。CLI: `py er_final_human_report_01.py --family x|y|z --run <dir> --out <dir>`。runnerからは`stage_pages`の外(`page_verify`成功後)で任意に呼ぶ。失敗しても組立成果物は変えない。
- 構成: (1)Family別アダプタ(`read_x`/`read_y`/`read_z`/`read_legacy`)が保存記録を**共通中間表現**へ変換 (2)共通レンダラが中間表現だけを見てHTMLを書く。レンダラはFamilyを知らない。
- **共通中間表現(1音声単位)**: `unit_id`、`level`、`role`、`range`(part/chunk/本文範囲の表示名)、`text_display`(最終表示本文の該当範囲)、`text_tts`(LR後の最終TTS入力)、`text_asr_expected`(`resolve_expected_text_after_local_rewrite`の戻り値、`er020:859-891`)、`adopted`{`ref`,`sha256`,`how`=`sha_match`/`verified_flag`/`human_adopt`/`unknown`}、`style`{`normal_label`,`adopted_label`,`changed`(bool/None=記録なし),`kind`=`MINIMAL_EN`/`MINIMAL_JA`/`ENGLISH_LOCK`/`Z_DIALOGUE_LEGACY`/`OTHER_APPROVED`}、`lr`{`fired_in_history`,`adopted_in_final`,`superseded_by_human`,`before`,`after`,`changed_spans[]`}、`history[]`(block・attempt・Style・結果の短文)、`gaps[]`(記録なしの項目名)。
- 既存の純関数を**読取専用で再利用**する(新規ロジックを増やさない): `resolve_expected_text_after_local_rewrite`(`er020:859`。ただしHR個別承認entryは`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`で原文が正解=`:852,868`)。**import先はこの1関数のみ**とし、公開ページbuilder・TTS実行・Prompt生成モジュールは一切importしない(§5)。

---
## 3. データ源と読取規則

### 3-1. Familyごとの記録の所在(実測)

| Family | 音声単位の記録 | Style記録 | LR記録 | 採用attemptを示す記録 | 実測で見えた問題 |
|---|---|---|---|---|---|
| X | `<run>/<lv>/audit/tts_generation_results.json segments[seg]`(chunkは`*_kN`子+親) | attemptごと`style_prefix{len,sha256,head200}`、`instruction_type`(`minimal_fallback`等)、`instruction_label`(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`)、`standard_attempts_log`/`fallback_attempts_log` | `local_rewrite_recovery{selection.selected{rewritten_segment,changed_span_before/after},retts_result{attempts_log,style_prefix,sha256,path},status}`、`canonical_text_before_local_rewrite` | LR採用時=`retts_result`が最終。非LR=entry直下`sha256`/`path`と`attempts_log`末尾 | **entry直下`fallback_used`が元ブロックの結果で、LR後の最終採用Styleとは別**(AI島Std `full_story_part1_k2`: `fallback_used=True`だが最終=LRブロック第1回の通常Style)。M3 `STD_FALLBACK_USED_OR_UNKNOWN`(`er019_family_x_style_profile_01.py:717`)がこのflagを見てBLOCKした経緯と同根 |
| Y | 同形(`er121_output/…/<lv>/audit/tts_generation_results.json`) | 同形 | 同形+`local_rewrite_audio_superseded_by_human_approval` | HR採用時=`adopted_attempt_audio_path`・`adopted_audio_sha256`・`ypl7_user_approval_record_*.json{adopted_attempt,adopted_audio_sha256,approved_by}` | E-1 a2 `y_voice_1`: `fallback_used=True`、最終=人間承認のattempt5=EN短文Style(Fallback)。LRは記録が残るが最終音声は原文 |
| Z | `tts_generation_results.json segments[clip]`(`entry.attempts[]{phase,attempt,style_prefix_sha256,style_prefix_head,verified}`)、`entry.style{instruction_label,fallback_used,fallback_attempts}`、`entry.style_actual` | `style_actual{sha256,adopted_phase,adopted_instruction_type,result_fallback_used,secondary_top_level}`、attempt wav横の`narration/attempts/*.json{sha256,route,instruction_text,verified}` | `entry.audio_text_deviation{canonical_text_before_local_rewrite,audio_text_after,diff_summary}` | **entryに採用attemptの明示記録なし**。`style_actual`は経験則(`er063:1996-2036` 「fallback段→標準段の順で最後にstyle記録を持つattempt」) | (a)告げ口心臓Adv `kp2_en`: `style_actual.sha256=9d905cfe…(K2)`だが最終wavのsha256=attempt3(ENGLISH_LOCK `dcd08dca…`)。(b)猿の手Std `full_story_part1_c10`: `attempts[]`は元ブロック3回分(standard×2+fallback×1)でLR後のattemptがない。最終wavはどのattempt wavとも不一致(`full_story_part1_c10_original.wav`=LR後の減速前と推定、Style記録なし) |

### 3-2. 「最終採用attempt」確定アルゴリズム(読取規則)
入力=1音声単位のentry+attemptファイル群。優先順に最初に確定できた根拠を採用し、`adopted.how`に記録する。

1. **人間承認採用**(`adopted_attempt_audio_path`/`ypl7_user_approval_record_*`または`local_rewrite_audio_superseded_by_human_approval`が真): 採用attempt=承認記録のattempt。LRは「最終音声に反映なし」(`lr.superseded_by_human=True`、赤にしない)。
2. **sha一致**: 最終音声(減速前の`*_original.wav`があればそれ、無ければ`*.wav`)のsha256と、`attempts/*.json`の`sha256`(または`attempts_log[].sha256`/`retts_result.sha256`)が一致するattempt。一致が複数ある場合は最終saved_atのもの。**route=`post_slowdown`等の擬似attempt(instruction空)は除外**(告げ口心臓a2で9件、b1bで10件の親/連結音声は子chunkの集合なので子単位で判定)。
3. **LR採用**(`local_rewrite_recovery.status=RESOLVED_BY_LOCAL_REWRITE`、Zは`audio_text_deviation`の`audio_text_after≠canonical_text`): 採用attempt=LRブロックの末尾の`verified=True`attempt(X/Y=`retts_result.attempts_log`、Z=`attempts[]`の末尾)。**元ブロックのattempt(LR前)は実行履歴に回し、Styleを最終採用として扱わない**。
4. **verifiedフラグ**: 非LRで`attempts[]`/`attempts_log`に`verified=True`が1件だけある場合はそれ。複数/0件なら次へ。
5. 上記で確定できない → `adopted.how="unknown"`、`gaps+=["採用attempt"]`、LR/Fallbackの最終採用状態は**「記録なし」**(推測しない)。

**Fallback表示条件(原文§6-B「Styleが変わらない再試行は表示しない」)**: 採用attemptの有効Style sha(attemptの`style_prefix.sha256`/`instruction_text`のsha)≠そのRoleの通常Style sha(policy `third_style`と`er019_family_x_style_profile_01.py`の承認Style sha/`er063.z_expected_style`)のときだけ`style.changed=True`。同shaなら再試行のみ=表示しない。種別(`kind`)は`er127_tts_block_policy_01.py:99-117`の`third_style`(FALLBACK_MINIMAL_EN/MINIMAL_JA/ENGLISH_LOCK/LEGACY_DIALOGUE)とattempt Styleから決める。**採用attemptが特定できないときはentry直下の`fallback_used`を根拠にしない**(§3-1 X・Y・Zの実例)。

**LR表示条件**: `lr.adopted_in_final`=規則2/3で採用attemptがLRブロック。変更語句=`selection.selected.changed_span_before/after`(X/Y)または`audio_text_deviation.diff_summary`・前後英文の単語差分(Z)。変更語句が取れない場合は前後英文の単語差分(単純なLCS、`build_hr_packet_aif3_01.py:36 diff_rows`同方式)で代替し、「差分は自動計算」と明記。

**LR+Fallback重複**: 区間全体=青(採用attemptがFallback Styleのとき)。語句=赤。Style名は**LR後ブロックの採用attemptのStyle**から取る(原文§6-C「採用されなかった試行のFallbackを最終採用Styleとして誤表示しない」)。LR前の元ブロックでFallback Styleを試した事実は灰色の実行履歴にのみ記す。

### 3-3. 実データで確認した検証結果(読取規則の根拠)
- **X AI島Std** `full_story_part1_k2`: `fallback_used=True`、`fallback_attempts_log[0]`(attempt3、`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、`post_slowdown_ng=True`)。`local_rewrite_recovery.retts_result.sha256=2a5d0fc5…`=entry直下`sha256`。LRブロックattempt1のstyle sha=`3a680861…`(通常Style)=`style_profile.expected_base_sha256`。→ 最終=通常Style、LR=赤、Fallback=青にしない。
- **X AI島Adv** 同segment: `attempts_log`に`minimal_fallback`(attempt3)があるが`fallback_used=False`、最終attempt=LRブロック第1回(`english_style_prefix_wide_margin`、`<default:ENGLISH_STYLE_PREFIX>`)。→ 同判定。
- **X Word Gacha Adv** `full_story_part3`: LR `If you've felt…`→`If you have felt…`、attempts_log=標準Style3回+LRブロック1回(verified)。Fallback試行記録なし。
- **Z猿の手Std** `full_story_part1_c10`: 前述(b)。→ 「記録なし」。
- **Z告げ口心臓Adv** `kp2_en`: 前述(a)。最終wav sha256=`e8c29484…`=`attempts/kp2_en_attempt3_custom31eb2f72.json`の`sha256`、`instruction_text`長1246・sha`dcd08dca…`(末尾「Pronounce the phrase specifically as an English word or phrase…」=ENGLISH_LOCK)。attempt1・2はK2(長332・sha`9d905cfe…`、`verified=False`)。`style_actual.source="adopted_attempt.style_prefix"`が`9d905cfe…`(K2)を指し、`secondary_top_level`に本当の採用Style(`dcd08dca…`)が退避されている。`style_actual_vs_approved`の`all_match=True`はこの誤同定の上に成り立つ(Style Gateの精度の論点=UD-3「承認済みStyle照合維持」に直結、§10)。
- **Y E-1**: a2 `y_voice_1`=人間承認attempt5(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、sha`dba23e66…`)、b1b=attempt6(`english_style_prefix_wide_margin`)。両方 `local_rewrite_audio_superseded_by_human_approval=True`。`adopted_audio_sha256`はentryと承認記録で一致。

### 3-4. 記録欠落時の表示
- 欠落項目ごとに`gaps[]`へ記録し、カード内に黄色の「記録なし」枠(`fhr-gap`)+要約表に件数。**LR/Fallbackの最終状態を「なし」と書かない**(「なし」と「記録なし」を区別。サンプル§5)。
- 全体カバレッジ表: 音声単位総数/採用attempt確定数(how別)/記録なし数/Fallback件数/LR件数。記録なしが1件でもあれば資料冒頭に警告帯を出す(受入時にFableが見落とさないため)。

### 3-5. W1(委任_01)への要求(Phase Bで不足なら追記対象)
W1が棚卸す「LR・Fallback発動記録」に、最低限次が**音声単位ごと・採用attempt紐付きで**含まれること: ①採用attemptの特定子(sha256またはattempt id) ②採用attemptのStyle sha/label ③LRの前後英文・変更語句・対象範囲 ④元ブロック/LRブロックの区別(attemptに`block`) ⑤Zの`attempts[]`にLR後ブロックのattempt。現行の保存形では①はX/YがLR時、Zが非LR時に導出可能、②はX/Y/Zの大半が可能、④⑤はX/Y一部のみ(Zは不可)。

### 3-6. Phase Bの記録補強(2案。**どちらも新Family別ロジックではなく追記のみ**)
| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| R1(推奨の第一段) | **保存形は変えず**、読取側のsha一致規則だけで足りる範囲を表示。Z猿の手のような記録なしは「記録なし」と表示 | TTS経路を触らない=リスク最小 | Z LR後のStyleは表示不能のまま(新規runでも) |
| R2(推奨の第二段) | 各Familyの採用確定時に**加法的なキー`final_adoption_record`**(`unit_id,adopted_sha256,adopted_style_sha,adopted_style_label,block=original/lr,lr_before/after,human_adopted`)をentryに追記(既存キーは不変) | 読取が1経路になり記録なしが消える | Production TTS経路の変更(Opus条件A対象) |
推奨: Phase BはR1で資料を完成させつつ、Z LR後attemptのStyle記録(`attempts[]`へ`block`と`style_prefix_sha256`を加える)を**最小のR2**として別委任で行う。Style Gate精度(§3-3 告げ口心臓)は資料作成とは独立に是正する(§10 A-1)。

---
## 4. 表示仕様

### 4-1. 色・書式(原文§6)
| 要素 | 書式 | 備考 |
|---|---|---|
| LR変更後の語句 | 赤`#c00000`・太字・二重下線 + チップ`LR` | 英文全体ではなく変更語句だけ赤 |
| LR変更前の語句 | 赤・取消線 | 前後英文を併記(「変更前」行は灰色の注記行で、語句だけ赤) |
| Fallback対象テキスト | 濃い青`#0a2a6b`のテキスト全体+左に5px青線 + チップ`Fallback` | 区間全体=その音声の対象範囲(本文の該当chunk/KP/日本語音声全体) |
| Fallback注記 | 同じ濃い青 | 必須: 発動の事実・最終採用Style名・通常Style→何へ・範囲 |
| 実行履歴 | 灰色背景枠。色の意味を持たない | 採用されなかった試行・LR前ブロック・人間承認の経緯 |
| 発動なし | 灰色チップ`発動なし` | 0件も明示 |
| 記録なし | 黄色破線枠+チップ`記録なし` | 推測しない |
- 色のみに依存しない: 全カードに文字ラベル、LRは下線/取消線、Fallbackは左線。印刷(白黒)でも区別可能。
- 技術情報(開始/終了時刻・cooldown秒・attempt wav path・sha256)は本文に出さない(sha先頭8桁のみ、折りたたみ`details`の「根拠」内に任意で)。
- 注記は音声ではない。`<audio>`は採用attemptのwavをmp3化したものだけ。**注記テキストはTTSへ渡す経路を持たない**(§5)。

### 4-2. 重複時レイアウト(原文§6-C)
```
[LR][Fallback] 重複   (Role・範囲)
┃ (青い左線) …区間全体は青… <赤太字二重下線: 変更後語句> …
┃ Fallback: 最終採用Style=英語短文Style(Minimal)。通常Styleから切替。範囲=Part 2 chunk 3(全体)   ← 青
LR: 変更前 <赤取消線> → 変更後 <赤太字>(採用attempt=LRブロックのもの)                           ← 灰注記+赤語句
実行履歴(灰): 元ブロックでのFallback試行・LR前の不一致…(最終採用ではない)
```
サンプルHTML§9-A。

### 4-3. 日本語短文Style(Minimal)・ENGLISH_LOCK・Z Dialogue
- 日本語音声Fallback=青、`kind=MINIMAL_JA`、本文は日本語(LRなしと明記しない=LR欄は出さない)。サンプル§9-B(合成)。実データのJA minimal採用例は今回の既公開4件・告げ口心臓に無く、**実データでの表示確認は未実施**(合成例のみ)。
- ENGLISH_LOCK=青、`kind=ENGLISH_LOCK`(実例=告げ口心臓Adv KP2、サンプル§8)。
- Z Dialogue Style切替=青、`kind=Z_DIALOGUE_LEGACY`(3回目=従来Dialogue Style)。Z Dialogue実データでの切替採用は今回の対象runには無い=**未確認**。

### 4-4. Chunk/区間の対応表示
- X/Y/Z本文はchunk単位で単位化し、カード見出しに`Part N / chunk i of M`と本文範囲(最初の数語〜末尾)を出す。`chunk_plan_*.json`・`chunk_tts_evidence_*.json parents`を読む。親(連結音声)単位のLR/Fallbackは子の集約として表示(親の`fallback_used`は読まない)。

---
## 5. 混入防止の構造的保証

**保証したいこと(原文§2)**: 赤/青・注記・変更履歴が、制作スクリプト・TTS入力・ASR正解・学習者向け公開ページ・KP/KW/文法表示・Style Promptに入らない。

| 層 | 設計 | 検査 |
|---|---|---|
| コードパス分離 | 生成器は`json/html/hashlib/os/sys`と`er020.resolve_expected_text_after_local_rewrite`のみimport。公開page builder(`er019_family_x_listening_page_01`/`er063_family_z_audio_01`のpage部/`er_user_listening_page_common_01`/`er121_*page*`)・TTS(`er003_*generate*`/`er127`のTTS実行部)・Prompt/Style組立・KP/文法表示を**import禁止**。逆向き: それらのモジュールが`er_final_human_report_01`をimportしない | **test-1**: ASTでimport集合を検証(双方向) |
| 読取専用 | run dirへ書かない。書込は`--out`配下のみ。`--out`が`user_test/`または`er0*_output/`配下ならSTOP | **test-2**: 生成前後でrun dirの全ファイルsha256が一致。`--out=user_test/x`で終了コード≠0 |
| 出力先分離 | `final_human_report/…`。`user_test/`の学習者向けindexからリンクしない。`<meta name=robots noindex>` | test-3: 学習者向けindex/ページに`final_human_report`文字列0件 |
| 専用識別 | CSS class接頭辞`fhr-`、判別コメント`<!--FINAL_HUMAN_REPORT-->`、チップ文言(`LR`/`Fallback`/`記録なし`の組)は生成器内の定数`FHR_TOKENS`に集約 | **test-4(混入検知)**: 下記の全対象に`FHR_TOKENS`・`fhr-`・`#c00000`+`#0a2a6b`のclass定義・「Local Rewrite採用(音声は原稿から変更」が**0件** |
| 既存page checkへの追加 | `er_user_listening_page_common_01.check_page`(:265-358。公開pageの⏸混入検査と同形)に、公開pageへ`FHR_TOKENS`/`fhr-`が含まれたらNGの検査を**追加**(Phase B) | test-4に含める |
| TTS/ASR側 | `tts_generation_results.json segments[*].text/canonical_text`・`chunk_plan`・`segment_plan_*.json`・attemptの`instruction_text`・`resolve_expected_text_after_local_rewrite`の戻り値に`FHR_TOKENS`が無い | test-4 |
| 資料側の自己検査 | 生成した資料に**学習者向け本文として公開されうる文**(KP/文法の学習用表示)が転記されていない=資料は「確認用の転載」と明示し、学習用表示HTML(`study_text`由来)は埋め込まない(本文英文と日本語訳の対応が必要な場合は`parts.json`の英文のみ) | test-5 |

対象の「混入先」一覧(test-4が走査): ①`user_test/**/*.html`(公開試聴ページ)②`parts.json`/`article.md`/`*_support_texts.json` ③`study_text/*.md`・KP/文法の学習用表示(`er120_part2_wiring_01.public_study_html`出力)④`tts_generation_results.json`のTTS入力フィールド ⑤`audit/tts_block_progress/*.json`の`lr.text` ⑥attempt json `instruction_text`(Style Prompt)⑦`*_script*.md`等の制作スクリプト。

UD-1との整合(装飾と実英文の混同防止、原文§2末): LRによる**実際の英文変更**は別の経路(最終表示本文・TTS入力・ASR正解の一致、W2/W3設計)で反映する。本資料の赤は「装飾」であり、実英文には含めない。資料の`text_display`列は**最終表示本文そのもの**(装飾前の素の文字列)を保持し、赤/青は描画時にspan/classで重ねる(素の文字列から装飾を除去しても元と一致するtest-6)。

---
## 6. A/B/C等既存Familyへの適用

方針: 音声生成方式は置換しない。**資料生成器の読取アダプタ`read_legacy`は、保存記録の構造が適用可能なrunだけ表示し、不足は不足と書く。**

| 記録の有無(run単位の判定) | 判定 | 資料の表示 |
|---|---|---|
| `tts_generation_results.json`に`attempts_log`+`fallback_used`がある | **Fallbackの有無のみ適用可能** | Fallback有無=青(Style名は「記録なし」)、採用attemptは`verified`/sha一致で判定 |
| 上記+`local_rewrite_recovery`がある | LRも適用可能 | 赤表示可 |
| `local_rewrite_recovery`が無い(実測=下表の全run) | LR欄=「このrunはLRの記録形式を持たない」 | 「LR: 記録形式なし」 |
| `attempts_log`も無い(`er013_output` 12run実測) | **記録不足で表示不可** | 「表示不可: 記録形式が未対応」と明記、サンプル§9-C |

実測(保存データを走査、`segments`のキー出現数。調査対象外のFamily A/B/Cは件数の事実のみ): `er012_output`(Voices等)=6run/segments87中`attempts_log`85・`fallback_used`39・`attempt_audio_path`あり・`local_rewrite_recovery`0・`style_prefix`0。`er014_output`=15run/84中`attempts_log`82・`fallback_used`40・LR0。`er003_output`=7run/81中`attempts_log`77・`fallback_used`21・LR0。`er005_output`=6run/81中`attempts_log`71・`fallback_used`34・LR0。`er013_output`=12run/192中`attempts_log`0。→ 結論: Legacyは**Fallbackの有無のみ**表示可能(Style名は記録なし)、LRは0件(記録形式なし)。Family A/B/Cは「今後のActive Production Familyではなくバックアップ・過去資産」(`CURRENT_SPEC.md:1664`)のため、Legacy資料の自動生成は新規runが無い限り不要=**既存run分の遡及生成はしない**(必要時のみ手動実行)を推奨(判断候補C)。

---
## 7. 既公開4件+告げ口心臓への適用(`W4_SAMPLE_01.html`参照)

| 対象 | 保存元 | 表示内容 | サンプル節 |
|---|---|---|---|
| X AI島 Std | `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/audit/tts_generation_results.json segments[full_story_part1_k2]` | LR赤(AIs→AI agents)。Fallback=不採用のため青なし(実行履歴に灰色で記載) | §1 |
| X AI島 Adv | 同 b1b | LR赤(AIs→AI systems)。minimal_fallback attempt3は不採用 | §2 |
| X 英単語ガチャ Adv | `…/word_gacha__run_wg_01/b1b/audit/…[full_story_part3]` | LR赤(you've→you have)。UDR #183(a)承認 | §3 |
| Z 走れメロス Adv | `er026_output/family_z_production_e2e_01/melos/run_e2e_04/b1b/audit/…[full_story_part3_c1]` | LR赤(Melos→He) | §4 |
| Z 猿の手 Std | `…/the_monkeys_paw/run_sf_prod_01/a2/audit/…[full_story_part1_c10]` | LR赤(guest→visitor)+Fallback「記録なし」 | §5 |
| Y E-1 Std/Adv | `er121_output/family_y_production_01/redelivery_fee/run_01/{a2,b1b}/audit/…[y_voice_1]`+`ypl7_user_approval_record_y_voice_1.json` | Std=Fallback青(EN短文)、LR案は人間承認で不採用(赤なし)。Adv=通常Style・LR案不採用 | §6・§7 |
| Z 告げ口心臓 | `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01/{a2,b1b}/audit/tts_generation_results.json`+`narration/attempts/*.json` | LR 0(Std20・Adv19単位走査)、Fallback: Adv KP2「mock」ENGLISH_LOCK 1件(青) | §8 |

注: AI島は現状の公開本文が`AIs`のまま(UD-1・UD-2の反映は別委任)。資料の「変更後」は、UD-1反映後に最終表示本文となる文を指す。メロス・猿の手はUD-1反映前の公開ページ(Local Rewrite注記あり)で、反映後は注記が不要になる。

---
## 8. test計画(Phase B。本書は計画のみ、test未作成)

1. **単体: 採用attempt判定**(`er_final_human_report_01_test_01.py`): ①sha一致が複数→最終saved_at ②LR採用で元ブロックattemptを最終Styleにしない(AI島Std型fixture: `fallback_used=True`+LR最終通常Style→Fallback非表示) ③人間承認attempt優先(Y E-1型) ④採用不明→`how=unknown`・「記録なし」(猿の手型) ⑤post_slowdown擬似attemptを除外 ⑥Z `style_actual`と最終sha不一致(告げ口心臓型)でsha一致を優先 ⑦attempt jsonが非UTF-8/破損(告げ口心臓委任_03で`kp2_en_attempt2…json`がUTF-8不可の指摘あり)→`gaps`に記録し落とさない。
2. **単体: 重複**: LR+Fallbackでの色分け、Style名=LRブロック採用attemptから、元ブロックFallbackは履歴のみ。
3. **単体: 記録欠落**: 各欠落(attempt/Style/LR前後)で「記録なし」、「発動なし」と区別。
4. **混入検知**(§5 test-1〜6): AST import双方向、run dir不変、出力先制約、公開HTML/TTS入力/ASR正解/Style Prompt/KP表示/study_textに`FHR_TOKENS`0件、素の本文の復元一致。
5. **Family別integration**(保存データfixtureで実行、API 0): X(AI島 Std/Adv・ガチャ Adv)・Y(E-1 Std/Adv)・Z(メロス Adv・猿の手 Std・告げ口心臓 Std/Adv)・Legacy(er012/er014各1run=Fallback有無のみ、er013=表示不可)。期待値は**§3-3の実測値**(例: 告げ口心臓Adv Fallback=1・LR=0、AI島Std Fallback=0・LR=1)。不整合な出力を期待値にしない。
6. **既存test**: `er019`/`er121`/`er063`の公開page test・`er_user_listening_page_common_01`のcheck_page testが変わらずPASS(追加検査のみ)。
7. **runtime evidence(Phase B受入)**: 実runの完了後に資料生成→URLで目視(赤/青/ラベル/区間対応)。有料runは最小限(原文§11)。本設計の資料生成自体はAPI 0。

---
## 9. Phase B実装の作業分解(影響範囲の見積り)

| # | 作業 | 変更先 | 規模 | 並列 |
|---|---|---|---|---|
| B1 | 共通中間表現+レンダラ+CSS | 新規`er_final_human_report_01.py` | 中 | 可 |
| B2 | Xアダプタ(LR/Fallback採用判定、chunk親子) | 新規(同ファイル内) | 中 | B3・B4と並列 |
| B3 | Yアダプタ(人間承認採用) | 同上 | 小 | 可 |
| B4 | Zアダプタ(`attempts[]`+attemptファイルsha照合) | 同上 | 中 | 可 |
| B5 | Legacyアダプタ(Fallback有無のみ・表示不可判定) | 同上 | 小 | 可 |
| B6 | 混入検知test・AST test・run dir不変test | 新規test | 中 | B1と並列 |
| B7 | `check_page(public)`へ`FHR_TOKENS`検査追加 | `er_user_listening_page_common_01.py`(加法) | 小 | 可 |
| B8 | runner完了hook(任意、失敗非ブロッキング) | X/Y/Zのrunner末尾(`er078_pass_with_warning_registry`と同形) | 小 | B1後 |
| B9(別委任) | Z LR後attemptのStyle記録(R2最小) | `er063_family_z_audio_01.py` | 小〜中 | 独立。Opus条件A対象 |
| B10(別委任) | Z `style_actual`採用attempt同定の是正(§3-3 告げ口心臓) | `er063:1996-2036` | 小 | 独立 |
クリティカルパス=B1→B2/B3/B4→integration。B6・B7・B9・B10は並列可。所要見込み(実装+test)=B1〜B8で並列時1委任相当(別途見積り)。

**Opus条件A(新構造・処理フロー)で見てほしい観点**: ①新設vs拡張の判断(§1) ②採用attempt確定規則の網羅性と反例(§3-2。特にchunk親子・再利用entry・resume・Master Audio Store再利用音声=LRなし/Style記録なし) ③混入防止の構造的保証が実際に破れないか(§5。特に`er_user_listening_page_common_01`との境界) ④R1/R2の線引き(§3-6) ⑤UD-3とZ Style Gate精度の関係。

---
## 10. 判断候補(区分付き。`USER_DECISION_REQUIRED`の判定はFable)

| ID | 内容 | 区分 | 根拠 |
|---|---|---|---|
| A-1 | Z `style_actual`の採用attempt同定が実際の採用音声と食い違う(告げ口心臓Adv KP2。§3-3)。資料とは独立に是正(sha一致で同定)。UD-3「承認済みStyle照合維持」の精度に関わる不具合=PM_GOVERNANCE 11-8(承認済み設計原則との矛盾=不具合)に該当する見込み | **A**(既存仕様内で自己解決) | 原文§5「承認済みStyleとの照合は維持」、`er063:1996-2036` |
| A-2 | 告げ口心臓の「Fallback 0」はAdv KP2 ENGLISH_LOCK 1件が実在(承認済みKP_EN 4回構成の範囲内=§7 policy KP_EN。品質NGではない)。資料に青で表示する。受入記録の「Fallback 0」を訂正 | **A** | `er127_tts_block_policy_01.py:112`、`narration/attempts/kp2_en_attempt3_custom31eb2f72.json` |
| B-1 | 記録補強の線引き=R1(読取のみ)で資料を完成+Z LR後attemptのStyle記録(R2最小、B9)を別委任で行うか | **B**(Fable判断) | §3-6、Opus条件A対象 |
| B-2 | Z公開試聴ページの既存LR注記(`er063:2465-2468`)とstyle列: UD-1反映後は本文=音声で注記が不要。原文§2は「学習者向けの通常公開ページ」への混入禁止。user_test配下のZ試聴ページを「学習者向け公開ページ」とみなして注記を撤去するか(提案: 撤去し最終Human報告へ移す。style列・制作情報も同様に学習者向けから外すか) | **B** | 原文§2、`er019_family_x_listening_page_01.py:150-175`(Xの制作情報・事後試聴リストも同居) |
| B-3 | 出力先dir名(提案`final_human_report/<family>/<slug>/<run>/`。GitHub Pagesの既存配布経路を使用、`user_test/`外) | **B** | PM_GOVERNANCE 7-X(配布経路GitHub Pages) |
| C-1 | Legacy A/B/Cの既存run分の資料遡及生成はしない(新規run時のみ・必要時手動)。表示可否の判定ロジックは実装 | **C**(軽微・実害なし) | `CURRENT_SPEC.md:1664`、§6 |
| C-2 | JA minimal・Z Dialogue切替の**実データ表示確認は今回対象runに該当なし**=合成例で代替(サンプル§9)。実run発動時にPhase B受入で目視 | **C** | §4-3 |
| C-3 | 資料内`details`に出すsha先頭8桁(根拠表示)は技術情報の最小限として許容。時刻・cooldown・pathは非表示 | **C** | 原文§6末 |
| D | **なし**。色・注記範囲・混入禁止・技術情報不要・LR/Fallback重複表示はすべて原文§2・§6で決定済み(再質問しない) | — | 原文§2・§6 |

### 新規Open候補(登録はFable。SSOT未編集)
- **OPEN候補1**: Z `style_actual`の採用attempt同定が実採用Styleと不一致(`er063:1996-2036`、告げ口心臓Adv `kp2_en`)。分類=**修正へ進む**(同一Phase B内の別委任B10で着手)。
- **OPEN候補2**: Z LR後attemptのStyle記録欠落(猿の手Std `full_story_part1_c10`)。分類=**修正へ進む**(B9。R1だけで資料は出せるが「記録なし」が残る)。
- **OPEN候補3**: X/Yのentry直下`fallback_used`が元ブロック基準でLR後の最終採用Styleとは別(AI島Std)。M3の`STD_FALLBACK_USED_OR_UNKNOWN`(`er019_family_x_style_profile_01.py:717`)の誤BLOCK要因。UD-3でW3が扱う想定。分類=**修正へ進む**(W3委任に引渡し)。

---
## 11. RESULT_PACKET用4行

1. 既存仕様整合: `er127_tts_block_policy_01.py:99-123`(policy・LR_ROLES)、`er020_tts_retry_local_rewrite_01.py:852-891`、`er019_family_x_style_profile_01.py:685-743`、`er063_family_z_audio_01.py:1996-2036,2440-2475`、`er019_family_x_listening_page_01.py:150-175`、`er_user_listening_page_common_01.py:265-358`、`CURRENT_SPEC.md:1664`、原文§2・§5・§6。
2. 未承認機能の既定値: 本書は設計のみ・コード変更0。Phase Bの資料生成器は既定で呼ばれない読取専用CLI(flag・暗黙ON経路なし)。
3. 失敗終了時の最終成果物: 失敗しても資料未生成のまま組立成果物は不変(資料は後処理)。実在の成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/W4_FINAL_HUMAN_REPORT_DESIGN_01.md`・`W4_SAMPLE_01.html`。目的適合: 原文§6のA/B/C(赤/濃青/重複)・§10-7〜9を満たす設計とサンプルまで。実装・実run確認は未(Phase B)。
4. 撤去・残置: 撤去提案=Z公開ページのLR注記(`er063:2465-2468`、UD-1反映後・B-2判断待ち)。残置=既存HR依頼ページ・事後試聴リスト。Grep: 撤去対象識別子`Local Rewrite採用(音声は原稿から変更`は`er063_family_z_audio_01.py:2465,2468`のみ(本書時点で未撤去)。
