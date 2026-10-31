# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_01 DESIGN_01(設計のみ・API 0・Production code変更0。実装=委任_02)

根拠=`CURRENT_STATE_01.md`(同dir)。ユーザー原文=`docs/pm/delegation_log/2026-10-31_ASR-FLAP-T-PRODUCTION-WIRING-01_USER.md`(以下「原文:行」)。
Status: Flap-T救済方式(Trial M1)=**APPROVED_FOR_PRODUCTION(原文:7)**、目標=PRODUCTION_WIRED(原文:8)。Trialの`VALIDATED`からの格上げ根拠は原文のみ。**正式Productionで既定ON**(原文:71)。11-7の限定例外ではなく通常のProduction実装。

## 1. 範囲と線引き(11-8)
- 範囲内: Family X/Y/Z × Standard/Advanced の正式経路(原文:5)。既存ASR閾値・Primary/Secondary条件・最終ANDゲート・CS救済・同音救済は**無変更**(原文:30-32)。
- 範囲外(触れない): Family A/B/C(scope外は従来コードパスのまま)。承認品質定義の変更は「下記条件を満たす米国英語Flap-T発音を許容する範囲」に限定(原文:28)。ASR収束を救済根拠にしない(`CURRENT_SPEC.md:1864`)。AY/AW核・複数読み・未登録語・未確認Voiceは救済しない(原文:22-26)。
- 量産単価+0円: 量産経路に新ASR/TTS/LLM call追加なし(CMU辞書はローカル)。追加は一回限りの開発probe(4節)。

## 2. 不変条件(Trial I-1〜I-10を踏襲 + Opus M1〜M6の確定仕様)
I-1 文字列t↔d置換禁止(CMU音素列+flap環境のみ)/I-2 母音完全一致/I-3 全t/d差位置がflap環境(直前=強勢母音、直後=無強勢母音、R/子音直後・音節的n・語頭語末・クラスター不可)/I-4 canonical強勢読み単一(putting型は不可)/I-5 AY/AW核は自動救済しない(NG維持)/I-6 1:1語置換のみ、CMU未登録・例外は同値でない(fail-closed)/I-7 ASR収束を根拠にしない/I-8 Voice適用境界/I-9 既存閾値・Gate・retry上限・最終ANDゲート不変/I-10 救済は必ず警告ラベル付き+根拠ログ。詳細=Trial `DESIGN_01.md`2節。**Productionで確定する追加仕様**:
- **M1 tokenizer**: 判定単位を `er109_asr_orthographic_equivalence_01._TOKEN_RE`相当(`:274-281`、数字・通貨・時刻・序数・分数・記号もtoken)に揃える。差分は「word tokenの1:1置換でflap対(I-2/I-3を満たす)」のみ許し、**数字・記号tokenの差が1つでもあれば非救済**。Trial protoは数字を落とし `The latter 13 option`↔`The ladder 30 option` をRESCUEにする(実測)ため、この点だけは移植ではなく再実装。回帰test: 数値付き文(KP票経路含む)が救済されない。
- **M3 label/version**: 既存の`ORTHO_LABEL`(`ORTHOGRAPHIC_EQUIVALENT_MATCH`)をPrimary/票のlabelとして流用(既存の`label==ORTHO_LABEL`判定・Store再利用ガードの`ortho_contributed`・`make_voter`の印が追加改修なしで効く)。ただし判定objectの`eq.version`は**flap専用version**(`er139_flapt_equivalence_v1`+CMU sha短縮)で、`er109 LAYER_VERSION`とは異なる。これにより `explain_protected`(`er109_xz_scope_01.py:255`)は`decision_not_equivalent_or_version_mismatch`でFalse=**値DIFF・否定差を解除しない構造保証**(flap層は最終ANDゲートを決して緩めない)。警告ラベル`FLAP_T_EQUIVALENT`を`ORTHO_WARNING_LABELS`(`:33`)へ追加(=`ortho_contributed`の(4)で捕捉)。
- **M6**: auditにCMU辞書sha256(`cmudict`の辞書file)・`pronouncing/cmudict` version・flap規則version・Voice表sha256・Voice/model/wav shaを記録。Whisper票にも適用(票ごとに`decision()`を通る=同一基準)。親子flag: 親=`er109 is_active_for_run()`(flag∧scope X/Y/Z)、子=`FLAP_T_EQUIVALENCE_ENABLED`。
- 品質定義の明文化(原文:28、CLOSEOUT 8節): 「語彙としての意図は検証しない。米音として許容できる実現形かを見る(米音では/d/も[ɾ]化し区別不能)」をCURRENT_SPECに記載。

## 3. 構成(形態B: 新規module + `decision()`に1分岐。er109本体は無変更)
### 3-1 新規file(命名はer139。重複なし: 既存最大er138)
| file | 内容 |
|---|---|
| `er139_flapt_equivalence_01.py` | 純関数 `judge_pair` / `evaluate`(M1 tokenizer)/ `FlapEq`(`equivalent`,`version`,`spans=[]`,`warnings`,`rules`,`audit()`)/ Voice適用ゲート `decide(canonical,text,sink)`(provenance台帳をcontextvarから読む)/ `is_enabled()` / CMU sha取得。lru cacheは**(canonical,text)のみ**keyの純規則判定(voice非依存)。Voice判定はcacheの**外**(M2) |
| `er139_flapt_provenance_01.py` | 出自台帳 `sha256(wav) → {voice, model_id, path(fl/pro), source}`、contextvar `current_wav_sha`、`judging_wav(sha)` context manager、`note_tts_sent(voice,model)`(pending)、`bind_pending(path)`、`register_child(parent_sha,child_path,transform)`、`hydrate_from_attempt_json(...)` |
| `er139_flapt_voice_table_01.json` | 静的Voice表(4節)。各entryに根拠probe(`voice_probe_02.json`/追加probeのclip sha一覧・日付)と`confirmed:true/false`、表全体のsha256 |
| テスト: `er139_flapt_equivalence_01_test_01.py` ほか(8節) | |

### 3-2 既存fileの変更(最小・追加のみ)
1. `er109_xz_scope_01.py`: `decision()`(:149)で、`eq`が`not eq.equivalent`のとき `er139.decide(...)`を1回呼ぶ分岐を追加。成立なら`OrthoDecision(canonical,text,FlapEq,("FLAP_T_EQUIVALENT",),scope)`を返す。`ORTHO_WARNING_LABELS`に`FLAP_T_EQUIVALENT`追加。`flapt_contributed(aj)`(sitesのer109 versionが`er139_flapt*`)を追加。**呼出元(er006/er078/er104/er019/hr rejudge)は無変更**=新規call siteゼロ。
2. `er006_secondary_asr_01.py` `evaluate_attempt_with_cascade_detail`(:874): 関数本体を `with er139.judging_wav(az.sha):` で包む(:972で`az`確定後)。Primary(:1135)・Secondary closure(:1188-1211)・KP Whisper票・judge側(`er078:786-796`等)が全て同contextで走る。
3. `er104_kp_three_asr_vote_01.py` `vote_check_from_audit`(:424): wav_pathのsha(`sha256_file`:413)で同context。
4. TTS出自の記録点(M2、2点のみ=SDK境界):
   - Standard: `er005_cost_logger.py` `_patch_gemini`(:171-224)で、TTS成功時に既に取得している `sent_voice`+`model_id` を `note_tts_sent(voice, model_id)`へ(1行追加)。flash-lite直叩き(`er033_tts_flash_lite_backend_wiring_01.py:195`)も同じ`generate_content`を通るのでここで捕捉。
   - Batch: `er006_batch_tts_wiring_01.py` `_resolve_single_item`(:207)の成功経路で `note_tts_sent(voice_name, model_name)`。
   - 束縛: `er002_common.write_wav_float`(:411)の末尾で、pendingがあれば`sha256(path)`へ束縛して**消費**(単一用途・時間失効120秒)。pending無し=何もしない(Store再利用コピー・組立wavは束縛されない)。
   - 減速/高速化後処理: `er003_v1_n3_01_tts_generate.py` `apply_a2_slowdown_postprocess`(:196)と`generate_with_a2_slowdown_outer_loop`(:508)で、出力wavを親(`_original.wav`)の出自で`register_child`(Std 6%減速・Z Adv 1.06x高速化とも。判定は変換後wavのshaに対して行われるため)。
   - 保存音声の再judge(`er019_family_x_validation_inheritance_01.py:323`、`er109_hr_lock_rejudge_01.py`): attempt JSONの`voice`/`model`/`audio_sha256`から`hydrate_from_attempt_json`(sha一致検証つき)した場合のみ有効。**未hydrateは従来どおり不適用**。
5. `er078_reuse_value_guard_01.py`(:85-92と同型): `flapt_contributed(entry)`かつ(`not is_active_for_run()` または Voice表sha不一致 または 当該(voice,model)が現表で未確認)ならblock(新reason `FLAP_T_EQUIVALENT_AUDIO_OUT_OF_SCOPE_OR_VOICE_UNCONFIRMED`)。既存`ortho_contributed`ガードは変更なし。
6. 変更しない: er006_preprod_hardening(分類器)、er078 judge本体の状態機械・`APPROVED_EQUIVALENCE_BASES`、CS層、retry/fallback/LR/er127、Primary/Secondary閾値、Prompt、辞書。

### 3-3 Voice/model受渡しをこの方式にする理由(Opus注3・M2への回答)
- 代替案「`attempt_ctx`にvoice追加」は呼出元10箇所(CURRENT_STATE 4節)+LR/減速後/KP vote再評価の全てに引数追加が必要で、取りこぼし=サイレント不適用。さらに`attempt_ctx`は"leafが思うVoice"であり**実際にAPIへ送った値**(`effective_voice`の結果、Z `voice_override`、Batch/Standard)とずれうる。
- 採用案は(a)**API境界の実送信値**(cost loggerが既に`tts_voice_sent`として独立記録、`FZ-TELL-TALE-HEART-NARRATOR-VOICE-01`で受入に使用済み)を(b)**wavのsha256へ束縛**(判定対象wavのshaは`az.sha`として既にjudgeが持つ)ので、Store再利用・resume・別Voice旧音声の誤適用が構造的に起きない(shaが台帳に無ければ不適用)。
- fail-closed: 台帳にshaが無い/voiceが取れない(multi-speaker config等でprebuilt voice名が取れない)/modelが表に無い → `decide()`は `flapt_declined: voice_unconfirmed|provenance_missing` をsinkへ(RESCUE相当だったときだけ)記録して**従来NG**。
- contextvarで安全な根拠: judge・分類・票構築は同一スレッド(Whisperは転写のみ別スレッド=`er104:343`、分類はスレッド外)。X/Y/Z runnerは単一process内逐次(既存`_RUN_SCOPE`もprocess globalで同前提)。

### 3-4 `decide()`の判定順(Productionでの最終形)
1) `er109.is_active_for_run()`(親)∧`FLAP_T_EQUIVALENCE_ENABLED`(子、既定True)でなければNone。2) lang=="en"。3) M1 tokenizerで1:1のword置換のみ、数字/記号token差0。4) 各差分語を`judge_pair`(CMU音素・flap環境・母音一致・単一読み・AY/AWは`REQUIRES_EXTRA_EVIDENCE`=非救済)。全差分がRESCUEのときのみ次へ。5) **Voiceゲート**(current_wav_shaの出自→(voice,model)が表で`confirmed:true`)。6) FlapEqを返す(警告`FLAP_T_EQUIVALENT`、根拠=語対・音素列・環境・voice/model・wav sha・表sha・CMU sha・規則version)。例外はすべて「同値でない」+sinkへ記録(runを止めない)。

## 4. Voice表と追加probe(原文:44-50、M4/M5)
- **静的Voice表**(M4): キー=(voice, model_id)。Trial許可リスト13(probe)を引継ぎ、Schedar\|pro・Zephyr\|proは**独立probe完了までconfirmed:false**(循環解消)。表整合test: X/Y/Z計画Voice(`ClipSpec.voice`群・Z男女Voice・Y/X既定)×model(flash-lite/2.5-pro)の全組合せが「confirmed」または「明示的に未確認(fail-closed)」のいずれかとして表に載ること(新Voice追加で表更新を忘れたら落ちる)。
- **追加probe(M5)**: 対象7組合せ = Zephyr\|pro, Schedar\|pro(独立), Algieba\|pro, Charon\|pro, Aoede\|pro, Fenrir\|pro, Puck\|pro。既存ツール`tools/flapt_voice_probe_02.py`(Production leaf呼出のみ)を再利用。clip: 観測7項目(latter/metal/betting/atom/waiting/coating/"the latter one")のみ(対照語は不要)=7 clip/組合せ。単価=2.5-pro 約¥0.26/clip(`VOICE_PROBE_02.md`5節実測)→ **7×7×¥0.26 ≈ ¥12.7**(12 clip版なら≈¥21.8)。判定基準はTrialと同一(≥2観測項目で≥2系統がd綴り=FLAP_DEMONSTRATED、t綴り優勢=T_SPELLED→confirmed:false)。T_SPELLEDやINDETERMINATEのVoiceは**その組合せだけ**fail-closedで残す(他の実装は止めない、原文:50)。
- Z Adv dialogueの1.06x高速化: 既存probe wavへatempo 1.06を当ててASRのみ(Aoede/Schedar/Zephyr/Fenrir相当の代表数clip、約¥0.05/clip、合計≈¥1)。維持されなければZ Adv dialogueだけ高速化版は不適用に倒す(表にspeed条件を持たせる)。
- 見積合計: **≈¥14〜23。Cap案¥25**(承認済みScope内・300円以下=7-7でAI自律、日次1,000円内)。コスト根拠は実測単価。run前に`tools/stop_scope_check_01.py`、並列2 shard、storm guard遵守(最小起動間隔≥150秒、前回の109秒事例の再発防止)。

## 5. 到達性(Family×Level)と既存経路との整合
| 対象 | EN judge経路(Flapが効く場所) | Voice/model(表の状態見込み) | 備考 |
|---|---|---|---|
| X Std(A2)/Adv(B1B)本文・KP・vocab_extra | `crosslevel_02_common:554`/`repro01:378`(KP vote)/`news_tail_fix:280`/`n3:146`(減速後) | Aoede/Charon\|fl=確認済み。\|pro(旧)=probe後 | ⑨ latter(Aoede\|fl)が主目的 |
| Y Std/Adv | 同上(Yは`er121`が共有leaf) | fl×6 Voice=全確認済み | |
| Z Std/Adv narrator・dialogue・KP | 同上+`er012_b_family_voices:590`(dialogue) | fl{Aoede,Charon,Fenrir}確認済み、pro{Orus,Kore,Erinome,Sulafat,Leda,Iapetus}確認済み、{Algieba,Charon,Aoede,Fenrir,Puck,Schedar,Zephyr}\|proはprobe次第 | Adv dialogue 1.06xは4節 |
- 既存ASR救済との整合: er109が先、Flapは`equivalent=False`時のみ=既存の勝敗・ラベル不変(P1)。CS層はA2/B1本文で別経路(語末脱落+corroboration)、Flapは語中t/dのみで重複しない。
- 最終ANDゲート: flap判定は`explain_protected`でFalse→値DIFF/否定差は従来どおり`NG_PROTECTED`。KP票は値ガード解除済みなので、**M1の数字token非救済をKP票経路でも回帰test固定**。
- retry/fallback/regeneration/resume: CURRENT_STATE 5節。救済は「当該attemptの合格を1つ増やす」のみ=試行回数・上限・待機(180秒)・LR・HRの条件は不変。resumeは再judgeしない/再judge時は台帳hydrate必須(未hydrate=不適用)。
- 警告の後続保持: `asr_judgement.warnings`に`FLAP_T_EQUIVALENT`(Primary警告→`unified_judge`のwarnings→`PASS_WITH_WARNING`)。`orthographic_equivalence.sites[*].er109`に根拠audit(`record_site`)。事後試聴リスト(`er078_pass_with_warning_registry_01.py:61`)・Store継承(`asr_judgement_inherited`)に流れることをintegration testで固定(adopted segmentの最上位`asr_judgement`に残り、attempt log内に埋もれないこと)。

## 6. 既定ON・flag(原文:71)
- `FLAP_T_EQUIVALENCE_ENABLED = True`(module定数、rollbackスイッチ。env/引数/設定dictから変更不可=AST test)。単一読取`is_enabled()`。DefaultOn test: (1)X/Y/Z scope内でlatter/ladder(許可Voice)が救済、(2)scope外/A/B/Cは従来(Noneで完全一致)、(3)flag既定値がTrue(literal)、(4)起動script・`.env`にflapt関連キーが無い。**既定OFFで完了報告しない**。
- 11-7の限定例外ではない(ユーザー正式採用)ため「未承認・既定OFF」記録は不要。OPEN-626の旧記述(既定OFF)は本決定で置換済み(SSOT)。

## 7. 受入条件(原文:73-89)の検証計画
| # | 条件 | 検証 | 手段(費用) |
|---|---|---|---|
| 1 | latter/ladder・metal/medal等の正例が救済 | 純関数test(Trial P01-P12移植)+**正式判定経路**(`evaluate_attempt_with_cascade_detail`にOpenAI/Azure保存転写をinject、台帳にAoede\|fl wav shaを注入)でPASS_WITH_WARNING | API 0 |
| 2 | Trial反例が誤救済されない | N01-N18/U01をproduction `decision()`で。保存転写6,979/NG 1,336全件のreplay(RESCUE=latter/bertieのみ、他0) | API 0 |
| 3 | writer/rider・title/tidalはNG維持 | X01-X03+probeのwriter転写(39)をreplay | API 0 |
| 4 | 未確認Voiceは救済されない | 台帳なし/表に無い/confirmed:false/T_SPELLED、flag OFF、scope外の各ケース。Schedar\|pro・Zephyr\|proが独立probe前に不適用であること | API 0 |
| 5 | 警告と根拠ログ | auditに語対・音素・環境・voice/model・sha・表sha・CMU shaが残る、`asr_judgement.warnings`、事後試聴リスト | API 0 |
| 6 | 通常のPASS/NG判定に意図しない変化なし | **全回帰の失敗集合がbaseline(`92a4e79c3`)と同一**(既存4件は不変)。`er109_wiring_signature`型の署名比較で非flap行の署名完全一致(golden再生成ではなく、flap行のみ期待追加) | API 0 |
| 7 | Family別・レベル別の到達性と実動作 | 5節の表を各セルで: (a)静的到達(runner→leaf→judgeの呼出+台帳束縛の存在をAST/integration test)、(b)runtime発火(下記9節) | API 0〜最小 |

## 8. test計画
- Unit(新規): Trial 36移植+M1(数字・通貨・時刻token差で非救済)/複数読み/CMU未登録/AY・AW/語境界/大文字小文字・句読点/例外時fail-closed/lru cacheがvoiceを跨がない(同一(canonical,text)でVoice許可→不許可の順に呼んでも結果が反転しない)。
- Provenance: SDK境界hook(Standard `_patch_gemini`・Batch `_resolve_single_item`)が実送信voice/modelをpendingに載せる(fake client)、`write_wav_float`でsha束縛・消費、pending失効、再利用コピーは束縛されない、減速/高速化の`register_child`、hydrate(sha不一致は拒否)。**Z `voice_override`(Fenrir指定)がSDK境界の実送信値として台帳に載る**(Aoede既定との取り違えなし)。
- Integration: `evaluate_attempt_with_cascade_detail`(Primary/Secondary/Whisper票3系統)でRESCUE→PASS_WITH_WARNING→`asr_judgement.warnings`、`explain_protected`が値/否定差を解除しない(`latter 13`/`not`差でNG_PROTECTED)、KP票(vote_required)で数字付きが非救済、Store再利用ガード、事後試聴リスト、`er019 validation_inheritance`再判定(hydrate有無)。
- Validator/静的: AST test(flag literal True・env/引数非参照・`decide`を呼ぶのは`er109_xz_scope_01.decision`のみ・`evaluate`系の直接呼出禁止)、Voice表整合(4節)、既存`er109_xz_isolation_01_test_01`/`er109_xz_scope_01_test_01`/`er109_wiring_golden_test_01`/`er078_asr_unified_wiring_static_audit_01`/er006・er078・er104各test/Repetition QA(`er011_open121_repetition_qa_*`)/`run_project_regression.py`を**変更前後のFAILED集合差分**で比較(新規失敗0が合格条件。baseline既存失敗は4節CURRENT_STATE参照)。
- 実行時間: er109系3 fileだけで約190秒、全回帰は長時間→4 shard並列(既存`reg.sh`/`shard_*`方式)。

## 9. Production runtime発火証拠の取得方法(新規API 0を原則)
1. **正式判定経路replay(API 0)**: ⑨ Meta `latter→Ladder`(`phase3_rejudge_02.json`: Aoede\|fl、OpenAI「Ladder」/Azure「Ladder.」、attempt JSON `vocab_extra_3_en_attempt1_custom60ebc452.json`)を、実際の正式adapter `evaluate_attempt_with_cascade_detail(..., attempt_ctx={vote_required:True, vote_whisper_fn=<保存転写>})`へ注入(台帳へはattempt JSONの`audio_sha256`+voice/modelをhydrate)。X scope(`run_scope("X")`)で実行し、PASS_WITH_WARNING+`FLAP_T_EQUIVALENT`+audit記録を取得。同じ入力で台帳なし/flag OFF/scope外ではNGに戻ることも取得(ON/OFF対照)。Z Bertie→Birdie(Zephyr\|pro/Schedar\|pro)は独立probe後に許可/それまでは不適用の双方を取得。
2. **実wavでのSDK境界束縛の実証(最小API)**: 既存のFX4 vocab流れと同型の1 clip生成(Production leaf `generate_narration_snippet` 経由、Aoede\|fl・`latter`、¥0.1)で、cost loggerの`tts_voice_sent`/`model_id`→pending→wav sha束縛→judge時の出自参照 が実run上で連鎖することを確認(ASRは保存転写に置換可、実ASR呼出を1回含めても約¥0.15)。Batch経路は`_resolve_single_item`のhook存在とfake batch responseで確認(Batch実行はStandardと費用同等だが1 clip分を許容枠で追加可)。
3. **Family別実run(必要最小)**: X(⑨相当vocab 1 clip)、Y(姓選択で使うVoice 1 clip)、Z(Narrator/dialogue各1 clip、Fenrir/Algieba等)を`run_scope(...)`付き既存runner入口の最小segment実行で台帳束縛→judgeまで通す。各clipは¥0.1〜0.3(pro)。合計≈¥3以内。ここで「flapを起こす文が出るか」は保証できないため、**発火そのものは1.のreplay(保存転写)で、到達性(束縛・context・scope)は2./3.で**証拠化する分担。実音声でflap転写が自然発生するまで再生成を繰り返さない(費用規律。probeで代替済み)。

## 10. 費用・Cap案
| 項目 | 見積 | 根拠 |
|---|---|---|
| 追加Voice probe(7組合せ×7 clip) | ≈¥12.7(12 clip版≈¥21.8) | 2.5-pro実測 約¥0.26/clip(`VOICE_PROBE_02.md`5節) |
| Z高速化1.06x ASRのみ | ≈¥1 | ¥0.05/clip |
| 到達性実run(X/Y/Z 各1〜2 clip+ASR) | ≈¥3〜5 | ¥0.1〜0.3/clip |
| **委任_02見積** | **≈¥17〜28(Cap案¥30)** | 300円未満=7-7でAI自律、日次1,000円内 |
| 量産単価への影響 | **+0円** | 量産経路に新API呼出なし。再生成減の効果は上限見積(Z The Open Window 1回E2Eで約¥21、Xは⑨で約¥0.26+HR 1件解消)だが独立probe後に再評価(循環分は除外) |
Cap超過見込み時はSTOPして報告。分割・日付分割はしない。

## 11. Dangling Reference・旧ルール撤去要否
- Trial文書の「既定OFF・未承認・Production未配線」記述(`ASR-FLAP-T-EQUIVALENCE-TRIAL-01/DESIGN_01.md`,`CLOSEOUT_02.md`, OPEN-626旧文)は採用決定で**置換**(SSOT側にsuperseded注記。Trial文書は履歴として保持)。
- `tools/flapt_equivalence_proto_01.py`はTrial専用のまま残し、Production moduleとは**独立コピー**(Trial protoの冒頭「Productionからimportされない」を維持)。parity testでProduction判定==Trial判定(M1差分=数字tokenのみ意図的に相違)を固定。
- 撤去する旧規則/検査: **なし**(新規層の追加のみ)。矛盾しうる既存検査: `er078_asr_unified_wiring_static_audit_01.py`のcall inventory(baseline既に失敗3件)、`er109_xz_isolation_01_test_01.py`の「decision()の挙動固定」系 → 変更後に期待を更新する場合は「flap分岐の追加分のみ」と明示。
- Grep確認(実装後): `FLAP_T_EQUIVALENT`/`er139_`/`ORTHO_WARNING_LABELS`の参照先、台帳`note_tts_sent`の呼出が2点のみ、`FLAP_T_EQUIVALENCE_ENABLED`のliteral。

## 12. 判断候補(最小限)
- **該当なし(A既判断で包含)**: 既定ON/Voice表のfail-closed/追加probe(≈¥20)/ER109同型の第3層はいずれも原文:2・3・4で承認済み。`er002_common.write_wav_float`・`er005_cost_logger`・`er006_batch_tts_wiring_01`への**no-op追加hook**は、Family A/B/Cの出力・判定を変えない(台帳は読まれない)ため承認範囲内の実装手段(B)。ただしA/B/Cが使う共有moduleへの加算変更なので、Fableが不要と判断すれば台帳束縛を`er019/er063/er121`のrunner側`family_scope`内に限定する代替(束縛範囲は狭まり、leaf直叩きの取りこぼしリスクが増える)も取れる。**推奨=本設計**(取りこぼしゼロ・scope外は完全no-op、AST testで固定)。

## 13. 委任_02の作業分解と並列化
並列A: er139 module+unit test(M1含む)/並列B: provenance module+hook+test/並列C: 追加Voice probe(別PID、API、Cap¥25、先に`stop_scope_check`)/並列D: SSOT雛形・replay script。直列: `decision()`接続→integration→回帰(失敗集合比較、4 shard並列)→runtime evidence(1.のreplay→2./3.)→Fable独立照合用RESULT。クリティカルパス=probe結果→Voice表確定→回帰・replay確定。見込み: probeと実装は並行で、全体は実装+回帰が支配的(probe待ちは表のconfirmed更新のみ)。
