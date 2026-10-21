# S5 Trial環境検証結果(委任_05 C-1、API 0・JPY0、Production file無変更)

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 / 2026-10-22 / 判定: **PASS**(S5条件「Trial環境で修正後の検出・回帰テストPASS」充足 -> C-2でProduction実装可)
根拠原文: ユーザー原文§1「S5を条件付き採用: `【概数表記】`のタグ漏れを検出する。まずTrial環境で修正後の検出・回帰テストを実施し、PASSを確認してからProductionへ実装」。

## 方法
- スクリプト: `er090_b3_core_number_rounding_trial_03_s5.py`(実行 `.venv/Scripts/python.exe er090_b3_core_number_rounding_trial_03_s5.py` / `-m pytest ... -q`)。証跡: `er090_output/b3_core_number_rounding_trial_02/evidence/s5_trial_result_01.json`。
- 修正後regexを同ファイルに複製(`S5_TAG_LEAK_RE` / `S5_MARK_RE`)。Production関数(`w1.strip_tags` / `w1.assert_no_tag_leak` / `w1.clean_ja_for_next`)の**module globalだけを `with` 内で差替え**て実関数の挙動を測定。Production sourceは無編集(testで `概数表記` が現行regexに無いことを確認)。
- S5版: `MARK_RE = 【(?:中核数値|周辺数値|\s*概数表記\s*)】`、`TAG_LEAK_RE = 【\s*(?:事実|[FＦ]|中核数値|周辺数値|概数表記)[^】\n]{0,30}】`(現行から`概数表記`の追加のみ。+2行)。

## 結果
| 検証 | 結果 |
|---|---|
| (i) `【概数表記】`残留fixture 5種(文頭/数字直後/複数/空白入り`【 概数表記 】`/単独行) | **現行Production: 未検知5/5**(`assert_no_tag_leak` PASS=漏れる)。**S5版: 検出5/5**(TagLeak)かつ`clean_ja_for_next`で**除去5/5・残留0**、`marks_echoed`計上(r0_meta)1〜2 |
| (ii-a) 正常文サンプル5種(`【速報】`、鉤括弧「概数表記」、語句としての概数表記、事実タグ等) | 現行とS5版の検知結果が**5/5完全一致**(誤発火0。`【事実3】`は従来どおり検知) |
| (ii-b) 既存本文コーパス **253ファイル**(Trial2 12arm出力[phase2 144 md]、記事A/B他の Production `ja_writer/revision2.md`・`original.md`・`r0_with_tags.md`・`b1b/article.md`・`a2/article.md`) | `概数表記`を含むファイル0。**S5版により検知結果が変わるファイル0 / 253**(誤発火0) |
| Production無変更確認 | `w1.TAG_LEAK_RE` / `w1.MARK_RE` に`概数表記`なし(現行のまま)。pytest 6 PASS |

## 解釈・注意(Opus/Fable確認用)
- S5版では漏れは`strip_tags`(MARK_RE)で**除去**されTTSに読まれない。除去前のrawは`marks_echoed`(r0_meta)へ記録。`TagLeak`(STOP)になるのは、MARK_REが除去できない変形(例: `【概数表記 補足】`)に限る=従来の【事実】変形と同型で、STOP増加は極小。
- 実測の漏れ頻度は Trial1/2 で 0(4記事 x JA/Adv/Std)。S5は無音の品質リスクに対する安全網。
