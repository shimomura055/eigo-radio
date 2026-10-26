# OPUS_RESULT_01 — Opus独立技術レビュー結果(逐語。条件A、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01設計)

出典: sandwich-pm(Fable)が委任_02の委任文へ逐語転記したもの。Fable判定=GO with changes採用(M-1〜M-11は実装前必須、R-1〜R-7推奨)。


## 1. 結論: GO with changes(実装前に必須修正 M-1〜M-11 を設計へ反映すること)

- 骨格(BLOCK_PROFILES表、cooldown_core、lr_recover の深さガード、scopeによるA/B/C温存、D6案A)は妥当です。仕様にも適合しています。
- ただし重大な欠陥が1件あります。D3は「Adv ③=`_run_a2_minimal_fallback_attempt`を再利用」と書いていますが、この関数はAoede音声で生成するため、L1(Charon音声の部位)ではVoiceが変わってしまいます。これは仕様違反です。
- そのほか、未定義のまま放置すると品質判定がすり抜けたり(fail-open)、重複生成が起きたりする点があります。resume(途中再開)・Gate検知・Master Audio Store競合・STOP例外の4点で、契約の定義が不足しています。

## 2. 論点別判定表

| 論点 | 判定 | 根拠(ファイル:行) | 指示 |
|---|---|---|---|
| O-1 抽象・scope gate | 要修正 | `er109_xz_scope_01.py:85-87` の `current_scope()` は docstring で「判定には使わない」と明記されています。leaf は segment_id を `derive_segment_key` で自己解決します(voice01:124-126)。layout が不正な場合は segment_id=None になり、設計どおりだと黙ってlegacy(旧600秒・LR後1回)へ落ちます | **M-1**: scope内でpolicyを解決できない場合(segment_id=None/未知ID)は、例外で止める(fail-closed)。shellは「unknown→None」ではなく、表上の明示的な `SHELL_EN` 行で除外する。`current_scope()` の docstring/契約を「判定に使う唯一の読取関数」へ改める。X/Y/Z production moduleから8 leafへのcall siteがすべてscope内であることを静的testで固定する。2アダプタ(loop型/stage型)は「表1枚+2アダプタ」として許容 |
| O-2 LR再入・resume | 要修正 | guardの再入スキップ(`er011:685-686`)は、lr_recover が外側guardの実行中に呼ばれる場合に限り成立します。LR artifact は `er011_output/local_rewrite_recovery/{theme}/{level}` に置かれ、run非依存です(voice01:373)。BlockProgress は書換え後の本文をshaでしか持たず、本文を復元できません(D12) | **M-2**: BlockProgressのkeyは(segment_id、元原稿のsha、Style/Voice/backend/profile/policy の指紋)とする。書換え後の本文そのものをBlockProgress内に保存し、resume時に旧run/旧themeのLR artifactを拾わないこと。「再生成かresumeか」の判別はZ ctxの明示信号(`explicit_regenerate`、Lockの`consuming_regenerate_approval`、本文/Style不一致)を流用し、「`--only-*` なら新規サイクル」とはしない(待機中に落ちた後の再実行で①②を作り直してしまうため)。**M-3**: 不変条件test:(a)lr_recover入口で `out_path in _ACTIVE_GUARDED_OUT_PATHS` をassert。(b)record_outcomeが数えるTTS数=実TTS呼出数(LR block・技術的再試行を含む)。(c)LR blockへ渡すStyleは「呼出元の元Style(発音hint付与前)+元の resolver flag」に統一する。voice01:140-145 で hint 付与済みの style_prefix_override に resolver=True を重ねると、hintが二重に付与される |
| O-3 Z ctx統合範囲 | 妥当 | `er122:282-338`(n_startedの先行書込・実時間cooldown)は既にOpusレビュー済みです | **R-1**: legacy方式(ロールバック時のみ)のAdv外側ループは、er012_b の局所attempt番号(max_attempts=残予算)で判定するため、③前の180秒が抜けます。通算ordinalで判定すること(U-07据置と両立可) |
| O-4 U-03/HRQ一本化 | 要修正 | `er020:771-776` の NO_NG_SPAN 判定は最終転写を使います(この点は妥当: ③がQA単独NGなら書換え対象がない)。一方、減速後判定は独自にHRQを書いています(n3:162-172) | **M-4**: 終端の登録はLRの全非RESOLVED結果(NO_NG_SPAN/NO_CANDIDATE_PASSED_QA/LR例外)と、減速後の終端NGを網羅し、「終端NG1件=HRQ1行」をtestで固定する。③が技術STOP(Secondary/Whisper不能)の場合はLR・HRに入れず、既存の技術STOP(再開可能)の意味を維持すると明記する |
| O-5 Gate不変 | 妥当(条件付き) | Gateはresult dictの形式に依存しています。`_final_style_record` は top-level の `style_prefix` を先に読み、無ければ attempts_log 末尾を読みます(style_profile:534-548)。Adv判定は `instruction_type=="minimal_fallback"`、Std判定は `fallback_used` を見ます(:713-741) | **M-5**: 採用されたattemptの `style_prefix`(実送信文字列)・`instruction_type`・`fallback_used`・`local_rewrite_recovery` を top-level に正規化し、attempts_log は採用attemptを末尾にする。leaf matrixの③PASS/LR PASSの結果を `m3_assembly_gate`(fx_20261017)と `y_style_gate` に通し、期待どおりの違反(ADV_/PREVIEW_MINIMAL_FALLBACK、STD_FALLBACK_USED_OR_UNKNOWN、KP解説の FINAL_STYLE_SHA_MISMATCH、LOCAL_REWRITE_RECOVERY)が出ることをtestで固定する。Gateの緩和は別途ユーザー判断で正しい |
| O-6.1 D6 | 要修正→案A | §3参照 | **M-6**(§3の条件) |
| O-6.2 D11 | 妥当 | `er020:135-159` に `topic_intro_en` が未登録。原文§4がZ冒頭英語の是正を明示しています | T-ROLE に「A/B/Cに同名IDが無い」ことを追加(未確認) |
| O-6.3 A/B/C golden | 妥当(補強要) | `FamilyAUnchangedTest` は working tree の差分=0 で判定するため、commit後は常にPASSし、保護になりません | **R-2**: 証拠はgoldenのみと扱う。変更した全leafのscope外呼出(新kwarg無し)と、A runner(`er003_v1_n3_01_tts_generate.generate_a2_segments`)1経路をgoldenに含める |
| O-6.4 shell | 妥当 | 表外。Store再利用で生成は通常0 | **R-3**: 最終報告の星取表に「表外・現行維持」と明示し、例外を隠さない |
| O-6.5 クランプ | 妥当 | crosslevel:149 | — |
| O-7 KP 2+2 | 要修正 | ① `er006_master_audio_store_01.py:119` で manifest を読み、:206 で generate_fn を実行し、その後に保存します(read-modify-writeでlockなし)。cooldownを `_gen_lock` 内に置くと、180秒+TTSの間、古いmanifestを抱えたままになり、並列process(evidenceは6並列)が他processの登録や `reuse_blocked` 印を上書き・消去し得ます。② 3複製には差分があります: repro01:842/864 の `primary_instruction_type`/reason文、k2_store:65-70 の STYLED系ラベル、er063:1079/1094 の `attach_kp_vote_check`、引数 disfluency_qa | **M-7**: 待機を get_or_generate の外へ出すか、保存直前にmanifestを再読込してmergeする。統合は呼出元ごとの差分をadapter引数で保持し、待機以外のシナリオで3 call siteの出力dictが従来と一致することをgoldenで確認する(または統合を「共通cooldown helper+3箇所呼出の静的test」に縮小する)。待機は circuit-open 判定の後、Lock段のTTSが実際に走るときだけ入れる。Store hit時に待機しない解釈は原文§2の目的(TTS生成の間隔確保)に整合 |
| O-8 evidence | 要修正(小) | EVIDENCE_PLAN §2/§6 | **M-8**(F-3と共通)。追加実走は §4-c |
| F-1 Style透過 | 要修正 | ①②は呼出元のStyleをそのまま通します(Y=er121:571/605/717)。③は backend 依存の固定定数で、profile固有のFallbackは存在しません(style_profile にFallback定義なし)。核へStyle名を持ち込まない構造自体は妥当です。ただし T-Y が「`STYLE_PROFILE="default"`不変」をassertしており(TEST_PLAN:27)、FAMILY-Y-STYLE-PROFILE-FIX-01 と衝突します | **M-9**: T-Yは「呼出元が解決したprofileを透過する」test(default/fx_20261017の両方)に置換する。kp_two_stage は「Y=MINIMAL」等のFamily対応を内部に持たず、primary_fn を呼出元から受け取る。BlockProgressの指紋(M-2)にprofileを含める |
| F-2 scope未設定経路 | 要修正 | scopeに入るのは X:er019:1428/1795、Y:er121:543/631、Z:er063:1490 です。ほかに Trial/tool(er113:843、er114:600、er118、er019_clobber_restore、validation_inheritance、er121_e1)もscopeに入り、新flowになります | M-1で fail-closed にする。**R-4**: Trial/toolが新flowになることを記録する(VALIDATED成果物の再現性)。scopeを使う既存test(er103/er109系)がleafを実sleepで通らないよう、clock/sleepを注入できるか確認する(Productionにenvでの迂回口は作らない) |
| F-3 evidence注入 | 要修正(小) | — | **M-8**: 注入はdriver側のmonkeypatchのみとし、Production moduleへhookやenvを追加しない。LRへ渡った `last_asr_text`=注入した転写、LR block内の判定=未patchの本物judge、であることをordinal別の `injected_override_count` で記録する。U-03はQA gate出力のNG化で十分 |

追加の必須修正(設計に記載なし):
- **M-10(D3、重大)**: `_run_a2_minimal_fallback_attempt`→`generate_english_component_minimal_instruction` は `p9a.VOICE_NAME`(="Aoede"、p9a:133)で生成します(repro01:605)。L1 `generate_charon_english` は Charon です(voice01:169/211)。設計どおりにするとAdv topic_intro/preview/comment の③がAoedeになり、「Voice保持」「Voice変更はScope外」に違反します。L1の③は自関数内のminimal分岐(voice01:192-227 と同じCharon/`SAFETY_MARGIN`/fallback定数+発音hint)をordinal 3で使い、force_secondary を追加すること。L2はp9a.VOICE_NAMEで一致しているため流用可です。T-STYのVoice一致testは必ずL1を含めること。
- **M-11(D2/D14)**: cooldown中のSTOPは専用の例外型にし、runnerの最上位まで伝播させる。途中で `record_outcome`(Lock化)や、`_generate_or_reuse`/`secondary_run_scope.guard_generate` によるSTOPPED結果の保存(再利用対象になる)を起こさないことを、runner単位のtestで固定する(guard_generate の例外処理は未確認)。あわせてI-3を明確化する: 技術的再試行を使い切ったattemptも ordinal を1つ消費し、「②NG」として③前の待機対象になる(現行どおり。番号を進めない解釈は無限ループの危険があるため採らない)。

## 3. D6の採択案: 案A

理由:
1. 現行L4は、減速後NGの後にL3を `max_attempts=残予算2, standard_attempts=min(2,2)` で呼び直します(n3:397-404)。このとき `fallback_budget=0` となり(crosslevel:188)、**③がFallback Styleにならず**、標準Styleの3回目になります。案C(現状維持)は原文§2「③=Fallback Style」に違反します。案Bも外側ループを残す限り同じ問題の再設計が必要です。
2. 案Bは、内側guardが減速前OKでLockをRESOLVEDにし、その後 finalize が再度 record_outcome を呼ぶ二重記録構造(n3:309-328)を残し、継ぎ目が増えるだけです。
3. U-09(減速後最終NGはLRなしHR)は、棚卸しで「ユーザー逐語承認は未確認・C分類」とされています(AUDIT REPORT_01:300)。Fableの前提「承認済み仕様U-09」は不正確で、2026-10-26原文の「Std英語本文=LRあり・③NG後にLR」が正です。案Aはこれに一致します。

**M-6(案A採用の条件)**:
- (a) 実装は post-hook を引数で受け取る形にし、既定はNoneとする。scope外のL4・Z Adv dialogueの `generate_with_a2_slowdown_outer_loop`(K-07)は温存する。
- (b) attempt内の順序: TTS→ASR判定→PASSなら original退避→減速→減速後ASR判定。attempt音声は減速前・減速後の両方を別route名で保存する。
- (c) 期待テキスト=そのattemptの送信文(LR blockでは書換え後の文)、Lock key/HRQの `lock_canonical_text`=元原稿を、BlockCtxから明示的に渡す。attempt dictに対して `resolve_expected_text_after_local_rewrite` に頼らない(LR block内ではまだ `local_rewrite_recovery` が無い)。
- (d) `_post_slowdown_unified_judge` のslot(現在は固定 `slot:1`、n3:147)をブロック通算slotに変更し、HR記録は終端slotでのみ行う(M-4と一体)。
- (e) LRへ渡す転写は、NGの原因になった転写(減速前PASSなら減速後の転写)とし、`ng_source` を記録する。
- (f) 採用結果の top-level に `slowdown_applied`/`original_path`/`slowdown_info`/`post_slowdown_*`/再計算sha256/比例補正したtrim_info を残す。`check_std_slowdown`・`std_chunk_slowdown_violations`・`drop_cached_std_chunks_without_slowdown` がchunk単位で現行どおり通ることをgoldenで確認する。
- (g) chunkはchunkごとに独立した1ブロックとする。

## 4. 見落としリスク

- a. M-10(L1の③でVoiceがすり替わる)。T-STYで検出できる見込みはありますが、設計の記述自体が誤りです。
- b. M-7(Master Audio Store manifestの更新消失)。既存の潜在的な競合を、180秒待機と6並列evidenceが顕在化させます。`reuse_blocked` 印の消失は、ブロック済み音声の再利用につながる品質リスクです。evidence実施前に修正するか、Storeをprocessごとに分離すること。
- c. evidenceの追加(約10円、Cap内): ① Std chunk の「①減速後NG→②PASS→Assemble Gate PASS(誤BLOCKなし)」の実走1件(案Aの新しい意味づけの実証)。② Adv L1 ③の実走で、Voice=Charonを `speech_metadata`/sidecarで確認する。任意でLR block内kill→resume(`lr_used`)の実走1件(R-5)。
- d. clip単価の見積りが、最大6TTS+LR LLMに未対応の可能性があります(Z `E2E_TTS_CLIP_EST_JPY`、Yのguard見積り。未確認)。予算guardの見積りを更新すること(R-6)。
- e. ROW_MAPPING Y-S-06 の「y_voice_1 Algieba」は古い記述です(er121:13 によれば2026-10-26にPuckへ変更)。軽微。
- f. Adv ③採用がGate対象になることでHR待ちが増える見込みを、最終報告の量産・制作時間の項で数値化すること(Gate緩和の判断材料。R-7)。

## 5. 要約

1. 判定は GO with changes です。D6は案Aを採用し、案C(現状維持)は「③=Fallback Style」に違反するため不可です。
2. U-09はユーザー承認済みではありません(C分類)。新仕様どおり、減速後NGからもLRへ進むのが正しいです。
3. 重大な指摘は、Adv L1の③がAoede音声になるVoice変更(M-10)です。
4. LR再入禁止には、guard実行中であることのassert、resume時の書換え本文の保存、再生成とresumeの判別(Z方式の流用)が必要です(M-2/M-3)。
5. Gate規則は変えずに済みますが、③/LRをGateが検知できる結果フィールドの契約testが必須です(M-5)。
6. KP統合は、Store manifestの競合と3複製の出力差の保持が条件です(M-7)。
7. scope外でpolicyが解決できないときはlegacyへ落とさず停止させ、F-2の取りこぼしを防ぎます(M-1)。
8. F-1: 核はStyleを呼出元から透過する構造で妥当です。T-Yの「default不変」assertは置換が必要です(M-9)。
9. STOP例外の伝播と、技術失敗attemptの数え方を明文化します(M-11)。
10. evidenceはLean 46件に約10円の実走2件を追加すれば十分です。注入はdriver側のみとします(M-8)。

