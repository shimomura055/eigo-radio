# EVIDENCE_01 — 学習項目選定UI 出現回数表示(occ-v1) 実装・公開・検証(委任_02、2026-10-31)

管理ID: SELECTION-UI-OCCURRENCE-COUNT-01 / OPEN-632。ユーザー指示原文=`docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md` §4。設計=`DESIGN_01.md`、規則表=`RULES_01.md`(ユーザー確認用)、精度=`PRECISION_01.md`(§8に委任_02追記)。
**AI API費用0円**(決定論の集計。有料APIは一度も呼んでいない)。Production到達: 既存の正式export(`export_form_data_01.py`)で**既定ON**(Fable判断=表示方針は承認済み)。**集計規則のユーザー確認(受入4)待ち**のため、自己でPRODUCTION_WIREDとは書かない。

## 1. 結論
- 集計module昇格(`er140_selection_occurrence_count_01.py` + loader `er140_selection_occurrence_sections_01.py`)・exporter統合(既定ON)・UI(`occurrenceOf`/`occurrencePage`、UI版 **`sel-v3-rev06-a`**)・test batch公開・公開URL実操作まで完了。Opus必須M1-M6と推奨を全て反映。
- 公開URL(test batch、`test:true`・latest不変): `https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html?batch=occ-a-test`(10セット=X/Y/Z x Standard/Advanced + 確認用2セット)。個別ページは各チップのリンク(例 `...?batch=occ-a-test&set=occ_userfive__b1b`)。URLは`tools/selection_batch_url_01.issue_batch_url`(smoke PASS必須)で発行(`evidence_02/issue_batch_url.txt`)。
- 公開URL実操作(Playwright): **PC 52/52 PASS・mobile 52/52 PASS**(`evidence_02/occ_live_{pc,mobile}.json`)。live smoke PASS(`evidence_02/smoke_occ-a-test.json`、UI版rev06-a一致)。
- 精度再検証(27 member・253項目): 確定335/保留3・誤カウント0・取りこぼし0(oracle範囲)。委任_01との差分0行(§5)。

## 2. 変更(P=Production経路、T=test/証跡)
| ファイル | 内容 |
|---|---|
| P `er140_selection_occurrence_count_01.py`(新規) | 集計規則occ-v1(純関数・API 0・flag/環境変数を読まない)。er105の活用表・除外表を読み取り専用で再利用 |
| P `er140_selection_occurrence_sections_01.py`(新規) | X/Y/Zのrun dirから4区分+titleの英語本文を1行=1 unitで読む(取得不能区分は`None`=未集計) |
| P `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py` | `convert(occurrence="auto")`既定ON・`attach_occurrence`・`augment_form_data`・`published_reference_conflict`(M4)・CLI `--without-occurrence`(既定は使わない)・自己検査・export報告の警告 |
| P `user_test/selection_form_v3/form_logic.js` / `index.html` | `occurrenceOf`/`occurrencePage`(表示専用)、`groupHtml`に回数行、`#occHint`、CSS `.occ`、`ASSET_VERSION`=`sel-v3-rev06-a` |
| P `tools/selection_form_live_smoke_01.py` | 回数行==候補数(旧data=ページ単位案内)・「出現 0回」の断定表示なし、を追加 |
| T `tools/augment_form_data_occurrence_01.py`(新規) | 既存dataへ回数だけ足した**別stem**dataを出す(export再実行なし)。M4 guard適用 |
| T `user_test/selection_form_v3/data/*__occ01.json` x10 + `articles.json`(10 entry追記) + `batches/occ-a-test.json` | テストmember(新stem・新slug`*_occ`)とtest batch。**既存の公開済みdata/batchは1バイトも変更していない**(§4) |

**変更していない**もの(Grep/diff確認): `buildText/buildStructured/buildReadable/doneSig/makeCode/selectRemaining`(node testで`occurrence`を読まないことを固定)、localStorage状態、`er128_form_readable_restore_01.py`、batch publish tool、N5/KP候補抽出・Prompt・Gate・閾値、er105(読み取りのみ)。

## 3. Opus必須6件の対応表
| # | 対応 | 実装 file:line | test |
|---|---|---|---|
| M1 前方活用へer105除外表を適用(1語Wordは保留) | `risky_forms`(PLURAL_EXCLUDE・COMPLETION_EXCLUDE=全語数、PARTICIPIAL_ADJ_EXCLUDE・PAST_ALSO_OTHER_WORD=1語のみ)と`excl`パターン(該当形を含む一致を保留へ) | `er140_selection_occurrence_count_01.py:96`(risky_forms)・`:137`(_lemma_patterns) | `er140_..._test_02.py` `M1ExclusionTables`(build→building・lie→lay・good→goods・see→saw=保留、`leave out`←`left out`=確定維持、S完全一致は常に確定)7件 + `Er105Snapshot`(表のsha固定) |
| M2 前置詞兼用の不変化詞の分離形 | `_PREP_PARTICLES`(in/on/over/through/around/along/down/up/off/by/about/across/past)。分離形(代名詞1語)で不変化詞が句末の語で、直後が句読点・文末以外なら保留 | `er140_...count_01.py:36`・`:302`(prep_like) | `M2PrepositionalParticles`(`put it in boxes`保留、`put it in.`/`,`/文末=確定、over/through/around/along/down/up/off/on、`put it away tonight`=確定、`put on hold`=確定)5件 |
| M3 先頭be/have/doを活用対象に | `_FUNC_VERBS`/`_FUNC_VERB_FORMS`(閉じた表。junk形`bed`/`haved`を作らない) | `:39`・`:40`・`:78`(inflect_forms) | `M3FunctionVerbHead`(`was in the way`・`had a look`・`did away with`・`to be in the way`・junk形なし・中間語は活用しない)5件 |
| M4 公開済みbatch参照fileの上書き禁止 | exporterに`published_reference_conflict`(`data/batches/*.json`の`member_sha256`と書込み予定内容[LF正規化sha]を照合。不一致=rc=5 `REFUSED_PUBLISHED_REFERENCE`、ファイル不変)。出力は新stem/新slugへ | `export_form_data_01.py:392`・`:517` | `er140_selection_occurrence_export_test_01.py` `PublishedReferenceGuard`(different拒否・同一内容[CRLF不問]許可・新stem許可・batchesなし許可・CLI rc=5で既存file不変・CLI既定ONで新stemへ書出)6件。実運用確認=`evidence_02/m4_published_sha_check.txt`(6 batch・59 member全て記録shaと一致) |
| M5 候補なのに0回は「確認できません」 | `occurrenceOf`: 本文等0回かつタイトル0回(または区分未取得で0)=`unconfirmable`「出現回数を確認できません」。タイトルのみ=`出現 本文等0回・タイトルのみ1回` | `form_logic.js:123`・`:135` | `selection_form_logic_test_01.js` `OCC M5`/`OCC occurrenceOf: ok`/`OCC 保留と未集計`(node 6件追加、全体92 PASS)。公開URL: `force away`(Standard)=「出現回数を確認できません」、`Now in Session`=「出現 本文等0回・タイトルのみ1回」(`display_examples.md`) |
| M6 `occurrence`欠落=ページ単位の案内+export警告 | UI: `occurrencePage`→`#occHint`(赤)「出現回数を集計できませんでした(この記事のデータには出現回数がありません)」。一部欠落=その候補だけ「確認できません」。exporter: 区分本文が読めない場合は`occurrence`を入れず`occurrence_meta.error=sections_not_found`+stderr `[OCCURRENCE][WARN]`+stdout JSON `occurrence.status=UNAVAILABLE`(`data_warnings`へは二重に出さない) | `form_logic.js:151`・`index.html:153,178`・`export_form_data_01.py:174` | node `OCC M6`、py `test_no_sections_found_gives_no_entry_occurrence_and_a_warning`・`test_unavailable_sections_are_recorded_not_zero`。公開URL: 旧batch(`twotier-a/b`)はページ単位の案内(§4) |

## 4. 旧batchが無変更・sha一致で表示できること(M4の実機確認)
- `git`: 既存`*__prod.json` 28件は本作業の全commitで変更なし(`git log c9fac776f..HEAD -- user_test/selection_form_v3/data/*__prod.json`が空)。
- 6 batch(sub04-a/b/c・twotier-a/b・occ-a)・59 memberの記録`member_sha256`と、HEADのblob(LF正規化)のsha256が**全一致**(`evidence_02/m4_published_sha_check.txt`)。
- 公開URL(PC/mobile): `twotier-a-18sets-test`・`twotier-b-5sets-test`を開き、`#shaBanner`(sha不一致警告)が出ない・候補が表示される・回数なしdataはページ単位の案内になる(`occ_live_{pc,mobile}.json` check「5 旧batch」)。スクショ=`shots/O7_old_batch_set_*.png`。
- **注意(表示の変化)**: 旧batchのページには赤字「出現回数を集計できませんでした」が1行出るようになった(M6に従う。データ・Done署名・照合コードは無変更)。

## 5. 精度再検証(委任_01の27 member・253項目を正式moduleで再実行)
`tools/run_precision_02.py`(API 0・read-only)→`evidence_02/`:
| 指標 | 委任_01 | 委任_02(er140) |
|---|---|---|
| 確定ヒット | 335 | **335** |
| 保留(加算しない) | 3 | **3** |
| 委任_01との差分(`diff_vs_01.tsv`) | - | **0行** |
| 誤カウント | 0(複数回41項目の全ヒット+非exact全件を人手確認) | **0**(同一ヒット集合のため結論継承) |
| 取りこぼし(oracle 45行を人手分類) | 0(境界1) | **0**(`nearmiss_02.tsv`=旧と同一45行、judgement引継ぎ。無関係28・派生9・構文違い7・境界1) |
| 旧`occurrence_count`との不変条件 | 251/253 | **251/253**(不一致2=`surname_choice` adopted 旧4/現3。**export時自己検査が実際に警告を出した実例**) |
- 差が0行である理由: M1(除外表)・M2(前置詞兼用)・M3(be/have/do)・縮約's・sb/sth・人名スロット・S/U和集合は、既存253項目の実本文では自然発生しない(委任_01の「sep/slot系は自然発生0件」と同じ)。新規則の効きは (a) 単体test 64件 (b) ユーザー指定5表現+`leave`の実本文集計(§6)で確認。
- 単体test: `er140_selection_occurrence_count_01_test_01.py` 30件(委任_01から引継ぎ)・`_test_02.py` 34件(新規)・`er140_selection_occurrence_export_test_01.py` 15件・node `selection_form_logic_test_01.js` **92 PASS**(うち回数関連6)。全PASS。
- oracleの限界(不規則活用・先頭be/have/do)は`PRECISION_01.md` §8に追記。

## 6. 表示例(実データ。公開URLをPlaywrightで読んだ文言、PC/mobile一致)
全10セットの全候補(`display_examples.md`)から抜粋:
```
[散らかり記事 Advanced / ユーザー指定5表現(occ_userfive__b1b)]
put away      出現 6回｜本文4・Comment1・In One Line1 （put it away、put that away、putting something away含む）
in the way    出現 1回｜本文1
force away    出現 1回｜本文1 （force it away含む）
leave out     出現 5回｜本文3・Comment1・Preview1 （left out、leave it out含む） ＋似た形1（未計上）
in sight      出現 5回｜本文3・Comment1・In One Line1
leave(単語)   出現 1回｜本文1（ほかにタイトルに1回） （leaving含む） ＋似た形5（未計上）   <- left等は別語にもなるため保留(M1)
[散らかり記事 Standard]   force away  出現回数を確認できません   <- 本文に無い項目。0回と断定しない(M5)
[X untidiness b1b]        Now in Session  出現 本文等0回・タイトルのみ1回 / clutter  出現 5回｜本文2・Comment1・Preview1・In One Line1
[Y redelivery_fee b1b]    sit right with someone  出現 1回｜本文1 ※Comment・Preview未集計   <- KP-onlyのrunでComment/Previewが無い(0と偽らない)
[Z yuki_onna / Y surname_choice / X untidiness a2 など6水準全て]  `出現 N回｜…` を Phrase・Word の両方で表示(`display_examples.md`)
```
ユーザー指定5表現は本文grepの正解(`PRECISION_01.md` §4: put away 6/6・in the way 1/1・force away 1/0・leave out 5/3・in sight 5/3)と一致。スクショ: `shots/O2_userfive_b1b_*.png`(PC/mobile)・`O3_*`(Standard)・`O4_*`(X)・`O5_unavailable_*`・`O1_top_*`・`O6_top_all_done_*`。

## 7. 公開URL実操作の内訳(`occ_verify_01.py`、PC 1280x900 / mobile 390x844 touch、各52項目)
1 トップ=10セット・個別フォーム非表示 / 2・2b 全10セットの全候補に回数行(Phrase・Word両方・注記表示・集計不能の警告なし・横スクロールなし・回数行が画面幅内) / 3a 6水準(X/Y/Z x Standard/Advanced)に`出現 N回｜…` / 3b-3l 表示例(上記)・区分内訳・保留・未集計・確認不能・タイトルのみ / 4a 選択・コメント・Done後も回数行は不変 / 4b 再読み込み後も選択・コメント3種・Done保持 / 4c 下のTopへ戻る=同batchトップ・Done 1/10 / 4d `?set=`個別URL直接オープン / 4e 全10セットDone / 一括コピー(SET 10件・連番・stem一意・END・コメント各1回・コピー成功表示・**er128 `confirm-batch --dry-run`で受入**) / 4f **一括コピー本文に出現回数が入らない**(受領形式・照合コード無変更) / 5 旧batch2種(無変更sha一致) / 6 JSエラー0。
- ローカル(LF配信)事前検証でも同一(52/52)。CRLF配信(作業ツリーそのまま)ではUIがrawバイトで計算するd6と`er128`の正規化d6が食い違うが、GitHub PagesはLF blobを配信するため公開では発生しない(既存の挙動、本変更と無関係)。

## 8. 既存機能への影響
- Done/コメント/入力保持/一括コピー/受領形式/2階層/Topへ戻る: 無変更(上記4a-4f、node 86件の既存test全PASS)。回数は選択条件・並び順・LIMITS・Done署名・照合コード(AIF1/BATCH1)に入らない(`OCC invariance` test)。
- 既存の旧test: `form1_selection_form_v3_test_01.py` は8件失敗(2F+6E)。原因は(1)hard-codedの`len(files)==10`(ベースラインで既に28件。`ls data/*__*.json`)、(2)sparse worktreeに未追跡の実run/`KP-CANDIDATE-PHR...`が無い、(3)`os.listdir(data)`の各要素を`open`するtestが`data/batches`ディレクトリでPermissionError(batchesディレクトリは本変更前から存在)。いずれも本変更が原因ではない(ベースライン同一コミットでの実行比較は、C:空き容量の都合で新worktreeを作れず未実施=推論での判定)。`er119_hr_selection_flow_test_01.py`は同sparse環境で21 errorsがベースラインと同数(`git stash`で比較実行済み)。

## 9. 残リスク・限界
- **集計規則のユーザー確認(受入4)が未了**。確認後にStatus=PRODUCTION_WIRED。表の境界(代名詞1語の分離=確定、1語の除外表該当形=保留、名詞句・人名の穴=保留)に意図とのずれがあれば、`RULES_01.md`の行を変えるだけで実装と1対1で直せる。
- 多義(同綴別義)は判別しない(ユーザー原文§4-4/§4-8の範囲)。注記と「数えた形」の行内表示で補う。
- テストmemberは`occ_userfive`(表示確認用の仮項目)を含む。`test:true`でlatestに載せず、利用者向け一覧(`listBatches`)にも出ない。
- 既存の公開済みbatch(twotier等)はdata無変更のため回数は出ない(M4)。回数を出すには新stemでexportし直して新batchで公開する。
