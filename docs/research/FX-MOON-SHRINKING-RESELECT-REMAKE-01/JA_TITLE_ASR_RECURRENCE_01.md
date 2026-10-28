# JA_TITLE_ASR_RECURRENCE_01(FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03、2026-10-28)

対象: Family X『月は少しずつ縮んでいる？』Standard(a2)日本語タイトル `月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密`。run=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`。ユーザー原文=`docs/pm/delegation_log/2026-10-28_FX-MOON-SHRINKING-RESELECT-REMAKE-01_USER_04.md`。

調査は保存音声・ASR記録の再利用(API 0)+再ASRの小規模実行(OpenAI 12回・Azure 3回、費用見積≒¥0.99、Cap ¥5内。TTS再生成0)。**Production変更0・修正commitなし**(§4)。

## 0. 結論(先に)

1. **真因**: 今回の3回NGは「F1+F2/E3/E4の発動漏れ・配線漏れ」ではない。**2026-10-25のTask Bで原因R1として特定済みで、解決策が未採用のまま残っている型**である。日本語の読み比較が助詞「は」を「は」と読み、「わ」と読まないため、原稿『月のしわ』とASR転写『月の詩は/月野氏は/月の死は…』が**構造的に一致しない**(`er011_ja_asr_variant_layer_01.py:96-98`が形態素解析のkana(ハ)をpron(ワ)より優先)。今回の18転写(記録6+再ASR12)では、OpenAI・Azure・ローカルWhisperのどれも『しわ/シワ/皺』と書かず、常に『詩は/氏は/死は/市は』系(同音のため文字を選べない)。過去(ms_03の保存3本+Task Bの再転写9本)でも『月のシワ』と書いたのは1件のみ(`phase3_run/usage_log.jsonl`)。
2. **既存対策の実態**: F1+F2・E3・E4はいずれも**誤PASSを減らす(PASS集合を縮める)是正**で、構造上、この誤NGを救う機能を持たない。誤NGを救う案(v2の読み規則[助詞は→わ]・②B-light β)はTask Bで「VALIDATED(限定)」まで検証されたが、ユーザー決定(`docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_03.md` §1「①v2・②B-lightのProduction採用を意味しない」)により**Production未採用・未配線**。今回の3音声と過去(run_ms_03)の3音声を**現行Production判定器に通すと全6本が記録と同じNG**(§2B)。Task Bの採用分は当該題を救っておらず、評価時点で「base 2→F1F2 1(12転写中)」と、当該題の通過数をむしろ減らす側だと記録されていた(`B_LIGHT_EVAL_02.md` §1)。`DECISION_LOG.md:22501`にも「救済はv2/β担当」と書かれていたが、v2/βが未採用のため**担当が不在のまま**。
3. **TTS発音ミスかASR誤判定か**: 数値は正しく読まれている(ローカルWhisper 6/6が『8,900』、Azureも8900)。『しわ』部分は全ASRが同音の『詩は』系に収束し、同一音声のOpenAI転写が毎回崩れ方を変える(§2A)ことと整合し、**ASRの同音選択・誤認識が主因と見るのが自然**。ただし**TTSが『つきの・しわ』と正しく読めているかは音声を聴くまで確定できない**(推測でPASSにしない)。特に今回#3(fallback)は、OpenAI『スギノ市は』・Azure『Sukino氏は』と冒頭「月の」が別音に聞こえている可能性があるため、Human Review用ページを用意した。
4. **新しい回帰か**: いいえ。過去から残存する既知の型。過去6音声の再判定も不変。
5. **修正**: 承認済み仕様の範囲内で是正すべき**配線漏れ・経路漏れ・回帰は発見なし**。この題を解決するのは新しい受理クラス(v2読み規則等)の採否で、これは**ユーザー判断事項(判断候補D)**。実装しない(§5)。
6. **配線総点検**: JA判定の入口は全Family共通の1関数。日本語音声のsegmentは全Familyで**Standardのみ**(Advancedは日本語音声なし)。F1+F2はX・Zで発火証拠あり、Yは「r5計測付き判定あり・F1の対象事象0件」=従来どおりruntime未確認。E3/E4は同一adapterに配線され、実runの発火は0件(API 0注入のruntime証拠のみ)。

## 1. 一次資料

- 今回3 attempt: `a2/audit/tts_generation_results.json` `segments.japanese_title.{standard_attempts_log,fallback_attempts_log}`、`a2/narration/attempts/japanese_title_attempt{1,2,3}_*.json/.wav`、`a2/audit/tts_block_progress/japanese_title.json`(final_status=STOPPED)。
- 過去: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/japanese_title_attempt{1,2,3}_*.json`、承認記録`a2/audit/fxnr10_user_approval_record.json`(adopted_attempt=2、sha f0c4b415…、scope=「this single segment / attempt 2 only; NOT a general ASR-check exemption」)。
- Task B: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`(ROOT_CAUSE_01、B_LIGHT_EVAL_02、OPEN517_*、OPEN333_*、`trace_moon_classify_01.out.txt`、`whisper_local_3wav_01.json`)、`OPEN_ITEMS.md` OPEN-515(行1030)/OPEN-517(行1032)/OPEN-333(行836)、`CURRENT_SPEC.md:2257`(Variant Layer承認)・`:2919-2920`(F1/F2/R-5)・`:2931`(OF-AUW-08 JA受理集合)、`DECISION_LOG.md:22476-22521`(委任_07A/10/12/14)。
- 本調査の再現script・出力は同フォルダ: `ja_title_trace_01`・`ja_title_rejudge_01`・`ja_title_detection_check_01`・`ja_title_whatif_unadopted_01`・`ja_title_whatif_fresh_01`・`ja_title_reasr_01`・`ja_asr_wiring_matrix_scan_01`(`.py`と`.out.*`)、`tally517_reselect_01.out.json`・`tally333_reselect_01.out.json`、`ja_title_local_whisper_reselect_01.json`。Human Reviewページ=`user_test/fx_moon_title_asr_listen_01/index.html`(生成=`build_title_listen_page_01.py`)。

## 2A. 今回3 attemptの事実

正本=`tts_generation_results.json`のasr_judgement。ASRのmodel_id(`r5.models`)=Primary openai_asr/gpt-4o-mini-transcribe、Secondary azure-speech-stt。**Azureは3回とも実行済み**(`secondary.called=true`、各¥0.31〜0.36)。

| attempt | OpenAI(Primary)転写 | Azure(Secondary)転写 | 値ガード P/S | 記録判定 | 現行Production再判定 |
|---|---|---|---|---|---|
| #1 標準1 sha 6801464b… | 月野氏は8,900本超。その奥に潜む岩の上着の秘密 | 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | EQUAL/EQUAL | NG_BOTH secondary_not_accepted | 同じ |
| #2 標準2 sha dd3dbc1e… | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 | 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | EQUAL/EQUAL | NG_BOTH secondary_not_accepted | 同じ |
| #3 fallback sha 45309c9f… | スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。 | Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | EQUAL/EQUAL | NG_BOTH secondary_not_accepted | 同じ |

- ローカルWhisper(参考・本番判定外、`ja_title_local_whisper_reselect_01.json`): #1 `月の死は8900本長`(small)/`月の死は8,900本帳`(medium)、#2 `月の死は8900本長、`/`月の死は8,900本蝶、`、#3 `月の詩は8900ポンチョ、`/`月の死は8,900ポンチョウ。`。
- **F1(READING_MATCH最終Gate)**: 発動せず。Primaryの`equivalence_basis`がREADING_MATCHではない(`primary.label=TRUE_CONTENT_MISMATCH`、`r5.f1.reading_match_primary_pass=false`、`final_gate={applied:false}`)。rollback定数`READING_MATCH_FINAL_GATE=True`(`r5.f1.rollback_const_READING_MATCH_FINAL_GATE=true`)。F1が止めたのではない。
- **F2(かな数詞統一)**: 非発動(`r5.f2.enabled=false`)。F2はREADING_MATCH PASSの最終Gateのみが対象。値側は3回とも値ガードEQUAL(`8,900本`↔`8,900本`/`八千九百本`/`8900本`、`reason=same_surface/same_value_unit`)で、**数値は問題ではない**。
- **E3/E4(Candidate E)**: 非発動(`asr_judgement`に`candidate_e_full_diff`・`candidate_e_cascade_return`のキーなし。`tally333_reselect_01.out.json` e3_fired=0・e4_fired=0)。Candidate Eには到達したが、`_span_pair_reading_variant_match('しわ','詩は')=False`(`ja_title_trace_01.out.txt`)で「読みで説明できない差分」のままTRUE_CONTENT_MISMATCH。仮想形『詩わ』なら`True`(同ファイル最終行)=**原因は助詞「は」の比較規則のみ**。E3/E4が拒否・Cascade戻ししたのではなく、それ以前に、承認済みの同音異表記救済(Candidate E)が助詞「は」で成立しない。
- **段階別のNG原因**: (1)Primary: 値EQUALだが読み比較で`しわ`↔`詩は`(#1は`のしわ`↔`野氏は`)が不一致→TRUE_CONTENT_MISMATCH。(2)Secondary(Azure)も同型(`詩は`)で、#1は`超`→`ちょ`(末尾欠け)、#3は`Sukino氏`。(3)Secondaryの受理は文字一致のみ(`er007_ja_secondary_asr_01.py:647 _secondary_accept`が値等価層を通さない=R4)で緩和経路がない→`secondary_not_accepted`→NG_BOTH。(4)標準2+fallback1=3回で`final_status=STOPPED`。
- **再ASR(今回、OpenAI×4/wav・Azure×1/wav、`ja_title_reasr_01.out.json`)**: 同一音声でも毎回表記が変わる。#1: `月の詩は8,900本超`/`月野氏は八千九百本超`/`月の詩は八千九百本調`/`好きの詩は八千九百本超`。#2: `月の詩は8000900本超`×3/`月野氏は発線900本超`。#3: `杉の市は、8000坪の`/`月野市は、八千九百本超`/`月の死は、発生900本超`/`月野氏は、発生900本超`。**12/12で『しわ/シワ/皺』なし**。数詞は『8000900』『発線900』『発生900』のように崩れる(Task BのR2と同型)。各転写を同wavのAzure転写と組み合わせて現行Productionへ通すと**12/12とも非PASS**(NG_BOTH 4・NG_PROTECTED 7・NG_EXCLUDED 1)。
- **Human Review**: `user_test/fx_moon_title_asr_listen_01/index.html`(今回6音声+過去ms_03の3音声、原稿、OpenAI/Azure/Whisper転写、記録判定、再転写)。聴いてほしい点は1つ: 冒頭「月のしわ」が自然に『つきの・しわ』と聞こえるか。特に今回#3(なお過去ms_03 #3[fallback]もAzureは『杉野氏は』と転写したが、ユーザーは聴いて問題なしと判断済み=Azureの『つきの→杉野』誤認識の前例)。過去ms_03の3本はユーザーが「どれも問題ありません」と判断済み(`2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_06.md`)。

## 2B. run_ms_03(過去)との突合・現行Production再判定

| ms_03 | OpenAI転写 | Azure転写 | 当時の判定 | 現行Production再判定(`ja_title_rejudge_01.out.json`) |
|---|---|---|---|---|
| #1 | 月野詩は8000句800本超え。… | 未実行 | NG_PROTECTED p1_value_diff | 同じ(Azure呼出0) |
| #2(ユーザー個別承認) | 月の死は八千九百本超。… | 月の詩は8900本超。… | NG_BOTH secondary_not_accepted | 同じ |
| #3 | 月の氏は8000900本超。… | 未実行 | NG_PROTECTED p1_value_diff | 同じ(Azure呼出0) |

- **同じ失敗クラスか**: ms_03 #2は今回#1/#2と同型(値EQUAL・読みが助詞「は」で不一致)。ms_03 #1/#3は値側(OpenAI数詞崩れ)でP1打切り(`er078_asr_unified_judge_01.py:641-642`。JAはAzureを呼ばない。R2。KP英語[vote_required]のみP1をskip)。今回は3回とも値は揃い、読み不一致だけが残った。**根はms_03も今回もR1(+R2)**。
- **Task Bの採用分は当時の3音声を救うか**: 救わない(上表、再判定で確認)。Task B評価(月題12転写、`B_LIGHT_EVAL_02.md` §1): base 2 / base+F1F2(採用分) 1 / +β(未採用) 5。E3単独で月題#1が1/677(0.148%)新規NG化(`DECISION_LOG.md:22501`「承認済み仕様どおり。救済はv2/β担当」)。
- **誤PASS検出の確認**(現行Primary判定、`ja_title_detection_check_01.out.json`): 『月のすわ』・値10倍(89,000)・値違い(8,000/八千百)・岩→石・語脱落は全て非PASS。回帰test(`er011_ja_asr_variant_layer_candidate_e_cascade_return_test_01.py`・`…full_diff_test_01.py`・`er078_asr_r5_measurement_test_01.py`・`er078_asr_value_guard_kana_unify_test_01.py`)=**104 passed**。Task B評価セット: F1F2 N-3増分誤PASS0・既知負例9/9遮断、E3/E4はPASS集合が縮むのみ(`DECISION_LOG.md:22476,22499,22515`)。
- **未採用候補のwhat-if**(検証のみ、API 0、`ja_title_whatif_unadopted_01.out.json`・`ja_title_whatif_v2_primary_01.out.json`・`ja_title_whatif_fresh_01.out.json`):
  - v2 Primary層(助詞は→わ等価): 今回#1・#2=PASS(警告JA_PRON_EQUIVALENT)、#3=NG維持。ms_03 #2=PASS、#1/#3=NG維持(値崩れ)。再ASR12転写中3件PASS。
  - β(Secondary=値の証人+Primary=読み): 今回#1・#2=PASS_WITH_WARNING(試聴必須)、#3=NG(primary_reading)。再ASR12転写中6件PASS。うち1件は#3由来の`月野市は`(読みが原稿と合う扱い)で、#3の実音声が「スギノ」系なら**誤PASSになり得る**ため試聴確認が前提。strict読み(v2規則なし)では0。効果の大半はv2読み規則に依存(`B_LIGHT_EVAL_02.md` §9と同結論)。
- **隠れた別欠陥(実測)**: 原稿の桁区切り『8,900』を、ASRが『8900』と書くだけで(他が完全一致でも)Primary・Secondaryとも不一致になる。実測: `月のしわ、8900本超！その奥に潜む「岩の上着」の秘密`→TRUE_CONTENT_MISMATCH(content_diffs=`','`の脱落)。AzureはTask Bで見たとおり桁区切りを書かない(今回3回とも`8900`)。Task BのR3(`er007_ja_asr_validator_01.py`のnormalize_ja)・R4(`_secondary_accept`に値等価層なし、`CURRENT_SPEC.md:2931`「値等価正規化後の一致を含む」との乖離)で、**R1が解消されても、ASRが『しわ』と書いても、この題はR3/R4で落ちる**。JA原稿363件中この題のみが桁区切りを含む。

## 2C. 配線総点検

### 承認済み仕様vs実装

| 対策 | 承認の位置づけ | 実装(rollback定数) | 一致 |
|---|---|---|---|
| F1+F2(OPEN-517)+OPEN-523/524 | ユーザー`APPROVED_FOR_PRODUCTION`(2026-10-25 USER_03 §1、X/Y/Z共通) | `er078_asr_unified_judge_01.py:80 READING_MATCH_FINAL_GATE=True`、`er078_asr_value_guard_01.py KANA_WORD_BOUNDARY_CHECK/WEAK_KANA_REGION_COMPAT=True`、R-5計測 | 一致(`CURRENT_SPEC.md:2919-2920`) |
| E3(OPEN-333 数値entryの非数値差再検査) | 承認済み不具合是正(11-8、Opus条件C。`DECISION_LOG.md:22497-22505`) | `er011_ja_asr_variant_layer_01.py:411-413`定数True、`:376` | 一致 |
| E4(便乗PASS=cascade_eligible差分) | 承認済み不具合是正(`DECISION_LOG.md:22513-22521`) | `er011…:386 CANDIDATE_E_CASCADE_DIFF_RETURN=True` | 一致 |

- 全てProduction正式module(er078/er007/er011)内で、DEV/Trial専用ではない。rollback定数はenv/flag/引数から切替できない(`rg` の結果、定義module+testのみ)。現行値は全てTrue(実行確認済み)。
- JA判定の入口は全Family共通の`n3_tts.generate_a2_japanese_with_reading_safety`(→`ja_secondary.evaluate_attempt_ja_with_cascade`→`unified_judge`)。X(`er019_family_x_audio_production_runner_01.py:2051,2069,2199`)・Y(`er121_family_y_audio_01.py:695,705`)・Z(`er063_family_z_audio_01.py:1071,1132`)が同じ関数を呼ぶ(静的証拠)。
- 統一judge配線静的監査`er078_asr_unified_wiring_static_audit_01.py`は14 PASS/1 FAIL。FAILは英語KP3票系の3呼出(`er103_proper_noun_alarm_policy_01.hr_residual_summary`・`er104_kp_three_asr_vote_01._classify`・`er104_kp_vote_reuse_01.evaluate_vote`)のallowlist未登録と`er019_family_x_validation_inheritance_01.rejudge_with_current_judge`のcount差。**JAの配線漏れではなく英語側のallowlist記録不整合(別件)**。

### retry / fallback / regeneration / resume

- retry・fallback: 今回runの標準#1/#2・fallback#3の全てにr5付きasr_judgementがある(`fallback_attempts_log[0].asr_judgement.r5`あり)=同一判定器が全attemptに適用。
- 再生成: 統一3回構成(2標準+fallback、180秒待機、`er127`)内で同じ判定器。Local RewriteはEN 5 roleのみ(JAは対象外=承認済み)。
- resume/継承: `er019_family_x_validation_inheritance_01.py:262-264`(`rejudge_with_current_judge`)で、JA(a2のtitle/preview/comment/KP日本語意味)は日本語Primaryを再導出せず、元の正式Validationを維持して**最終ANDゲート(値DIFF・否定差)のみ再適用**(AUW 委任_04の承認済み設計)。E3/E4は継承JAには再適用されない(PASS集合が縮む是正のため、旧PASSが継承で残り得る。実害の有無は未測定)。

### Family × Level × Section 行列

正式run記録から機械集計(`ja_asr_wiring_matrix_scan_01.out.json`)。列=(JA segment数 / うちr5付き[Production commit 58cbf7786以降の判定を通った印] / F1最終Gate評価あり / READING_MATCH PASSでF1が対象になった事象)。nは過去run全体の累計。

| Family×Level | Section | 集計 | F1+F2 分類 | E3/E4 分類 |
|---|---|---|---|---|
| X Std | タイトル | 31 / 12 / 9 / 0 | 配線のみ(同一adapter・r5実行あり。対象事象0) | 配線のみ(共通adapter。実run発火0) |
| X Std | Preview | 25 / 2 / 2 / 1 | **WIRED+runtime証拠**(`tally517_reselect_01.out.json`、`OPEN517_RUNTIME_EVIDENCE_02.md`) | 同上 |
| X Std | Comment | 100 / 8 / 8 / 5 | **WIRED+runtime証拠**(F2 enabled 5) | 同上 |
| X Std | KP日本語意味 | 54 / 8 / 8 / 0 | 配線のみ(事象0) | 同上 |
| Y Std | タイトル | 12 / 7 / 6 / 0 | 配線のみ(runtime未確認) | 同上 |
| Y Std | Preview | 5 / 4 / 0 / 0 | 配線のみ(runtime未確認。『思いどおり/思い通り』表記差でNG_BOTH 4=F1/F2で救えない型) | 同上 |
| Y Std | Comment | 24 / 9 / 9 / 0 | 配線のみ(runtime未確認) | 同上 |
| Y Std | KP日本語意味 | 6 / 3 / 3 / 0 | 配線のみ(runtime未確認) | 同上 |
| Z Std | タイトル | 27 / 6 / 6 / 2 | **WIRED+runtime証拠** | 同上 |
| Z Std | Preview | 25 / 4 / 4 / 2 | **WIRED+runtime証拠** | 同上 |
| Z Std | Comment | 75 / 12 / 12 / 8 | **WIRED+runtime証拠** | 同上 |
| Z Std | KP日本語意味 | 107 / 22 / 22 / 2 | **WIRED+runtime証拠** | 同上 |
| X/Y/Z Adv | 全Section | JA音声segmentなし | 対象なし(日本語音声を作らない構成。runtime: b1bのlang=ja asr_judgement 0件) | 対象なし |

- 分類規則: 「WIRED+runtime証拠」=その行のSectionでF1が対象になった事象が1件以上。「配線のみ」=F1最終Gate評価の記録はあるが対象事象が0件(コード・記録上は同一関数を通るが、READING_MATCH PASSの事象がまだ無い)。X全体のF1実動作はPreview/Commentで確認済みで、判定コードはSection共通。
- E3/E4: 共通adapterで全JA判定が通る。**実runでの発火は全Familyで0件**(今回run=`tally333_reselect_01.out.json`、Y=`OPEN517_RUNTIME_EVIDENCE_03_Y.md`)。発火証拠はAPI 0注入のみ(`open333_runtime_fire_01.out.txt`:E経由PASS 23→21・拒否発火5attempt/8pair、`open333_e4_runtime_fire_01.out.txt`:発火74、Azure原稿どおり→PASS_WITH_WARNING 74/74・同じ誤り→NG_BOTH 74/74)。E3/E4は「発火しない=誤PASSがない」が正常のため0件は欠陥の証拠ではないが、「正式runtimeでの発火証拠」という厳密基準では**未取得**。
- 承認済み意図的除外=Adv(日本語音声なし)・英語Section・EN専用Local Rewrite。**未配線のSection=なし**(JA音声の全Sectionが共通経路)。Family A/B/Cの旧経路(J5/J9/J10)も同adapter経由(互換性のみ。触れていない)。

## 3. 原因の整理(Task B R1〜R4との対応)

| 要因 | 内容 | 今回 | 状態 |
|---|---|---|---|
| R1 | 助詞「は」をハで比較(`er011…:96-98`)。『しわ』↔『詩は/氏は/死は』が一致しない | 6/6本+再ASR12/12で成立 | **未解決・v2読み規則[P-1]の採否待ち** |
| R2 | OpenAIの数詞崩れで値DIFF→P1がAzureを呼ばず即NG(`er078:641-642`) | 今回の記録3本は値が揃い不発。再ASR12転写中7件(NG_PROTECTED)、過去ms_03 #1/#3 | 未解決(βの担当。ユーザー採否待ち) |
| R3 | 桁区切り『8,900』をnormalize_jaが除去しない | 潜在(今回のASRが偶然『,』を書く/Azureは常に書かない) | 未修正。承認済み仕様内の不具合候補(§5 J3) |
| R4 | Secondary受理に値等価層なし(`CURRENT_SPEC.md:2931`との乖離) | 潜在 | 未修正。承認済み仕様内の不具合(OPEN-515 R-6、分類=修正へ進む) |

## 4. 実施した修正

なし。理由: (1)この題の解決に必要なR1は、受理面を広げる新しい受理クラス(ユーザー決定USER_03 §1で採用範囲外と明示)で、11-8の「承認済み仕様との矛盾の是正」に該当しない。(2)R3/R4は承認済み仕様内の不具合候補だが、単独ではこの題を救わず(R1が支配的)、受理面を広げる方向の変更でもあるため、独断で先行せず次委任案として提示する。Production・Prompt・閾値・flag・承認記録は未変更。追加したのは調査script・出力・Human Reviewページのみ。

## 5. 判断候補(根拠付き、A既判断/B承認範囲内で自己解決/C現タスクと独立/D真に新しい判断)

| ID | 内容 | 区分 | 根拠 |
|---|---|---|---|
| J1 | v2読み規則(助詞は→わ/へ→えの発音等価。桁区切り正規化を含む)のProduction採否。採ればこの題の#1/#2型を「PASS+警告+試聴必須」で救済。増分誤PASSは評価セットで0(N-3 30+N-1 150)、再ASR12転写中3件PASS | **D**(ただし「承認済みCandidate Eの(c)同音異表記[`CURRENT_SPEC.md:2257`]が助詞「は」で成立しない実装不備」と再分類できるなら**B**。再分類はFable/Opus判断) | `DECISION_LOG.md:22501`(Fable: 判断候補D)、USER_03 §1 |
| J2 | ②B-light β(Secondaryを値の証人にする複合判定)の採否 | **D** | `B_LIGHT_EVAL_02.md` §8-9(VALIDATED[限定]・低優先、効果の大半がJ1依存) |
| J3 | R3(桁区切り)・R4(Secondary値等価層)の先行是正。承認済み仕様内の乖離。J1と独立に先行可(API 0・1委任、Opus条件C相当の軽量レビュー推奨) | **B**(Fableが委任すれば足りる。ユーザー判断不要) | `CURRENT_SPEC.md:2931`、OPEN-515 R-6(「別件・修正へ進む」) |
| J4 | 6音声の試聴(特に今回#3)。J1/J2採否や承認音声の再利用判断の前提 | Human Review(仕様判断ではない) | `user_test/fx_moon_title_asr_listen_01/index.html` |
| J5 | 承認済み音声(sha f0c4b415…)の新run再利用注入 / 題の変更 | 本委任の範囲外(Fableの別ルートで確認中) | 承認記録scopeは「this single segment / attempt 2 only」 |

自己評価: この題を通す最短・低リスクの経路は「J4で聴取→承認済み音声の再利用(J5)」(費用0、既承認の同一text・同一sha)。J1は、効果が実質この題と同型(助詞「は」を含む短いタイトル/文)に限られ、Task B評価でも「月題中心・汎化未確認」のため、再発防止としては**必要十分な小さな規則か、運用(同型NGで承認済み記録を先に確認)で足りるかの選択**。推奨は、J3を先行(欠陥の是正)、J1は今回の試聴結果と合わせてユーザー判断(採るなら小さな規則として実装・Opus条件C)。J2は当面不採用が妥当。

## 6. 残る問題

- R1〜R4(上表)。Task B採用分(F1+F2/E3/E4)は仕様どおり動作しているが、誤NG救済の担当(v2/β)が未採用。
- Y: F1+F2はruntime未確認(F1対象事象0)。費用見積≒¥1/回の最小実走は可能だが、READING_MATCH PASSが出るかはASR次第で確実ではない(自然発生の次のY正式runでtally517を回す案が低コスト)。
- E3/E4: 実run発火0(API 0注入証拠のみ)。継承JAへの再適用なし(承認済み設計)。
- `er078_asr_unified_wiring_static_audit_01.py`のallowlist記録不整合(英語KP3票系、JA無関係)。
- 同型の将来再発を避けるための最小の運用案(要Fable判断、新規仕組みは増やさない): ASR NGでSTOPした報告には、①同一canonicalの過去NG(`er011_output/attempt_history.jsonl`をGrep)、②該当OPEN(OPEN-515/517/333)の採用状況、③F1/F2/E3/E4の発動有無(r5/candidate_e_*)を1行ずつ添える。

## 7. 次工程(Standard組立・両レベル試聴ページ)

Std組立は`japanese_title=STOPPED`で停止中のまま(Gate迂回なし、TTS再生成・承認記録注入は未実施)。Adv(b1b)完成ページ(Advのみ)は不変。再生成は、現行判定で12/12非PASS(R1が原因)のため通過見込みが低く、費用だけ増える。進めるには、J4(試聴)の結果とJ5(承認音声再利用/題変更)の判断、またはJ1採用後の再判定(保存転写のAPI 0再判定)のいずれかが必要。

## 8. Status(対象別、混同なし)

| 対象 | Status |
|---|---|
| F1+F2(OPEN-517/523/524) | APPROVED_FOR_PRODUCTION。PRODUCTION_WIRED: X・Z(Fable受入2026-10-25)。Y=コード配線済み・runtime未確認 |
| E3 / E4(OPEN-333是正) | 承認済み不具合是正としてProduction適用済み(APPLIED)。共通adapterに配線済みだが実run発火0・API 0注入証拠のみ(PRODUCTION_WIRED判定語はFable) |
| v2読み規則(P-1) / β | VALIDATED(限定)。**未採用・未配線**(判断候補D) |
| 今回の月Std題 3音声 | REJECTED(ASR NG・STOPPED)。ただし音声自体の正否は未確定(Human Review待ち) |
| run_ms_03 #2の音声 | ユーザー個別承認済み(当該run・当該segmentのみ)。本runへは未注入 |

## 9. 費用

今回の追加: OpenAI ASR 12回(約83秒)+Azure ASR 3回(20.73秒)=見積≒¥0.99(Azure 20.73s×¥0.0447=¥0.93、OpenAI 82.9s×¥0.0008=¥0.07。cost loggerのyen欄は未算出のため`BUDGET_PLAN_01.md`の単価ベース推定)。TTS 0。本委任Cap ¥20内。run累計(これまで¥20.78)→約¥21.77。
