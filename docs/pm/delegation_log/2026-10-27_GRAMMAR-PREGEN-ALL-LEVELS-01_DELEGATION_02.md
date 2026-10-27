## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02(Opus条件Aレビュー反映`DESIGN_02.md`+F-0 schema契約+F-1共通核実装(er120: 事前生成stage・level必須引数化・v2 schema・重複生成防止)+F-8核test。API 0・JPY0。ユーザー正式決定【全面修正版】APPROVED_FOR_PRODUCTION、原文=`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`。設計=委任_01(commit 5a2c3dba1)、Opusレビュー原文=下記)。並行Agent: (a)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S(Std候補率計測DEV script+evidence元run実現性確認、read-only+DEV出力のみ)、(b)KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03(evidence、`er128`最小是正あり得る)。**`er128_kp_confirmed_content_01.py`・`er119_kp_human_review_01.py`・フォームexporter・X/Y/Z runner・ページbuilderは本委任で編集しない**(F-4 adapter=委任_03、F-5/F-6=委任_04)。あなたの所有=`er120_part2_grammar_production_01.py`、`er120_part2_wiring_01.py`、`er119_grammar_review_01.py`、新test `er120_part2_pregen_test_01.py`、既存er120/er119_grammar test更新、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{DESIGN_02,SCHEMA_CONTRACT_01,OPUS_REVIEW_01,IMPLEMENTATION_02,TEST_PLAN_02}.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`(本件条件A依頼・指摘・採否記録。編集直前にorigin/main最新確認)、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_{OPUS_RESULT_01,DELEGATION_02}.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG2.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み新仕様のProduction実装第1段(共通核)。到達上限=IMPLEMENTED(核)。
- 禁止: Part 2 Prompt(STEPA/STEPB)本文・sha・eligible7・Trial-08 Tier・解説品質/文章量の変更、新flag、levelをAdvancedに限定する条件の残置、`b1b`既定値の残置、Step B呼出点の複数化、所有外ファイル編集、禁止Git操作(`add -f`/`pull --rebase`含む)。
- 時間見込み: 約4h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。Opus原文を`..._OPUS_RESULT_01.md`へ逐語保存。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_02.md` をN=718から順に試し、先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02」のものを採用(同時刻に委任_02Sあり)。

## Fable判定(Opus指摘の採否=必須修正1〜7全件採用。追加判断)

- O-1のISSUE解消手段=「別候補を選ぶ/省略する」+「ユーザー了承で現状のまま進める操作(`--user-ref`必須・記録)」の2つを採用(既存`confirm-revise`と同型の保護フロー継続であり新Product原則ではない。発生実績0/28)。
- 速度: 事前生成は直列で実装、evidenceで所要時間を計測し2分超なら並行化検討(budget guardの原子性確認後)。
- HR提示: TOP2枠→全候補(最大8、超過分は依頼書に「他N件・解説未生成」)=ユーザー原文§3の解釈としてDECISION_LOGに記録(SSOT文案に含める)。
- v1進行中run(確定済み・結果なし)の事前生成は選定済みidのみ(`stepB_generated`明示)。不在宣言(auto)済みならTOP1のみ生成(任意最適化=採用)。
- `_assert_study_ready`はpages/page_verifyのみ(tts_a2に付けない)。
- Xの公開済み記事scriptは書き換えない(履歴)。今後は`public_study_html(level=)`必須+両levelブロック検査(委任_03)。
- 将来の原価低減(2 ITEM/1 call)は今回実施しない(記録のみ)。
- evidence費用上限は¥150へ再設定(案件見積300円以下=AI自律、委任_05)。

## Opusレビュー(逐語)

## GRAMMAR-PREGEN-ALL-LEVELS-01 DESIGN_01 Opus独立技術レビュー(条件A、read-only、API 0)

### 結論
条件付きで実装に進めてよい。骨格(Step A''→全候補のStep B事前生成→HR/フォーム→確定・凍結→finalize LLM 0→公開)は妥当。ただし次の4点は、実装前にDESIGN_01/EVIDENCE_PLAN_01へ反映が必要。
- (1) 事前生成の`ref_ja=None`と、既存のref_ja照合の組合せで解消不能なSTOPが生じる。
- (2) フォームで文法を0件選んだときの文法reviewの確定方法が未定義。
- (3) evidence方式Aの前提(元runに音声あり)が事実と違う。
- (4) 文法処理のlevel既定値が暗黙に`b1b`へ落ちる箇所を撤去する。

### 論点別

**O-1 工程順の副作用: 要修正(重大1・中1)**
- 重大: 凍結なしの経路でref_ja照合が必ず失敗する。CLI確定のみでKCPレコードが無い場合や、auto採用の場合が該当する。
  - `er120_part2_wiring_01.py:186-187`の`require_final`は、凍結が無いと`ref_ja_pool`を渡す。`er120_part2_grammar_production_01.py:1326-1327`は`result.ref_ja != lookup_ref_ja(...)`でPart2Stale(「再生成が必要」)にする。
  - 事前生成物はref_ja=Noneなので、候補文がPart 1の引用文と一致すると必ずStaleになる。新設計ではfinalizeがStep Bを呼べないため、解消手段のないSTOPになる。
  - 設計§3-(b)が根拠とする`pool_ref_ja_issue`(er128:979)は、凍結がある場合しか呼ばれない(wiring:131-135, 188-192)。
  - 修正案: v2結果(事前生成由来)では`require_fresh_part2`にref_ja_poolを渡さない。代わりに凍結の有無に関係なく「Part 1訳とStep B訳が食い違うか」を同じISSUE(rc=4)で検査する。
- 中: このISSUEは解消手段が無く、行き止まりになる。`pool_ref_ja_issue`の解消策はrevokeだけ(er128:990)で、同じ候補を選び直すと同じISSUEになる。
  - 修正案: 「別候補を選ぶ/省略する」と、ユーザーが明示的に了承して現状のまま進める操作(user_ref必須、記録が残る)の2つを解消手段として定義する。了承操作を新設するかはFableが判断する(発生実績は0/28で稀)。
- 妥当: 事前生成の位置、失敗時はKP発注前に止まる点、`explain_signature`にMODELが入るため未確定分だけ再生成される点、確定後は`frozen:<sha>`で判定する点。
- 軽: 速度。2 level×最大8 callが直列でKP候補生成の前に並ぶ。まず直列で実装し、evidenceで所要時間を測る。2分を超える場合に限り、KP候補生成との並行化またはlevel単位の並行化を検討する(budget guardの原子性の確認後)。

**O-2 Standard本文への候補抽出: 妥当(条件付き)**
- D-a(Prompt無変更)は「解説品質・学習内容を独断で変えない」というユーザー原文に忠実。
- ただし前提の食い違いを事実として記録しておく。Std節は「Standard(A2)」(er019:3037)なのに、STEPA/STEPBは「B1〜B2相当」の学習者向け(er120:55, 118)。STEPAの基礎項目除外(er120:91)により、Stdの短文では候補0件が多くなると予想される。サンプル(`er019_output/part2_hr_evidence_01/run_r1/a2/article.md`)を見ても短文中心。
- これは偽陽性ではなく過少抽出のリスク。候補0件は固定文面(`ZERO_P2`、er120:154)で表示され、品質事故にはならない。
- Std本文(article.md)は`# `見出しと`## In one line`の構造をAdvと共有しており、`paragraphs_from_article_md`はそのまま使える。
- 要追加: EVIDENCE §4のStd候補率計測(≤¥7)は実装前に前倒しで実行できる(後述O-10)。0件率が高い場合や解説の難度が合わない場合は、事実として報告する。

**O-3 重複生成の防止: 要修正(中)**
- (i) Step B呼出点を1か所に集約し、spyで呼出回数を固定する方針は妥当。
- (ii) `legacy_postselect`の判定が「事前生成ファイルが無いこと」に依存しており、抜け穴になる。copy-runでの欠落や手動削除でv2の結果だけが残った場合も旧経路に入ってしまう。
  - 修正案: 旧経路の条件は「review schema v1 かつ part2_result schema v1」に限定する。v2の成果物があるのに事前生成ファイルが無い場合はINTEGRITYでSTOPする。
- 追加: 確定済み・結果なしの進行中の旧run(v1)では、事前生成を選定済みidだけに限定する(`pregen_stage(ids=...)`)。未選択候補への課金を避けるため。出所は`stepB_generated`(ユーザー未閲覧)と明示する。
- 同様に、事前生成の時点で不在宣言(auto)が既にあれば、TOP1だけを生成してよい(任意の最適化)。
- (iii) reselectの後、HR提示の前に必ず事前生成を通す状態遷移を明記する。`grammar-show`は未生成の候補に解説を出さず、「制作を再実行」と案内する。

**O-4 2件採用: 要修正(中2・軽1)**
- 中: フォームで文法0件を送信すると行き止まりになる。`cmd_from_form`は文法が空ならsidecarを作らず(er128:1243-1246)、文法reviewはPENDINGのままrc=4で待ち続ける。
  - 修正案: 同じロック内で`omit`を適用する(reason=`form_submission_no_grammar`、zero_reason=`human_omit`)。0件の確定もレコードに残す。
- 中: ロックの順序と書込みの順序が未定義。KPのロックは`rv.review_lock(kp_dir, KIND_KP)`(er128:1229)。
  - 修正案: 検証は書込みの前にすべて済ませる。順序は KPロック→文法ロック で固定する。書込みは 文法review→sidecar→KPレコード保存 の順にし、KPレコード保存を確定点(commit点)とする。同じidで再送信したときは冪等(同じ結果)になるようにする。
- 軽: `decision.explanations_sha256`をファイル全体のshaにすると、新候補の追加だけで確定が古い扱いになる。選定・提示したidごとのsha(`explanation_sha_by_id`)にする。
- 妥当: v1読取互換、v1署名式の保存、表示順=本文出現順(段落番号→段落内の位置)、autoはTOP1のみ。items[]の並び・sha・署名がクリック順に依存しないこと(T5)。
- 要確認(Fableの記録事項): 現行HRはTOP1/TOP2の2件枠を提示し(er120:872-892、TOP_N=2「ユーザー正式決定」er120:50)、reselectで枠を進める方式。新設計は最大8件の全候補を提示するため、HRの提示方法の意味が変わる。ユーザー原文§3「文法候補ごとに…生成」と費用式「0.3円×候補数」から、全候補提示が自然な読み方。DECISION_LOGに解釈として明記すること。

**O-5 Family差の解消: 妥当(軽2)**
- Xの公開ページscriptのうち実際に共通関数を呼んでいるのは`er019_nws2_final_page_01.py`だけで、集約の回帰範囲は小さい。
  - 既に公開済みの記事scriptは書き換えない(履歴扱い)。今後のX公開ページと`build_player_html`(er019:3022)は`public_study_html(level=)`を必須にし、両levelのブロックが揃っていることを検査で強制する。
- Y/Zの新unitは葉ノードのままにする(TTSへの依存辺を張らない)。現行のDEPENDENTSもpart2は葉(er121:45-52、er062:66-70)。
- `_assert_study_ready`を`tts_a2`に付けると、文法(音声に入らない)がStd TTSを待たせる。付けるのはpages/page_verifyに限るのが妥当(Delivery)。

**O-6 Validator/test撤去: 要修正(中1・軽1)**
- 中: 置換後の検査は「自levelの節に1個」だけでは弱い。levelを取り違えたブロック(Std結果がAdv節にある等)も件数検査を通ってしまう。
  - 修正案: 共有builderの`<section>`単位で切り出し、levelごとに`verify_outputs(html_text=その節)`で4者一致(確定・結果・md・HTML)を検査する。
- 中: level既定値が暗黙に`b1b`へ落ちる箇所を撤去する。`er128:850 or "b1b"`、`_write_grammar_sidecar`の`discover_dirs(run)[0]`(er128:1255-1258)、`LEVEL_KEY`(er119_grammar_review:24, 227)。
  - 新APIではlevelを必須の引数にする。`discover_dirs(level)`はpathから推定せず、`grammar_candidates.json`の`level`欄と一致することを確認し、不一致ならfail-closed。
- 軽: `m.LEVEL`はv1読取専用の定数として残し、新コードからの参照を0件とするGrep検査をT15に追加する。

**O-7 費用: 妥当**
- 外挿は保守的で、PREGEN_MAX=8は妥当(実測の最大は4)。全候補の解説を見て決めるという要件があるため、遅延生成・上位K件だけの生成は要件違反になる。採らないのが正しい。
- 8件を超えた分は依頼書(md)に「他N件・解説未生成」と出す(フォームUIは変えない)。
- 将来の原価低減案(今回は実施しない): STEPB_PROMPTは2 ITEMを1 callで扱える(er120:149)。まとめて呼べば入力固定部の費用を削れるが、品質の同等性が未検証のためTrialが必要。

**O-8 evidence方式A: 要修正(重大)**
- 元runの事実が計画と違う。指定された3つのKP75 runはいずれもKP review待ちで止まっており、音声もHTMLも無い。
  - Y/Zはrootにcost_log・review_request等しか無い。Xの`uk_train_speaker_playback__run_kp75_ev_01`にはstudy_textも無い。
  - このためpagesまで進めるには有料TTSが要る。Y `STAGE_EST_JPY`はtts各¥30(er121:35)、Xはa2で¥7.39の先例。≤¥40は根拠を失う。
  - KCPのY evidenceでも、copy-runではpagesまで到達できなかった(EVIDENCE_Y_01 §限界)。
- Z melos kp75の元runはAdv候補0件(`n_eligible: 0`)で、Step A''は再利用されるため、Z Advは0件経路しか踏まない。受入4/5/6の非0件経路を示せない。同じ本文でも0件/1件と揺れている(A''の非決定性)。
- 修正案:
  - Familyごとに、pagesまで追加TTSなしで到達できるかを事前に確認する(read-only)。
  - 到達できなければ、kp stage以降(TTSを含む)を正式runnerで実行する。同時に費用を再見積する(おそらく¥80-150。案件見積¥300以下ならAI自律の範囲)。
  - 6セルそれぞれで、非0件経路(候補≥1→事前生成→表示→確定→公開)を最低1回実証する。0件だけのセルは「非0件はmockのみ・runtime未観測」と明記する。
  - 2件採用は最低1経路(X Adv等)でruntime実証する。Z(候補≤1)は2件のruntime実証ができないことを明記する。
  - Z Stdは、Std候補率計測で候補≥1の本文を選んで元にする。
- 「正式初回Production」の解釈: kp以降を正式runnerで初めて通すことで満たすとみなすのは妥当。方式Bを次の通常制作に相乗りさせる運用も妥当。

**O-9 失敗時成果物: 要修正(軽)**
- フォームexporter(F-5)と`grammar-show`にもfail-closedを入れる。対象は事前生成が不完全な場合・`part2_failed.json`がある場合・explanations_shaが候補docと不一致の場合で、データを出さずにエラーにする(`candidates_available`扱いにしない)。
- 前回runの古い`review_request.md`が残る場合は、上書きするか「古い」と明示する。

**O-10 実装順序: 要修正(軽)**
- F-5(フォームexporter)とF-6(KCP)は受入2〜5の前提なので、クリティカルパス上にある。
- 短縮案:
  - F-0でスキーマ契約(grammar_explanations_v1、review v2、frozen v2、result v2、`form_grammar_items`)を1枚に固定する。その上でF-1/F-2/F-3/F-5/F-6/F-8を同時に着手する。
  - Std候補率計測(≤¥7、既存関数を使うDEV script、Production非接触)を今すぐ並行で実行する。D-a・evidence元runの選定・費用見積の不確実性を、実装前に減らせる。
  - O-8の元run実現性確認(read-only)もF-1と並行で行う。
  - KCP/FORM所有ファイルの扱いは計画どおりFableが決める。

### 実装前に必須の修正(DESIGN/EVIDENCE反映)
1. v2結果のref_ja照合を置き換え(凍結の有無に関係なく、同じISSUEで検査)。ISSUEの解消手段を定義。(O-1)
2. `legacy_postselect`を「review・result ともschema v1」に限定。v1進行中runの事前生成は選定済みidだけ。(O-3)
3. フォームで文法0件のとき、同じロック内でomitを適用。ロック順・書込み順・冪等性を規定。idごとのsha。(O-4)
4. levelを必須引数にし、`b1b`既定値と`discover_dirs()[0]`を撤去。candidates docの`level`欄で一致確認。(O-6)
5. 節単位の4者一致検査。(O-6)
6. EVIDENCE_PLANの元run・費用を再設定。6セルそれぞれで非0件経路を実証、2件採用を1経路で実証。(O-8)
7. exporterと`grammar-show`のfail-closed。(O-9)

### Fableがユーザー判断に上げるべき事項
現時点ではなし。
(以下略: 条件付き事項2点はFable判断、evidence費用増額は自律範囲、HR提示変更はDECISION_LOG記録で足りる)

(Opusレビュー原文ここまで)

## 実施事項

1. **`SCHEMA_CONTRACT_01.md`(F-0、最優先・先行commit)**: `grammar_explanations.json`(v1: items[{candidate_id, level, title, explanation_md, translation_ja, explanation_sha256, explain_signature, generated_at, model_id, source=`pregen`|`stepB_generated`}], `part2_failed.json`形式)、`grammar_human_review_v2`(pick≤2、omit/human_omit/`form_submission_no_grammar`、zero_reason、selected_ids、`explanation_sha_by_id`)、`part2_grammar_v2`(items[]、本文出現順、v1読取互換)、frozen v2(items[])、`form_grammar_items`(フォームexporter/KCP from-form向け: candidate_id/level/title/explanation_full/explanation_sha256)、level必須・`grammar_candidates.json.level`一致。委任_03/04が参照する唯一の契約。commit message `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02a: schema契約F-0(文書先行)`。
2. **`DESIGN_02.md`**(DESIGN_01+Opus必須修正1〜7+Fable判定、`[O-n]`印)、`OPUS_REVIEW_01.md`(採否表)、Opus台帳記録。
3. **F-1実装(er120/er119_grammar_review)**: `pregen_stage(level, ids=None)`(直列、PREGEN_MAX=8、signature一致で再利用、失敗→`part2_failed.json`+STOP rc=3、再開で未生成分のみ)、Step B呼出点をpregenに集約(`run_part2`/finalizeからの`generate_explanation`呼出撤去、事前生成物なし=Part2Stale fail-closed、v2成果物あり+事前生成物なし=INTEGRITY)、`legacy_postselect`=review v1かつresult v1のみ、v2のref_ja照合置換(凍結有無に関係なくISSUE rc=4、解消手段2種の記録)、level必須引数化(`LEVEL_KEY`/`m.LEVEL`はv1読取専用、新コード参照0)、review v2(pick≤2/omit同一ロック内/冪等)、result v2 items[]本文出現順、autoはTOP1、HR依頼書(`er119_grammar_review_01.py`)に全候補の「文法名+解説全文」(8件超は「他N件・解説未生成」)、`grammar-show`のfail-closed、節単位4者一致検査関数`verify_outputs(level, html_text=節)`(builderへの配線は委任_03)。
4. **test(F-8核、`er120_part2_pregen_test_01.py`)**: Step B spyで呼出回数固定(pregen 1箇所)、legacy判定、INTEGRITY、ref_ja ISSUE、level必須/`b1b`既定値0件Grep、v1互換読取、review v2 pick/omit/冪等/クリック順非依存、result v2順序、PREGEN_MAX超過表示、failed再開、Prompt sha不変、既定rc=4維持(T1,T11)。既存er120 14件・er119_grammar test回帰(期待値変更は理由付きで最小)。
5. `IMPLEMENTATION_02.md`、`TEST_PLAN_02.md`(T1〜T15+委任_03/04残分)。

## 事前指定Read一覧

- `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{DESIGN_01,IMPL_PLAN_01,TEST_PLAN_01,CURRENT_FLOW_01,ADV_ONLY_INVENTORY_01}.md`、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md`(文法sidecar・M6・from-form節)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_02.md`(grammar schema)
- `er120_part2_grammar_production_01.py`(全体。特に :42-60,:118,:149-154,:540-560,:872-892,:1098-1120,:1163-1330)、`er120_part2_wiring_01.py`(全体)、`er119_grammar_review_01.py`(全体)、`er128_kp_confirmed_content_01.py:835-1000,1168-1268`(読むのみ)、`er119_isolation_test_01.py`(ALLOWED構造)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_02.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er120_*test*.py"`、`--pattern "er119_grammar*test*.py"`、`--pattern "er119_*test*.py"`、`--pattern "er128_*test*.py"`(er128側の失敗=契約変更起因なら委任_04へ引継ぎ記載)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_GPG2.md`にOPEN-559更新文案、DECISION_LOG追記文案(HR提示TOP2枠→全候補の解釈、ISSUE解消手段、evidence費用上限¥150)。

## Git

- F-0 commit(先行)+本体commit: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02: 文法解説事前生成の共通核(pregen stage・level必須・review/result v2・Step B呼出集約・ref_ja ISSUE化・legacy限定)+Opus反映DESIGN_02+test(API 0)`。trailer: `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/02`。push。

## 報告

`docs/pm/RESULT_PACKET_GPG2.md`: (0)T-0、(1)DESIGN_02変更点(O対応表)、(2)schema契約要点、(3)実装差分(ファイル:行)、(4)test結果、(5)委任_03(adapter/ページ/Validator)・委任_04(KCP/FORM接続)への引継ぎ(契約・関数名・残作業)、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾10行要約。