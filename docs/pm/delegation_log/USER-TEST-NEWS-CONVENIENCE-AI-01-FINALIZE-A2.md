## 管理ID

`USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2`。報告は`docs/pm/RESULT_PACKET_NEWS_CONVENIENCE_AI_01.md`を累積更新(末尾に「## FINALIZE-A2」節を追加、最終★ブロックが累積Full Report)。一時ファイル`docs/pm/ACTIVE_TASK_NEWS_CONVENIENCE_AI_01.md`継続。現在main=origin/main=`ed60b03c`(要fetch確認)。**並行Agentなし。** `docs/pm/locks/audio_stage.lock`を原子的作成(`open(path,"x")`)で取得し終了時に削除(音声処理はASR再検証のみ、TTS再生成なし)。`er005_cost_logger.install()`を最初に呼ぶ。

## ユーザー正式判断(2026-09-17、そのまま実行)

コンビニAI A2 `point_two`新候補(FIX-02で確認ページ提示したattempt9由来の音声)をユーザー試聴: **`Oimo no` = OK/承認**。よって`Oimo no Canele`=USER APPROVED、`AI while`=USER APPROVED。**追加TTS再生成不要。** B1は前回承認済み(語順script整合修正完了)、追加試聴要求なし。

## 実施内容(A2)

1. **Human Approval記録**: 確認ページ(`a2/human_review/point_two.mp3`/`point_two_review.json`)で提示した音声と同一のwav(attempt9由来、sha256照合。不一致ならSTOP)を、既存正式手順`er003_v1_n3_01_assemble.record_human_approval()`(Tiny Bags A2 CLOSEOUT-03/Space Weapons B1と同一)で`audit/human_approved_segments.json`へ記録。approver=user、根拠=FIX-02確認ページURL(SHA `187d51b4`)、管理ID。`review_lock_state.json`は先例どおり`human_approval_reference`追記(state文言は既存Gate設計に従う)。
2. **A2既定slowdown正式適用**: 承認済み音声へ既存Production関数`apply_a2_slowdown_postprocess()`を適用(Tiny Bags A2 CLOSEOUT-03の`a2_full_story_part2_slowdown_apply_01.py`と同型、TTS新規生成なし)。post-slowdown状態を必要手順どおり確認(内蔵Primary ASR再検証の結果を記録。固有名詞表記ゆれで再検証がPASSしない場合は、Human Approvalが既にGate参照優先フィールドを満たすため、Gateが`HUMAN_APPROVED`として通過することを確認。追加でLedger Phrase List付きSecondary ASRを1回実行し、slowdown後音声でも"Oimo no Canele"/"AI while"が転写上維持されていることを証跡化)。duration比・peakを記録。FIX-02で確認ページに提示した音声が既にslowdown適用済み(duration 21.67s、6%適用後)であるかを先に確認し、二重適用を避ける(適用済みならその音声をfinalとして採用し、Gateの`MISSING_MANDATORY_A2_SLOWDOWN`判定が出ないことを確認)。
3. Assembly(`er003_v1_n3_01_assemble`、Audio Validation Gate、override禁止)→PASS必須。
4. `build_web_player_common.py`でplayer.html(記事dir root、web/episode.mp3+segments+manifest)。
5. `user_test/unified.html?src=er014_output/user_test_news_convenience_ai_01/convenience_ai/a2/player.html&level=A2&en=<A2タイトル "Pickles in a Lemon Tart? When AI Joins the Convenience-Store Kitchen" URLエンコード>&ja=<「日本のコンビニ、AIで新しい味を開発」URLエンコード>`(rawcdn.githack、commit/push後SHA)。
6. Playwright headless Chromium E2E(page load/Play開始/currentTime進行≥2秒/audio errorなし/script表示[point_twoの新canonical文言"is scheduled to go on sale"と"Oimo no Canele"を含む]/60秒seek/Key Phrase・Comment box表示)、evidence JSON+screenshot保存(`docs/pm/closeout_136_e2e/convenience_ai_a2_finalize.json`+`.png`)。
7. B1: `b1b/parts.json`/`article.md`/player scriptが"Then Lawson planned a sale of the finished product."で整合していること、B1 player URL(SHA `187d51b4`)が有効(HTTP 200+既存E2E evidence `b1b/human_review/e2e_evidence_fix02.json`参照)であることを確認のみ(再試聴要求なし、再build不要)。

## Status/SSOT

- コンビニAI A2/B1 = **`USER_TEST_READY`**としてcloseout(記事品質のユーザー判断待ちなし)。
- `DECISION_LOG.md`: `## USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2`(索引+本体): Oimo=USER APPROVED、point_two final採用(attempt/sha256)、slowdown適用結果、Assembly/Gate、E2E、A2/B1 USER_TEST_READY、Sheet行確定。
- `OPEN_ITEMS.md`: post-slowdown再検証経路(`apply_a2_slowdown_postprocess`の内蔵再検証がPhrase List付きcascadeを使わず固有名詞で誤ブロック)を**独立Open Item(次番号、OPEN-168想定)として登録**(問題/実例[Tiny Bags A2 full_story_part2・コンビニAI A2 point_two]/Status=`OPEN / DEFERRED`/期限=量産前/Blocking対象なし/候補対応[post-slowdown再検証へLedger Phrase List付きSecondary ASR cascadeを配線、CURRENT_SPEC L1286の既知ギャップ]、今回はProduction変更なし)。OPEN-159の該当観測にOPEN-168への参照を追記。
- `ARTIFACT_REGISTRY.md`: コンビニAI A2/B1行をUSER_TEST_READY(ユーザーPASS)+最終URL+E2E evidenceパスへ更新。
- Sheet投入用行を確定(記事タイトル(English)=A2代表/日本語タイトル/概要/Family=News/ノーマル(A2) URL/Advanced(B1) URL/備考=最新ニュース)。専用記事一覧ファイルは存在しない(CLOSEOUT-03で確認済み)ためARTIFACT_REGISTRYのみ。
- `CURRENT_SPEC.md`: 変更不要(確認のみ、無変更証跡)。
- Git: 明示add、`git add -A`禁止、wav禁止、mp3可、fetch→merge、trailer `Task-ID: USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2`。

## STOP条件
承認対象wavと確認ページ音声のsha256不一致/Gate不通過/E2E失敗/git conflict/費用¥30超(ASR数回のみ想定)。承認代行禁止(ユーザー承認は上記のとおり明示済み)。

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。事前指定Read: 本RESULT_PACKET(FIX-02節)、`fix_02_pipeline.py`、`audit_fix_02/*.json`、`docs/pm/RESULT_PACKET_NEWS_LIGHT_03.md`(Human Approval+slowdown先例)、`er014_output/user_test_news_light_01/tiny_bags/audio_fix/a2_full_story_part2_slowdown_apply_01.py`、`er003_v1_n3_01_assemble.py`(record_human_approval/_segment_gate_status)、`docs/pm/closeout_136_e2e/`、OPEN_ITEMS OPEN-159行+末尾採番。事前指定外Readは理由付き報告。

## 報告項目(「FINALIZE-A2」節、★ブロック内)
H1.A2 Oimo=USER APPROVED(記録箇所) H2.point_two final採用(attempt/sha256/確認ページ音声との一致) H3.slowdown適用結果(二重適用回避の確認、duration比、内蔵再検証結果、追加Secondary ASR結果) H4.Assembly/Gate(duration/peak/clipping、Gate判定) H5.Browser E2E evidence H6.A2 final player URL H7.B1 script/audio整合確認(再試聴なし) H8.A2/B1 USER_TEST_READY H9.Sheet行確定 H10.SSOT(DECISION_LOG/OPEN_ITEMS[OPEN-168]/ARTIFACT_REGISTRY/CURRENT_SPEC無変更)/Git SHA H11.未処理USER_DECISION_REQUIRED有無 H12.cost H13.ユーザー判断 A/B(想定: いずれも「なし」) H14.無変更証跡/lock記録/事前指定外Read。
