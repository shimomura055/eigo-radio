# PRODUCTION_IMPACT_02: Trial B(正実施)採用時の影響(read-only、Production無変更)

共通事項(生成順序・retry・prior再利用・Family X影響・旧Phase1経路)は`PRODUCTION_IMPACT_01.md`の1〜9節を踏襲。ここは正実施Trial Bで追加判明した点と、QDC。

## 採用時の変更箇所(想定、未実装)
- `er062_family_z_writer_01.py::run_support_std` L853-876(Comment 1生成): Comment 1のみ`fam_c.generate_family_c_a2_comment`経路をやめ、Advの`run_support_adv`(L893-928)と同形式でrole=`a2gen.COMMENT_1_ROLE`(無改変流用可)+ctx(`【本文(これから聞く部分)】Part1`+`NOT_NEWS_NOTE`)を`generate_with_lint`で生成。Comment 2/3は現行のまま。
- L878-890(Preview): 現行のまま(`er026.build_family_z_preview_prompt()`+Comment 1重複回避)。Trial B'と同一なのでPreview側のPrompt・コード変更は不要。
- lint例外: `er062_family_z_structure_01.py::lint_support_text` L676-678(ja:`LISTEN_INSTRUCTION`=`_LINT_LISTEN_JA`[L642]に「注目して」を含む+`fam_c`禁止語句)を、Std Comment 1のみ緩和する設計が必要(今回3/3 NG)。緩和しない場合は`generate_with_lint`のretry1→`FamilyZLintStop`で量産が止まる。これはGate仕様変更に当たる。
- 品質下限: Comment 1が36〜41字のため、`check_a2_comment_quality`(min 40字)は`generate_family_c_a2_comment`経由では不合格になる。上記のとおり同経路を迂回するか、基準を分けるかの設計が必要。
- Family X/C共通定数(`fam_c`、`a2gen`)は変更不要(読取流用のみ)。`prior`再利用の依存方向(Comment 1→Preview)は現行と同一で、追加ロジック小。
- テスト: `er062_family_z_writer_01_test_01.py`のStd Comment 1呼出前提(role/経路)更新、lint例外のテスト追加(約4〜6件)。

## QDC(Std記事1本あたり、実測)
- API呼出数: 変化なし(Comment 1回+Preview 1回。lint retryが増える場合のみ+)。
- 追加費用: Trial B'実測 Comment 1+Preview の1ペア=約JPY 0.12(6生成合計JPY 0.3637÷3)。現行Std方式と同数のため実質増分は0。lint例外が無い場合のretry増は最大+0.12/記事程度。量産70円/記事セットへの影響は0.2%未満(無視可能)。
- 時間: 生成は現行と同じ直列2呼出で、遅延の増減は実測差なし(Comment 1の出力が短い分わずかに短縮の可能性)。
- 品質リスク: lint 3/3 NG(例外設計なしでは採用不能)、注目点の事実ずれ(2/3)、Preview再話寄り。
- Gate: 新しい処理フロー設計(Opus独立技術レビュー条件A)+ユーザー`APPROVED_FOR_PRODUCTION`が前提。
