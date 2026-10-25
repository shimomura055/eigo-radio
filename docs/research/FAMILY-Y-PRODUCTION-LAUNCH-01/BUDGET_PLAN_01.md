# BUDGET_PLAN_01: Family Y Production立上げ 費用概算(Phase 0。**見積依頼であり増額承認ではない**)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_01 / 2026-10-25(JST)。**本委任(Phase 0)の実費=0円**(API 0・TTS/ASR 0・runner起動0)。以下は全て**推定**(根拠は既存Trialの実測)。実測が出たら差し替える。為替=pricing_snapshot.jsonの160円/USD(各BUDGET_LOG準拠)。

## 0. 前提(既存成果物の再利用)

- 再利用する(宅配の再配達・案B固定): Voice R0(Leakage Gate PASS、`er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md`)、改訂Lead・人物紹介(`REDELIVERY_REVISION_01`、Gate PASS)、案B本文。再生成しない(来歴検査付きで取り込み、DESIGN_01 §7)。
- 再利用しない(正式経路で新規に作る): 英訳(5パート+紹介+Lead+案Bが新構成のため)、Preview/Comment/KP(最終英文から選定、本文実在Gate要)、全TTS/ASR(紹介segment追加・Y segment ID・Productionの検査経路)。
- 使用モデル(25節): 生成=`gpt-6.1-sol`(最新世代最上位系)、判定/補助=`gpt-6-luna`、TTS=`gemini-3.8-flash-lite-tts`(承認済み正式backend)。本番ラインのモデル選定は別判断。

## 1. 単価の実測根拠

| 項目 | 実測(円) | 出典 |
|---|---|---|
| Voice R0 生成(3 Voice、Gate込み) | 19.8〜25.5(宅配 run_01 25.344+Gate 0.145、SNS run_03 23.667、改善R0 02a/02b 20.64/19.80) | `OPINION_BASED_02/BUDGET_LOG_OB_05.md`、OPEN-463 委任_22/25 |
| Lead(1 call) | 1.08〜2.14 | `REDELIVERY_AUDIO_01/BUDGET_LOG_01.md` §1、`REDELIVERY_REVISION_01/BUDGET_LOG_01.md` §2 |
| 人物紹介(3本を1 call) | 約2.7/call(v1+v2で5.43) | 同 |
| Closing一般化(Prompt 02, high, 1生成+Gate判定) | 16.8〜21.5(平均19.21、宅配21.0/SNS17.4) | `CLOSING_GENERAL_01/EVAL_02.md`(vi)、`BUDGET_LOG_02.md` |
| Leakage Gate 1判定(luna high) | 0.05〜0.6 | 同 |
| 英訳(Adv忠実英訳+Std簡易化)+英語監視 | 1.04+0.54=1.58 | `REDELIVERY_AUDIO_01/BUDGET_LOG_01.md` §1 |
| scaffold(Comment/Preview/タイトル/KP/gloss) | 1.52 | 同 |
| TTS+ASR(Std+Adv、再生成1件込み) | 19.72(旧構成・In One Line有) | 同 |
| Part 2(A''+B) | 0.40〜0.41/セット(HR再選定等で最悪約0.9) | `PART2-GRAMMAR-PRODUCTION-WIRING-01/BUDGET_PLAN_02.md` |
| KP HR(2 call目・確定集合QA等) | +1.0〜3.0/セット(推定) | `KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/BUDGET_PLAN_02.md` §1 |
| Part 1(Adv) | 約0.3〜0.8(推定。Y用は未測定) | OPEN-512(X/Z実測の範囲) |
| 日本語読み調査(Web検索付き) | 0〜22.8(1回限り。Ledger登録後は再発しない。Y Trialで見積外22.8円の実績) | OPEN-463 委任_08/09 |

構成変更による増分(推定): 紹介segment(各level 3本)とLead延長で音声尺+約9〜11%(`REDELIVERY_REVISION_01/DESIGN_01.md` §3)→ TTS/ASR 22〜26円。

## 2. 見積(区別して提示)

### (1) 正常系1記事の完成費用

| 内訳 | A: 『宅配の再配達』案B固定・再利用あり | B: 通常のY記事(再利用なし・Closing一般化) |
|---|---|---|
| 日本語Voice R0+Gate | 0(再利用) | 20〜26 |
| Lead+人物紹介 | 0(再利用) | 4〜8 |
| Closing(生成+Gate) | 0(固定。Gate 1判定 0.05〜0.6) | 17〜22.6 |
| Closing Gate FAIL時の期待追加(局所書換え) | 0(固定は書換え禁止・FAILはSTOP) | 0.5〜1.4 |
| 全体Voice+Closing Gate(5パート一括確認) | 0.3〜0.8 | 0.3〜0.8 |
| 英訳(Adv+Std)+監視 | 1.6〜2.5 | 1.6〜2.5 |
| plan/support/KP/Part 1/Part 2/KP HR | 3.2〜5.7 | 3.2〜5.7 |
| TTS/ASR(Std+Adv) | 22〜26 | 22〜26 |
| **合計** | **約27〜35円**(再試行なし)。TTS再生成2〜4件込みで〜39円 | **約69〜93円**(中央約81円)。日本語読み調査が発火すると+0〜23円 |

**量産単価**: 目標70円/記事セットに対し、Bの中央値は約81円で**約11円超過**、下限(69円)でようやく目標内。主因はY固有のsol呼出2系統(Voice R0 20〜26円+Closing 17〜22円=約40円)。Xの定常平均(約75円)と比べ同等〜やや高い。**これはTrial単位の推定であり、量産実績ではない**(情報収集の人手約25分は円換算していない。LLM化の費用も未測定)。

**原価低減の余地(Charter原則3)**: 承認済み範囲を変えずに取れるもの=①Closing Gate FAILを全文再生成でなく局所書換えで受ける(期待-3〜4円/記事、PROMPT_GATE_ALIGNMENT_01 I-1)②Lead/紹介の反復生成を避ける(一発合格率の改善、-2〜5円)③Master Audio Storeの再利用(固定phrase、効果小)④日本語読み調査をLedger登録で1回限りにする(0〜23円の上振れ抑制)。**承認が要るもの(独断では取らない)**: Closing medium化(単価-55%だがRound 2で宅配が劣り不採用候補)、Voice R0の効率化、Closing出力schemaの簡素化(Prompt変更)。立上げ後の実測でユーザー判断として提示する。

### (2) 検証・再試行込みの立上げ総額(Phase 1〜2の有料作業の合計)

| 項目 | 内容 | 見積(円) |
|---|---|---|
| E-1 | 宅配(案B固定)を正式経路で1記事完成(上表A)。再試行余裕込みの上限〜39 | 27〜39 |
| E-2 | HRなし(auto)・HRあり(wait→選択→再開)の両経路。本文・body TTSは再利用、KP差分のみ(各4〜9) | 8〜18 |
| E-3 | 一般化Closing経路のruntime evidence(SNSの年齢制限、Voice既存): Lead/紹介+Closing+Gate+英訳まで(音声なし) | 24〜36 |
| 試験的少額call | routing/model_id確認(luna 1 call等) | 1〜2 |
| 再試行余裕(E-1+E-3の約25%) | HR Lock、翻訳retry、Gate書換え | 13〜18 |
| **合計** | | **約73〜113円(中央約93円)** |

- 任意(判断候補なし・Fable判断): E-3をSNSの**全音声E2E**まで拡張する場合 +26〜32円。必要十分性の観点では、Closing本文は案Bと同形式の1段落でTTS経路は宅配E-1で検証済みのため**不要と考える**(推奨しない)。
- 案件個別Cap提案: **150円**(見積上限113円+約30%)。承認済みScope(APPROVED_FOR_PRODUCTION)内・案件見積300円以下のため、7-7によりユーザーの都度承認は不要(Fable確認)。日付・stage分割による境界回避なし。
- 計上外: Opus条件Aレビュー等のClaude Code利用分(日次API費用の対象外)。

### (3) 本日承認済み予算残額

| 項目 | 円 | 根拠 |
|---|---|---|
| 日次上限(JST 2026-10-25) | 1,500 | 委任文 |
| 日次累計(`daily_dev_cost_01.py` adopted) | 974.35 | 実行出力(records 941、files 1,077)。`max(log, ledger)`方式 |
| 未反映分(Closing一般化 Round 2) | +94.28 | ツールは`raw_usage_log.jsonl`のみ走査し、Round 2は`raw_usage_log_high/medium.jsonl`名のため未捕捉(`daily_dev_cost_01.py:99-105`)。OPEN-463 委任_33記載の実費 |
| **日次累計(補正後)** | **1,068.63** | |
| **本日残額** | **431.37** | |
| 並行案件の控除(上限) | KP HR evidence ≤300、JA ASR Phase 3 ≤60 | 委任文 |
| 並行控除後の残(最悪ケース) | **71.37** | 上限満額使用時 |
| 並行控除後の残(想定使用時) | 約350〜380 | KP HR 30〜60(`BUDGET_PLAN_02`)+JA ASR Phase 3 約21 |

- 補足: ツール捕捉外(run dir外・ログ外課金、Batch等)があるため日次累計は**下限値**(`uncaptured_kinds`)。
- **本日中にY有料runを起動する予定はない**(Opus条件Aレビュー→実装→test が先、最短でも翌日JST以降)。よって「本日残額71〜431円」は(2)の実走に使われず、実走は新しい日次枠で行う(日付分割による境界回避ではなく工程上の自然な順序)。

### (4) 不足時の追加予算希望額

**現時点で追加希望額0円**。(2)の上限113円は日次1,500円・7-7自律範囲内。次の場合のみFableへ報告(`判断候補`): 見積が個別Cap150円を超える見込み(再利用が効かず通常記事相当[約69〜93円]を複数回要する/HR Lockが多発/Closing Gate FAILが連続)、日次上限超過見込み、新仕様の採用が必要になった場合。

## 3. 受入条件12項目と証拠(E-1〜E-5)

| # | 受入条件 | 証拠 |
|---|---|---|
| 1 | 正式初回経路 | E-1(`er121_*`runnerで宅配を初回〜完成まで) |
| 2 | Y固有構成維持 | E-1(5パート・3 Voice・紹介・In One Lineなし・注意書き・mapping検査) |
| 3 | Prompt 02+sol highの実使用 | **E-3**(宅配は案B固定のため不使用。SNSで実使用を記録) |
| 4 | model_id・routing・Prompt hash記録 | E-1/E-3の`closing_record.json`・usage log |
| 5 | HRあり・なし両経路 | E-2 |
| 6 | 適用対象共通仕様の実装 | 台帳の『適用』行(YL-A*)ごとのtest+E-1 runtime(OPEN-484 a〜f) |
| 7 | retry・fallback・regeneration・resume維持 | test+E-1の再開/部分再生成 |
| 8 | Regression・Validator・integration PASS | E-4(全回帰、自分起因failed 0) |
| 9 | 正式E2E実動作 | E-1(限定試聴ページの実再生検査) |
| 10 | SSOT・Git | E-5 |
| 11 | 未完了事項のOPEN追跡 | OPEN-520+台帳 |
| 12 | 承認内容と出力一致 | 案B sha一致・Prompt sha一致・固定注入表示 |
| 別Status | ユーザー最終試聴PASS | `USER_LISTENING_PENDING`(先取りしない) |
