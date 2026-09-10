# PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-RESTRUCTURE-01

## 目的

`DECISION_LOG.md`(1,334,377バイト/826,259文字≈37.6万token、開発Line最大の
Claude Token発生源)を、`PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01`
(以下T-1)と同方式で、**内容・意味・Status・履歴を一切変えずに**「必要
部分だけ読める構造」へ分割した(ユーザー正式採用、2026-09-11)。要約・
言い換え・削除は行っていない(切り貼りのみ)。

## 1. 構造分布(全文を読まずに機械抽出)

`DECISION_LOG.md`は次の3部構成であることを、見出し行(`^## `)・
`^\*\*最終更新`行・管理ID出現位置・各エントリ文字数の機械抽出で確認した。

| 領域 | 範囲(元の行番号) | 内訳 |
|---|---|---|
| ヘッダー | 1〜200行 | タイトル+管理ID`ER-PM-001`ラベル+「最終更新」チェーン13件(reverse-chronological、うち12件は単一物理行の巨大paragraph[最大36,062文字/行]、最古の1件のみ通常の折返し段落)+末尾の小さな凡例(「区分について」)。ヘッダー全体80,313文字。 |
| 本文 | 201〜11,499行 | `## <管理ID>: <タイトル>`見出し単位の決定エントリ231件(時系列昇順、oldest→newest)。合計745,946文字、中央値2,620文字/件、最大11,777文字/件、最小163文字/件(サイズは正規分布的でなく裾が長い)。 |
| 末尾 | 11,499〜11,502行 | `## 参照元`小節(163文字、ナビゲーションのみ)。 |

直近25件(本文末尾、chronological)は合計90,143文字(全体の10.9%)しかなく、
残り206件(89.1%)が「古い決定の履歴」に相当する。

## 2. 採用した分割方式と理由

**方式**: (a) ヘッダーチェーンは最新1件のみ本体に残し、古い12件を
`DECISION_LOG_HISTORY.md`の`## ER-PM-001_CHAIN`節へ原文のまま移動。
(b) 本文231件のうち直近25件(chronological末尾)を本体にそのまま残し、
古い206件を`DECISION_LOG_HISTORY.md`へ原文のまま(各エントリの元見出し
ごと)移動。(c) 本体に全231件の原文見出しを列挙した「索引」節を新設
(要約なし、既存見出し行の切り貼りのみ、本体内/履歴のいずれかを明記)。

**理由**: `OPEN_ITEMS.md`(T-1)は「行単位のStatus要約+履歴全文」という
構造(現在値としてのStatusが常に更新される)だったのに対し、
`DECISION_LOG.md`は最初から`## <ID>: <タイトル>`見出し単位で意味的に
完結したエントリのtime-ordered append-onlyログであり、要約すべき
「現在値」は存在しない(全エントリが等しく確定済みDecisionの記録)。
そのため新規要約は作らず、「直近だけ本体に残し、古いものは原文のまま
1つの履歴ファイルへ切り出す」方式(T-1のOPEN_ITEMS_HISTORY.mdと同じ
単一ファイル方式)を採用した。月別ファイル分割(候補(a)の別案)は、
多くの古いエントリに明示的な日付欄がなくタイトル内の日付表記も不統一
なため、決定論的な月境界の切り方が一意に定まらずリスクが高いと判断し
見送った。単一履歴ファイルでもGrepでの管理ID検索コストは変わらない
(Grepはマッチ行のみを返すためファイルサイズに比例して高コストには
ならない)。

## 3. 実施(決定論的script、手作業編集なし)

- `er011_decision_log_restructure_01.py`: 上記分割を実施し、
  `er011_output/decision_log_restructure_01/manifest.json`へ全移動範囲
  (元ファイルの行番号)を記録。
- `er011_decision_log_restructure_verify_01.py`: git HEAD(分割前)の
  `DECISION_LOG.md`をmanifestの行範囲から再構成した全文が空白正規化後に
  完全一致すること、分割後の実ファイル(`DECISION_LOG.md`+
  `DECISION_LOG_HISTORY.md`)からも236チャンク(固定5+kept25+moved206)
  全件が原文のまま該当ファイルに含まれること、エントリ数(231件、
  kept25+moved206)が一致すること、管理ID/OPEN番号/日付/URL/ファイル
  パスの出現件数が分割前後で完全一致することを確認。

## 4. 検証結果

`er011_output/decision_log_restructure_01/verify_result.json`より:

```
manifest_line_ranges_reconstruct_original: true
all_chunks_present_verbatim_in_correct_file: true (236/236)
normalized_length_match: true
content_entries_total_ok: true (231)
kept_plus_moved_ok: true (25+206=231)
counts_match: true (mgmt_id 1377 / OPEN-xxx 575 / date 397 / url 23 / filepath 1762、前後とも同一)
ALL_PASS: true
```

## 5. 効果実測(代表アクセスパターン)

| 指標 | 分割前 | 分割後 | 備考 |
|---|---|---|---|
| (a) 本体全文読込 | 826,259字(≈375,572 token概算) | 133,671字(≈60,760 token概算、本タスクの記録エントリ追加後) | -83.8%。分割前は巨大単一行(最大36,062字/行)がありRead toolの行数ベースpaginationが実質機能しなかった(本タスク実施中、`Read limit=200`が「59,698 tokensでtoken上限超過」でエラーになる実例を確認)。 |
| (b) 代表管理ID3件のGrep+該当エントリ読込 | 同一ファイル内、Grep自体はマッチ行のみ返すため低コスト。ただし該当箇所を`offset/limit`で狙って読む場合、行番号の把握にファイル全体の見出し一覧(11,502行)を要する場面がある。 | `PM-CLOSEOUT-CONSOLIDATION-71`(本体、6,521字、行2036-2170)・`ER-006-AUDIO-COST-SPEC-FIX-01`(2026-08-22、履歴`DECISION_LOG_HISTORY.md`、6,392字、行4128-4272)・`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`(本体内で言及、Grep1回で直接ヒット)。エントリ自体の文字数は不変(原文のまま移動のため)だが、直近IDは本体のみのGrep対象(133,671字)で完結し、履歴ファイルを開かずに済む。 | 直近作業(過去数日〜PM-CLOSEOUT-CONSOLIDATION-6x〜74系)は本体だけで完結、2026-08系の古いIDのみ履歴ファイルを要する。 |
| (c) 末尾追記(Edit)時の文脈 | Edit対象は`## 参照元`直前(ファイル末尾)。ファイル自体は826,259字だが、Editツールは対象行付近のみでよく、行数ベースでは差が出にくい。 | 同様に末尾追記(行133,671字時点)。実際に本タスクでも新規エントリを`## 参照元`直前へ追記し正常動作を確認。 | 末尾追記自体のコストは分割前後で大差ないが、分割前は追記前に全体構造を把握しようとして誤って全文読込に至るリスクが高かった(本体が375K token相当だと1回のRead呼び出しで完結しない)。 |
| (d) 最大行長 | 36,062字/行(ヘッダーチェーン内、旧式の単一行paragraph) | 本体1,718字/行、履歴ファイル22,071字/行 | 巨大行は履歴ファイル側に隔離され、本体を扱う通常作業では発生しなくなった。 |

## 6. Git操作

対象ファイルのみ明示的に`git add`(`git add -A`不使用): `DECISION_LOG.md`・
`DECISION_LOG_HISTORY.md`(新規)・`er011_decision_log_restructure_01.py`
(新規)・`er011_decision_log_restructure_verify_01.py`(新規)・
`er011_output/decision_log_restructure_01/`(新規)・`CLAUDE.md`・
`docs/pm/PM_BRIEF.md`・`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・本REPORT。
並列稼働中の他タスク生成物(`er011_output/discovery_generalization_towels_trial_11/`・
`er011_output/news_ledger_enrichment_ab_trial_12/`・`FAMILY-A-*`REPORT等)は
一切stageしていない。

- commit hash: `e32fe4d`(push成功、origin/main、d742335..e32fe4d)
- raw URL(`DECISION_LOG.md`): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
- raw URL(`DECISION_LOG_HISTORY.md`): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG_HISTORY.md

## 7. 禁止事項の遵守

要約・言い換え・削除は行っていない(検証scriptで空白正規化後の完全一致を
確認)。`OPEN_ITEMS.md`・`CURRENT_SPEC.md`は編集していない。コード・
Prompt・Production実装の変更、API呼び出しはいずれも実施していない
(追加API費用¥0)。`git add -A`は使用していない。
