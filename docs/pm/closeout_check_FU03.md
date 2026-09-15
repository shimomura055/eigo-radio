# PM Closeout必須確認(ユーザー指定10項目) — FU-03(PM-CLOSEOUT-CONSOLIDATION-135)

作成: 2026-09-15、Sonnet委任(Git記録・Web到達確認・SSOT反映・最終REPORT作成担当)。

## (1) Discovery A2旧604語版が最新候補として残っていないか

**✓ OK**。旧604語版は`er014_output/four_type_observation_01/discovery/
a2_before_regeneration_604w/`へ退避(履歴保持、削除せず)。現行
`discovery/a2/article.md`・`reader_facing_article.txt`は530語版。
`index.html`は本タスク(f)で「旧版・不採用」表記へ更新し、530語版のみを
最新候補として提示する(下記(6)関連の更新と同時実施)。
`USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03_REPORT.md`(本タスク作成)
でも604語版playerは掲載しない方針を明記。

## (2) Family C Comment 4が新規B1に混入していないか

**✓ OK**。`home_robots_b1/segments.json`・`home_robots_b1/player.html`を
Grep(`comment_4|Comment 4|comment4`)した結果、いずれも**0件**
(実測コマンド結果、本タスクで確認済み)。B1は最初からComment 1〜3構成
(`COMMENT_NUMBERS=(1,2,3)`)で生成されている。

## (3) Family C Comment 3修正済みか(A2 v2・B1両方)

**✓ OK**。A2 v2: `docs/pm/RESULT_PACKET_FU03_FAMILYC_A2.md`2節、
ユーザー原文をそのまま採用、ASR一致・player表示一致確認済み。B1:
`docs/pm/RESULT_PACKET_FU03_FAMILYC_B1_2.md`2節(CONT1)、主語
「ロボットが」「マヤは」明示版、ASR一致・player表示一致確認済み、
テスト1件追加(`test_comment3_fixed_text_override_states_explicit_
subjects`)。

## (4) Discovery B1 Human Review playerが分かりやすいか

**✓ OK**。`er014_output/four_type_observation_01/discovery/audio/b1b/
human_review_player.html`をGrepした結果、5要素すべて存在を確認
(実測): canonical=7件、ASR=7件、diff=35件、seek=7件、attempt=26件。
canonical script・各attemptのASR transcript・差分ハイライト・推定seek
位置・個別mp3再生(attempt切替)の5要素が揃っている
(`docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`A節参照)。

## (5) Voices Previewが「個別例外」と記録され正式前例化していないか

**✓ OK**。`OPEN_ITEMS.md` OPEN-151追記・OPEN-154登録行・`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-135`エントリのいずれにも「**当該記事1件限りの
個別例外**」「**将来の新規記事・再生成の前例にはしない**」の文言を明記。
OPEN-151のStatus欄は`PARTIAL / USER TEST READY`のまま変更していない
(`PRODUCTION_WIRED`は宣言していない)。

## (6) Trend B1表示がB1へ整理されたか(player・REPORT・index.html・CURRENT_SPEC)

**△ 一部完了、index.htmlは本タスク(f)で対応**。player:
`trend/audio/b1b/player.html`は`build_player_b1_label.py`で表示文字列
4箇所を「B1」へ更新済み(commit `60e274d7`)。CURRENT_SPEC:
「B1(独立生成Natural Spoken News English)」節に命名ルール1段落を追加
(既存定義行・604-605/844行の歴史的記述は変更しない)。REPORT:
`USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03_REPORT.md`(本タスク作成)
で「B1」表記を使用。index.html: 本タスク(f)で「B1B¥69.54」等の残存表記
を「B1¥69.54」へ更新(下記index.html更新記録参照)。過去REPORT
(`USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`・
`EDITORIAL-4TYPE-FOLLOWUP-02_REPORT.md`)本文中の「B1B」表記は**過去の
確定REPORTであり本タスクでは書き換えない**(履歴改変を避けるため、
置換候補一覧は`docs/pm/b1b_naming_investigation.md`4.1/4.2節に記録済み、
必要ならユーザー判断で別タスクとして実施)。

## (7) OPEN-154/155登録済みか

**✓ OK**。`OPEN_ITEMS.md` 298行目(OPEN-154)・299行目(OPEN-155)に新規
登録済み(Status: `USER_DECISION_REQUIRED`)。

## (8) 280語以下/500語以上報告ルールが正式記録されたか

**✓ OK**。`docs/pm/PM_GOVERNANCE.md` 9-11節「A2記事の語数報告義務」に
恒久ルールとして追記(hard gateではなく報告義務である旨を明記)。
`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-135`エントリ(6)にも記録。

## (9) ユーザー承認事項の反映先一覧

| ユーザー承認事項 | 反映先 |
|---|---|
| Comment 4なし(Family C恒久) | `home_robots_v2/spec/episode_spec_v2.md`、`DECISION_LOG.md`本エントリ(2) |
| Comment位置決定原則 | `home_robots_v2/spec/episode_spec_v2.md`、`DECISION_LOG.md`本エントリ(2) |
| Word-count報告ルール(280語以下/500語以上) | `docs/pm/PM_GOVERNANCE.md`9-11節、`DECISION_LOG.md`本エントリ(6) |
| Voices Preview個別例外 | `OPEN_ITEMS.md`OPEN-151追記・OPEN-154登録行、`DECISION_LOG.md`本エントリ(4) |
| B1命名ルール(ユーザー向け=B1、内部id=b1b) | `CURRENT_SPEC.md`B1節命名ルール段落、`DECISION_LOG.md`本エントリ(3) |
| OPEN-154/155登録 | `OPEN_ITEMS.md`298-299行 |
| Discovery A2 604語版不採用→530語版採用(≥500語flag) | `OPEN_ITEMS.md`OPEN-135追記、`discovery/a2_before_regeneration_604w/`、`DECISION_LOG.md`本エントリ(1) |
| Discovery B1人間承認方式(Human Review player) | `OPEN_ITEMS.md`OPEN-153追記、`discovery/audio/b1b/human_review_player.html`、`DECISION_LOG.md`本エントリ(1) |
| OPEN-153維持(標準=Gemini 2.5 Flash TTS、3.1は将来retry候補) | `OPEN_ITEMS.md`OPEN-153(内容変更なし、追記のみ) |

いずれも上記のいずれかのSSOTファイルに反映済みであることを確認した
(本タスクで新規に落ちていた項目は発見していない)。

## (10) APPROVED_FOR_PRODUCTION未配線項目が残っていないか

`OPEN_ITEMS.md`を`Grep APPROVED_FOR_PRODUCTION`した結果、26箇所ヒット
(24件の異なるOPEN項目本文中の言及、うち大半は「その決定のみ
APPROVED_FOR_PRODUCTION」という部分承認の記述で、後続の追記により
`PRODUCTION_WIRED`または`PARTIAL`等へ状態が進んでいる)。本タスクで
Read範囲を「該当行の先頭200字」に限定したため(委任文Read一覧どおり)、
全24件の現在の正式Status欄を1件ずつフル確認してはいない。判明している
範囲での分類:

| OPEN項目 | 現在のStatus(本タスクで確認できた範囲) | 未配線か |
|---|---|---|
| OPEN-151(Voices 2/3 Voices可変Writer) | `PARTIAL / USER TEST READY`(明示的にPRODUCTION_WIREDではないと複数回記録) | 未配線のまま継続(Analytical Leakage残存のため、既知・追跡中) |
| OPEN-122(Connected Speech Equivalence Layer) | 範囲限定で`APPROVED_FOR_PRODUCTION`(2026-09-07) | 本タスクでは配線状況フル確認せず(スコープ外、200字snippetのみ) |
| OPEN-123(Transcript Style Normalization) | 範囲限定で`APPROVED_FOR_PRODUCTION`(2026-09-07) | 同上 |
| OPEN-117(Key Phrase表示/TTS gloss分離) | `APPROVED_FOR_PRODUCTION`(2026-09-06) | 同上 |
| OPEN-119(Key Phrase EN ASR False Rejection Cascade対策(c)) | `APPROVED_FOR_PRODUCTION`(2026-09-06) | 同上 |
| OPEN-116(KP Validator Numeric/Homophone/Gloss規約) | 3判断`APPROVED_FOR_PRODUCTION`(2026-09-06) | 同上 |
| その他(OPEN-83/95/112/113/115/118/120/121/125/127/128/135/141/142/145/146/147) | 200字snippet中にAPPROVED_FOR_PRODUCTIONの語が部分的に含まれるが、多くは別の決定(サブ項目)や他Open Itemの参照であり、当該行自体の現在Status欄が`APPROVED_FOR_PRODUCTION`のままとは限らない | 本タスクでは個別確認していない(**未確認**、推測で「配線済み」とは書かない) |

**結論**: 本タスクの事前指定Read範囲(該当行の先頭200字)では、
「Status欄が`APPROVED_FOR_PRODUCTION`のまま長期未配線になっている」と
断定できる新規項目は見つからなかった。ただしOPEN-151は明示的に
`PARTIAL`(未完全配線)であることが複数の追記で確認できる、既知の
追跡中項目である。その他約20件は個別のフル行確認をしていないため、
**「未配線が完全にゼロである」とは断定しない**(次回Closeout時に全件
フル確認するタスクを別途起票することを推奨、ただし本タスクでは新規
Gate追加はしない)。
