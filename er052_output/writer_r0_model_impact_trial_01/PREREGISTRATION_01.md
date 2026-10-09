# PREREGISTRATION_01: WRITER-R0-MODEL-IMPACT-TRIAL-01(Phase 2実行前に固定、2026-10-10)

性質: Trial/DEV。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、採用判断なし。本書作成時点のAPI支出=¥0(Phase 1はAPI非呼び出し)。数値は「実測」「見積」を区別する。USD/JPY=160(既存運用値)。

## 1. 入力artifact(3テーマ共通で FACTLOCK-ASTRA-E2E-TRIAL-01 の新仕様腕 `runs/<theme>/new/` を再利用。research/ledger/B3/注記は再生成しない)
ルート: `er052_output/factlock_astra_e2e_trial_01/`。注記版B3の版: 3テーマとも B3注記仕様v2(サイドカー `spec_sha256`=8d145c3d...1e57、揃っている)。space_weapons は `new/`(`new_prev_b1/`は旧B1腕で使わない)。`runs/<t>/new/storyline_b3/selected_brief.md` と `inputs/<t>/selected_brief_annotated.md` は同一sha(機械確認済み)。

| テーマ | 台帳 `runs/<t>/new/research_ledger/verified_fact_ledger.txt` | 注記版B3 `runs/<t>/new/storyline_b3/selected_brief.md` | annotation.json(inputs/) |
|---|---|---|---|
| streaming_price | 11eb38bd8532096c...9481ce3 | 8f5047b77e8754f5...50293b7d6f0 | 236a58e5cf8f1931...4b774de |
| space_weapons | f172a253f24b99d6...6868 | b25d3a8d201b888c...364045 | 2b692de41368604a...cb0ce287e99 |
| byd_recall | 06ae3dca98cd237a...b67dafd | 0d5fb346c3669e01...e8011087f9a93e02 | 8156837f771bd8be...49264557 |

完全sha256(正): streaming_price 台帳 `11eb38bd8532096c2ad11569ab06ea3e4fd1e113f001a52d6a6ee789e9481ce3` / 注記版B3 `8f5047b77e8754f5e597054afe79524d0783f2cfbe16bc2d2670d50293b7d6f0`。space_weapons 台帳 `f172a253f24b99d66cf0ffbe187857dddb3f6e3fa6cc1186700942519f4a6868` / 注記版B3 `b25d3a8d201b888c56e79014878253991e1ee984403c5093db01781988364045`。byd_recall 台帳 `06ae3dca98cd237a3bf4ab8b3a58b3e8103ff7761662a5868ba0f46c9b67dafd` / 注記版B3 `0d5fb346c3669e01644e8011087f9a93e02677fa9af075abb23791da07dcc0e8`。
Research出力そのもの(`runs/<t>/new/` 配下のresearch生出力)はR0入力に使われない(R0入力=注記版B3の Storyline+Selected Facts のみ。台帳はFlaggerの根拠として使用)。

## 2. R0呼び出し構造(判定: (a))
- Fact Lockは R0 Prompt に組み込まれた同一LLM呼び出し(`er052_factlock_writer_trial_01_run.apply_factlock_patches()` が `jaw.CONCRETENESS_CONTROL_AN3_BLOCK` をFact Lock R0ブロック `build_r0_block` に差替え。ブロックsha256=`74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1`、E2E各テーマの `r0_meta.json` と一致を確認済み)。独立stage(b)ではない。決定論処理(c)でもない。
- R0生成関数: `er019_family_x_ja_writer_o_r1_r2_01.build_original_prompt(...)` → `jaw.call_fresh(client, DEVELOPER_MESSAGE, prompt, WRITER_EFFORT="high", "ja_original")`。モデルは `jaw.WRITER_MODEL`(定数、既定 gpt-6-luna)で決まる。**本Trialのdriverは実行時に `jaw.WRITER_MODEL` を差替えるだけ**(Production code無編集・ファイル非変更。E2E runnerが既に同型のmonkeypatchを使用)。
- 出力条件: Responses API、`reasoning.effort="high"`、developer message固定、`temperature`/`max_output_tokens`/`seed`は指定しない(既存R0と同一。全モデルで同条件)。
- 後処理(全セル同一): `strip_markdown`は使わない(R0は`.strip()`のみ)→`clean_ja_for_next`(`fl.strip_tags`で【事実N】等を除去、残存はTagLeak)→末尾改行。これはE2E runnerの`worker_new_r0`と同一。
- **E2E R0 stageとの差(要Fable確認、判断記録)**: E2E R0 stageは生成後に同モデルの Fact Check(`ja_original_check`)を実行し、MAJORならmust-fix再生成1回、記号検出でも再生成が走る。本Trialは「Fact逸脱リスクのR0素の差」を見るため、**全セルで生成1回のみ(Fact Check・must-fix・記号must-fixは実行しない)**。理由: Fact Checkはユーザー指示のChecker範囲に近く、再生成が走ると素のR0出力が失われ、セル間で再生成回数が揺れて比較条件が崩れる。記号検出は測定のみ記録。この差分はFableの規則「R0 stageに属するLLM呼び出しは全て比較対象モデルで実行」の文言とは異なる解釈(Fact Checkを生成の一部とみなさない)。→ Fable判断欄。

## 3. 固定条件・モデルID
- 比較対象(ユーザー指定): `gpt-6-luna` / `gpt-6.1-sol` / `gpt-6-astra`。実測model_idはAPI応答の`model`欄を記録。
- 同一Prompt(3モデル間でsha一致を機械確認): streaming_price `37a6174bbd5ac24af7c098cb3744da34cf2feae64957057baad904184994a66c`(2445字) / space_weapons `29d462e94970cefba4cd3ebabaef08c86e95c06a20fa5015ac6aebc14866506a`(2642字) / byd_recall `c2d7b29f394604103a76811f8a2d38ca4662548004efb3abff813ab1c2970d2f`(2211字)。全文は `prompts/<theme>.txt`、`prompts/prompt_manifest.json`。
- 再試行: 各R0呼び出しの失敗時は同条件で最大1回。再失敗セルは欠損として報告(別モデル・別条件で埋めない)。
- 既存Luna成果物(E2E の `new_writer/r0.md`)は比較に使わない。Luna R0も本Trial内で新規生成(sha比較は参考記録のみ)。

## 4. Risk Flagger構成(既存のまま、変更なし)
- D0: `detectors/d0_directional.py`(決定論)。D2: `prompts_flagger.d2_system()`(万能、confidence付き、severity常に重大、type=5種+その他)を**記事モード**(`--ledger --article`相当: 記事を文分割して全文と全台帳を1呼び出しで渡す)で実行。**D2rank(上位3強制)は使わない**。Flag件数は固定しない。
- 判断(要確認): ユーザー指示の「文単位でconfidence付きFlagを全件」に合う既存構成は`d2`(記事モード)。同構成の記事モード実行は過去Trialでは`d2rank`が主で、`d2`記事モードでの実績は無い(コードは`--detector d2 --ledger --article`で実行可能、変更不要)。Prompt・検出器の変更なし。
- Flaggerモデル: `gpt-6.1-sol`、effort=`medium`(run_flagger_01.pyの既定。P3/P4と同じ)、prompt_cache_keyは既存実装どおり。
- sha: prompts_flagger.py `730bc55f7ff1a8186e5555c431c75b2f67dc45951bb32315935b99ff15973e0c` / run_flagger_01.py `0962b6e42314f39cd211242f4583fa76ca0e3078d7ec9ea562a77e5ca820f675` / flagger_lib.py `4cb071ff03801bea020393c71000c7883adc6d118c313878e54e5c162ce8a2da` / d0_directional.py `972634b4edb491a811460a88abc61e5d227d73c07a92b83b24e8495a27db4583` / ledger_restore_01.py `7e465e5b7513153085532ca6ac8e04b534d570ffd218c642bc70cac9f15d17de` / D2 system prompt sha256 `b8dacc147009a13bea886d5d97d387fc5ff06171d878fcae7fdddbd18fd6d405`。
- detectors配下は無変更。driverは`run_flagger_01`の関数をimportし、出力先(`RESULTS_DIR`/`LOGS_DIR`/`flagger_lib.LEDGER_PATH`)を実行時に本Trial配下へ差替えて使う(detectors配下へ書かない)。Flagger側の費用ガードも本Trialの台帳基準。
- Flag種類: D2は既存の`type`(rollback反転/主体対象入替/否定反転/数量時系列/不在断定/その他)を出力する。これは既存タイプをそのまま記録する。ユーザー指定7分類への対応付けは**Sonnet暫定分類(未確定)**として別欄に付与(理由欄から後付け、Flaggerは変更しない)。

## 5. 集計定義(事前固定)
- Flag総数 = D0 ∪ D2 の文単位ユニーク件数(既存`union_flags`: (文,type)で統合。D0の`gate_only`Flag[不在断定・数量時系列・増減/許可反転]は既存規約どおり和集合に入れず、別欄で件数のみ併記)。D0/D2別件数も併記。
- confidence統計(最小/最大/平均/中央値)はD2のみ(D0 Flagのconfidenceは決定論ルールの値で別扱い、分布は別掲)。全Flag保存。「confidenceは絶対評価に使わない」。
- R0生成費用=R0のusage×登録単価(`er005_output/cost_baseline_01/pricing_snapshot.json`、Standard。luna 入力$0.1/出力$0.5、sol 入力$2/出力$10、astra 入力$10/出力$50 per 1M tokens)。処理時間=呼び出し所要秒(wall、実測)。
- 有用/誤検知の最終確定はしない(ユーザー判断)。モデル優劣は書かない。

## 6. 既知例チェックリスト(ユーザー列挙7件、全R0の該当文を引用して再発有無を記録)
1. Disney+: 改定理由が明示されていないという台帳外断定 / 2. Disney+: Reutersのコメント要請・Disneyの回答状況という台帳外情報 / 3. 宇宙兵器: 能力が秘密・非公表という台帳外断定 / 4. 宇宙兵器: 1衛星→satellites複数化 / 5. BYD: 2件公告合計183,211台→1件公告化 / 6. BYD: 数字・対象範囲の取り違え / 7(補): 新規逸脱(上記以外)も同様に記録。1〜6はFlagger出力に依存せず、R0本文とFactとの機械的・目視照合(Sonnet、未確定ラベル)でも確認する。

## 7. 費用見積(見積。実測ではない)と上限
- 入力: R0 Prompt 2211〜2642字(日本語混在、約1.8k〜2.0k tokens。E2E Luna実測 input 1667〜1958 tokens)。出力: E2E Luna R0実測の最大 6,070 tokens(byd_recall、reasoning含む)×1.3 = 7,891 tokens を各モデルの上限見積とする(Sol/Astraのreasoning量はLunaと違い得るため不確実性あり)。
- R0(1テーマ3モデル): Luna ¥0.7 + Sol ¥13.3 + Astra ¥66.3 = ¥80.3、3テーマ ¥240.9。Astra単価の出典: pricing_snapshot.json(OFFICIAL_PRICING_PAGE_FETCHED、取得2026-10-08、既存E2Eの請求照合は未実施、ガード係数x1.5は不要としてここでは実見積)。
- Risk Flagger(D2のみ課金、gpt-6.1-sol): 既存実測 d2rank記事モード38呼び出し平均¥2.43・最大¥3.79・最大入力8,759 tokens・最大出力749 tokens。d2は出力Flag数が増え得るため1記事 ¥6を上限見積: 9本 ¥54(D0は¥0)。
- 合計見積 ≈ ¥295。ユーザー事前承認の上限¥500以内 → Phase 2実行可。**実行中停止ライン: 累計(R0実費+Flagger実費)が見積×1.2=¥354 または ¥500 に達したら新規呼び出しを停止して報告**(走行中のprocessは完走)。
- 事前承認(¥500以内)を超えるため以下で停止: 見積が¥500超になった場合/Prompt・Fact Lock・Flagger仕様変更が必要になった場合/対象テーマ追加/Production code変更が必要になった場合。

## 8. STOP条件(ユーザー指示)
Prompt変更必要/Fact Lock仕様変更必要/Risk Flagger仕様変更必要/対象3テーマを増やしたくなった/500円超見込み/Productionコード変更必要/新しいProduction仕様を入れたくなった。Trial終了時分類: REJECTED/VALIDATED/USER_DECISION_REQUIRED(Sonnet提案、Fable確定)。

## 9. 環境
実行python: `.venv/Scripts/python.exe`(Python 3.14.6、openai 2.45.0)。driver: `r0_trial_driver_01.py`(sha256 は RUN_LOG_01.md に実行前後で記録)。repo HEAD(実行前)=ec2c128acaf58fc48838869a547df4291ff59bdc。使用ライブラリsha: er019_family_x_ja_writer_o_r1_r2_01.py `b3b5b9ff...b28e6` / er052_factlock_writer_trial_01_run.py `6a04e22d...2a55` / er052_factlock_astra_e2e_runner_01.py `d556a65d...e8` / pricing_snapshot.json `0f2c3dcb...fd29`。
