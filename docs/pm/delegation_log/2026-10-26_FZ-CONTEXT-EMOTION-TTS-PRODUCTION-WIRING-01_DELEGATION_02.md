## 管理ID

FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02(Phase 1: Opus条件Aレビュー反映→DESIGN_02→Production実装+offline test、API 0。Phase 2[有料runtime evidence]は別委任)。並行Agent: なし(全停止)。本委任の所有=`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/**`、Z側Production code(`er063_family_z_audio_01.py`、`er012_b_family_voices_production_01.py`[既定None引数追加のみ]、`er003_v1_n3_01_tts_generate.py`[既定0/None引数追加のみ]、新module `er122_fz_ctx_policy_01.py`等、対応test)、`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_{DELEGATION_02,OPUS_REQUEST_01}*`、`docs/pm/RESULT_PACKET_FZCW2.md`、`docs/pm/ACTIVE_TASK.md`、SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`のみ。CURRENT_SPECはPhase 2完了後)。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み新仕様(APPROVED_FOR_PRODUCTION、ユーザー2026-10-26)のProduction実装(Phase 1)。到達上限Status(本委任)=IMPLEMENTED_PENDING_EVIDENCE。**PRODUCTION_WIREDとは書かない**(Phase 2 runtime evidence後にFable判定)。
- 禁止: 有料API 0(`.venv\Scripts\python.exe`起動禁止。testは`py`+`netblock_harness_01/sitecustomize.py`遮断下)/Family X/Y/B/Cの挙動変更禁止(hook=None・既定値で**バイト同一**、parity testで固定)/ユーザー仕様(ctx→ctx即時→600秒cooldown→従来方式→HR Lock/STOP、総3回)・Trial方式(Prompt/モデル/感情検査規則=`er118`と同一、sha固定)を変更しない/新しい品質基準を作らない/Trial一時機構(`redirect_production_sinks`、`PHASE1_GO`、`use_case`、Trial出力dir)をProduction経路に持ち込まない/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。共有SSOT(DECISION_LOG/OPUS台帳)は**HEAD blob+自hunkのみ**でcommit。
- 修正範囲の線引き(11-8): 範囲内=ユーザー決定§2/§3の実装、Opus M-1〜M-10/R-1〜R-2の反映、既存A/B/C/X/Yの不変保証。範囲外=試行回数・cooldown時間・感情分類・品質閾値の変更、dialogue Local Rewriteの新設、X/Yへの適用。
- Opus独立技術レビューGate(11-3): 条件A実施済み(本委任はその反映)。Fable照合: Claude案とOpusは骨子で一致、M/Rは実装の穴の是正で既存ユーザー承認内容を変えない→**Fable判断で全件採用、実装へ進む**(ユーザー判断事項なし。J-1はLR未配線の事実を完了報告で開示)。
- 時間見込み: 3〜4時間(DESIGN_02 30分、policy/state module+hook 90分、notes正式経路+adapter 45分、test群 60分、SSOT/commit 15分)。並列化: 単一Agent(同一ファイル群)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約214/残約786/本委任JPY0/承認区分: C。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。(本委任は実TTSなし。Phase 2のevidence driverのコマンド案には明示して書く)
T-3: 本委任はCapなし(JPY0)。有料API呼出が必要と判明したら実行せずSTOP。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 637 --out docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_02.md`(先頭が「## 管理ID」+「FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02」でなければ633〜648を順に試す)。Opus依頼文(prompt先頭「## 管理ID\nFZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 Opus独立技術レビュー」、index 635付近)も`docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_OPUS_REQUEST_01.md`へ保存。check実行は委任_02分。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`(保存済み、再掲しない)。実装で特に守る逐語: 「**TTS総試行回数は初回を含め最大3回。** Fallbackを追加の4回目として扱わない。」「特に、再開によって1〜2回目の文脈・感情付きTTSを不必要に再実行したり、3回の上限を超えたりしないこと。」「3回目のFallbackでは、今回の文脈・感情情報をTTS指示から完全に除外する。」「特に、ASRの表記違いだけを理由に不要なTTS再生成を行わないこと。」「Family X/Yには適用しない。」

## Opusレビュー原文(逐語。`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md`へ一字も変えず保存。先頭に`# OPUS_REVIEW_01(条件A、2026-10-26、read-only、JPY0。以下Opus所見の逐語)`の1行を付ける)

FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 Opus独立技術レビュー(条件A、実装前、read-only、JPY0)

## 結論
骨子(clip単位のpolicy object+永続state、共有ループは1コピーのまま既定Noneのhookで差し込む案A)は妥当で、ユーザー仕様を実装できる設計です。ただし回数の数え方・再開・証跡まわりに、仕様違反や誤記録につながる穴が複数あります。Phase 1着手前に、以下のM-1〜M-10を設計へ反映する必要があります。ユーザーへ戻す必要がある論点はありません(J-1は完了報告での明示開示で足ります)。

## 論点別判定
**1. 状態機械**
- (a) TTS呼出前に`n_started`を書く方式: 問題なし。3回超過は構造的に防げる。
- (b) 再開時の累積計上: 要修正(M-1)。
- (c) Advの`mark_prev_postprocess_ng`: 要修正(R-2に統合して簡素化)。cooldown判定は「n=3を始める直前」だけで決まり、前回の判定結果に依存しないので、矛盾そのものは無い。
- (d) 明示再生成とresumeの判別: 要修正(M-4)。
- (e) ASR OK確定直後〜checkpoint前のクラッシュ窓: 要修正(M-4)。「最大3回は超えない」だけでは許容できない。
- (f) cooldownを実時間の経過で数える: 問題なし。前回の開始時刻から600秒以上の実時間が空けば「NG後10分」を満たす。ただし再開時の証跡には、前回開始からの総経過秒を記録すること(`maybe_cooldown_before_attempt`の`cooldown_requested_seconds`は残り秒になるため、er020:81〜87)。

**2. hook案A**: 問題なし(条件付き、M-2・M-9)。B/C優劣は重点(1)で述べる。

**3. fallback時の完全除外**: 設計は問題なし。ただしtestの基準点が無効化する(M-9)。ctx試行内の`minimal_fallback`は許容(重点(3)で述べる)。

**4. X/Y/B/C無影響**: 問題なし(条件付き、M-5・R-2)。`REUSE_DENY`は`audit`と`narration`を拒否するため(er063:726)、新しいstate/notesも音声も新runへ漏れない。

**5. 感情情報の自動受理**: Fable目視を外すことは問題なし(要開示)。LLM失敗時の扱いは要修正(M-7)。

**6. 強制NG**: Gate迂回ではない。共有ファイルの汚染は要対応(R-1)。

**7. Trial観測6項目**: 問題なし。補足として、ctx音声はpeakが高めです。clip単位の既存条件`check_clip_audio_quality`(peak_max=0.999)を超えた場合、retry対象ではなく(verified判定にclippingは入らない)Gate停止になります。品質面は安全側ですがDelivery面のリスクなので、Phase 2でpeak分布を観測値として報告すること(新基準ではない)。

**8. 費用・時間**: 問題なし。再導出した+0.098円/callの方が式を再現できるので、保守側として採用してよい。clip内ブロック待機を既定にし、deferralはPhase 2の実測後に判断する方針も妥当。

**9. Local Rewrite**: 問題なし(J-1の意見は後述)。

## Fable重点3点
**(1) 案A**
- 案Aが最善です。案B(Z専用に複製)は、`evaluate_attempt_with_cascade`の呼出が1箇所であることを前提にした既存test(er012_b_open479_xz_segment_id_test_01.py:87-88、er078_asr_unified_wiring_13_test_01.py:344)と衝突し、ASR判定の進化からも乖離します。
- 案C(`max_attempts=1`で3回呼ぶ)は呼出のたびに`record_outcome`が走ります(er011:697)。1回目NGでLockが立ち、外側をguardで包む作り込みが必要になるので劣ります。
- hook=NoneならB/Cの挙動はバイト同一に保てます。条件は次の3つ。
  - 新引数をキーワード専用で末尾に置く。
  - er012_bに新しいimportを足さない(hookはduck typing。er109_xz_isolation testのABC_FILES)。
  - hookのstyleがNoneのときは`style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`(er012_b:520)をそのまま使う。
- 二重計上・NG化・クラッシュ窓はM-1〜M-4で扱います。

**(2) 自動受理**
- 外してよいと判断します。根拠は三つ。
  - 77件で覆し0件。
  - Fableのレビューは出力を一度も変えていない。
  - Trial側のBUDGET_PLAN_01:48が「量産では自動化が必要」と事前に記載している。
- よって品質基準の緩和ではなく、判定結果が同等の工程置換です。CURRENT_SPECと完了報告には「Trialでの目視レビューを決定論の検査へ置換した」と明記すること。
- 残余(LLM創作の上限約3.9%)はnotes保存のみで許容してよい。
- LLM失敗時は「全clip中立で続行」ではなく技術STOP(再開可)にすべきです(M-7)。
- Trial未検証storyの表示名fallbackは、安全側(誤DISCARD=中立化)なので許容。ただし表示名の取得元を改善する(R-2)。

**(3) 強制NG**
- NG方向だけの上書きで、Production codeに注入口も無いので、Gate迂回には当たりません。
- 注意点は二つ。
  - 1点目: repetition QAの段階でNGにすると、ASRの判定自体はPASSのままです。そのため最終slotでASRがHR queueへ書く経路(er006:908)が発火しません。E-4の期待値「HR queue行」は、強制NG経路では成立しない可能性があります。
  - 2点目: E-1でもdriverがpatchを掛けるなら、注入0(上書き呼出0回)をassertすること。
- ctx試行内の`minimal_fallback`は許容します。既存Z dialogueに元からある試行内の技術安全装置で、「既存の品質・安全仕様を維持」に該当します。ただし採用時の扱いは三つ必要です。
  - 最終方式として`minimal_fallback_in_ctx_attempt`を記録する。
  - 完了報告で件数を開示する。
  - 回数の数え方を定義する(M-3)。

## J-1への意見
- LRを新設せず「3回NG→STOPPED→HR Lock→STOP」とする既定が、ユーザー原文に最も忠実です。
- 原文は「既存のLocal Rewrite処理へ」です。Z dialogueには既存のLRが無いので(EXISTING_SPEC_CHECK §2、er003_n3:319)、その段は空になり、「LRで解決できなければ既存のHR/STOP規則」へ直行するのが文言どおりです。
- LRをdialogueへ新設すると、古典作品のセリフをLLMで書き換えることになります。音声と表示本文の乖離を生むProduction挙動の意味的変更なので、ユーザー承認なしには入れられません。
- ただしユーザーはLRが存在する前提で書いた可能性が高いです。非ブロッキング扱いで埋もれさせず、次の二点を完了報告に明示すること。
  - Z dialogueにはLRが未配線であり、受入表「3回NG→LR/HR/STOP」は「HR/STOP」で満たしたこと。
  - LR配線を希望する場合の選択肢とQCD影響。
- 本設計は将来のLR配線の障害になりません(DESIGN_01 §C-6の要件で足ります)。

## M(必須修正)/R(推奨)一覧(12件)

**M-1 再開時の累積計上(二重計上)【実装前Fable判断】**
- Advで前プロセスのpass1が完了していると、その試行は前プロセスの`record_outcome`で計上済みです(er011:373,384)。pass2中に落ちた後の`carried_log()`がpass1の行を再び返すと、累積TTS回数を二重計上します。
- 一方、外側ループは新プロセスで`generations_used=0`から数え直します(er003_n3:449-454)。carriedを除くと、今度は外側ループの会計が実際の消費を下回ります。
- 修正案: stateの試行ごとに「guarded呼出が戻った=計上済み」の印を持たせます。
  - `carried_log()`は未計上の試行行だけ返す(Std単一呼出の途中クラッシュ分)。
  - 外側ループには、既定0の`prior_generations`引数(前例 er003_n3:404)を追加し、計上済み分を渡す。既定値ならB/Cは不変。

**M-2 試行の位置づけ(最終slot判定)のずれ**
- 再開後、Stdでも試行番号はループ内の番号から数え直されます(er078:23-25)。そのため通算n=3の試行が`is_last_slot=False`になり、最終NGのHR queue行が欠落します(er006:908)。Advでも外側ループの`is_last_slot`(er003_n3:459)が同様にずれます。
- 修正案: dialogue側が`max_attempts=min(外側の残予算, policy.remaining())`を渡し、ループ内の番号と通算nの最終slotを一致させる。hookのstopは安全網としてだけ残す。
- testは再開後のHR queue行と`is_last_slot`をassertすること。

**M-3 minimal_fallbackの数え方の不整合【実装前Fable判断】**
- Stdはループ1周を1試行と数えます。Advの外側ループは行数で数えます(minimal_fallbackでは1周に2行、er012_b:538-545、er003_n3:305)。
- このためAdvでは、ctx試行で`minimal_fallback`が起きると、外側の予算が先に尽きてn=3の従来方式が実行されないことがあります(ユーザー仕様「2回NG→3回目従来方式」に反する)。
- 選択肢:
  - (i) n=ループ1周とし、Z dialogueに限り外側ループの数え方をpolicyに合わせる(既定Noneの引数でB/Cは不変)。
  - (ii) 既存の行数会計(CURRENT_SPEC「4回目以降は生成しない」)を維持し、この稀なケースは安全側としてHRへ送ることを明記・test化。
- どちらでも安全です。既存のA2予算規則と整合させてFableが選び、記録すること。

**M-4 明示再生成とresumeの判別、確定直後クラッシュの窓**
- 「DONE_OKのstate+checkpointに該当entry無し」は、明示再生成のときにも、guarded呼出から戻った後〜`save_checkpoint`前(er063:1434-1448)のクラッシュでも生じます。
- 現案(新規開始)のままだと、クラッシュ時には次のことが起きます。
  - ctxで合格済みのclipをn+1から作り直す。
  - n=2で落ちた場合は、10分cooldown後に従来方式へ切り替わる(方式が変わる)。
  - n=3で落ちた場合は、合格音声があるのにstopになり、誤ったHR Lockが立つ。
- 修正案:
  - 再生成の判定は明示的な信号だけで行う。`--only-clips`の対象であること、`consuming_regenerate_approval`、本文shaの不一致(er011:329-338)。
  - dialogue()は`record_outcome`の直後に、結果dictとwavのshaをDONE_OKとしてstateへ保存する。明示信号が無く、shaが一致すれば保存した結果を採用する(API 0)。それ以外は新規開始とし、理由を記録する。
  - Advで減速後の判定前に落ちた試行は、NG(消費済み)として扱う。

**M-5 prepare/policyの呼出位置**
- `build_reuse_key`は`load_results`/`_merge_checkpoint`/`migrate`/`prune_cached_to_plan`(er063:1409-1412、1234、1267、1300、1327)で、clipループより前に使われています。
- policyキーが`spec.extra`経由で付くなら、prepareがループ直前では遅すぎます。再開時に新policyのentryがkey不一致で捨てられ、再課金になります。
- 修正案: LLMを呼ばないpolicy解決を:1401と:1409の間(style_record検査の後、cached読込の前)で行い、全dialogue specへ付ける。LLMのnotes生成はその後でよい。testは、再開時に新policyのentryが再利用されることをassertすること。

**M-6 Adv narratorのchunk展開に対する入力adapter**
- Productionのplanでは、Adv narratorの100語超の段落がchunk spec(`<親>_k<j>`)に展開されます(er063:593-600)。
- これをそのまま文脈抽出へ渡すと、clip距離(`NEIGHBOR_MAX_CLIP_DISTANCE=4`)や直前・直後の地の文がTrialと変わります。idの正規表現で除外すれば地の文が欠落します。
- 修正案: `extra.chunk.parent_id/parent_text`で親clip列へ畳み戻すadapterを置く。
- TEST-01はTrial moduleとの一致だけでなく、「`build_level_plan(chunk_plans有り)`→adapter→Trialの`segment_plan` clips」の一致を必須にすること。
- `validate_emotion_items`が参照するグローバル`ALLOWED_NAMES`(er118:294)は引数化し、story別に一致testを置く。

**M-7 LLM失敗時の扱い**
- 1回再試行しても失敗した場合は、「全clip中立で続行」ではなく、そのlevelのTTS前に技術STOP(再開可・承認不要)とする。
- 理由: 全clip中立はTrialで検証されていない退化状態で、承認方式(文脈・感情付き)の基本要件を欠く成果物を黙って出荷することになります(Charter「判断を求める前の確認」(4))。再開の費用は小さい。
- 個別項目の欠落(`missing_item`)は既存のDISCARDED処理のまま続行でよい。

**M-8 effective styleの誤記録**
- `_effective_style_sha`(er063:1161-1169)は、dialogueに対して常に`ENGLISH_STYLE_PREFIX`のshaを記録します。このままだと、ctxで採用したclipが「従来style」と記録されます。
- 修正案: 採用された試行の実効style sha(ctx/従来)を記録する。`save_tts_attempt_audio`のmetadata(er012_b:583)にもmodeを追記する。読み手はレポートscriptのみ(er026_fz_style_table_17.py)なのでGateへの影響はない。

**M-9 不変性testの基準点**
- TEST-05/TEST-12の比較基準`git show HEAD:`は、Phase 1をcommitした瞬間に新コード同士の比較になり、testが無意味化します。
- 修正案: 基準を変更前のcommit(例 ab111631c)に固定するか、golden fixture(送信prompt列・attempts_log・戻り値)をPhase 1の冒頭で凍結する。

**M-10 PRODUCTION_WIRED判定に必要なruntime evidenceの不足**
- (a) 「1回目NG→2回目PASS(即時、待機0)」の実runtimeがStd/Advとも無い。E-2のattempt 2は強制NGのため。1回目だけ強制NGにするE-5を追加する。n=1 NG後にkill→再開を同時に含めれば、cooldown外の再開も1回で検証できる。
- (b) Advの外側ループ継続(n=1が減速後NG→pass2でn=2)を実runtimeで検証する。減速後判定の側でNGを注入する。
- (c) E-4は「可能ならAdv」ではなくStd/Adv両方にする。
- (d) 強制NG経路ではASR由来のHR queue行が出ない前提で、E-4の期待値を書き直す。

**R-1 共有ファイルの汚染**
- forced runでも、プロセス共通のファイルへ書き込みます。`er011_output/attempt_history.jsonl`(er011:112)、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(er006:481)、cost集計など。
- 推奨: driverが前後の行数とrun dirの識別子を記録する。forced由来のHR queue行は「evidence専用・対応不要」として台帳で無効化する。費用は量産単価ではなく開発費に計上する。
- driverは正式runnerのmain()を同一プロセスで起動し、起動時のguard(STOP確認・SDK入口のSTOP guard・cost logger)を全部通すこと。

**R-2 細部**
- policyの固定はlevel単位でなくrun単位にする(b1bはlegacyで完了済み・a2は未着手のrunで、level間に方式が混在するのを防ぐ)。
- 本文が変わった場合の扱いを一本化する。A-4のsha一致規則と「該当clipだけ中立化」が矛盾しているため。推奨はlevel単位でLLMを再呼出(Q＞C、1 call)。
- `mark_prev_postprocess_ng`は廃止し、「採用はfinish()のみ」で表現して簡素化する。
- 表示名のfallbackには、key名のTitle化より既存のspeaker table/rosterの表示名を優先する。
- STOP時の例外型は既存のSTOP系に揃える。
- Std/Adv間のcooldownは直列に加算されるため、Phase 2で壁時間を実測する。

## 「実装前にFable判断」と「実装中確認で足りる」の区別
- 実装前にFable判断: M-1、M-3、M-4、M-7。
- 実装中確認で足りる: M-2、M-5、M-6、M-8、M-9、R系。
- M-10はPhase 2計画の修正(E-5追加など)です。

## X/Y/B/C無影響の確認方法
- (1) hook=Noneでのparity test。基準は固定commitまたはgolden fixture(M-9)。成功・NG・技術失敗・minimal_fallback・stop_retryingの各シナリオで、送信prompt・`attempt_ctx`・attempts_log・戻り値が一致すること。
- (2) er012_bとer003_n3の差分が既定値の引数追加だけであること。er012_bに新しいimportが無いこと(er109_xz_isolation testを通す)。
- (3) X(er019)/Y(er121)はこの関数群を呼びません(Grepで確認済み)。runner moduleのsource sha不変と、新moduleがimportされていないことを確認する。
- (4) 既存test群(er078_*、er012_*、er063_*、er109)のPASS数を前後で比較する。
- X/Yの実runtime検証は不要(呼出経路が無いため)。

## 要約
1. 案A(既定Noneのhook)は案B/Cより優れ、B/Cの挙動をバイト同一に保てる。設計の骨子は妥当。
2. 必須修正は10件。回数会計(再開時の二重計上・minimal_fallbackの数え方・最終slot判定のずれ)、DONE_OKと明示再生成の判別、prepareの呼出位置とchunk畳み戻し、LLM失敗時は技術STOP、effective styleの誤記録、test基準点の固定、runtime evidence不足。
3. Fable目視の撤去は判定結果が同等の工程置換なので可(要明記)。強制NGはGate迂回に当たらないが、共有ファイルへの書込の識別・無効化が必要。
4. J-1は「既存LRが無い→既存のHR/STOPへ直行」が原文に忠実。LR新設は新仕様なので行わず、完了報告で明示開示する。
5. M-1・M-3・M-4・M-7は実装前にFableが判断すること。ユーザー判断が必要な論点は無い。

(Opus原文ここまで)

## Fable決定(DESIGN_02と実装に反映)

- **M-1 採用**: state各試行に「計上済み」印。`carried_log()`は未計上行のみ。外側ループへ既定0の`prior_generations`引数(既定値でB/C不変)。
- **M-2 採用**: `max_attempts=min(外側残予算, policy.remaining())`で通算nと最終slotを一致。hook stopは安全網。test必須。
- **M-3 Fable判断=(ii)採用**: 既存の行数会計(CURRENT_SPEC「4回目以降は生成しない」=ユーザー原文「TTS総試行回数は初回を含め最大3回」と同義)を維持。ctx試行内でminimal_fallbackが発生し外側予算が先に尽きる稀ケースは安全側でSTOPPED→HR Lockへ送る。理由: 承認済み会計規則を変えず、実TTS生成が3回を超えないことを優先(Q>D)。DESIGN_02に明記・test化し、Phase 2で発生件数を開示。(i)への変更はユーザー判断事項として完了報告の開示項目に載せる。
- **M-4 採用**: 再生成判定は明示信号のみ(`--only-clips`対象/`consuming_regenerate_approval`/本文sha不一致)。`record_outcome`直後に結果dict+wav shaをDONE_OKとしてstateへ保存し、sha一致なら採用(API 0)。Advで減速後判定前クラッシュの試行はNG(消費済み)扱い。
- **M-5・M-6・M-8・M-9 採用**(M-9=基準commit `ab111631c`固定+golden fixture凍結をPhase 1冒頭で実施)。
- **M-7 採用**: 感情notes LLMが1回再試行後も失敗→そのlevelのTTS前に技術STOP(再開可・承認不要・既存STOP系例外型)。`missing_item`は既存DISCARDED処理で続行。
- **M-10 採用**(Phase 2計画へ: E-5[1回目のみ強制NG+n=1 NG後kill→再開]、Adv外側ループ継続[減速後判定側で注入]、E-4 Std/Adv両方、E-4期待値から「ASR由来HR queue行」を外す)。BUDGET_PLAN_02で再見積(300円超なら報告)。
- **R-1・R-2 採用**(policy固定=run単位、本文変更時=level単位でLLM再呼出、`mark_prev_postprocess_ng`廃止、表示名=既存roster優先、STOP例外型統一、forced run由来のHR queue行は台帳で「evidence専用・対応不要」)。
- Opus補足: Phase 2でctx音声peak分布(`check_clip_audio_quality` peak_max=0.999)を観測値として報告(新基準ではない)。
- J-1: LR新設せず。完了報告でLR未配線・HR/STOP直行・LR配線希望時の選択肢とQCDを開示(本委任ではDESIGN_02とOPEN_TRACKING_02に記載)。

## 事前指定Read一覧

1. `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/{DESIGN_01,TEST_PLAN_01,EXISTING_SPEC_CHECK_01,SPEC_LEDGER_01,BUDGET_PLAN_01,OPEN_TRACKING_01}.md`(DESIGN_01/TEST_PLAN_01は全文、他は該当節)。
2. Opusが引用した行(Grep→該当範囲): `er012_b_family_voices_production_01.py` :500-600、`er003_v1_n3_01_tts_generate.py` :290-330, :400-480、`er011_*` :100-120, :320-400, :690-700、`er078_asr_unified_attempt_ctx_01.py` :15-40、`er006_*` :470-490, :900-915、`er020_*` :70-95、`er063_family_z_audio_01.py` :580-610, :720-730, :1150-1175, :1225-1240, :1260-1335, :1395-1460、`er118_fz_dialogue_context_tts_trial_01.py`(`validate_emotion_items`、CONTEXT合成、`NEIGHBOR_MAX_CLIP_DISTANCE`、`ALLOWED_NAMES`)、`er118_fz_full_episode_trial_01.py`(notes生成・segment_plan)。
3. 既存test: Glob `er078_*_test_*.py`、`er012_*_test_*.py`、`er063_*_test_*.py`、`er109_*_test_*.py`(件数・実行方法。`er012_b_open479_xz_segment_id_test_01.py:80-95`、`er078_asr_unified_wiring_13_test_01.py:340-350`は該当範囲Read)。
4. `netblock_harness_01/sitecustomize.py` 先頭(使い方)、`run_project_regression.py --help`。
5. `docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `OF-KPRS-M1`(直近書式)。`DECISION_LOG.md` 先頭30行。`docs/pm/PM_BRIEF.md` Grep `ACTIVE_TASK固定ヘッダ`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Phase 1冒頭: `git rev-parse HEAD`を記録し、golden fixture(hook=Noneでの送信prompt列・attempt_ctx・attempts_log・戻り値を、成功/NG/技術失敗/minimal_fallback/stop_retryingの5シナリオでmock経由取得)を`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/golden/`へ凍結(変更前コードで生成。sha記録)。
- X/Y不変: `er019_*runner*.py`・`er121_*.py`が新module/新引数を参照しないことをGrep(0件)、runner source shaを前後で記録。
- OPUS_FINDINGS_LEDGER.md: OF-FZCW-M-1〜M-10・R-1〜R-2(12行)をRAISED→FABLE_DECIDED(採用、M-3=(ii))→IMPLEMENTED(本委任で実装したもの)で追加。
- DECISION_LOG.md: 新規エントリ1件(委任_02 Fable決定: Opus M/R全件採用、M-3=(ii)、J-1=LR新設せず開示、Phase 1実装完了=IMPLEMENTED_PENDING_EVIDENCE)。
- OPEN_ITEMS.md: OPEN-528行末に「委任_02 Phase 1実装完了(IMPLEMENTED_PENDING_EVIDENCE、test N PASS、API 0)。次=Phase 2 runtime evidence」を追記。
- ACTIVE_TASK.md: 固定ヘッダで上書き(管理ID=本件 委任_02/APPROVED未配線=OPEN-528(Phase 1済み・Phase 2待ち)/UDR-blocking=OPEN-526・527・529・531・532/当日費用=2026-10-26 約214/1,000)。

## 実行コマンド全文

- 変更前基準の回帰(遮断下): `$env:PYTHONPATH="netblock_harness_01"; py run_project_regression.py --pattern "er078*_test_*.py"`、同`"er012*_test_*.py"`、`"er063*_test_*.py"`、`"er109*_test_*.py"`、`"er118*_test_*.py"`(`--help`で実引数を確認し実値で記録。変更前後で各PASS/FAIL数を比較。既存失敗がHEADでも同じかを記録)。
- 新規test(遮断下): `$env:PYTHONPATH="netblock_harness_01"; py -m pytest er122_fz_ctx_policy_01_test_01.py er063_fz_ctx_wiring_test_01.py -q`(ファイル名は実装に合わせ、`_test_`を含める)。
- 接続試行0: 遮断harnessのログ/出力をRESULT_PACKETへ。
- X/Y/B/C不変: `git diff --stat -- er019_*.py er121_*.py`(空)、`er012_b`/`er003_n3`の差分が既定値引数追加のみであることを`git diff -- <file>`抜粋で示す。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件)。
- Phase 2用evidence driverのコマンド案(実行はしない。RESULT_PACKETに実値で記載): 例 `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er122_fzcw_runtime_evidence_01.py --case E-1 --work the_monkeys_paw --level a2 --run run_fzcw_e1_01 --budget-jpy 60` 等、E-1〜E-5×Std/Advの全コマンド。

## 実装要求(DESIGN_02に従う)

1. `DESIGN_02.md`: DESIGN_01+Fable決定(M-1〜M-10/R-1〜R-2)の反映。§0にM/R対応表(各項目の実装箇所ファイル:行)。CURRENT_SPEC文案(§J)を更新(「Trialでの目視レビューを決定論の検査へ置換」「Z dialogueにLR未配線、3回NG→HR Lock/STOP」「M-3=(ii)」を明記)。
2. 新module(例 `er122_fz_ctx_policy_01.py`): clip単位policy object(n_started/counted印/DONE_OK結果+wav sha/mode列[ctx,ctx,legacy]/cooldown開始時刻と総経過秒)、永続state(run dir配下)、`before_attempt(n)`→style(ctx or None)、`finish()`のみで採用、resume復元、明示再生成信号、run単位policy固定、技術STOP(M-7)。
3. 感情notes正式経路: Trialと同一Prompt/モデル/`validate_emotion_items`(引数化したallow-list、story別data、既存roster表示名優先)、level単位1 call+1回再試行、run内不変、本文sha変更時はlevel単位で再呼出、保存先=run dir、cost logger経由。Adv narrator chunk展開の畳み戻しadapter(M-6)+TEST-01(plan→adapter→Trial segment_plan一致)。
4. hook(案A): `er012_b`/`er003_n3`へキーワード専用・既定None/0の引数のみ追加(新import禁止)。`er063`のdialogue生成でpolicyを:1401〜:1409間で解決(M-5)、`max_attempts`をM-2どおり、`prior_generations`をM-1どおり、`record_outcome`直後にDONE_OK保存(M-4)、effective style/mode記録(M-8)、reuse_keyへ方式識別。
5. test群(TEST_PLAN_01+Opus): §6の6ケース(cooldownは時間mock)、fallback完全除外(attempt 3 prompt=基準commitの旧prompt とバイト一致、CONTEXT 0件)、parity(hook=None、golden fixture 5シナリオ)、resume(各n直後のクラッシュ、cooldown中のクラッシュ→総経過秒)、上限3回超過禁止、M-2(再開後のis_last_slot/HR queue行)、M-3(ii)(minimal_fallbackで予算先行消費→HR送り)、M-4(DONE_OK sha一致で再利用・明示再生成で新規)、M-5(再開時reuse)、M-6(chunk畳み戻し・story別ALLOWED_NAMES)、M-7(LLM失敗→STOP、再開可)、X/Y不変(Grep+sha)、er109 isolation。
6. `TEST_PLAN_02.md`・`BUDGET_PLAN_02.md`(M-10反映のPhase 2見積、300円判定)・`OPEN_TRACKING_02.md`(J-1開示文、M-3(i)の選択肢、残Open Item)・`EVIDENCE_PLAN_02.md`(E-1〜E-5×Std/Advの手順・期待値・強制NG注入の対象判定点・共有台帳の前後行数記録・HR queue行の無効化手順・peak分布の観測)。
7. Phase 2 evidence driver `er122_fzcw_runtime_evidence_01.py`の実装(本委任ではmock testのみ、実行なし): 正式runner main()を同一プロセスで起動、Gate出力をNG方向のみ上書き、E-1では上書き0をassert、専用run dir、公開page出力なし、evidence JSON(`path`/`forced_ng_injection`/共有台帳前後行数)。

## SSOT追記文

上記Grep節のとおり。CURRENT_SPECは編集しない(文案のみDESIGN_02 §J)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(DECISION_LOG.md/OPEN_ITEMS.md/docs/pm/OPUS_FINDINGS_LEDGER.md)。CURRENT_SPEC/REPORT_LEDGER/UDR=なし。
- commitは2つに分ける: (1)設計・Opus原文・golden fixture(`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/**`、delegation_log 3ファイル) (2)実装+test+SSOT(新module・test・`er063`・`er012_b`・`er003_n3`・driver・SSOT 3ファイル自hunk)。wav/raw_usage_log/STOP/lockは含めない。
- commit message例: (1)`FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: Opus条件Aレビュー(M-1〜M-10/R-1〜R-2)反映のDESIGN_02・test/evidence計画・golden fixture凍結(API 0)` (2)`FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: Z dialogue ctx→ctx→cooldown→legacy policy実装(案A hook・既定None、X/Y/B/C不変、test N PASS、API 0、IMPLEMENTED_PENDING_EVIDENCE)`。
- `git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FZCW2.md`: (0)T-0 (1)結論(IMPLEMENTED_PENDING_EVIDENCE、M/R反映状況表=番号/実装箇所/test名) (2)test結果(新規N PASS、既存群の前後PASS/FAIL数、接続試行0) (3)X/Y/B/C不変の証拠(diff抜粋、Grep、sha、parity test) (4)fallback完全除外の証拠(test名・比較基準commit) (5)M-3(ii)の挙動と発生時の記録名 (6)Phase 2 EVIDENCE_PLAN_02要約とBUDGET_PLAN_02(見積・300円判定・Guardrail) (7)driverの安全性(注入口なし・NG方向のみ・E-1 assert) (8)SSOT追記行・自hunk証拠 (9)commit hash×2・push・raw URL (10)一覧外Read (11)Fable向け懸念(Phase 2実行前に確認すべき点)。最終行に要約10行以内。