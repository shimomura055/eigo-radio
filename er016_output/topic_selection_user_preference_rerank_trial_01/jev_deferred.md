# Jev arm: DEFERRED

管理ID: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(修正3回目、2026-09-25ユーザー方針変更)。

## 状態

Jev armは**正式にDEFERRED**。本Trialの3-way比較(Luna/Terra/Sol)はJevと未比較のまま完了した。Jevへの接続・呼び出しは本委任(fix03)では一切行っていない(`JEV_API_KEY`も読んでいない、`--env-file`未使用)。

## 理由(4点)

1. **official TypeSafe Jev access unavailable**: TypeSafe公式Jevは現在新規登録不可であり、公式API accessを取得できない状態にある。
2. **non-official wrapper(`www.jevai.org`)は比較対象に使用しない**: 前回委任(`_fix02.md`)の調査で、`www.jevai.org`はサイト自身が「community for Jev model playbooks...not the official product site」と明記しており公式製品サイトではないことが判明した(`jev_api_notes.md`参照)。ユーザー方針により、非公式サービスをモデル比較のarmとして使用しない。
3. **access取得後、同じ60件・同じTeacher Data・同じ評価条件で追加測定可能**: 将来公式access取得後にJev armを追加する場合、本Trialで固定した以下をそのまま再利用できる: Candidate Pool 60件(`candidate_pool.json`、sha256=`fe39660b643f6081b40c4a9f851407f1fb0dc3aa711c2ebd43a6b137cd856a24`)、Teacher Data 57件(`docs/pm/topic_selection_user_eval_dataset.json`)、Preference Prompt(`prompts/rerank_lts_shared_prompt.json`、developer文・user文・JSON schema)。
4. **現在の3-way結果はJev未比較**: `model_agreement.md`/`predicted_scores_all.md`はLuna/Terra/Solの3モデルのみを対象としており、Jevとの一致率・相関は含まれない。

## 既存Jev関連ファイル(履歴として残す、削除せず)

- `jev_probe.json`(1件probe、成功)
- `jev_probe_batch5.json`(5件probe、成功)
- `jev_api_notes.md`(API仕様調査ノート、公式サイトでない旨の記載を含む)
- `jev_decision_schema.md`(request/response schema記録)
- `stop_reason.json`(前回`_fix02.md`時点の60件抽出429/502 STOP記録)
- スクリプト内`cmd_rerank_jev`/`call_jev`/`jev_score_question`等の実装(`er016_topic_selection_user_preference_rerank_trial_01.py`、削除せず保持。`--step rerank`のルーティングは本委任でarmsにJが含まれる場合、これらを呼ばず即座に`DEFERRED`メッセージで終了するようguardのみ更新した)。

## Production採用判断ではないことの明記

本記録はJev armの実施可否に関する事実整理であり、Luna/Terra/Sol/Jevいずれについても Production採用判断ではない。到達上限は`VALIDATED`(3-way比較部分)であり、モデル採用はユーザー評価取得後にユーザーが判断する。
