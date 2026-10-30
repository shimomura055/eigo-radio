# KP-DIFFICULTY-4LEVEL-DISPLAY-01 EVIDENCE_02(委任_02、2026-10-30)

生データ=`kpd02_out/`(本dir)。実費=約3.94円(Cap 5円固定・未超過)。

## 1. フォーム表示(§4.4)

- 実装(小差分): `user_test/selection_form_v3/form_logic.js` に `DIFF_LABEL`/`difficultyOf(it)`(表示専用。選択・LIMITS・doneSig・makeCode/buildReadable・batchCodeは不参照)、`index.html` の `groupHtml` で用語`<label>`直後にバッジ(`<span class="diff diff-{level}" data-diff>｜易|中|難|激難(レア)|未判定</span>`)+CSS5色。1行を増やさない(用語行末尾の1要素)。単体・一括は同じ`render()`/`groupHtml`を通る。
- 表示規則: entry.difficultyが無い旧data・source=not_graded(旧docの再export)=バッジなし(従来と同一)。判定不能(level=unknown/定義外)=灰色「未判定」(欠落を隠さない・選択は妨げない)。
- node test: `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/selection_form_logic_test_01.js` 70→73件ALL PASS(新3件: difficultyOf表示規則/署名・照合コード・readable・counts・allowed・LIMITS不変[difficulty付与前後で`doneSig`・`buildReadable`(AIF1コード含む)がバイト同一、コピー本文に難易度文字なし]/rare候補でも選択可)。
- Playwright(`kpd02_verify_display_01.py`、`kpd02_verify_display_result.json`、`kpd02_shots/kpd02_{batch,single}_{pc,mobile}.png`): 27 checks ALL PASS。PC/mobile x 単体/一括: 全候補行にバッジ1個(9/9)、5種類すべて表示、横スクロールなし、選択3件+Done成功、セット切替後もバッジ維持、JSエラー0、コピー本文に難易度なし(AIF1あり)、旧data/not_gradedはバッジ0・行は従来表示、実リポジトリdata(不変)バッジ0。fixtureは一時dirに生成しroute差替え(本番data不変)。
- 02A回帰: `sub02a_verify.py` 70/70 ALL PASS(バッジ追加後)。

## 2. 精度検証(実LLM、`kpd02_accuracy_01.py`/`kpd02_compare_01.py`、出力 kpd02_out/kpd02_llm_results.json・kpd02_compare_result.json)

- 対象: 既存run(kp75_ev_01)の保存済み`kp_candidates.json` 6セット55候補=X(ai_island_temple a2/b1b)・Y(redelivery_fee)・Z(melos) x Std/Adv(docは書き換えず)。
- モデル: (1)gpt-6-luna(本番と同じ`er119_kp_difficulty_01.grade`、routing=SUPPORT_MODEL、最新世代)、(2)別系列 gemini-3.8-flash(同一Prompt/schema、thinking_budget=0、最新Flash系)、(3)Sonnet 5.5実読(LLM結果を見る前に確定=`kpd02_sonnet_labels.json`、blind)。
- 結果(n=55): luna-Sonnet 一致17/隣接37/2段階以上1、gemini-Sonnet 24/31/0、luna-gemini 36/18/1。3者すべて隣接以内=53/55、3者完全一致12/55。2段階以上乖離: `pull someone under`(Z-b1b: Sonnet=難/luna=易/gemini=中)、`obey`(Z-b1b: Sonnet=中/luna=易/gemini=難。lunaとgeminiで2段階差)。目標(2段階乖離0〜1件/60件)=Sonnet基準で1件=充足。
- 分布: Sonnet 易3/中37/難15、luna 易25/中30/難0/激難0、gemini 易19/中34/難2。**lunaは55件で難・激難を1件も出さない(下方バイアス)**=隣接許容内だが、難/激難のバッジが実際にはほぼ出ない可能性がある(下記は改善候補)。候補が元々「平易でも学習価値のある表現」を含み、激難が出ないのは候補の性質上ありうる。
- 同一表現のStd/Adv差: 7表現中6が同一、`obstacle`(Std=中/Adv=易)と`pull someone under`(Std=中/Adv=易)が1段階差=許容内。
- ユーザー表示例(Promptに入れていない。実例文付き3項目、a2/b1b): luna rely on=易/易(期待=易、一致)、make room for=易/易(期待=中、隣接)、narrow down=中/中(期待=難、隣接)。gemini=易/易、中/中、中/中。例は「実判定を指定するものではない」(原文§4.4)、隣接段階差は許容、全例隣接以内。lunaの理由文例: narrow down=「候補を絞る比喩的な用法に慣れが要る」。
- 費用: luna 55候補+例6=8 call 約0.45円(0.056円/セット)、gemini 2.89円。本番の追加単価=lunaのみ=約0.11円/記事セット(Std+Adv各1 call)=70円の約0.16%(DESIGN_01見込み0.2〜0.6円より低い)。既存工程の置換による相殺はなし(別責務)。
- 改善候補の事前評価(採用していない・本番Prompt不変): Prompt較正案v2(rule5「迷ったら極端を避ける」→「易=中学〜高校初級の基本語に限る/それ以外の句動詞・比喩・文語は原則中以上/全部同じ段階にしない」、rule4例の追加、評価対象表現・ユーザー例は不含)をluna単独で同55件に適用(`kpd02_variant_luna_01.py`、約0.51円): Sonnet一致27/隣接28/2段階以上0、分布 易13/中39/難3/激難0、Std/Adv差は`pull someone under`解消。ただしユーザー例のrely on(a2)=中へ動くなど不安定性もあり、同一データでの調整(過適合の可能性)・単一ラベラーのため、Cap残も少なく本番採用せず記録のみ(v1は受入基準を満たすため必要十分で停止=Charter 1)。

## 3. 配線証跡

- 共通経路の根拠: X=`er019_family_x_audio_production_runner_01.py:997`、Z=`er026_family_z_fiction_production_runner_01.py:2218`、Y=`er121_family_y_runner_01.py:583`が全て`er119_kp_wiring_01.run_kp_with_review`(:60)→`kcand.make_generate_fn`→`er119_kp_candidates_01._generate_candidates_impl`(最終段 :501-505、`difficulty_grading`:515)。level=a2→process A2_SUPPORT/b1b→B1_SUPPORT(`er119_kp_wiring_01.py:70`)。Std/Advとも同一関数。
- 実run相当の統合(`kpd02_wiring_real_01.py`、`kpd02_wiring_real_result.json`): 本番の生成経路(make_generate_fn→ensure_kp_review→_generate_candidates_impl)を通し、難易度callだけ実LLM、他段(P7/W5'/canon/gloss/QA)はtest mock(Env)。a2・b1b各1 call: `difficulty_grading`={version=kp_difficulty_v1, prompt_sha256=3d9c3c83…fff, model_id=gpt-6-luna, status=OK, n_graded=8/8, response_id=resp_0c53fae8…/resp_0446049e…}、cost logger(`er005_cost_logger`, `kpd02_wiring_cost_logger_raw.jsonl`)に provider=openai/model_id=gpt-6-luna/input 1092/output 399・390/success を記録。`export_form_data_01.convert`で全候補(8/8)のentry.difficultyに透過、公開フォームの`form_logic.js`(`validateArticle`=[]・`difficultyOf`)が同じdataを表示判定して一致。mock難易度だけを外したため、P7/W5'の実選定callは含まない(実記事の完全runは追加費用が¥5 Capを超えるため未実施。新規記事の正式run時に自動で付与される)。
- fail-open(失敗経路): test isolation下で難易度API遮断時、doc=status FAILED_OPEN・n_unknown=8・候補8件全て残存・全件「未判定」(初回の実行で偶発的に確認、`er119_kp_difficulty_test_01.test_failure_is_fail_open…`でも固定)。旧doc=export時 unknown/not_graded→フォームはバッジなし(従来どおり、候補は減らない)。
- resume: `test_resume_does_not_regrade_and_keeps_saved_values`(保存済みdocの難易度を維持し再課金しない)。retry/補完/再選定: `BackfillDifficultyTest`ほか(最終集合確定位置1か所のため全経路を覆う)。
- 公開URL: 公開済みdata(`user_test/selection_form_v3/data/*.json`)は難易度field無し(grep=0)=本番では**新規記事が出るまでバッジは表示されない(従来表示)**。公開フォーム自体(JS/HTML)はpush後に反映(Pagesのcache遅延あり)。live確認はFable(push後、本ファイル末尾の結果欄)。

## 4. §7 12項目の判定

| # | 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | 正式初回Production経路 | 充足 | 上記3の共通経路、既定ON(flagなし)・承認済み |
| 2 | X/Y/Z x Std/Adv適用 | 部分(静的+統合) | 3 family呼出箇所file:line、a2/b1b実判定。**Family別の実記事Production runでの難易度付与は新規記事待ち** |
| 3 | 正式runtimeでの表示・判定証拠 | 部分 | 実LLM+本番生成経路+cost logger+export+フォームJS+Playwright表示。**公開フォームに実記事のバッジが出る実証は新規記事待ち**(既公開dataは旧doc) |
| 4 | Regression/Validator/Integration test | 充足 | er119_kp_difficulty_test_01 27 OK、backfill 66 OK、node 73 PASS、Playwright 27+sub02a 70 PASS |
| 5 | retry/fallback/regen/resume整合 | 充足 | 上記3 |
| 6 | DEV/Trial専用でない | 充足 | 正式生成経路の既定動作 |
| 7 | actual model_id/Prompt/routing | 充足 | response.model=gpt-6-luna、prompt sha、routing=SUPPORT_MODEL、cost logger |
| 8 | SSOT更新 | 充足 | OPEN-622・DECISION_LOG・CURRENT_SPEC |
| 9 | Dangling Reference | 充足(要Fable確認) | 追加のみ・撤去なし。新規参照先(`difficultyOf`/`DIFF_LABEL`)はtest・index.htmlから解決 |
| 10 | Git反映 | 充足(push後) | origin/main |
| 11 | Fable独立受入 | 未(Fable) | |
| 12 | 承認仕様と実動作の一致 | 条件付き | 4段階表示・Gateでない・候補削減なし・現行Production方式で動作=一致。lunaの下方バイアスは隣接許容内(2段階乖離1/55) |
