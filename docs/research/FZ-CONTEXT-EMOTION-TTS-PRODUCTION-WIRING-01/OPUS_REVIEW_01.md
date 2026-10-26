# OPUS_REVIEW_01(条件A、2026-10-26、read-only、JPY0。以下Opus所見の逐語)

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
