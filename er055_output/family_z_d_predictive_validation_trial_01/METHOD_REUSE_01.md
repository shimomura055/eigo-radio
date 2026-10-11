# METHOD_REUSE_01 既存Seed生成→英語Story Writer方式の特定と再利用方針
管理ID: FAMILY-Z-STORY-D-PREDICTIVE-VALIDATION-TRIAL-01 委任_01 (2026-10-11、有料API 0円、Trial限定・Production非参照)

## 1. 既存方式の所在(根拠行)
結論: 「Seed生成→英語Story生成」の既存方式 = `er018_fiction_external_seed_selection_criteria_trial_02.py`(FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02)。
- Seed生成: `call_seed`(L335)、`SEED_DEVELOPER_MESSAGE`(L276)、`SEED_USER_TEMPLATE`(L288)、`SEED_JSON_SCHEMA`(L309、strict、フィールド original_summary / seed_elements(2-6) / discarded_elements / conversion_plan)。reasoning effort=medium、リトライなし。
- 英語Story生成: `STORY_PROMPT_TEMPLATE`(L395、A2、1-2人・最大3人、主人公のみ固有名、Listening-friendliness)、`build_story_prompt`(L438)、`step_story`(L450、effort=high、`e_axis.call_with_retry(max_attempts=2)`=空出力等の同一条件再試行のみ)。定数は`er018_fiction_story_dna_e_axis_redesign_01.py`: `WRITER_DEVELOPER_MESSAGE`(L315)、`COMMON_PRINCIPLES`(L181)、`MAX_CHARACTERS=3`/`WORD_TARGET=350`/`WORD_ACCEPTABLE_RANGE=(280,420)`(L326-328)、`generate_story`(L382)。
- ER-026 runner(`er026_family_z_fiction_production_runner_01.py`)は**Text Writerを持たない**。`import ...trial_02 as trial02`(L65)、`STORY_REGISTRY["melos"].trial_seed_dir`(L182-L190、`er018_output/.../stories/03_japanese_lit_2`)から**Trial-02の成果物(seed.json/story.md)を読み**、`resolve_canonical_text`(L291: 語数280-420・人名ルール・sha256)で採用するのみ。よってFamily ZのSeed→Writer生成の実体はTrial-02。走れメロス run_01の英語本文もTrial-02生成物(385語、`gpt-5.6-luna`、story effort=high、attempts=1)。
- 走れメロスの入力: Trial-02の`SEEDS`(`03_japanese_lit_2`)内の**editor(Sonnet)が自分の言葉で書いた`source_brief`+作品固有`conversion_plan`**(約200語)。**原作全文は入力していない**。
- 他に該当経路なし(`call_seed`等を使うのはTrial-02のみ。er054系は評価Prompt専用、Writerなし)。

## 2. 当時のモデル・現行状況
- Trial-02実使用: `gpt-5.6-luna`(seed/story/actual model_id一致、`raw_usage_log.jsonl`)。Trial-02コードの`MODEL_LUNA=routing.WRITER_MODEL`は2026-10-08以降`gpt-6-luna`(routing冒頭コメント)。**そのまま再実行すると5.6ではなく6-lunaになる**(旧5.6は`require_model_or_override(...,"gpt-5.6-luna",override_reason)`で明示)。
- 単価(pricing_snapshot): gpt-5.6-luna 0.2/0.02/1.2、gpt-6-luna 0.1/0.01/0.5、gpt-6.1-sol 2/0.1/10、gpt-6-astra 10/1/50 ($/1M)。いずれも登録済み。gpt-5.6-lunaは公式現行ページに掲載なし(棚卸し`dev_eval_model_inventory_01.md`: 未確認)。API可用性は有料呼出しなしでは未検証(未実行)。

## 3. 再利用可否と STOP 判定
- Prompt・schema・語数・A2制約・effort・retryは**無変更で再利用可**(driverがTrial-02のASTから逐語抽出、testで差分0を固定)。
- **STOP相当の不整合(要判断・1件)**: 既存方式のSeed入力は「editor作成のsource_brief+作品別conversion_plan」であり、ユーザー指示の「原作本文を入力」と形が異なる。選択肢:
  - (X) brief方式(既存と完全同一): Claude/Sonnetが両作品のbriefを書く。長所=既存と同一。短所=brief作成者の要約・強調が作品間で非対称になり、「同一条件」「D評価に引きずられない」を破る恐れ(作者はDを既知)。
  - (Y) raw方式(推奨、driver既定): `source_brief`スロットの見出し1行のみ差替え(`[Original text -- the full public-domain source text ... Title/Author]`)、本文に原作全文(日本語)を入れる。`conversion_plan`は両作品共通の中立文1つ(作品固有情報なし、Trial-02の作品別planを置換)。他は逐語。逸脱はこの2点のみ(testで`header以外同一`を固定)。
  - 独自変更は行っていない。driverは`--seed-input raw|brief`両対応(briefは`--brief-dir`にID.json)。**どちらで実行するかはFable/ユーザー判断(USER_DECISION_REQUIRED)**。
- 日本語長文入力への非対応は無い(各5,015/2,909字、gpt-6系は十分なcontext)。語数制約の不整合なし。
- 原作との対応確認項目: Seedの`original_summary`と`seed_elements`(中心事件・主要要素)が既存項目。無い項目(主要人物/転換点/結末/余韻)は**事後にPython/Claudeで整理**(Writerへの追加指示なし)。

## 4. モデル案(実行しない・判断待ち)
| 案 | モデル | 最新か(PM_GOVERNANCE 25) | 位置づけ・理由 |
|---|---|---|---|
| M1 既存そのまま | gpt-5.6-luna | 旧世代(例外: 既存方式の再現。ただし比較対象の既存結果は今回なし) | 当時と同一モデル。可用性未検証、現行Production routingとも不一致 |
| M2 現行Production Writer | gpt-6-luna | 最新世代の効率系(最上位ではない) | Trial-02コードを今日そのまま走らせた場合の結果と同一。Production A2_WRITERと同一で「ラインが実際に書く英語」を予測するDの目的に最も近い。最安 |
| M3 推奨系 | gpt-6.1-sol | 最新世代の推奨系 | 25節の原則に最も素直。現行Production Writerではない |
| M4 最上位 | gpt-6-astra | 最新世代の最上位 | 品質上限の確認向け。高額 |
Fable推奨: **M2(gpt-6-luna)+Y(raw)**。理由: ユーザー指示「既存方式を可能な限り再利用」を満たしつつ、(1)Trial-02を現行で走らせた結果と同じ、(2)Production Writerと同一でDの予測対象が一致、(3)費用が約1円。25節の最新原則上は「最上位/推奨系ではない効率系」を使う点を明記(例外種別: ライン組込候補の性能確認=Production Writerそのもの)。M3を併走する案は追加Trial扱いのため委任外(ユーザーが望むなら別途)。

## 5. Blind設計
- driverが読むファイル: `er054_output/family_z_story_pool_trial_01/sources/<ID>/{text_plain.txt,fetch_manifest.json,card.html}`のみ。`SEALED_*`/`PHASE_C_*`/`PHASE_D_*`/`PAST_COMPARISON*`/`SCORE_TABLE*`/`ANALYSIS_01`/`/screening/`/`family_z_story_quality_model_comparison_trial_01`配下/`rights_data*`/`RESULT_01`等はパス判定で`SealedAccessError`(testで5パターン確認)。
- Prompt内に評価語(短編化適性、D=…、extractability等)が無いことを実Prompt全文でtest。Dスコア・作品順位・過去評価はSeed/Writerへ渡さない。
- 『檸檬』を低品質に書く指示・高評価側に有利な調整は無い(両作品でPrompt同一、conversion_planも共通1文)。

## 6. 公平性チェックリスト
| 項目 | 担保 |
|---|---|
| 同一Writer仕様・モデル・effort・retry上限 | 1回のdriver実行内で同一(`--model`1つ、seed=medium/story=high、attempts≤2)。testで固定 |
| 同一Prompt(差分=原作本文+タイトル・著者のみ) | test_same_prompt_except_source_title_author |
| Trial-02と差分0 | test_identical_to_trial02_constants_and_story_prompt、raw見出し以外同一 test |
| 語数範囲外でも再生成しない | run_metaに記録のみ(ユーザー指示: 不必要な再生成禁止) |
| 権利 | 没年(芥川1927・梶井1932)>70年、青空文庫fetch http200。run_meta.rightsに記録(test済み) |
| 実費・上限 | 承認額なしrealは拒否、上限見積>承認額なら拒否、逐次budget_guard(testで確認) |
| 記録 | actual model_id、usage、cost、所要秒、prompt sha256、developer message、response_id |
| 出力 | seed.json/story_en.md/run_meta.json(+監査用seed_prompt.txt/story_prompt.txt)。音声・TTS・Assembly等は無し |

## 7. 残リスク
- rawモードのSeed出力量(reasoning)が既存briefより増える可能性(見積に反映、上限1.5倍)。
- Writerは作品名を知っている可能性(既存方式でも同様)。原作に引きずられた補完が起こり得る(記録・事後確認で把握)。
- 『蜘蛛の糸』の「御釈迦様」「陀多」等の名前規則(主人公のみ固有名)はWriter任せ。語数・人名はdriverで修正しない。
