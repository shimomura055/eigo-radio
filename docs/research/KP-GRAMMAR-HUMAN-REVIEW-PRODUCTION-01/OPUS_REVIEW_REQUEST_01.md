# OPUS_REVIEW_REQUEST_01(条件A: 新しい構造・処理フロー設計の独立技術レビュー依頼)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_01 / 日付: 2026-10-25 / 依頼先: Opus(独立レビュー。`PM_GOVERNANCE.md` 11-3条件A)
対象: `DESIGN_01.md`(本dir)。事実根拠: `EXISTING_SPEC_CHECK_01.md`。ユーザー指示原文: `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md`。
レビュー対象は設計のみ(実装前)。Production file変更0。以下の論点ごとに「OK/要修正/代替案」と根拠(ファイル:行)を返してください。**必須(M)/推奨(R)の分類**もお願いします。

## レビュー観点の背景(30秒版)
- 新工程=「KP候補をTOP 8で順位付け→Humanが3件(KP)+5件(単語解説=Part 1、Advのみ)を選ぶ→確定結果を後続へ」。Human不在時は**明示宣言があるときだけ**AI順位の上位(KP3/解説5)で継続。
- 接続面は据え置き: 確定KPは従来どおり`keywords_canonicalized.json`(rank 1..n)。Part 1だけ別fileの`vocab_confirmed.json`(5件)を読む。
- 既存のKP外側retry/canon/gloss/Redundancy/CMU/SRC D1は**候補段階で適用**(基準不変)。

## 論点(優先順)
### O-1 状態機械の安全性(最重要)
1. **NG復活防止**: 6層の防御(DESIGN §c-3)で十分か。`candidate_id`+`phrase_key`+`used_form_key`の3キー照合で、基本形化・人称一般化・大文字小文字・活用で表層が変わるケースを取りこぼさないか。NG registryを記事ID単位で保持し、本文が変わっても同句に適用する方針の副作用(本文変更で別文脈の同句がNGのまま)は許容か。
2. **未レビューとNGの区別**: `verdict=null / NOT_SELECTED / NG`の3値+`UNREVIEWED_AUTO_ADOPTED`と`REVIEWED(accept_ai_default)`の区別は十分か。AUTO後に事後Reviewで`REVIEWED`へ遷移できる設計(降格遷移なし)で矛盾はないか。
3. **誤自動確定の防止**: autoは「明示宣言のみ」(runner引数`--kp-review auto`、`declare-absent` CLI)。読取点を`read_mode_declaration()`1つに限定する方針で、環境変数・設定dict・既定引数・テスト用hookからの経路が残らないか(hook注入は`kp_fn`等のtest用が既存にある。`er026…:1486-1493`)。期限付き自動切替を採らない判断(DESIGN §b-2)への異論。
4. **競合**: Human操作(select/reselect)と再実行(resume)が同時に走る場合のfile競合(`kp_human_review.json`のatomic更新・署名)、RESTART_STORM(同一run 5分3起動で自動STOP、`PM_GOVERNANCE.md:3496`)との相互作用(待機rc=4の再起動が近接した場合)。
### O-2 既存KP機構との重複・整合
5. 既存の外側retry(`run_kp_with_outer_retry`、`er003_v1_n3_01_scaffold_generate.py:729-872`)を**候補生成の内部で再利用**する設計の妥当性。`excluded`seedにNGを入れる方法、`failures`/`red_attempt`カウンタ、`stop_check_fn`(STOP sentinel確認)との整合。
6. **item単位除外への改訂(O-3の前提)**: 現行は「1件でも不適合→attempt全体INVALID→再選定」。TOP 8でそのままでは再選定が頻発する。「Gate判定基準は不変、不適合itemだけ`dropped`へ」は品質を実質緩めないか(例: 8件中3件が不適合でも有効5件でattempt成功となり、旧規則なら再選定していたケースで質が下がる懸念)。目標数(KP3/vocab5)未満のみretryとする閾値の妥当性。
7. canonicalization 3状態(PASS/REVIEW_REQUIRED/INVALID)を候補単位に写す方法。応答全体が`INVALID`のときの扱い(現行canon gateのretry)と、REVIEW_REQUIRED itemを`qa_fail`旗付き・AUTO対象外・Human選択可とする解釈が、承認済み仕様「REVIEW_REQUIREDは自動採用しない・人間確認後に採用可」およびOPEN-504の是正(採用はPASSのみ)と矛盾しないか。
8. **Redundancy QAを候補全体(≤8)で1回**実行し、以後はpair照合のみ(API 0)とする設計。Redundancy QA promptは5件想定の記述(`developer_message_for(n)`で件数語のみ可変)で、8件入力・28ペアの判定品質は保たれるか。「選択集合の再判定を省略」して取りこぼすリスク(Human選択の3件間で候補全体判定が見落とした重複)。
9. KP 3-ASR vote(`er104`)=音声合否判定は無変更の前提。確定KPが変わっても`phrase`単位のMaster Audio Storeと票reuseは影響を受けないか(`er104_kp_vote_reuse_01.py`)。
### O-3 Prompt 2-R(`DESIGN §a-1`)
10. Prompt 2は一字一句固定・sha固定のユーザー承認資産。TOP 8のための最小差分(「3つ」→「学習価値の高い順に最大8つ」/条件6/理由1文)で**上位3件の選定品質が変わらないこと**をどう担保するか(DESIGN: 保存済み約12記事での新旧比較、悪化時の代替P2=2 call構成)。比較設計(指標・合格基準・事前登録)の助言。理由出力(`reason_ja`)追加によるTop選定への影響。
### O-4 署名・reuse・resume整合
11. `selection_signature`の構成(text_sha|candidates_sha|kp ids|vocab ids|ng ids|status)と、既存の下流署名(Z `ensure_stage`のinput_sha=`_sha(text)`、`kp_expl_b1b`sig、Part 1 `phrases_signature`、T1署名)との**加算関係**に抜け・二重化がないか。特にZ `ensure_stage("kp_<lv>")`のinput_shaが本文のみであるため、**Human確定が変わっても`kp_<lv>`のreuse判定が通ってしまう**危険(出力ファイルshaは確定後に変わるため不一致でSTOPするはずだが、`_sync_kp_result`相当の来歴更新が必要か)。
12. `--regenerate-stage kp_<lv>`が確定済みでSTOPする挙動変更(従来の黙示的再抽選の廃止)で、既存運用手順(`CURRENT_SPEC.md:2052`等)に副作用はないか。X `_kp_already_generated`(1レベル1回)との整合。
### O-5 Part 1の5件化の副作用
13. `vocab_confirmed.json`を分離してKP音声のsegmentが5件に増えないようにする方式の妥当性。追加2件は`keywords_canonicalized.json`に入らないため、**gloss gate・人称gate・SRC gate・CMU・解説(`kp_explanations`)の対象外になる**。候補段階のGate(gloss再整合・SRC D1・人称整合`_gloss_person_gate`)が追加2件にも等価に適用されると言えるか(Zの`_gloss_person_gate`・`_src_gate`は`keywords_canonicalized.json`を読む実装)。
14. Part 1の消費者(`study_html_for_audio_dir`/X `_part1_kp_items`/Z `_kp_items_b1b`/`_assemble_study_rows`/Z `stage_pages`)を`part1_items(kp_dir)`に一本化する方針で、旧run互換(`vocab_confirmed.json`無し→KP items)に問題はないか。公開済みページの再生成方針は本件で変更しない前提(`CURRENT_SPEC.md:2052`)。
### O-6 文法部分の分離可否・Family Y
15. 共通核を`kind`非依存に作り、grammarの薄い層はPart 2採用確認(G-1)まで実装しない分離方針の妥当性。Part 2のProduction配線(Step A''/B・描画)が前提となる以上、核のみ先行しても未使用コードにならないか。TOP 2の定義(`select_tiered`順の先頭2件、同一文除外)はTrial-07「2件目ロジック廃止」(件数を満たすための選定をしない)と矛盾しないか(TOP 2は同時採用でなく代替案)。
16. Family Y: 共有`sc.run_key_phrases`を変えずに新moduleで入る構造で、Y正式入口新設時に本Human Reviewを漏れなく通せるか。OPEN-484への追記内容(受入条件(g))の十分性。Yを「未整備」と追跡し`PRODUCTION_WIRED`としない扱いでよいか。
### O-7 運用切替の妥当性
17. 「無宣言=待機(rc=4)」で9記事/日の運用が成立するか(HR負担見積: 約30〜55分/日、推定)。`--accept-ai`を`REVIEWED`扱い(AUTOと区別)にする判断。`declare-absent`の一括宣言が「誤った一括自動確定」を生む余地(宣言対象の限定・記録の十分性)。
18. 実装の優先順・段階化: 核(状態機械+CLI)→X→Zの順で、各段のruntime evidence(BUDGET_PLAN_01の4 run)で足りるか。

## 添付・参照
- 設計: `DESIGN_01.md`、既存仕様: `EXISTING_SPEC_CHECK_01.md`、検証計画: `TEST_PLAN_01.md`、費用: `BUDGET_PLAN_01.md`
- 主要コード: `er105_kp_fulltext_selector_01.py`、`er003_v1_n3_01_scaffold_generate.py`(`run_key_phrase_canonicalization:475`/`run_key_phrase_redundancy_qa:557`/`run_kp_with_outer_retry:729`/`run_key_phrases:875`)、`er019_family_x_audio_production_runner_01.py`(`run_theme_scaffold:608`)、`er026_family_z_fiction_production_runner_01.py`(`stage_kp:1693`)、`er062_family_z_writer_01.py`(`ensure_stage:690`/`run_kp_stage:1309`)、`er003_kp_general_explanation_01.py`、`er003_kp_source_sentence_ja_01.py`
- Fableが判断する事項(Opusの技術判断対象外): I-1(Std単語解説)、G-1〜G-3(Part 2採用承認)、I-2(Prompt固定の扱い)。Opusには「技術的に成立するか」「リスク」のみ意見を求めます。

## 回答形式(希望)
各論点 `O-n: 判定(OK/要修正/代替案) / 根拠 / 必須(M)か推奨(R)か / 実装時の確認test`。全体として「実装着手可/修正後可/再設計」の総括を1行。
