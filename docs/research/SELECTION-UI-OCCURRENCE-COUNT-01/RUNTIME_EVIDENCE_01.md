# RUNTIME_EVIDENCE_01 — 出現回数 occ-v1 の正式Production経路 runtime evidence(委任_03、2026-10-31)

管理ID: SELECTION-UI-OCCURRENCE-COUNT-01 / OPEN-632。**AI API 0円**(集計moduleは`re`/`unicodedata`/`json`のみimport、LLM/TTS/ASRのstage未起動)。証跡=`evidence_03/`。

## 1. Production経路の特定(重要な事実)
- 選定フォームdata(`user_test/selection_form_v3/data/<stem>.json`)の**唯一の正式生成経路**は、KP候補doc(`kp_candidates.json`)を入力とする exporter CLI `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(`main` :449 → `convert(..., occurrence=(False if a.without_occurrence else OCC_AUTO))` :513 → `attach_occurrence` :371-372)。runner(X `er019_family_x_audio_production_runner_01.py:915-951`[`--scaffold-only kp`]・Y `er121_family_y_runner_01.py:614 stage_kp`・Z `er026_family_z_fiction_production_runner_01.py`)は**KP候補docを書くところまで**で、exporterを呼ばない(`grep export_form_data` に runner ヒット0。Grep結果は本書§6)。したがって「runnerのscaffold/export段がexporterを呼ぶ箇所」は存在せず、**exporter CLIがX/Y/Z x Std/Advの共通・唯一の正式経路**(既存の全form dataも同CLIで作成。HR手順書=`FORM_DATA_01.md` §4)。runner stage単独実行での代替は不要(=代替ではなく正式経路そのもの)。
- 既定ON: `OCC_AUTO = "auto"`(:162)。止める手段は`--without-occurrence`(:481)のみ。**起動script・手順書・`.env`・runner内に同flagの使用なし**(§6 Grep)。集計module(`er140_*`)は環境変数・flagを読まない(Grep: `os.environ`ヒット0)。

## 2. 6水準の実行結果(`evidence_03/exports/*__cli.json`・`six_levels_summary_03.json`)
実在の既存run dir(X=`untidiness_family_resource__run_fx4_01`、Y=`surname_choice/run_02`、Z=`yuki_onna/run_yo_prod_01`)に対し、exporter CLIを`--family/--level`だけ変えて実行(rc=0)。runner・API・TTS不使用。
| Family | Level | 候補 | `occurrence`付き | 確定計(区分別) | 保留 | 未集計区分 | 自己検査 | 備考 |
|---|---|---|---|---|---|---|---|---|
| X | Standard | 9 | 9/9 | 16(本文13・In One Line3) | 0 | なし | 9件OK | |
| X | Advanced | 12 | 12/12 | 15(本文11・Comment1・Preview1・OneLine2、+Title1) | 0 | なし | 12件OK | Titleのみ候補「Now in Session」=タイトルのみ1回 |
| Y | Standard | 10 | 10/10 | 17(本文17) | 2(bother/bothers) | なし | 11件中1不一致 | `adopted`=旧4/現3。**自己検査が警告(想定どおり)** |
| Y | Advanced | 12 | 12/12 | 17(本文17) | 0 | なし | 12件中1不一致 | 同上 |
| Z | Standard | 7 | 7/7 | 7(本文7) | 0 | なし | 7件OK | In One LineはXのみ。Standardの日本語Comment/Previewは英語tokenなし=0 |
| Z | Advanced | 10 | 10/10 | 11(本文11) | 0 | なし | 10件OK | |
全6水準で `occurrence`/`occurrence_meta`(区分別内訳・保留件数・未集計区分・自己検査)が出力された。

## 3. 手計算(規則表 RULES_01.md)との照合(`hand_contexts_03.txt` → `hand_check_03.py` → `hand_check_03_result.json`)
区分本文の該当行を緩いregexで列挙し、人が文脈を読んで確定/保留を判定→期待回数を記録→exporter出力と突合。**13項目(Phrase 6・Word 7、6水準すべてにPhrase・Word各1件以上)で13/13一致**。
- X Std: `hear it out`(本文1)、`supplement`(本文4[supplement x3+supplements x1]・In One Line2[supplements])
- X Adv: `hear it out`(本文1)、`clutter`(本文2・Comment1・Preview1・In One Line1)
- Y Std: `give something up`(本文1,選定表層`giving something up`)、`thankful`(本文4)、`bothered`(確定1・保留2=bother/bothers)
- Y Adv: `hold someone back`(本文1,選定表層`hold my son back`の完全一致)、`grateful`(本文4)
- Z Std: `slip away`(本文1)、`mist`(本文1) / Z Adv: `slip away`(本文1)、`bar`(本文2,`barred` x2)
**ユーザー承認3項目**の実module出力(`approved3_check_03.py`→`approved3_check_03_result.json`、6/6 OK): 承認1 `put away`←`put it away`/`put away`=確定2・`put the books away`=保留(承認3)、承認2 `build`←`building`・`lie`←`lay`・`good`←`goods`・`see`←`saw`=確定0・保留1(「＋似た形1（未計上）」)。

## 4. `published_reference_conflict` guard(M4)
公開済みbatchが参照する`user_test/selection_form_v3/data/surname_choice__a2__prod.json`へ、回数付きの新内容を出力させようとした → **rc=5・`REFUSED_PUBLISHED_REFERENCE`**(`m4_guard_03.stderr`、`.rc`)。file無変更(`git hash-object`=index blobと同一 97ad95af)。上記6水準のexportは`--out`を証跡dirにしており発火なし(正常)。

## 5. 後続経路(retry/fallback/resume/再生成/再export)との整合
- 構造: runnerのretry/fallback/resume/再選定/Local Rewriteは**KP候補doc・本文を更新するだけ**で、form dataの生成は常に最終的な`kp_candidates.json`+現行の本文fileを読むexporter CLI(同一`convert`)。回数は本文fileから決定論に再計算されるため、どの後続経路でも同じ関数・同じ規則を通る(経路別の分岐なし)。
- 再export(resume相当・同一入力): Y Std surname_choice を再実行2回 → 出力3本(初回+再2回)の**sha256完全一致**(`5dd0d0ab2ab9c88f…`)。
- 再生成後の本文変更の模擬(Local Rewrite/再生成相当。run dirを複製し`thankful`を1箇所`glad`へ):  `thankful` 本文 4→**3**、自己検査の不一致は1→**2**件(選定時の`occurrence_count`と食い違いを警告)=本文が変わったら回数に追従し、ずれを警告する(`evidence_03/exports/_regen_sim.*`)。
- 実例(自然発生): `surname_choice`の`adopted`(旧doc 4/現本文3)を自己検査が警告(上表Y)。

## 6. 既定値のGrep(Production到達経路)
- `grep -rn "without-occurrence|without_occurrence" *.py tools/ ...`(test・SELECTION-UI-OCC証跡を除く): exporter自身の定義のみ(:12,:326,:481,:513,:524,:526)。runner/起動script/手順書からの使用0。
- `grep -rn "export_form_data" er*.py tools/*.py`: test群と`tools/augment_form_data_occurrence_01.py`(別stem出力の補助)のみ。runner呼出0。
- `grep -n "^import|^from" er140_*`: re/unicodedata/hashlib/json/osのみ(network/LLM import 0)。
