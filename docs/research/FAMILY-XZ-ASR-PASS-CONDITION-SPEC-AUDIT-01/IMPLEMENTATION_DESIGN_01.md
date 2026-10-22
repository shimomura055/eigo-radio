# KP英語phrase「Primary・Secondary両方PASS必須」Family X/Z Production実装設計書(Opusレビュー用)

管理ID: FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_02 [D-1] / 2026-10-22 / Status: `APPROVED_FOR_PRODUCTION`(ユーザー原文=`docs/pm/delegation_log/2026-10-22_FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01_KP-DUAL-PASS-APPROVAL_USER.md`)、本設計時点は**未配線**(Production既存ファイル未編集=PRODUCTION_WIREDではない)。API 0・JPY0。
コード行番号は全て`git show HEAD:`基準。

## 0. 要件(ユーザー§1・§2・§4の要約)
①KP英語phrase=Primary(OpenAI)AND Secondary(Azure)の**両方PASS**。Primary単独/Secondary単独は不合格。Azure障害でPrimary単独PASSへ降格しない。同音救済も両Providerそれぞれが基準を満たす。②KP英語解説・③その他=現行維持(Primary PASS->Azure不要、Primary NG時のSecondary、承認済み例外、retry/fallback不変)。X/Z両方、正式Production初回経路で確認。

## (a) 判定モード: 既存`force_secondary`では不足 -> `dual_required`を最小追加
`er078_asr_unified_judge_01.py`(HEAD)の現行`force_secondary`(L259, L438-441, L554-557)の意味:
- Primary PASS + force -> Secondaryを呼び、許容集合PASS(かつ値/否定ガード)なら`PASS`(`force_secondary_agreed`)。Secondary NGは`NG_BOTH`、取得不能は`NG_SECONDARY_UNAVAILABLE`(PASS不可)。**ここは①の要件を満たす**。
- しかし **Primary NG**(P1/P2/P3、L424-434)ではforceは何も変えない。P3でSecondaryが受理すると`PASS_WITH_WARNING`(`secondary_confirmed`、L558-560)=`verified=True`。**ケース3(Primary NG/Secondary PASS -> 不合格)を満たさない = GAP-1**(unit testで現行挙動として固定済み)。
- Primary PASSがAMBIGUOUS値降格(L430)/length降格(L437)でP3へ回るとforceに到達せず(`primary_ng_reason`が先に確定)、Secondary単独で`PASS_WITH_WARNING`になりうる = GAP-1b。
- Primary PASSがAzure転写由来(非ラテンKP層`er006_secondary_asr_01.py:918-935`、Tier3 corroboration L871-)の救済(`adopted_text`=Azure転写)のとき、OpenAI自身はPASSしていないのにPrimary PASS扱い = GAP-3(①の「OpenAIがPASS」に反する)。
- 現KPはforceを渡さない(`generate_key_phrase_component_verified` L813-830、Z `kp_en` L817-836、X K2 `_styled_two_stage` k2_store L54-78)ため、Primary PASS -> Azure不呼出(take part型の見逃し = GAP-2、unit testで固定済み)。
- 既に充足している要件: Azure例外/空転写/circuit open = `NG_SECONDARY_UNAVAILABLE`(PASS不可、技術STOP記録。Humanは入れない)。値/否定ガードはSecondary転写にも独立適用。`SecondaryCache`で同一wav+engine+lang+phrase_hashは1回。

**新モード案(minimal fallbackのforce_secondary挙動=U2は不変、additive)**:
1. `AttemptCtx.dual_required: bool = False`。Trueのとき`unified_judge`は次の順で判定する(Falseなら現行コードパスを1行も変えない=byte-identical):
   - Primary ASR取得失敗 = `NG_PRIMARY_ASR_FAILURE`(現行どおり)。保護差(P1 値DIFF/否定差)・除外(P2)は現行の`NG_PROTECTED`/`NG_EXCLUDED`を維持(先に判定)。
   - Primaryが「OpenAI自身のPASS」でない場合は**Azureを呼ばず**不合格: 条件=(`pr.passed`がFalse)または(`pr.signals["primary_rescued_by_secondary"]`がTrue)または(最終ANDゲートのAMBIGUOUS/length降格で`primary_ng_reason`が確定)。state=新設`NG_DUAL_PRIMARY_NOT_PASS`(`STATES`に追加、`PASSING_STATES`には入れない)。
   - Primary OKなら**必ずSecondaryを呼ぶ**(forceと同じSecondaryCache経由)。取得不能 = `NG_SECONDARY_UNAVAILABLE`(現行どおり、Primary単独PASSへ降格しない)。Secondary受理(`_secondary_accept`)=`PASS`(`dual_agreed`、警告なし)、不受理 = `NG_BOTH`。`PASS_WITH_WARNING`/`SECONDARY_CONFIRMED`経路には入らない。
   - `audit["dual"] = {required, primary_pass, primary_text, secondary_called, secondary_pass, secondary_text, outcome}`(additive、runtime evidenceキー)。
2. Primary救済層の識別: adapter(`evaluate_attempt_with_cascade_detail`)が非ラテン層成功時・Tier3 corroboration成功時に`PrimaryResult.signals["primary_rescued_by_secondary"]=True`を立てる(judgeは`dual_required`時のみ参照=既定挙動不変)。CMU alternate/M1(Primary転写由来、追加ASRなし)は**Primary救済として維持**(Primary基準を満たす)。
3. 同音救済: 両Providerとも同じ`classify_asr_match`->`_step_alternate_pass`を通る。Primary側はcmu_alternate/(A-2で追加される多語同音)で救済、Secondary側は`_secondary_accept`内で同一救済=「両Providerそれぞれが基準を満たす」。A-2の変更点(`protected_check`配線)と衝突しない(本変更は`unified_judge`・adapterのctx受け渡し・PrimaryResult.signalsのみ)。
4. adapter: `cascade_enabled=False`かつ`dual_required`のときはfail-closed(Primary単独で通さず`verified=False`+technical_stop)。`FEATURE_FLAG_SECONDARY_ASR_ENABLED=True`が既定(`er006_secondary_asr_01.py:289`)のため通常は不発(防御)。

## (b) 配線点・role識別・Store再利用・resume
**識別は「呼出関数単位の明示引数」**(正規表現/文字列判定/segment_id判定に頼らない)。`generate_narration_snippet_verified_strict`(`er003_v1_repro01_main_generate.py:198`)に`dual_pass_required: bool=False`を追加 -> `build_attempt_ctx(..., dual_required=...)`(`er078_asr_unified_attempt_ctx_01.py`)-> adapter `actx["dual_required"]` -> `AttemptCtx`。**Trueを渡す呼出点(6箇所のみ)**:

| # | 経路 | 場所 | 備考 |
|---|---|---|---|
| 1,2 | X(default profile)+共有 | `generate_key_phrase_component_verified` L813/L826(Minimal 2 + English Lock 2) | **Family A/B/Cも呼ぶ共有関数**。新kwarg`dual_pass_required=False`(既定)を本関数と`ensure_key_phrase_english_component`にも追加し、X runnerだけが`True`を渡す。A/B/C呼出は引数なし=従来動作(27-7: A/B/C無改変) |
| 3,4 | X(K2 profile `fx_20261016`) | `er019_family_x_kp_en_k2_store_01.py:55`(`_styled_two_stage` primary)・`:67`(`_gen_lock`) | X専用 |
| 5,6 | Z | `er063_family_z_audio_01.py:~826`・`:~838`(`_kp_en_two_stage`) | Z専用 |

最大4回(Minimal/Styled 2 + English Lock 2)・`slot_offset/total_slots`・最終slotのみHR queue・`guarded_generate`は**不変**(dual NGは通常のNG attempt=次slotへ。最終slot NGのみ従来どおりHR Lock)。

**対象外の保証**: KP英語解説(`generate_key_phrase_explanation_en_verified` er019:~740、`KP_EXPLANATION_MAX_ATTEMPTS=3`)・`phrase_repeat`(複製のみ)・KP日本語・その他全音声は`dual_pass_required`を渡さない=既定False。**静的test(AST)**: リポジトリ内で`dual_pass_required=True`を渡す呼出が上表6箇所のみで、他モジュールに現れないことを固定(誤拡大・誤縮小の双方を防ぐ)。6箇所はmodule定数`KP_EN_PHRASE_DUAL_REQUIRED`(下記(g))を参照。

**K2 Master Audio Store再利用(ASR 0回で採用される経路)**: Store `get_or_generate`(`er006_master_audio_store_01.py:98-160`)は再利用前に`er078_reuse_value_guard_01.guard_entry`(保存転写のみ・API 0)を通す既存フックがある。KP英語entry(manifest実測394件: legacy `key_phrase_english_component` 354・`_k2` 40)は**Primary単独時代の採用**でSecondary証跡が無い(`asr_judgement`保持は40件のみ)。案:
- **案S1(推奨)**: `get_or_generate(..., reuse_gate=None)`(新kwarg、既定None=A/B/C不変)にKP dual用gateを渡す。entryに`dual_check`(Primary PASS+Secondary PASS+azure_text+sha256)が無ければ、**保存済みPrimary判定を引継ぎ(Primary再実行なし)Azureのみ1回実行**して両方PASSを確認 -> PASSなら`dual_check`をmanifestへ追記して再利用、NGなら`reuse_blocked`markを立て既存の「旧音声を`_reuse_blocked`へ退避->再生成」へ回す。保存Primaryが救済依存(`SECONDARY_CONFIRMED`警告entry)なら再利用不可として再生成。Azure結果をentryに永続化するため**同一entryの2回目以降は0円**。
- 案R(再生成): 全KP entryを再生成。TTS+Primary ASR+AzureがKPごとに必要でS1より常に高コスト・Delivery長、かつ承認済み音声を不要に入替える(品質リスク)。
- 費用比較: S1 = Azure 1回/entry ≒ JPY0.098(後述の実測)x 再利用されるentryのみ(全394件でも約JPY39の1回限り)。R = S1 + TTS + Primary ASR の全額。**S1を推奨**(品質: 両Provider確認を満たす、D/C: 最小)。
- 他の再利用点(同一out_dirの前回results・Z `generate_or_reuse_z`[`REUSE_ALLOW_PREFIXES`の`key_phrases/`]・X validation inheritance[`er019_family_x_validation_inheritance_01.py`])も同じ`dual_check`証跡を参照する共通helper(新規`er096_kp_dual_pass_01.py`、D-2)を呼ぶ。D-2で各再利用点を全数Grepし、gate漏れ0を静的testで固定。
- **resume/regeneration/retry**: dual判定は1 attempt=1 judge呼出に閉じ、attempt間の状態を持たない(circuit breakerはrun単位の既存RunStateのみ)。採用take保存時に`dual_check`を付与、未付与は上記gate。KP英語はLocal Rewrite対象外(4回構成のみ)。

## (c) Secondary転写の判定基準
Secondary側は既存の受理判定(`_secondary_accept`: `classify_asr_match`->`_step_alternate_pass`->M1、値・否定ガードをSecondary転写に独立適用)を**そのまま**使う。新基準を作らない。Azure Phrase List重み2.0・Provider routing・数値/否定の厳格判定は不変(`ledger_phrases`渡しのまま)。SecondaryCache・cost guard(`COST_GUARD_IN_UNIFIED_JUDGE`)も不変。

## (d) 費用・時間(出典付き)
- Azure単価: `er078_asr_unified_judge_01.py:110-113`(USD1/h、JPY160/USD、ceil秒)。KP wav実測(Master Store 394件のwavをwaveモジュールで計測): 平均1.676秒・ceil平均2.21秒・最大3.29秒 -> **1回 = JPY0.0983(ceil) / 0.0745(正確秒)**。
- 記事セット(Std+Adv)のKP英語phrase = 5 KP x 2 level = **10音声**(Z: `er063:534` `kp{r}_en`、Xも5 KP/level)。
- 追加Azure: 10 x 0.0983 = **JPY0.98/セット(上限: 全KP新規生成かつPrimary PASS時)** / 正確秒 0.75。OPEN-433(0.6〜0.9)と整合(出典: `docs/research/FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01/TRIAL_RESULT_01.md`、trial実費JPY1.04はPrimary込み)。
- 相殺: dual下ではPrimary NG attemptでAzureを呼ばない(現行はP3で1回呼ぶ) -> Azure削減。Store hit分はS1の初回のみ。
- 再試行増: Azure/Whisperによる追加不合格率は未実測。上限proxyとして`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/OFFLINE_C5K_TRIGGER_RATE_01.md`の「Primary PASSかつlocal Whisper不一致 = 28/333 = 8.4%」を使うと期待再生成 = 10 x 8.4% = 0.84回/セット。1回の再生成費用(TTS+Primary ASR+Azure)は本D-1では未算定 -> D-2 runtimeで実測しRESULT_PACKETに記載。Human Review増分: 最終slot(通算4回目)のみHRのため4連続dual NGが必要(proxy 8.4%^4 ≈ 5e-5/KP)。
- 時間: Azure KP平均0.72秒(同OFFLINE資料)x 10 = **+約7.2秒/セット**。
- 非ラテンKP層の救済発動実績: 全er0*_output中`non_latin_secondary`ステップは4件(grep)=救済依存はほぼ無く、「Primary救済=Primary NG」扱いでも再試行増は小さい。

## (e) 検証計画(ユーザー§4の9ケース)
| 層 | 内容 | ケース |
|---|---|---|
| (i) unit judge層 | `er096_kp_dual_pass_01_test_01.py`(本D-1作成、現行挙動固定+D-2後期待値の二相) | 1〜5,7,8 + U2不変 + Primary救済=NG |
| (ii) API 0 保存転写差込み | X/Z各KP関数(strict)を`routing.transcribe`/Azure outcomeのmock差替えで実行(実TTSなし) | 1〜5,9(4回構成・最終slotのみHR・次slot遷移) |
| (iii) 実API runtime evidence | X・Z各1 KP以上、**正式初回経路**(X runner/Z runnerのKP英語生成)。両Provider判定・呼出有無・model_id・routing・attempt/slotを`audit["dual"]`+telemetryに記録 | 1,6,7 |
| (iv) take part型拒否 | 旧`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/a2/narration/kp4_en.invalid_20261021.wav`(Primary PASS/Azure NG)をProduction judge(dual)へ。Azure再呼出1本(約JPY0.1)、またはTrial `er088_output`のAzure転写をcache差込み | 2 |
| (v) Azure障害注入 | mock例外/空転写/timeout/circuit open | 5 |
| (vi) ②③不変 | 既存回帰test群+telemetryでSecondary呼出0確認(KP解説・本文等) | 6,7,8 |
| (vii) minimal fallback不変 | 既存`force_secondary` test+本testのU2群 | 9 |
| (viii) A-2統合Regression | A-2完了commit後に1回で回す(既存回帰test群[er006/er078/er019/er063系]+4,032ペア再適用の同一runに本dual caseを追加) | 9 |

費用見積(出典付き): (iii)実API = X 1 + Z 1 KPで各 TTS+Primary+Azure ≒ JPY数円 + (iv) Azure 1本 JPY0.1 + 多語同音証跡キー同時確認 -> 合計目安JPY20〜40(委任文の目安)、案件300円以下。

## (f) A-2との統合計画
A-2(`er006_preprod_hardening_01_validation.py`/`er006_secondary_asr_01.py`編集中)完了commit後にD-2開始(同一ファイル競合回避。D-2が触る`er006_secondary_asr_01.py`のadapter部[`signals`/`actx`受渡し]はA-2の`protected_check`配線と別領域だが、同一ファイル編集は直列化)。Regression・runtime evidenceは共通化(KP実音声で多語同音証跡キーと`audit["dual"]`を同時取得)。

## (g) rollback
module定数`KP_EN_PHRASE_DUAL_REQUIRED = True`(新規`er096_kp_dual_pass_01.py`、env/flagではない)。False = 6呼出点が`dual_pass_required=False`を渡す = 現行挙動(byte-identical)。unit testで`True`/`False`双方を固定。本件はユーザー承認済み仕様(`APPROVED_FOR_PRODUCTION`)の既定ON実装であり、11-7の限定例外(未承認機能の既定OFF隔離)ではない。

## (h) SSOT案(D-2で実施、本D-1では`CURRENT_SPEC.md`未編集)
- CURRENT_SPEC新表: ①KP英語phrase=両方PASS / ②KP英語解説=Primary PASS / ③その他=Primary PASS(Secondary不要)、承認2026-10-22。
- 2818(統一判定: KPは「判定のみ統一」=本決定で①のみ上書き)、2820/2828(U2: force_secondaryの範囲=minimal fallbackのみ。①のKP英語phraseは別機構`dual_required`と明記、U2不変)、2827(KP 4回構成: 各slotで`dual_required`、最終slotのみHRは不変)、2831(U2)に追記。
- 1839(「同音救済はSecondary側も一致したときのみPASS」): 非KPは2818(AUW)で上書き済み(A-2のFable照合注記と整合)、**KP英語phraseは本決定で「両Providerがそれぞれ同音救済基準を満たしたときのみPASS」**として趣旨が復活。旧文言との関係を一文で整理し矛盾解消。
- Dangling Reference確認(D-2): Production .pyが`er088_*`・`er091_*`・`er092_*`(Trial/DEV)をimportしない(`git grep`で確認し静的test化)。

## Opus独立レビュー論点(11-3 条件A/C)
1. **Primary救済層の扱い**: 非ラテンKP層・Tier3 corroboration(Azure転写でPrimaryをPASSさせる)を「Primary不合格」とみなす案(本設計)でよいか。ユーザー§1の厳密解釈だが、2026-09-06承認の非ラテンcascade(Primary NG->Secondary救済)をKPで無効化する効果を持つ(実績4件のみ)。
2. **Primary NG時にAzureを呼ばない短絡**: 費用削減・時間短縮だが、runtime evidenceに「Secondary未呼出(Primary NG)」が残る。ユーザー§4「両Providerの実際の判定」を満たすか、Primary NGでも証跡のため呼ぶべきか。
3. **Store再利用 案S1(Azureのみ追加確認+永続化) vs 再生成**: S1で品質上十分か(Primary側は保存済み判定を信頼してよいか)。legacy 354件にSecondary証跡が無い点。
4. **共有関数への既定OFF kwarg追加**(`generate_key_phrase_component_verified`・`ensure_key_phrase_english_component`・`get_or_generate`・strict・`AttemptCtx`)のA/B/C非影響保証(27-7)と、AST静的testによる呼出点固定の十分性。
5. **Azure障害時**: `NG_SECONDARY_UNAVAILABLE`でPASS不可・技術STOP(HRに入れない)は維持するが、strictのslotループがtechnical_stopで中断しないため、障害中はTTS再生成が最大circuit閾値(3回)分走りうる。ループ中断を追加するか(最大試行・HR Lock意味の変更を伴うため非推奨)、現行circuit breakerで足りるか。

## 未配線test
`er096_kp_dual_pass_01_test_01.py`(16件: 現行挙動9 PASS・7 skip[D-2で有効化])。実行: `.venv/Scripts/python.exe -m unittest er096_kp_dual_pass_01_test_01 -v`。

---
# D-2 訂正(委任_03、2026-10-22、Opus独立レビュー OF-KPD-P-01〜12 + Fable採否を反映)
上記D-1設計のうち、下記は**本節が優先**(旧記述は履歴として残す)。Opus台帳=`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-KPD-P-01〜12)。

| 項 | D-1の記述 | D-2で確定した内容(実装=commit参照) |
|---|---|---|
| 論点A(GAP-3) | Primary救済層をPrimary NG扱い案 | **採用**。非ラテンKP層・Tier3・CS equivalenceなどAzure転写に依存して受理されたPrimaryは「Primary PASS」ではない(ユーザー§1「Secondary単独PASSでは最終合格としない」)。KP英語phraseに限り2026-09-06承認(CURRENT_SPEC:2111)を2026-10-22決定が上書き。救済フラグ`primary_rescued_by_secondary`は全層で立てる(P-06)。6呼出点は`segment_id`を渡さずTier3は到達しないが防御として持つ |
| (a)2 Primary NG時 | 「Azureを呼ばず不合格」(短絡) | **短絡しない**(P-05)。Primary NG(P3相当)でもAzureを呼ぶ(費用は現行P3と同じ・HRパッケージにSecondary転写が残る・実装単純)。Primary PASS時は`force_secondary`と同じ経路。最終的にPrimary自身がPASSしていなければ`NG_DUAL_PRIMARY_NOT_PASS`。P1/P2(値DIFF・否定差・除外表)の既存短絡は現行どおり |
| dual結果の保存 | `dual_check`をmanifestへ・`reuse_blocked` markで再生成 | X/Z専用フィールド**`kp_dual_check`**(`{version,ok,canonical_text,wav_sha256,primary{text,pass,rescued},secondary{text,pass},judge_state,source}`)に保存し、dual gateだけが読む。`reuse_blocked`はdualからは付けない(P-01)。gateは判定できなければ不合格(fail-closed) |
| Store再利用 | 案S1(Azure 1回追記) | S1は維持。ただし**旧共有key(`ensure_key_phrase_english_component`の`key_phrase_english_component`)のentryは上書きしない**: X default profileは`style_instruction_version`末尾`+dual1`のX専用keyを使う(Fable判断)。K2 key A/B(X専用)はS1ゲート。**Azure障害=技術STOP(印も再生成もしない)、Azure NGのときだけ再生成**。Store全件一括事前確認はしない(再利用時のみ) |
| 再利用点 | Store/他を「共通helper」 | 6点すべてが共通helper`kp_dual_reuse_ok`を呼ぶ: X(1)前回results `_generate_or_reuse_kp` role=english (2)`try_inherit_from_cached`(API 0) (3)Store key A (4)Store key B (5)X default `+dual1` key / Z(6)`generate_or_reuse_z` kp_en。再判定は保存Primary転写を現行分類器でAPI 0再判定し、非ラテン再構成・救済依存は不合格 |
| 共有module | `ensure_key_phrase_english_component`にkwarg追加 | **`er006_audio_cost_pilot_02_shared_narration.py`は編集しない**(Family A隔離不変条件、P-04)。X runnerの`_kp_english_generate_fn`既定分岐から`er096_kp_dual_pass_01.ensure_key_phrase_english_component_x_dual`を呼び、同一構造のMasterAudioKeyを組み立てて`repro01.generate_key_phrase_component_verified(..., dual_pass_required=True)`を呼ぶ。rollback時は共有関数へ委譲し`master_audio_id`一致(test固定)。kwarg追加は`generate_key_phrase_component_verified`・strict・`build_attempt_ctx`・`AttemptCtx`・`store.get_or_generate(reuse_gate=)`のみ(すべて既定OFF) |
| ENGLISH_LOCK前 | circuit open時もTTS最大回数 | **ENGLISH_LOCK段に入る前に`circuit_open()`を確認**し、openならTTSを回さず技術STOP(最大試行回数・HR Lockの意味は不変、P-02)。HR Lockモジュールは**変更しない**(U4/#86、OPEN-371継続)。最終slotの`NG_SECONDARY_UNAVAILABLE`→`STOPPED`→HR Lock(HUMAN_REVIEW_REQUIRED)に入る現行挙動はAPI 0 testで実証・記録(dual化で露出が増える点をユーザーへ明示=判断候補: OPEN-371のKP限定先行実装) |
| 監査 | `audit["dual"]` | `audit["dual"]`(required/primary_provider/secondary_provider/primary_pass/primary_text/primary_rescued_by_secondary/primary_rescue_layers/primary_not_pass_reason/secondary_called/secondary_pass/secondary_text/outcome)、Secondary step名`secondary_dual`、dual PASS時にclassificationをSecondary側で上書きしない、新state`NG_DUAL_PRIMARY_NOT_PASS`(PASSING_STATESに入れない。`done()`の警告→PASS_WITH_WARNING変換は不変)(P-08) |
| AST test | 6箇所 | `total_slots=KEY_PHRASE_TOTAL_MAX_ATTEMPTS`を渡すstrict呼出⇔`dual_pass_required`、`KP_EXPLANATION_MAX_ATTEMPTS`呼出にはdualなし。値はTrue直書き禁止(転送変数か単一flag読取関数`dual_enabled()`のみ)。Production .pyがer088/er091/er092/er093(Trial)をimportしない(P-09) |
| 範囲外 | - | 組立時のdual証跡欠落blockingゲート(ユーザー判断)、Store全件事前確認(ユーザー決定済み)、同一wavのAzure再試行(P-11)。**非blockingの監査**(組立時にKP英語のdual証跡欠落を警告ログ+summary記録)はFable判断で採用 |

実装ファイル: `er078_asr_unified_judge_01.py`(`dual_required`、`NG_DUAL_PRIMARY_NOT_PASS`)・`er006_secondary_asr_01.py`(救済フラグ全層・step名・classification非上書き・cascade OFF時fail-closed)・`er078_asr_unified_attempt_ctx_01.py`・`er003_v1_repro01_main_generate.py`(kwarg・circuit確認)・`er006_master_audio_store_01.py`(`reuse_gate`)・`er096_kp_dual_pass_01.py`(新)・`er019_family_x_kp_en_k2_store_01.py`・`er019_family_x_audio_production_runner_01.py`・`er019_family_x_validation_inheritance_01.py`・`er063_family_z_audio_01.py`。test=`er096_kp_dual_pass_01_test_01.py`(判定層)+`er096_kp_dual_pass_01_wiring_test_01.py`(配線)。rollback=`er096_kp_dual_pass_01.KP_EN_PHRASE_DUAL_REQUIRED`(既定True)。

## Fable判定(2026-10-22、PNMH委任_09で記録)

---
Fable判定(2026-10-22): `PRODUCTION_WIRED`。根拠=Family X(K2 profile・default `+dual1` profile)とFamily Zの正式初回経路で、KP英語フレーズの両Provider判定・呼出・採否・model_id・routingが記録され、初回dual PASSと、旧Store entry(Primary PASS/Azure NG)のS1不成立→再生成→dual PASSを観測。take part型(保存Azure転写10件)はdual PASS 0/10、実呼出でもNG_BOTH。KP英語解説・その他音声のAzure呼出0。再利用6点はfail-closed helper経由(test固定)。4,032ペア配線前後バイト一致、回帰2,339件PASS(既存失敗5件は無関係と分類)。量産影響(24 KP実測)=初回dual PASS 23/24、HR +約4%/KP(小標本)、追加原価+約JPY0.65〜0.89/10 KP音声、+0.5〜1.0秒/KP。Azure障害時に最終slotの技術STOPがHR Lockへ入る現行挙動(OPEN-371、2026-10-16 #86で当面許容)はdual化で露出が増えるが、障害時限定・実害未観測のため変更せず監視(OPEN-371へ追記)。手順逸脱の自己申告(`git add -f er096_output`、ignored混入0・実害なし)は記録のみ。
---
- OPEN-440=`CLOSED_PRODUCTION_WIRED`。
