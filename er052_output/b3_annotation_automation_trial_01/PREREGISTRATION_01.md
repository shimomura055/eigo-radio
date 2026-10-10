# PREREGISTRATION_01: B3-ANNOTATION-AUTOMATION-TRIAL-01(2026-10-10、Status=DRAFT_FOR_FABLE_USER_CONFIRMATION)

事前登録案。Phase 2実行前にFable/ユーザーが確定する。確定までPhase 2(課金API)は実行しない。確定後は結果を見て閾値・方式・モデルを変更しない(変更時は理由を記録して再登録、結果と混ぜない)。
設計詳細: `DESIGN_01.md`。「確認済み/未確認」の区別は同書に従う。

## 1 目的
注記版B3(Fact Lock用に`【事実N】`/`【中核数値】`/`【周辺数値】`を付与したB3)を、Trialで「Sonnet系worker A/B(Claude Code subagent)+決定論統合」で作っていた作業を、**Productionで安定して自動生成できるか**を、仕様v2を変更せずに検証する。対象仕様 = `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v2_ANNOTATOR.md`(sha256 `8d145c3d…1e57`)+テンプレートv2+運用明確化(a)(b)。

## 2 Ground Truth
Trialの `annotation/final/<slug>/selected_brief_factlock.md`(A/B統合結果)9テーマ(byd_recall, central_bank_mortgage, hormuz[B3 v2], meta, openai_copyright, semiconductor_earnings, small_bag, space_weapons, streaming_price[B3 v2])。sha256は `gt_inventory.json`。
- **GTは人間の正解ではない**(`claude-sonnet-5-5`の2回出力の決定論統合)。9テーマ全てでA単独とB単独のタグ件数が一致しており、誤り相関の疑いがある。GT一致は必要条件であって十分条件ではない。
- inbound_tourismはGTなし(Trial時点でA/B単独check FAIL)。**check-onlyのストレス入力**として扱い、GT比較指標には含めない。
- 旧4の過去の人手注記は使わない(仕様v2 §B)。

## 3 方式候補
- M-A: 単一呼び出し(Trial worker A相当)+単独check。新Prompt不要(Trial実プロンプト逐語)。
- M-B: 同一プロンプトでA/B 2呼び出し+`merge`(決定論)+統合後check。新Prompt不要。**本命**。
- M-C/M-D: 新Prompt必須。**本Trialの対象外**(別Phase。承認後)。
- M-AとM-Bは**同じ呼び出し結果を共有**して評価する(A出力=M-A、A+B=M-B)。

## 4 モデル(開発・評価用途の最新モデル原則 PM_GOVERNANCE 25節)
- `claude-sonnet-5`(最新Claude Sonnet系。Trial worker `claude-sonnet-5-5` と同系列。API名と`-5-5`の同一性は未確認→実行前に無料のmodels listで確認し報告)
- `gpt-6.1-sol`(OpenAI最新世代主力。cross-model参照)
- `gpt-6-astra`(最上位。任意・縮小実施。Fable判断)
- 旧/下位(gpt-5.6-*, haiku-4-5)・最廉価(gpt-6-luna)は使わない(理由が現時点で無い)。使う場合は実行前に例外理由を明記。
- Provider既定のthinking/effort(OpenAIはreasoning effort=medium、既存`xm_driver.py`と同じ)。`max_output_tokens`/`max_tokens`=16000(Trial外の新設定、Fable確認)。
- 報告には各runの使用モデルID(応答のmodel値)、最新か、最新でない場合の理由を記載する。

## 5 実験行列と反復
10テーマ × 2反復 × {A,B} × モデル。モデルごとに40 call(M-A/M-B共有)。再試行は形式FAIL時に同一入力・同一プロンプトで**1回まで**(Trial `RUN_ANNOTATION.md` 節6と同じ上限。元応答も保存)。STOP返答(仕様§4)は再試行しない。
入力はTrialの凍結入力(`stage_r/<slug>/…`)をそのまま使い、変更しない。プロンプトはTrial実プロンプト本文を逐語(`annot_driver.py:verify_provenance`で出所検証)。

## 6 評価指標と成功基準案(閾値はFable/ユーザーが確定。ここは案)
指標定義は `DESIGN_01.md` 4-2。評価は決定論スクリプト(`annot_eval.py`、`annot_driver.py pipeline_one`)。

ハードゲート(1つでも満たさなければ当該モデル・方式はREJECTED候補):
| ID | 基準案 | 備考 |
|---|---|---|
| H1 | 検査(a)本文非改変: 採用された出力の100% | 検査FAIL出力を静かに採用しない |
| H2 | 検査(b)(c)(d)(e)全PASSの出力のみ採用。FAIL出力を手で直さない | 完全版§J |
| H3 | M-B: GT 9テーマ中 merge PASS 9/9(2反復とも、再試行込み) | |
| H4 | 台帳に無いIDへの紐付け・VERIFIED以外への紐付け(AMBIGUOUSを除く): 0件 | |
| H5 | 仕様・プロンプト・検査script・GTを実行中に変更しない | |

性能基準(案):
| ID | 基準案 | 備考 |
|---|---|---|
| P1 | 初回(再試行前)の単独check PASS率 ≥ 80%(GT 9テーマ×2反復の18 call中14以上) | Trial参考: 最終採用の単独check PASSは18/18だが、初回FAILが複数あり(DESIGN 2-4) |
| P2 | GT比較 タグF1(9テーマのマイクロ平均): 事実 ≥ 0.90、中核 ≥ 0.90、周辺 ≥ 0.90 | 閾値は推定値(根拠となる実測は無い=未確認) |
| P3 | 位置一致した印の中核/周辺 分類一致率 ≥ 0.95 | |
| P4 | Fact ID対応一致率 ≥ 0.90 | |
| P5 | 安定性: 同一入力2反復の統合注記版完全一致率 ≥ 6/9 テーマ、かつ反復間タグF1 ≥ 0.95 | |
| P6 | 1記事(M-B・2 call)の費用がPhase 2実測で Fableが許容する範囲(目安: JPY 100以下/記事) | 見積midは約JPY 25/記事(仮定込み) |
| P7 | 差分一覧の人間目視(3テーマ以上): GTとの差分が「候補の誤り」か「GTの誤り/許容差」かを分類、重大誤り(誤った台帳紐付け・誤った中核化)0件 | 目視担当はFable/ユーザー決定 |

判定の割り当て案(事前登録):
- **VALIDATED**: H1〜H5全達成 かつ P1〜P5達成 かつ P7で重大誤り0件 かつ P6を満たす方式×モデルが1つ以上。ただし**VALIDATEDはTrial上の結果であり`APPROVED_FOR_PRODUCTION`ではない**。自動Production配線しない。
- **REJECTED**: H1〜H3のいずれかを全方式×全モデルで満たせない、またはP1/P2を全方式×全モデルで満たせない。
- **USER_DECISION_REQUIRED**: 上記の中間(閾値の一部のみ未達、モデル間で結果が割れる、GT側の誤りが疑われる、Production前提(書式・台帳欄)に不確実性が残る、M-C/M-D(新Prompt)の検討が必要、等)。
Closeout語彙は`REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`のみ。

注意(解釈上の限界):
1. GTは同系列モデルの出力。`claude-sonnet-5`は同系列ゆえ一致率が過大に出うる。`gpt-6.1-sol`の一致率が低くても「GTと違う」だけで「誤り」とは限らない(P7で切り分け)。
2. 検査script(`compute_expected`)がclassを再計算するため、classの誤宣言は検査で捕捉される一方、**印を付ける対象の選び漏れ(分類漏れ0)以外の語彙判断(事実境界・概念束ね)は検査で正解性を担保できない**。
3. 入力briefは短い(353〜772字)。長いbriefでの結果は未検証。
4. Productionのbrief書式・台帳スキーマが本Trialの凍結入力と同等かは未確認。

## 7 費用
見積は `DESIGN_01.md` 5節/`estimate_01.json`(sonnet-5 + sol の40call×2モデル: low JPY 414 / mid JPY 1,006 / high JPY 1,853。astra全量は高額)。**Phase 2のCap案: JPY 3,000**(Fable/ユーザー確定)。到達見込みで停止し報告。Phase 2開始前の無料作業: models listによるmodel_id確認。

## 8 禁止事項(本Trial全体)
- 注記なしB3を「W-1と同等」と扱わない。
- Trial用の手作業注記をProduction仕様として扱わない。
- 未検証の簡略方式(M-A単独、M-C、M-D)へ勝手に置換しない。M-Aは評価のみで、Production候補化は別途ユーザー判断。
- Trial成功だけでProduction採用しない。
- 仕様v2・テンプレート・Trial実プロンプト・検査/統合scriptを変更しない(変更はv3扱いで全テーマ再実行・結果を混ぜない)。
- retry/fallback/regenerationの上限(再試行1回)と検査Gateを独自判断で回避・無効化しない。
- Production正式経路(量産runner)へ本Trialのコードを混入させない。DEV/Trial専用経路(`er052_output/b3_annotation_automation_trial_01/`)に隔離。
- CURRENT_SPEC.md / Production コード / 既存Promptを変更しない。

## 9 Production配線しない宣言
本Trialの結果が良好でも、**自動Production配線は行わない**。Production採用(`APPROVED_FOR_PRODUCTION`)は人間ユーザーのみが承認する。採用提案時は重要変更のためOpus独立技術レビューGate(条件C、`PM_GOVERNANCE.md` 11-3)を通す。本ファイルのStatusは「Trial事前登録案」であり`APPROVED_FOR_PRODUCTION`ではない。
