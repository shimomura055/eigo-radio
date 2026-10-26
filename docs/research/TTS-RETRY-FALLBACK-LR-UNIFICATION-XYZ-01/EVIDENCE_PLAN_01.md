# EVIDENCE_PLAN_01 — Family×レベル別の正式runtime evidence計画(委任_03で実施。本書は計画のみ・API 0)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01。原文§6「本番相当の正式runtime evidenceをFamily・レベル別に取得し、単なるDEVテスト成功で完了扱いにしない」「actual model_id・routing・Style/Prompt・試行回数・待機時間・LR実行回数・最終判定を検証可能に」に対応。

**KPI provenance区分(該当なしの理由)**: 本evidenceは仕様配線の検証であり品質KPIの測定ではない。強制NG由来のHR queue行・attempt_history行・費用は「evidence専用・対応不要/開発費」として台帳で無効化する(FZCW COST_01と同じ扱い)。量産単価への影響は別途offline集計(BUDGET_PLAN_01 §4)で出し、本evidenceの費用を量産単価に混ぜない。

## 1. 方式: 「代表+固定」(同一共通核を通る部位は代表で取り、残りはoffline testで固定)

X/Y/Zは同じleaf関数(L1〜L8)と同じ`er127`共通核を通る。したがって全49行×Family×レベルを実走させる必要はなく、(a) **leaf種別ごと**に代表部位を実走し、(b) **Family/レベルごと**にrunner統合(Gate・HRQ・exit code・STOP・resume)を最低1経路で実走し、(c) 残りの部位はoffline test(T-MAP 49行・leaf matrix・golden)で固定する。代表の取り方は下表。
- **X**(`er019`): 全leaf種別(L1/L2/L3/L4/L5/L6/L7)をStd/Advで実走=共通核の主要検証。
- **Y**(`er121`): runner統合に絞る(Y Gate・HR終端・Voice本文[L4/L2]・KP・JA)。短文部位でLR/待機、本文Voiceで③/LR採用→Y Gate BLOCKの実挙動。
- **Z**(`er063`/`er026`): dialogue ctx(L8)・narrator chunk(L4/L2)・topic_intro_en(U-06の実証)・KP・JA・KP解説。
- 全部位を実走しない理由=費用と時間(§6)。ただし代表で見つかった差異が他部位に波及しないことはT-MAP+leaf matrixで機械的に保証する。

## 2. 強制NG注入(NG方向のみ。FZCW driver `er122_fzcw_runtime_evidence_01.py`の方式を一般化)

- 実TTS・実ASR・**実180秒待機(`time.sleep`)**・実LR(`gpt-5.6-luna`のLLM)・実Gate・実runner(`main()`を同一processで起動、runner起動guardを全部通す)。driverは**Gateの出力をNG方向にだけ**上書きする。`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示(Batch不使用。T-2)。
- 注入点(いずれも`ordinal`=clipごとの何回目の判定か、で指定。LR block内は通算ordinalを継続: ①'=4, ②'=5, ③'=6):
  1. **統一judgeの結果**(`evaluate_attempt_with_cascade`/JA版/KP 3-ASR vote): ordinal指定でNG化。**LRを発動させる場合は同時にPrimary転写へ「1語置換」を注入**(NG方向のみ)する。理由: judgeだけNG化するとASR転写=原稿のままでLRの`identify_ng_span`が`NO_NG_SPAN`になり、LRが動かない(動かないことはE-S7で別途検証)。1語置換転写をjudgeへ通すと本物のjudgeが`TRUE_CONTENT_MISMATCH`を返す=「注入した転写に対する本物の判定」。
  2. **disfluency/repetition QA gate**: ASR一致のままQAのみNG化(E-S7=U-03の再現)。
  3. **減速後再検証**(Std本文): `post`注入(FZCW E-6と同形)。
- 本物の判定に戻すordinal(③以降の実PASS)では注入しない。注入記録(`forced_ng_by_driver`・`driver_ordinal`・`driver_case`)を結果に残し、`injected_override_count`で上書き回数を数える。正常系(E-N)は`injected_override_count==0`をassert。
- 注入は**Style・Prompt・Voice・速度・model・待機・回数に一切触れない**(判定結果のみ)。evidenceが検証したい対象(Fallback Style切替・実待機・LR回数・試行回数)は注入の影響を受けない。
- Opus確認事項: 転写1語置換でLR経路を駆動する方式が「LR後も同じGate」の証拠として十分か。代替=自然にNGになる文面の探索(再現性なし・費用増)。

## 3. シナリオ定義(最低限要件(a)〜(g)との対応)

| ID | 要件 | シナリオ | 合格基準(全てevidence JSONから機械判定) |
|---|---|---|---|
| E-N | (a) | ①PASS(正常) | 注入0。TTS=1/clip、`cooldown_events==[]`、LR=0。追加生成・待機なし(V-01) |
| E-S1 | (b) | ①②NG→**実180秒**→③(Fallback Style)実PASS | `cooldown_actual_seconds>=180`(±tolerance 2秒)がちょうど1回、③の`style_prefix`/`instruction_type`がFallback、①②が元Style、Voice/model/速度が全attemptで同一、TTS=3(V-03/V-08/V-10) |
| E-S2a | (c) | ①②③NG→LR(Luna)→LR block①'**実PASS** | LR=1(`depth=1`のLRなし)、書換え後textが期待text、`script_version=v1`・`LR_REWRITTEN`警告付PASS、Style/Voice/速度保持、待機1回、TTS=4、HRQ行0、最終OK(V-05/V-09) |
| E-S2b | (c) | ①〜⑥全NG(LR block内も)→HR | TTS=6(それ以上なし)、待機2回(各≥180秒)、LR=1・再入0、③'がFallback Style、Lock=HUMAN_REVIEW_REQUIRED、HRQ**1行**、Gate BLOCK/STOP/rc(Family別)(V-05/V-06/V-11) |
| E-S3 | (d) | LRなし部位 ①②③NG→HR | TTS=3、待機1回、LR=0、Lock+HRQ1行+Gate BLOCK/rc(V-04/V-11) |
| E-S4 | (e) | KP英語 前段2NG→**実180秒**→ENGLISH_LOCK③(PASS) / 4回NG→HR | 待機1回(ENGLISH_LOCK段の直前)、③④=ENGLISH_LOCK、TTS=3(PASS時)/4(HR時)、HRQ=slot4のみ(V-07) |
| E-S6 | (g) | 180秒待機中に自processをkill→同一argsで再起動 | 再開後に①②の再生成0、待機は残り時間のみ(総経過≥180秒)、③1回、二重計上なし、TTS総数=3(V-12) |
| E-S7 | U-03 | ASR一致+disfluency/repetition単独NG(①②③) | ①②→180秒→③実行、③NG後`lr_applicable==False`、LR LLM=0・LR block=0、即HR、HRQ1行、TTS=3(L-08) |
| E-X5 | S-06 | KP解説の短文Style適合性 | 既存3 explanation textに③と同じminimal Styleで1 take、ASR PASS・disfluency NGなし。不適なら`style_seq`縮退(DESIGN_01 §8) |
(f) Zセリフctx②NG→180秒→legacy③はE-S1(L8 ctx)で取る。

## 4. evidence JSONの必須キー(原文§6「検証可能にする」)

各case 1ファイル(`er127_evidence_<case>.json`相当。保存先=既存の`er0XX_output/`構造に従い、本件は`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/evidence/`へ要約、run dirは各Familyの既存out_dir配下の新規run名):
`management_id` / `case` / `family` / `level` / `clip_id` / `leaf` / `policy`(profile名) / `actual_model_id`(attemptごと。`flw.resolve_actual_model_name`の戻り) / `routing`(`tts_backend`・TTS_EXECUTION_MODE=STANDARD・ASR primary/secondary/vote構成) / `attempts[]`(`ordinal`・`style_mode`・`style_prefix`のsha256とラベル・`instruction_type`・`voice`・`speed/slowdown`・`asr_judgement`・`verified`・`forced_ng_by_driver`) / `cooldown_events[]`(`requested`・`actual`・`started_at`・`ended_at`・`resumed`) / `lr`(`count`・`depth`・`status`・`ng_span`・`rewritten_text_sha`・`retts_attempts`) / `final`(`status`・Lock状態・HRQ追加行数・Gate結果・runner rc) / `tts_calls_total` / `cost_jpy`(`cost_log.jsonl`集計) / `injected_override_count` / `stop_scope_check`(開始時rc) / `evidence_only_ledger_invalidation`(強制NG由来の台帳行の無効化メモ)。

## 5. 実施手順・安全運用(委任_03)

1. 各case開始前に`tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 --run-dir <run> --out <json>`。rc=3なら新規API 0で停止・報告。
2. run dirは既存資産(X=coffee_prices等のtext・KP・Part)をコピーし、**LLM text生成は走らせない**(`--stages tts`系、`--only-clips/--only-segments`で対象clipのみ)。Z完成段の再実行が必要な場合は`--stages provision_shell,gate,assemble,pages,page_verify`を1起動で指定(OPEN-480)。
3. 6 process並列(X-Std/X-Adv/Y-Std/Y-Adv/Z-Std/Z-Adv。別run dir・別PID。scopeは`er109`のmodule globalだがprocessごとに独立)。各processの`--budget-jpy`をFamily/レベル別capに設定(§BUDGET_PLAN)。`kill`はE-S6の自PIDのみ(26-6)。起動PIDを記録。
4. 再起動はE-S6の1回だけ(委任文で明示許可が必要)。原因不明のrc≠0が2回続く/外部停止は再起動せず即STOP報告。
5. 完了後: Fable受入用に`injected_override_count`・待機実測・TTS総数・LR回数・費用を集計。強制NG由来のHRQ/attempt_history行は「evidence専用」で台帳化。
6. 正常系(E-N)と量産原価の比較は、既存run dirの`attempts_log`集計(API 0、BUDGET_PLAN §4)で出す。

## 6. 実施ケース一覧(Leanプラン=推奨。`full`との差は★)

| case | Family/Lv | leaf・部位 | シナリオ | 内訳(attempt数/種別) | 待機 | 期待円 | 保守円 | 天井円 | Lean |
|---|---|---|---|---|---|---|---|---|---|
| X-Std-1 | X/Std | L3 topic_intro | E-S1 ①②NG→180→③PASS | short×3 | 1 | 2.1 | 3.0 | 4.5 | ○ |
| X-Std-2 | X/Std | L3 topic_intro | E-S2a ①②③NG→LR→①'PASS | short×4 + lr×1 | 1 | 3.4 | 5.0 | 8.0 | ○ |
| X-Std-3 | X/Std | L3 topic_intro | E-S2b 全6NG→HR(+再入なし) | short×6 + lr×1 | 2 | 4.8 | 7.0 | 11.0 | ○ |
| X-Std-4 | X/Std | L4 in_one_line(減速) | E-S1 | body_s×3 | 1 | 3.0 | 4.8 | 6.6 | ○ |
| X-Std-5 | X/Std | L4 in_one_line(減速) | E-S2b(案A: 減速後再検証NG含む) | body_s×6 + lr×1 | 2 | 6.6 | 10.6 | 15.2 | ○ |
| X-Std-6 | X/Std | L7 japanese_title | E-S1 | ja×3 | 1 | 1.5 | 2.4 | 3.6 | ○ |
| X-Std-7 | X/Std | L7 japanese_title | E-S3 LRなし③NG→HR | ja×3 | 1 | 1.5 | 2.4 | 3.6 | ○ |
| X-Std-8 | X/Std | L6 kp1_en | E-S4 前段2NG→180→ENGLISH_LOCK③PASS | kp×3 | 1 | 1.8 | 3.0 | 4.5 | ○ |
| X-Std-9 | X/Std | L6 kp1_en | E-S4 4回NG→HR | kp×4 | 1 | 2.4 | 4.0 | 6.0 | ○ |
| X-Std-10 | X/Std | L3 topic_intro | E-S6 待機中kill→resume(①②再生成0・残り待機のみ) | short×3 | 1 | 2.1 | 3.0 | 4.5 | ○ |
| X-Std-11 | X/Std | 正常系(N-lite 2 clip) | E-N ①PASS無待機 | short×2 | 0 | 1.4 | 2.0 | 3.0 | ○ |
| X-Adv-1 | X/Adv | L1 comment_1 | E-S1 ①②NG→180→短文③PASS(Adv新規) | short×3 | 1 | 2.1 | 3.0 | 4.5 | ○ |
| X-Adv-2 | X/Adv | L1 comment_1 | E-S2a | short×4 + lr×1 | 1 | 3.4 | 5.0 | 8.0 | ○ |
| X-Adv-3 | X/Adv | L1 comment_1 | E-S2b 全6NG→HR | short×6 + lr×1 | 2 | 4.8 | 7.0 | 11.0 | ○ |
| X-Adv-4 | X/Adv | L1 comment_1 | E-S7 U-03: ASR一致+disfluency単独NG→LR不可→即HR | short×3 | 1 | 2.1 | 3.0 | 4.5 | ○ |
| X-Adv-5 | X/Adv | L2 in_one_line | E-S1 | body_s×3 | 1 | 3.0 | 4.8 | 6.6 | ★除外 |
| X-Adv-6 | X/Adv | L2 in_one_line | E-S2b(LR再TTSのStyle保持を確認) | body_s×6 + lr×1 | 2 | 6.6 | 10.6 | 15.2 | ○ |
| X-Adv-7 | X/Adv | L5 kp1_explanation_en | E-S1 | kpx×3 | 1 | 2.4 | 3.6 | 5.4 | ○ |
| X-Adv-8 | X/Adv | L5 kp1_explanation_en | E-S3 LRなし③NG→HR | kpx×3 | 1 | 2.4 | 3.6 | 5.4 | ○ |
| X-Adv-9 | X/Adv | L5 kp解説 適合性 | E-X5 既存3 text×minimal 1take(ASR PASS・disfluency NGなし) | kpx×3 | 0 | 2.4 | 3.6 | 5.4 | ○ |
| X-Adv-10 | X/Adv | L6 kp1_en | E-S4 PASS | kp×3 | 1 | 1.8 | 3.0 | 4.5 | ○ |
| X-Adv-11 | X/Adv | L6 kp1_en | E-S4 4回NG→HR | kp×4 | 1 | 2.4 | 4.0 | 6.0 | ○ |
| X-Adv-12 | X/Adv | L1 comment_1 | E-S6 resume | short×3 | 1 | 2.1 | 3.0 | 4.5 | ○ |
| X-Adv-13 | X/Adv | 正常系(N-lite 2 clip) | E-N | short×2 | 0 | 1.4 | 2.0 | 3.0 | ○ |
| Y-Std-1 | Y/Std | L3 topic_intro | E-S2b 全6NG→HR(Y側の終端確認) | short×6 + lr×1 | 2 | 4.8 | 7.0 | 11.0 | ○ |
| Y-Std-2 | Y/Std | L7 japanese_title | E-S1 | ja×3 | 1 | 1.5 | 2.4 | 3.6 | ○ |
| Y-Std-3 | Y/Std | L6 kp1_en | E-S4 PASS | kp×3 | 1 | 1.8 | 3.0 | 4.5 | ○ |
| Y-Std-4 | Y/Std | L4 y_voice_1(本文Voice) | E-S1 ①②NG→180→③PASS → Y Gate(STD_FALLBACK)BLOCK確認 | body_l×3 | 1 | 6.0 | 7.0 | 9.0 | ○ |
| Y-Std-5 | Y/Std | 正常系(N-lite 2 clip) | E-N | short×2 | 0 | 1.4 | 2.0 | 3.0 | ○ |
| Y-Adv-1 | Y/Adv | L1 comment | E-S2a | short×4 + lr×1 | 1 | 3.4 | 5.0 | 8.0 | ○ |
| Y-Adv-2 | Y/Adv | L5 kp1_explanation_en | E-S1 | kpx×3 | 1 | 2.4 | 3.6 | 5.4 | ○ |
| Y-Adv-3 | Y/Adv | L6 kp1_en | E-S4 PASS | kp×3 | 1 | 1.8 | 3.0 | 4.5 | ○ |
| Y-Adv-4 | Y/Adv | L2 y_voice_1(本文Voice) | E-S2a ①②③NG→LR→①'PASS → Y Gate(LOCAL_REWRITE_RECOVERY)BLOCK確認・Voice/Style保持 | body_l×4 + lr×1 | 1 | 8.6 | 10.4 | 14.0 | ○ |
| Y-Adv-5 | Y/Adv | 正常系(N-lite 2 clip) | E-N | short×2 | 0 | 1.4 | 2.0 | 3.0 | ○ |
| Z-Std-1 | Z/Std | L4 narrator chunk | E-S2b | body_s×6 + lr×1 | 2 | 6.6 | 10.6 | 15.2 | ○ |
| Z-Std-2 | Z/Std | L8 dialogue ctx | E-S1 ctx①②NG→180→従来③PASS | zdlg×3 | 1 | 2.0 | 3.0 | 4.5 | ○ |
| Z-Std-3 | Z/Std | L8 dialogue ctx | E-S3 3NG→TERMINAL_NG→rc=2 | zdlg×3 | 1 | 2.0 | 3.0 | 4.5 | ★除外 |
| Z-Std-4 | Z/Std | L7 japanese_title | E-S1 | ja×3 | 1 | 1.5 | 2.4 | 3.6 | ○ |
| Z-Std-5 | Z/Std | L6 kp1_en | E-S4 PASS | kp×3 | 1 | 1.8 | 3.0 | 4.5 | ○ |
| Z-Std-6 | Z/Std | L3 topic_intro_en(U-06) | E-S2a(新規にLR・待機が有効になることの実証) | short×4 + lr×1 | 1 | 3.4 | 5.0 | 8.0 | ○ |
| Z-Std-7 | Z/Std | 正常系(N-lite 2 clip) | E-N | short×2 | 0 | 1.4 | 2.0 | 3.0 | ○ |
| Z-Adv-1 | Z/Adv | L2 narrator chunk | E-S2b | body_s×6 + lr×1 | 2 | 6.6 | 10.6 | 15.2 | ○ |
| Z-Adv-2 | Z/Adv | L8 dialogue ctx | E-S1(減速後NG含む通算) | zdlg×3 | 1 | 2.0 | 3.0 | 4.5 | ○ |
| Z-Adv-3 | Z/Adv | L8 dialogue ctx | E-S3 3NG→HR | zdlg×3 | 1 | 2.0 | 3.0 | 4.5 | ○ |
| Z-Adv-4 | Z/Adv | L1 topic_intro_en(U-06) | E-S2a | short×4 + lr×1 | 1 | 3.4 | 5.0 | 8.0 | ○ |
| Z-Adv-5 | Z/Adv | L5 kp1_explanation_en | E-S1 | kpx×3 | 1 | 2.4 | 3.6 | 5.4 | ○ |
| Z-Adv-6 | Z/Adv | L6 kp1_en | E-S4 PASS | kp×3 | 1 | 1.8 | 3.0 | 4.5 | ○ |
| Z-Adv-7 | Z/Adv | L1 preview/comment | E-S1 | short×3 | 1 | 2.1 | 3.0 | 4.5 | ★除外 |
| Z-Adv-8 | Z/Adv | 正常系(N-lite 2 clip) | E-N | short×2 | 0 | 1.4 | 2.0 | 3.0 | ○ |

合計: full=49case / Lean=46case(TTS 161回、LR LLM 13回、実180秒待機 46回)。

## 7. 各Family・レベルで要件(a)〜(g)を満たす対応(最低限)

| 要件 | X Std | X Adv | Y Std | Y Adv | Z Std | Z Adv |
|---|---|---|---|---|---|---|
| (a) ①PASS | N-lite(2clip)+各case①部分 | 同 | 同 | 同 | 同 | 同 |
| (b) ①②NG→180→③PASS | X-Std-1/4/10 | X-Adv-1/7/12 | Y-Std-4(本文Voice) | Y-Adv-2 | Z-Std-2 | Z-Adv-2/5 |
| (c) LR→3回構成→最終(PASSとHR) | X-Std-2(PASS)/3(HR) | X-Adv-2(PASS)/3(HR)/6 | Y-Std-1(HR) | Y-Adv-1/4(PASS) | Z-Std-6(PASS)/1(HR) | Z-Adv-4(PASS)/1(HR) |
| (d) LRなし③NG→HR | X-Std-7 | X-Adv-8 | (代表: X。Yはleaf共通・runner統合はY-Std-1) | (同) | (代表: X) | Z-Adv-3(dialogue) |
| (e) KP英語4回 | X-Std-8/9 | X-Adv-10/11 | Y-Std-3 | Y-Adv-3 | Z-Std-5 | Z-Adv-6 |
| (f) Zセリフctx②NG→180→従来③ | — | — | — | — | Z-Std-2 | Z-Adv-2 |
| (g) resume重複なし | X-Std-10 | X-Adv-12 | (代表: X。YのBlockProgressはleaf共通) | (同) | (代表: X。Z ctxは既存E-3/E-5をZ-Std-2系で再確認) | (同) |

「代表: X」の欄は、同一leaf・同一`er127`共通核であり、runner固有の差(Gate・exit code)は左の統合case(Y-Std-1/Y-Std-4/Y-Adv-4等)で取るため、重複実走を省く(代表+固定)。Fableが「全欄を個別実走」を要求する場合の追加費用は§BUDGET_PLAN 追加案を参照。
