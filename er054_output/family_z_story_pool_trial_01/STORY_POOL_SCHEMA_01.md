# STORY_POOL_SCHEMA_01(Phase E: Story Pool一覧 schema設計。Trial専用、到達上限VALIDATED)

目的: Family Z(Literature)の候補作品を、権利・品質・多様性・推奨順位・選定状態つきで一覧管理する。
本Trialでは**空の雛形のみ**(`pool/story_pool_template_01.json`)。値の充填はPhase C/D後。Production(er026等)は参照しない。

## 1. 並列書込みの避け方
- 作品別エントリファイル `pool/entries/<ID>.json`(1作品=1ファイル、作品別処理は各自のファイルだけを書く)。
- 一覧 `pool/story_pool.json` は、全エントリを読んで決定論で結合する最終工程(単独・直列)だけが生成する。
- 順位(`recommendation.rank`)は結合工程でのみ付与(作品別処理は書かない)。

## 2. エントリschema(`entry`)
| フィールド | 型 | 内容 / 出所 |
|---|---|---|
| work_id | string | L01〜(固定ID) |
| title_ja / title_en | string | 作品名 |
| author | {name, birth_year, death_year} | `screening/<ID>.json` |
| genre | string | 例: 近代日本文学(短編) |
| source | {card_url, text_url, text_sha256_raw, text_sha256_plain, text_plain_chars, fetched_at, saved_dir} | `screening/<ID>.json`の`primary_source` |
| rights | {decision: PASS/REVIEW_REQUIRED/NG, reason, blocking_unconfirmed[], informational_unconfirmed[], us_status_record_only, translation_status, rights_checked_at (権利確認時点), rule_version} | `screening/<ID>.json`。米国statusは記録のみ(Z-1) |
| quality | {A,B,C,D: {verdict, evidence_quotes[], reason, confidence}, pass_count, overall: PASS/FAIL/REVIEW_REQUIRED, rule, model, eval_version, evaluated_at, quote_verified} | `phase_c_eval/<model>/<ID>.json`。複数モデル時は`quality_by_model{}`で保持 |
| appeal | string | 魅力(英語化時に残すべきもの) |
| compression_risk | {level: low/medium/high, notes, cut_candidates[]} | 短編化リスク |
| diversity | {theme, mood, era, region, narrator} | 多様性属性(テーマ・雰囲気・時代・地域・語り手)。pool全体の偏り確認に使う |
| recommendation | {rank: int/null, reason: string, tie_break: string} | 結合工程のみ。基準案=権利PASS→品質overall PASS→D適性→多様性(同属性の偏り回避)。基準はPhase Dでユーザー承認 |
| selection_state | enum: 未選定 / 採用決定 / 保留 / 不採用 | 初期値=未選定。**採用決定はユーザーのみ**(Trial内で自動付与しない) |
| next_step_conditions | string[] | 次工程(Seed化・英語Story生成)へ進む条件。例: 権利REVIEW_REQUIREDの解消、ユーザーのテーマ選定承認(PM_GOVERNANCE 13節) |
| generation_links | {seed_id, story_id, article_id, ...} | 生成履歴との紐付けID。本Trialでは全てnull(生成しない) |
| provenance | {screening_script, quality_driver, pool_schema_version, built_at} | 再現性 |

## 3. 制約
- `selection_state`は`採用決定`を自動で付けない。Status上限`VALIDATED`、Production採用はユーザーのみ。
- 権利`NG`は`recommendation.rank=null`・`selection_state=不採用`推奨(ユーザー承認後に確定)。`REVIEW_REQUIRED`は`保留`推奨。
- 作品固定10本(L01〜L10)。追加・差し替えは別管理ID。

## 4. 雛形
`pool/story_pool_template_01.json`(10エントリ、値はnull/空)と`pool/entries/`(空dir、`.gitkeep`なし。Phase C/D実行時に作成)。
