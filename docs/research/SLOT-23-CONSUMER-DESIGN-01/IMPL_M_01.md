# IMPL_M_01 M班(委任_05M): マーク発行(std_part1/display_spec)をnew_reviewへ接続 + 残整合(API 0)

## 1. 接続前チェック(C/D/E班の配線が全Familyで揃っていること。Grep一覧)
| 確認点 | X | Y | Z |
|---|---|---|---|
| display_spec参照点(flag非経由=`er128.display_spec_of`) | `er019_family_x_audio_production_runner_01.py:444 x_display_spec`→`:446` | `er121_family_y_audio_01.py:1443 resolve_y_highlights`(:1450 `cc.display_spec_of`) | `er026_family_z_fiction_production_runner_01.py:1563`(`cc.display_spec_of`)→`:1586 _resolve_level_highlights` |
| Std Part 1 level化(vocab対象level=Adv常時/Std=display_spec付き) | `:449-451`(`PART1_ALWAYS_LEVEL or x_display_spec`) | `er121_family_y_runner_01.py:713 _part1_level_enabled`(:1053で使用)/`:327 PART1_STAGES(level別)` | `er026…:1573 _part1_levels`(level別kp_part1) |
| Validator「Part 1ちょうど1個」 | `:3091-3095 X_PART1_BLOCK_COUNT` | `:1053-1055 FAMILY_Y_PART1_OUTPUT_MISMATCH` | `:2619 _verify_learning_items` |
| page_verify G3(`verify_highlights`) | `:3102,:3924` | `:1320-1337 _verify_highlights_on_page` | `:2615-2633 _verify_learning_items` |
| 全Family共通の入口 | `er119.vocab_enabled`(:501-504)、`er128._display_spec_for_new`(:272-)、`er003` level API(B班) | 同左 | 同左 |
→ **欠け無し。接続を実施。**

## 2. 変更点
1. `er119_kp_human_review_01.py` `new_review`末尾: `issue_std_part1_mark(r)`を1行接続(NOTE(M14)を置換)。KP reviewのみ(関数内で`kind==KIND_KP`のとき)。`prev`がマーク付きなら従来どおり継承(先行行)。**新規reviewのみ**: 既存の確定済み記事のreview/recordはこのcommitで書き換わらない(遡及なし。`reconsume`明示実行まで不変)。`issue_std_part1_mark`のdocstringも「接続済み」へ更新。
2. `er128_kp_confirmed_content_01.py` `verify_outputs`(G3): Part 1行/表示の検査を`elif level=="b1b"`から`if (level=="b1b" or rec.get("display_spec"))`へlevel化(elifではなく独立の`if`: display_spec付きa2はStd訳検査に加えPart 1検査も受ける)。display_spec無しa2は従来どおり(Part 1検査なし)、b1bは不変。
3. `er121_family_y_runner_01.py`/`er026_family_z_fiction_production_runner_01.py`: 関数内`import er128_kp_highlight_01 as g3`を、X(`er019…:438-441`)と同方式の遅延accessor`_g3()`(`importlib.import_module`)へ。挙動不変。`TestIsolation.test_abc_and_shared_functions_do_not_import_er128`の許可リストは**広げていない**(PASSへ復帰)。
4. test:
   - `er128_kp_confirmed_content_slot23_test_01.py`: `test_M14_new_review_does_not_issue_mark_yet`→`test_M14_new_review_issues_mark_now_connected`(素のnew_reviewがa2/b1b両方にstd_part1を付与・呼出点がnew_review内の1箇所のみ)に置換。`test_M14_display_spec_derived_for_both_a2_and_b1b`(B班判断(a)をa2/b1b両方で固定)、`test_M14_prev_without_mark_is_not_retroactively_marked_by_cc`(遡及なし)、`TestG3StdPart1Level`(display_spec付きa2はPart 1行・ページ照合、display_spec無しa2は不変)を追加。
   - 旧(マーク無し)記事の挙動を検証していた既存testは、マーク発行だけを無効化する`er119_test_support_01.legacy_unmarked_class/legacy_unmarked_flow`(test専用・production不変)で旧reviewを再現(対象はREGRESSION_M_01.md)。期待値(旧挙動)自体は変えていない=T1〜T4の『マーク無し旧fixtureのみNotIn』方針。

## 3. 旧経路残存Grep総括(S1〜S27/T1〜T5の最終状態)
| 項目 | 最終状態(Grep) |
|---|---|
| S1〜S9(er119 select/auto/finalize/最終QA/依頼書/er128 vocab突合) | `vocab_enabled(level, review)`(er119:501)+er128 `vocab_on`(:415)に集約済み(B班)。`level == "b1b"`残存はいずれも (i)Advanced固有(KP音声voice・support text等=Part 1非関連) (ii)`er119:504 vocab_enabled`/`er128:415,472,891,1422,1463`の『b1bは常時vocab、a2はdisplay_spec付きのみ』判定(意図どおり) |
| S10/S11 | `STD_CATEGORY2_NO_SLOT`はer128の定数(:86)・docstring・G1不変条件(:463-479,『display_spec付きでは0件』)・reconsumeのみ。**新規発行0**(読取互換のみ) |
| S12 | 本commitでlevel化(`er128:891`) |
| S13〜S16, S17〜S24 | Grepで`generate_part1_all_for_b1b`/`_part1_items_b1b`/`PART1_STAGE`(単体)/`.removed`=非test 0件。`kp_part1_b1b`は`er121…:44`のlevel別stage名一覧の1語のみ(`PART1_STAGES`) |
| S25/S26 | Y: `er121_family_y_runner_01.py:327`コメントに『旧PART1_STAGE…は撤去』の履歴記述のみ |
| S27 Validator | X/Y/Z各`ちょうど1個`(§1表)。マーク無し旧runのみ0個許容 |
| `Advancedのみ`文言(非test) | `er019_family_x_audio_production_runner_01.py:3839`(Part 2文法のtts/assemble入口=Part 1とは無関係)、`er121…:327`(撤去の履歴コメント)、`er019_nws2_final_page_01.py:5,72,74`(旧表示仕様の既存記事用=遡及なし用と明記、C班)、`er015_*`/`er052_*`は無関係な旧trial |
| `Part 1は無い`(非test) | `er019…:949`(『マーク無しStandard(a2、遡及なし)』と限定記述) |
| T1〜T5 | `assertNotIn("Vocabulary", …)`はer003 ZPart1Tests/er120 ZPart2Integrationの旧(マーク無し)fixtureに限定(`legacy_unmarked_class`付き)。マーク付きの正例はC/D/E班test(`er121_y_highlight_wiring_test_01`/`er026_z_highlight_wiring_test_01`/X側)で固定 |
| `import er128_*`直書き(runner) | X/Y/Z runnerとも0(`importlib.import_module`の遅延accessorのみ) |

## 4. CURRENT_SPEC更新要点(SSOT文案。Fable/別委任が反映)
- S29: `CURRENT_SPEC.md:1717,2083,2086,2101,2106,3111`『Part 1=Advancedのみ/Advanced=b1bのみ。Standard・A/B/C・Yへは拡張しない』→『2026-10-27ユーザー正式決定: ②追加解説(Part 1)はStandardにも新規記事から表示(Std=①+②、日本語解説)。表示有効化は確定レコードの`display_spec=LEARNING_ITEMS_123_V1`で決まる。マーク発行は`new_review`(委任_05M接続、新規reviewのみ・遡及なし・既存記事はreconsume明示実行まで旧表示)。旧「Advancedのみ」は旧記事の履歴として残す』。
- S29/:2095: 学習テキストページの正式入口は標準公開builder(`er_user_listening_page_common_01`系・Part 1 level化)。`er019_nws2_final_page_01.py`は旧表示仕様の既存記事・遡及なし用(C班がscript先頭に明記)。
- S30: OPEN-562=配線完了(接続commit後・F班evidence待ち。WIRED判定はFable)、OPEN-512=Std拡張注記。
- 新規発行停止: `STD_CATEGORY2_NO_SLOT`(読取互換のみ)。G3: Std Part 1行/表示照合もlevel化済み(§D-5)。
