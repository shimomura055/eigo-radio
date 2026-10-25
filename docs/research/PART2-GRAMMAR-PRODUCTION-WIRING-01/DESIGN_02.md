# DESIGN_02(Part 2 Production module: Opus条件Aレビュー反映)

管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_02 / 日付: 2026-10-25 / Status: **APPROVED_FOR_PRODUCTION(ユーザー2026-10-25)・module修正済み・未配線(PRODUCTION_WIREDではない)**。API 0・実費0円。`er019/er026/er062/er119/er006`・公開ページ・`er0XX_output/`既存成果物は無改変。
前提: `DESIGN_01.md`(原設計。原文は消さない)、`OPUS_REVIEW_01.md`(レビュー逐語)。実装: `er120_part2_grammar_production_01.py`(module内で完結する修正のみ)、`er120_part2_grammar_production_01_test_01.py`(99 PASS)。
Fable確定判断(委任_02 §2): M-1はTrial-07どおりに戻す(採用)、M-2〜M-7・R-1〜R-7採用、R-8は文面変更なし、C-6のOPEN-484追記採用。**Advancedのみ適用・Standard非適用**(closeout表に明記、§7)。

## 1. DESIGN_01との差分表
| 項目 | DESIGN_01(委任_01) | DESIGN_02(本委任) | 根拠 |
|---|---|---|---|
| 画面の【日本語訳】の出所(D-4) | 常にT1訳を1 call生成し、Step Bへ参考訳として渡し、画面にもT1訳を表示 | **D-4を撤回**。画面の訳=Step B自身の【日本語訳】(Trial-07)。`ref_ja`はPart 1のT1訳pool(`ref_ja_pool`)に英文が一致(`_qn`正規化の完全一致)したときだけStep Bへ渡す。pool一致なし=参考訳なし・**T1 callなし** | M-1。`run_trial_07.py:161-163`、`OUTPUT_07_melos_r1_USER.md` |
| LLM call数/セット | 3(A''+T1+B) | **2**(A''+B) | M-1 |
| `translate_sentence` / `translate_call_fn` / `translation_source=T1` | あり | **削除**(`translation_source="stepB"`、`ref_ja`/`ref_ja_source`を追加) | M-1 |
| `explain_signature` | cand+ref_ja(T1訳) | cand+`ref_ja`(pool一致時のみ)。poolが変われば署名が変わり失効 | R-7 |
| `require_fresh_part2` | 本文sha/署名/単一span/解説非空/候補ID自己整合 | `candidates_doc`・`grammar_review`を**必須**引数に追加し、(i)status前進可 (ii)`candidates_sha256`一致 (iii)選定=確定のchoiceに対応する候補 (iv)`explain_signature`を候補docの材料欄から再計算 (v)`selection_signature`再計算。ZEROも確定と候補docに結びつく。`ref_ja_pool`を渡せばpool一致も検査 | M-2, R-7 |
| `mode` | `"auto"`/`"wait"`文字列 | `"wait"`(既定)か、**er119の明示auto宣言dict**のみ。文字列`"auto"`・欠落dict・不正sourceは`Part2ReviewError` | M-3 |
| 待機点 | 1段(`run_part2`) | 2段に分離: **抽出**(`resolve_candidates`/`cand_stage_input_sha`、KP候補生成と同じ待機点の前)と**finalize**(`finalize_part2`、再抽出なし・`Part2PendingReview`専用例外・`final_stage_input_sha`) | M-3, M-4 |
| NG照合 | `rejected_ids`(id一致のみ、run内) | NG entry(`candidate_id`/`sentence`[正規化・段落番号無視]/`span`[同一段落内の範囲の重なり・包含])の**3方式**。`ng=`引数(共有registry I/F)。除外は`filtered_by_ng`に方式付きで記録 | M-5(a)(b) |
| 候補枯渇 | `select_from_candidates`が自動で`ZERO(no_candidate)` | 枯渇(全候補がNGで尽きた)=`RESELECT_EXHAUSTED`で待機(auto宣言があっても自動確定しない)。選択肢は`omit`(→ZERO/`human_rejected_all`)か`reextract`(上限内) | M-5(c) |
| 再選定の上限 | なし | `reselect_count<=2`(再抽出も算入)、再抽出は最大1回。超過は`Part2ReselectLimit`(=`Part2Error`)でSTOP。上限到達後は選択肢から`reselect`/`reextract`を外す | M-5(d) |
| TOP1/TOP2の扱い | 再選定で外した候補を`rejected_ids`に | reselectで外したTOP1/TOP2=**NG**(理由必須)。top2選択時のTOP1=**NOT_SELECTED**(NGではなく、再選定でも除外されない)。`verdicts`で区別 | M-5(e) |
| 0件の確定status | (er119未定) | 待たずに確定するZEROは`NO_CANDIDATE_UNREVIEWED`(`REVIEWED`ではない)。`UNREVIEWED_AUTO_ADOPTED`(auto_top1)も「レビュー済み」に数えない(`summarize_review_statuses`) | M-6 |
| 理由の記録 | なし | top2/reselect/omit/reextractは`reason`必須。`history`に却下候補の文・分類・tier・`tier_table_row`を残す。`accept_ai`はtop1のみ・`accepted_candidates_sha256`を記録(AUTOと区別) | M-6 |
| 失敗記録 | なし | `write_failed_record`→`part2_failed.json`(`next_command`付き)。再開は`finalize_part2`(Step A''を呼ばない) | M-7 |
| Part 1直後の連結 | `render_html_block(include_css=False)`固定 | `compose_study_html(part1_html, result)`(`include_css = not part1_html`) | R-1 |
| 一致検証 | なし | `verify_selection_matches_outputs(kind="grammar")`: 確定↔result↔md↔HTML | R-3 |
| TOP候補の重複除外 | 同一(段落,文)のみ | 同一段落内で範囲が重なる/包含する候補も除外。候補1件なら`choices`から`top2`を外す | R-4 |
| 29標本の回帰 | 19/4/6 | **19/4/6のまま**(R-4でTOP1・候補数分布とも不変。`test_R4_does_not_change_top1_on_29_samples`) | R-4 |

## 2. 確定record(`grammar_human_review.json`、`kp_human_review_v1`と同形・`kind="grammar"`)
`finalize_review_record(doc, sel, decision=…, prior_history=…)`が単一builder(er119が独自に作る場合も同形・`grammar_selection_signature`を共用)。
```
{"schema":"grammar_human_review_v1","kind":"grammar","level":"Advanced","text_sha256":"…","candidates_sha256":"…",
 "status":"REVIEWED|UNREVIEWED_AUTO_ADOPTED|NO_CANDIDATE_UNREVIEWED",      // 下流が進めるのはこの3つのみ
 "mode_declaration":{mode:"auto",declared_by,declared_at,reason,source}|null,
 "selection":{"choice":"top1|top2|omit|none","candidate_id":"g…"|null,"zero_reason":null|"no_candidate"|"human_omit"|"human_rejected_all"},
 "accept_ai_default":false,"accepted_candidates_sha256":null,
 "verdicts":{"g…":"SELECTED|NOT_SELECTED|NG|null"},     // null=未レビュー(AUTO)
 "ng":[{"candidate_id","para","sentence","span","feature_class","tier","reason","by","source","at"}],
 "reselect_count":0,"reextract_count":0,"history":[{"at","event":"reselect|reextract|finalize","by","detail":{…}}],
 "selection_signature":"sha256(kind,level,text_sha,candidates_sha,status,selection,verdicts,mode_declaration,ng ids)"}
```
PENDING/RESELECT系の途中状態はこのrecordを作らない(moduleは待機statusだけ返す。er119側が`PENDING_REVIEW`等を持つ)。
消費側の期待結果(`_expected_outcome`): `UNREVIEWED_AUTO_ADOPTED`→候補docのTOP1(source=auto_top1、auto宣言必須) / `REVIEWED`+top1|top2→該当候補(source=human_top1|top2) / `REVIEWED`+omit→ZERO(`human_omit`は候補あり、`human_rejected_all`は枯渇) / `NO_CANDIDATE_UNREVIEWED`→ZERO(`no_candidate`、候補0かつ`filtered_by_ng`空)。

## 3. er119に依存する項目の接続仕様(委任_03でKP HR側と突き合わせる)
| 項目 | module側(本委任で実装済み) | er119側へのI/F要求 |
|---|---|---|
| M-3 mode取得 | `normalize_mode`: `"wait"`/`None`か明示宣言dictのみ。関数既定に`auto`なし(testで全関数を走査) | `read_mode_declaration()`(KP HR M-6の失効規則含む)が上記dict形(`mode,declared_by,declared_at,reason,source∈{cli_runner_arg,declare_absent_cli}`)を返す**唯一の読取点**であること。runner引数・hooks・環境変数からdictを組み立てる経路をrunner側に作らない(委任_03で静的test) |
| M-5(a) 共有NG registry | `ng=`引数(NG entryのlist)をそのまま受ける(`resolve_candidates`/`apply_ng`/`reextract_candidates`)。entryは`ng_entry_from_candidate`の形 | `family+slug+level`単位の共有storeから読み、`reselect`時に`doc["ng"]`の増分を書き戻す。copy-runでNGを引き継ぐ。書込は排他lock(KP HRと共通) |
| M-6 status値 | `REVIEWED`/`UNREVIEWED_AUTO_ADOPTED`/`NO_CANDIDATE_UNREVIEWED`と`summarize_review_statuses` | 共通核のstatus enumに`NO_CANDIDATE_UNREVIEWED`を追加(grammar専用)、遷移: 候補0件→(待たず)`NO_CANDIDATE_UNREVIEWED`。`PENDING_REVIEW`/`RESELECTION_REQUESTED`/`STALE`は下流fail-closed(testで固定済み) |
| 署名 | `grammar_selection_signature(review)` | 共通核が`kind="grammar"`のsignatureとして同関数を使う(または同一payloadで実装し突合testを追加) |
| 提示 | `review_request(doc)`(`choices`が状態で変わる: 候補1件→top2なし、上限到達→reselect/reextractなし、枯渇→`omit`+`reextract`) | `*_review_request.md`の1ファイルにKPと文法のpendingをまとめ、**rc=4を1回**にする(M-3) |
| 決定入力 | `{"choice","candidates_sha256","reason","by","accept_ai"}`。`candidates_sha256`が現docと違えばstale拒否 | CLI(`top1/top2/reselect/omit/reextract`・`--accept-ai`・`--reason`必須判定)がこのdictを渡す |

## 4. 2段構成(M-3/M-4)とrunner接続方針(委任_03で実装)
- 段A「候補抽出」(`part2_cand_b1b`、input=`cand_stage_input_sha(paragraphs,label)`): 本文確定直後、KP候補生成と同じ待機点**の前**。`resolve_candidates`→`grammar_candidates.json`保存。
- 待機: KPのpendingと文法のpendingを1つの`*_review_request.md`/rc=4へまとめる(人の待機は1回)。
- 段B「finalize」(`part2_b1b`、input=`final_stage_input_sha(paragraphs,label,grammar_review)`): 再開後。`finalize_part2`(再抽出なし)→`part2_result.json`・md。待機系は`Part2PendingReview`で**出力を書く前に**抜ける。
- Z: `DEPENDENTS["r2"]`へ`part2_cand_b1b`、`part2_cand_b1b`→`part2_b1b`。`--regenerate-stage part2_b1b`=保存済み候補+現在の確定からの再finalize(再抽出なし)+子孫stale化、再抽出はreselect CLIのみ。`ALL_STAGE_NAMES`と`--regenerate-stage`のchoices(`er026:2499`)へ両stage。
- X: 失敗/PENDING後の案内は`--stage study_text`(Part 2を含むよう拡張)か専用stageの**1つだけ**。通常の`scaffold`/`all`再開はsupport(`er019:657`)・KPを再生成するため案内しない(M-7)。失敗は`part2_failed.json`+rc=3。再開時のsupport・KP・Step A''の呼出が0であることを統合testで固定。
- 使う側の確認(M-2): Z=`load_level_inputs`(b1bのみ。R-5)・`stage_pages`・`stage_page_verify`、X=`tts`/`assemble`/`player`入口と公開ページbuilder。いずれも`require_fresh_part2(..., candidates_doc=, grammar_review=)`。R-3の`verify_selection_matches_outputs`はZ `stage_page_verify`とX player末尾。R-2: Part 2描画は共通builder(`compose_study_html`を呼ぶ1関数)だけ。Standardページから呼ばない静的test。
- R-6: Zでは`ctx.stage_context("part2_*")`でstageタグ。時間の訂正: 現行の直列runnerでは「KPと並列で追加時間≒0」は成立しない。**+約30〜60秒/セット**(A'' 1 call+B 1 call。T1訳callが無くなった分だけ約5〜10秒短縮の見込み)。

## 5. M-1の確認事項(Trial-07照合)
- `run_trial_07.py:161-163`: `for it in inp: if t4._qn(it["sentence"]) == t4._qn(verb): f["ref_ja"] = it["sentence_ja"]` → `lookup_ref_ja`が同一規則。`OUTPUT_07_melos_r1_USER.md`: 画面の【日本語訳】はStep B出力。→ `render_markdown`/`render_html_block`は`EXPLANATION_HEADINGS`全4見出し(日本語訳含む)をStep B出力から描画。
- Step B promptの本文は不変(Prompt byte一致test維持。`参考訳(別工程で確定済み)`行はref_jaがあるときだけ追加される=Trial-07と同一)。
- ユーザー承認のT1方式はPart 1に限る決定(ユーザー確認不要となる形に戻した)。

## 6. 残リスク・未確認
- Zの`a63.build_pages`がstudy_htmlをb1bページだけに入れるか、X `--stage study_text`の現行前提(KP成功必須)をKP非依存のPart 2とどう分けるか、`verify_selection_matches_outputs`のHTML照合(ページbuilderが包んだ後も部分文字列として残るか)は**委任_03でrunnerを読んで確定**(本委任はrunnerを読まず触らない。Opus未確認事項と同じ)。
- er119の`mode_declaration`・registry・lockのI/F(§3)はKP HR委任_02の実装後に突合。
- KP HR `DESIGN_01.md` §kの「コーナーなし」(AUTO=適格0なら…)記述は別agent編集中のため触らない。Trial実出力(`ZERO_P2`文面を表示)が正で、委任_03で整合する。

## 7. closeout表への明記事項
| 項目 | 内容 |
|---|---|
| 適用レベル | **Advancedのみ**(Trial-07/08の全実績がAdvanced、Part 1前例と整合)。Standard(a2)は新仕様のため非適用(ユーザー確認不要・報告事項、Opus確認項目2) |
| X/Y/Z | X/Z=module準備済み・runner未配線(委任_03)、Y=正式入口なし(OPEN-484で追跡) |
| 承認対象外(不変) | Tier内順位・HIGH判定・OTHER拡張・Step A''/Step B Promptの文言(sha `51912fe1…`/`59588b59…`不変) |
