# RESULT_PACKET: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING

## 1. 判定

「B1B」は**両方**: (a) 内部compatibility identifier(ディレクトリ名・dict
key・CLI引数・定数名・article_id・cost集計keyとしてer003/er005/er006/
er007/er014の数十ファイルに埋め込み済み、renameは今回不要)、(b)
historical naming(2026-08-17 ER-003-B1-B2-SCOPE-FIX-01で確定した
「B1-A方式[旧2段階、廃止]」対「B1-B方式[Direct Generation、正式採用]」
比較Trialの名残。B1-A廃止後はユーザー向けに区別する意味がない)。
根拠行: `CURRENT_SPEC.md` 604-605行・844行。
既存SSOTルール`docs/pm/PM_GOVERNANCE.md` 9-9節(2026-09-13、ユーザー指示)
が既にこの方針(ユーザー向け=B1、内部識別子は変更不要)を確定済みであり、
今回は新方針ではなく9-9節の未適用箇所の洗い出し+Trend player分の実装。

## 2. 分類表要約

(a)コード内部(変更しない): `b1b/`ディレクトリ、`LEVELS["b1b"]`、
`--level b1b`、`B1B_*`定数、`B1_B_DIRECT_INSTRUCTION`等。
(b)表示文字列(B1へ統一対象): player title/h1/h2、REPORT地の文、
index.htmlセル。
(c)歴史的説明記述(そのまま残す): `CURRENT_SPEC.md`604-605/844行。
詳細は`docs/pm/b1b_naming_investigation.md`参照。

## 3. Trend player表示更新結果

`er014_output/four_type_observation_01/trend/build_player_b1_label.py`
(新規)で`trend/audio/b1b/player.html`の表示文字列のみ更新(音声・segment・
内部パス無変更)。`B1-B`出現4→0、`B1B`出現0、`(internal id: b1b)`注記1箇所
追加。確認コマンド結果: `B1B`検索=0件(想定通り)。`file:///|C:\\`検索=1件
ヒットしたが、これは修正前から存在する説明文の地の文
(「リンクは全て相対パス参照(file:///・絶対パス不使用)。」)であり実際の
href/src属性ではない(本タスクで新規発生した問題ではない)。

## 4. 置換箇所一覧・命名ルール文案

`docs/pm/b1b_naming_investigation.md` 4節に行番号付きで一覧化
(`USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`Trend section6箇所、
`EDITORIAL-4TYPE-FOLLOWUP-02_REPORT.md`Trend section5箇所、`index.html`
1箇所、`CURRENT_SPEC.md`5箇所[参考、Trend E2E完走記録])。Discovery関連の
同種箇所は対象外(Discoveryタスクの担当)として明示的に除外。命名ルール
文案は同ファイル4.5節(既存9-9節への追記提案、新ルールではなく具体例の
追加)。

## 5. commit対象候補

- `er014_output/four_type_observation_01/trend/build_player_b1_label.py`(新規script)
- `er014_output/four_type_observation_01/trend/audio/b1b/player.html`(表示更新)
- `docs/pm/b1b_naming_investigation.md`(新規、調査結果)
- `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING.md`(新規)
- `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING_check.json`(新規)

## 6. T-0・事前指定外Read・STOP有無

T-0: PASS(reasons無し)。`docs/pm/delegation_log/
USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING_check.json`。
事前指定外Read: `docs/pm/PM_GOVERNANCE.md` 9-9節(理由: `PM_BRIEF.md`
40-41行が9-9節を参照していたため、既存の正式ルールと矛盾しないか確認する
目的で1箇所追加Read。判定の根拠として重要だったため実施)。STOP: なし。
API呼び出し・Git操作は本タスクでは未実施(禁止事項どおり)。
