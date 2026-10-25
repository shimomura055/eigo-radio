# BUDGET_PLAN_03: Family Y Production立上げ 費用計画(委任_02C更新。**見積であり増額承認の依頼ではない**)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02C / 2026-10-25(JST)。`BUDGET_PLAN_02.md`からの更新点だけを書く(単価の出典・再利用/新規の前提はBUDGET_PLAN_01 §0〜§1・BUDGET_PLAN_02のとおり)。

## 1. 個別Capの更新(Fable判断、委任文転記)

| 項目 | 値 | 根拠 |
|---|---|---|
| 個別Cap | 150円 → **170円** | Fable判断(委任_02C)。BUDGET_PLAN_02 §2の提案(見積上限160円+約6%)を採用。承認済みScope(APPROVED_FOR_PRODUCTION)内・案件見積300円以下のため、7-7によりユーザーの都度承認は不要(`docs/pm/PM_GOVERNANCE.md` 7-7、2026-10-19)。日付・stage分割による境界回避なし |
| 既支出(Y立上げ累計) | **14.347円** | 02A実費(M-1較正5.97+M-2書換えevidence 8.38)。`BUDGET_PLAN_02.md` §1 |
| 本委任(02C)の実費 | **0円** | 有料API 0・Production run 0・実音声0(offline test/偽client/socket遮断のみ。`er121_family_y_text_core_article_test_01.py`は接続試行0を各テストで確認) |
| 残Cap | **155.65円** | 170 − 14.347 − 0 |

## 2. 立上げ総額の最新見積(E-1〜E-5)

BUDGET_PLAN_02 §2の内訳を維持し、02Cで実装が確定したため**テキスト側の内訳だけ**実装に合わせて細分化した(総額は変更なし)。

| 項目 | 内容 | 見積(円) | 02Cで確定した事実・根拠 |
|---|---|---|---|
| E-1 | 宅配(案B固定)を正式経路で1記事完成。再利用manifest(R0 Voice・改訂Lead・人物紹介) | 27〜39 | テキスト側はAPI 2 callのみ(Lead+紹介の補助判定1、案B判定1。luna、約0.3円)。Voice Gateは来歴検査付きの既存PASS記録を再利用(判定promptがDEV版とバイト一致のためsha一致)。残りは英訳・音声・ページ。**案BがFAILした場合は1判定で停止**(OT-27 案I) |
| E-2 | HRなし/ありの両経路(KP差分のみ) | 8〜18 | 変更なし |
| E-3 | SNS年齢制限: voices段(**SNS Theme Packageから実生成**)+Lead/紹介+closing(一般化)+Gate+英訳+planまで、音声なし | **44〜62** | 内訳(下表)。Voice段はTrial実績(SNS run_03=23.667円、宅配run_01=25.344円。`state.json` final_cost_jpy)と同じ処理構成のため20〜26円 |
| 試験的少額call | routing/model_id確認等 | 1〜2 | 変更なし |
| 再試行余裕(E-1+E-3の約25%) | HR Lock、翻訳retry、Gate書換え | 18〜25 | 変更なし |
| (済)M-1較正+M-2 evidence | 02A実費 | 14.35 | — |
| **立上げ総額** | | **約112〜160円(中央約135円)** | **Cap 170円に対し上限側でも約10円の余裕**(BUDGET_PLAN_02で指摘した超過懸念は解消) |

### E-3(新規生成)の内訳(02Cのcall構成による)

| 段 | call(model/effort) | 見積(円) | 出典 |
|---|---|---|---|
| Voice生成 | gpt-6.1-sol/high × 3(逐次) | 約16〜20 | Trial R0実績(Voice生成が大半)。Sol入力$2・出力$10/Mトークン(`pricing_snapshot.json`) |
| Voice出典付番・構造タグ・最終付番 | gpt-6-luna/medium × 7(付番3+構造1+最終付番3)。UNMAPPED再生成/構造発火時のみ追加(Sol 1+luna 2〜3) | 約0.7〜1.5(再生成発火時+3〜4) | Trial実績の範囲 |
| Voice Gate | gpt-6-luna/high × 1〜3(+FAIL時のVoice書換えSol/medium 1〜2) | 約0.2〜0.6(書換え発生時+2〜5) | M-1較正・M-2実測 |
| Lead | gpt-6.1-sol/high × 1(契約違反時のみ+1) | 約2 | `revision_01/raw_usage_log.jsonl`(入力872・出力1,163トークン) |
| 人物紹介(3本1 call) | gpt-6.1-sol/high × 1(+1) | 約2.5 | 同(入力1,614・出力1,391) |
| Lead+紹介の補助Gate | gpt-6-luna/high × 1 | 約0.1 | 同(入力約1,000・出力900〜1,400) |
| Closing一般化 | gpt-6.1-sol/high × 1(契約違反時のみ+1)+Gate luna × 1(+FAIL時書換えSol/medium) | 約17〜21(+書換え2〜6) | BUDGET_PLAN_02 §5・REWRITE_EVIDENCE_01 |
| **小計(英訳・plan前)** | | **約39〜48** | 英訳・planは別(BUDGET_PLAN_02のE-3総額に含む) |

- **逐次実行の理由**: Voice 3本の生成は並列化できるが、cost loggerの`logging_context`がプロセスglobal(`er005_cost_logger._CONTEXT`)でstageタグが競合し、費用のstage別計上と予算guardの正確性を損なうため逐次にした(DEVは並列で、stageタグ混在の可能性があった)。時間はVoice生成が3倍になる(1callあたりおよそ数十秒〜2分)が、費用への影響はない。
- 削減余地(Charter原則3): ①Voice段のmedium化等は品質判断(ユーザー承認事項)のため独断で行わない。②E-1のVoice再利用は既に反映。③cached_tokens・flex/Batch(R-6)は未確認(E-3実測時に`resp.usage`で確認)。

## 3. 正常系1記事の完成費用(参考、BUDGET_PLAN_02 §3から変更なし)

- A(宅配、案B固定、再利用あり): 約27〜35円(テキスト側は約0.3円)。
- B(通常のY記事、再利用なし): 約69〜93円(中央81円)。量産単価70円に対し約11円超過(実測後にユーザー判断として提示)。

## 4. 本日(JST 2026-10-25)の予算

02Cは有料API 0のため日次累計に加算なし。BUDGET_PLAN_02 §4の補正後日次累計(1,085.89円、本日残額414.11円)をそのまま引き継ぐ(他案件の並行消費は未反映。`docs/pm/tools/daily_dev_cost_01.py`で再集計すること)。

## 5. 未確認
- cached_tokens実測・flex/Batch可否(R-6): 未確認。E-3実測時に確認。
- 為替は`pricing_snapshot.json`のとおり(取得日2026-08-17、USD建て)。円換算の最終値は`er121_family_y_calibration_01.spent_jpy`型の集計(同スナップショット)で行う。
