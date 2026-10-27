# GRAMMAR_ZERO_INVESTIGATION_01 『告げ口心臓』文法候補0件(Std/Adv)の原因調査(委任_02、2026-10-27)

## 結論
- 判定=**正常動作(承認済みTrial-08選定方式どおりの0件)。実装不具合なし。** 抽出・parse・選定・事前生成・フォーム表示のどこでも候補は失われていない。LLMが最初から「該当なし」を返している。
- 修正なし(コード・Prompt・閾値・データ無変更)。再生成なし。本文・音声・KP/KW候補・フォーム選択状態・照合コードg10は不変。
- 残る論点は仕様側の特性(Z物語文は承認済み選定基準で0件になりやすい)。仕様変更は未実装、判断候補(区分D)として提示。

## 1. 実行記録(API 0)
run=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01`
- Adv `study_text/grammar_candidates.json`: prompt_id=part2_stepA8、template sha `51912fe1…`=現行`STEPA_PROMPT_SHA256`、model=gpt-6-luna(応答modelも一致)、`retried_for_parse=false`、`tier_table=[]`、`no_feature_paras`=P1〜P22全部、`uncovered_paras=[]`、`ng=[]`、`filtered_by_ng=[]`、`rejected_ids=[]`、status=NO_CANDIDATE。Std `a2/study_text/`も同じ構造。
- コード経路(`er120_part2_grammar_production_01.py`): `parse_candidates`(:479-526)は適格/不適格を問わずLLMが返した全featureを残し、`build_candidates_doc`が`tier_table(parsed["features"])`(:769)に全件を記録する。したがって`tier_table=[]`は「LLMがfeaturesを空配列で返した」ことを意味する(parser/Validator/NG/上限で落ちた場合は不適格理由付きで`tier_table`に残る)。構造不正は`Part2StructureError`で止まり0件扱いにならない(:479,:594)。`_default_call_fn_factory`は`status!=completed`を構造失敗にする(:568-572)。MAXOUT=13000に対し出力は2,449/1,959 tokenで切詰めなし。出力2,449 tokenのうちreasoning 2,367、実応答は約82 token=`{"features":[],"no_feature_paras":[P1..P22]}`の長さと一致。
- 事前生成: `grammar_explanations.json` items=[]・`skipped_over_cap=[]`(候補0なので対象なし)。「事前生成は実施済み」は「対象0件で事前生成工程を通過した」の意味に過ぎず、抽出の正常性の根拠にはしていない。
- 確定: `grammar_human_review.json` status=`NO_CANDIDATE_UNREVIEWED`(runnerが自動記録。人間の確定ではない)。
- フォーム表示: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:275`の固定文言。0件を忠実に表示しているだけ(「事前生成は実施済み」の文言は0件時は紛らわしい。下記7)。

## 2. 直接証拠(生応答の取得。委任の想定外の補強、実費¥0.788)
既存runは生応答を保存していないため、Production関数`extract_candidates`を無変更で同一本文へ呼び、生応答を保存(run成果物は不更新)。`grammar_zero_probe_02/`。
| probe | level | 結果 |
|---|---|---|
| b1b_1 | Adv | features=1: P11 "Faster it went, and louder." CMP、**teaching_value=LOW → 不適格(TV=LOW)** → 候補0 |
| b1b_2 | Adv | `features: []`、no_feature_paras全22段落 → 候補0 |
| a2_1 | Std | `features: []`、全22段落 → 候補0 |
既存2回(Adv 10-25 `run_p2_evidence_r3`・Std/Adv 10-27)と合わせ、**同一Adv本文(text sha `0c71c2f0…`)で4回中4回が適格0**、Std2回中2回0。両levelの原因は共通=LLMのfeature抽出段階で適格なfeatureが出ない(TV=LOWで落ちる場合を含む)。再現性があり、サンプリングの揺れで取りこぼした可能性は低い。

## 3. 比較対照(保存データ)
全`grammar_candidates.json`走査: 同じ現行Promptでも、X(AI島等)は1〜5件、Y(再配達)は2〜4件、Z物語は0〜1件(メロスAdv 28/29段落が「特徴なし」で多くの回1件、Std 0件。告げ口心臓Adv/Std 0件)。`STD_CANDIDATE_RATE_01.md`(5節): Z作品の候補率はAdv約0.7・Std約0.4/本、Z Std 0件が3/5。Z物語文での0件は既知・再現済みの傾向で、告げ口心臓だけの異常ではない。
Std本文にもPromptは「Advancedレベル・B1〜B2読解」の基準を使う(`er120:62`)。Std向けlevel差込は未承認事項(D-a(2))で、今回も適用していない。

## 4. 独立評価(本文を読んだ所見。API 0)
Prompt/Trial-08の基準=「構造を取り違えやすく、再利用できる読み方があり(HIGH)、基礎項目で説明が済まない」文。本文は短文中心で、複雑な構文が少ない(Poe原作を平易化した本文)。
Advanced(`writer/r2.md`)で候補になり得る表現(Prompt分類に当てはめた所見):
- P11 "Faster it went, and louder." — 比較級副詞の前置(FRONT/CMP)。実際にLLMが1回CMP候補に挙げ、TV=LOW(再利用性が低い)と自己判定。
- P9 近傍 "A bad dream, I explained; the cry was mine." — 引用目的語の前置+伝達部(FRONT・OBJECT_OR_COMPLEMENT相当だが伝達部の倒置は基礎項目に近い)。
- P2 "Pale blue, covered by a cloudy film—a vulture's eye." — コンマ・ダッシュ区切りの断片と同格(APPOS)。
- "I eased the door open so slowly he never stirred" — 目的語+補語(SPEC)と so…(that)の省略。ただし使役・知覚・keep/make/find型は基礎項目に含まれる。
- "Not pain—terror." — 省略(ELL)だが短い断片で学習の再利用性は低い。
Standard(`writer/std.md`): "I hated his eye, not him."(対比の省略)、"You should have seen my patience—he never even moved!"(should have+過去分詞)、"You could search all night and find no mark."(couldの暗黙の仮定)など。いずれも基礎項目(完了・助動詞・仮定法の基本形・並列)で説明が済み、H高(HIGH)に届く強い候補は見当たらない。
評価: **Stdは0件が妥当。Advは「弱い候補が数件ある」が、現行基準(再利用性HIGH)ではLLMの自己判定(LOW)も本評価も同様で、0件が基準どおり。** 基準を下げて補えば「不適切な候補の水増し」になるため行わない。

## 5. 判定
(i)正常(0件妥当)。(ii)不具合=なし(parser・Validator・上限・NG・事前生成・フォームのいずれも誤動作なし)。修正・再生成は不要のため有料再実行なし。

## 6. 判断候補(区分D・実装なし)
D-1: Z物語文の文法を現行基準のまま0件で確定してよいか(推奨=A案: 0件確定。品質基準を動かさず、Z Std 0件は承認済みの許容結果「0件可」)。
D-2(別案、新仕様のため要Trial): Z/Std向けに抽出Promptのlevel差込または物語文向けの対象定義を新設して候補率を上げる。承認済み選定方式の変更になり、Trial-08再検証・Opus条件Aが必要。QCD: Q=基準変更リスク、D=Trial+承認で遅延、C=1本あたり数円増。
いずれも本案件の完成版公開を止める理由ではない(0件で公開可能。0件はspec上許容)。

## 7. 残Open Item(分類)
- フォーム固定文言`grammar_note_ja`の「事前生成は実施済み」は0件時に誤解を招く(例: 実施済み=抽出が正常に済んだとの誤読)。分類=実害なし(軽微な文言改善)。修正は別worker/他案件の未コミット差分があるexporterへ入るため本委任では触れず、次委任案=0件時の文言を「抽出は実施。この本文では適格な候補が見つかりませんでした」へ(承認済み仕様内の表示修正、API 0)。
- Z物語文の候補率(Z Std 0件が3/5)の仕様論点=D-2。既存の登録済みOpen Itemとの関係は未確認(SSOT未編集)。
